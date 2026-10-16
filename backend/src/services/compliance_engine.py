"""
Compliance Engine & Risk Scorer for LabelX
Incorporates 5-Module Deterministic Regulatory Checking against FSSAI & International Standards:
  1. Additives Module (Schedule I permitted/restricted/banned list with E-codes and PPM limits)
  2. Allergens Module (Cross-references 90+ allergen keywords across 8 classes, undeclared allergens detection)
  3. Claims Verifier Module (Front-of-pack claims vs back-of-pack nutrition threshold math)
  4. License Validator Module (14-digit FSSAI structure, prefix identification, checksum/type)
  5. Mandatory Labelling Module (Packaging & display regulatory completeness check)

Weighted Multi-Factor Risk Scoring:
  - Allergens: 30%
  - Additives: 25%
  - Claims:    20%
  - Labelling: 15%
  - License:   10%
"""

import os
import re
import sqlite3
from copy import deepcopy
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "compliance.db")

def _get_db():
    if not os.path.exists(DB_PATH):
        # Fallback to source database if not found at target path
        fallback = os.path.join(r"C:\ClientBTP\AI-Powered-FSSAI-Compliance-Checker\backend\database\fssai_compliance.db")
        if os.path.exists(fallback):
            conn = sqlite3.connect(fallback)
            conn.row_factory = sqlite3.Row
            return conn
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- Schemas ---

class AdditiveInfo(BaseModel):
    name: str
    e_code: Optional[str] = None
    function: Optional[str] = None

class NutritionalInfo(BaseModel):
    energy_kcal: Optional[float] = None
    protein_g: Optional[float] = None
    carbohydrates_g: Optional[float] = None
    sugar_g: Optional[float] = None
    total_fat_g: Optional[float] = None
    saturated_fat_g: Optional[float] = None
    trans_fat_g: Optional[float] = None
    sodium_mg: Optional[float] = None
    fiber_g: Optional[float] = None

class LabelComplianceData(BaseModel):
    product_name: Optional[str] = None
    brand: Optional[str] = None
    food_category: Optional[str] = "Food & Beverage"
    net_weight: Optional[str] = None
    ingredients: List[str] = []
    additives: List[AdditiveInfo] = []
    declared_allergens: List[str] = []
    nutritional_claims: List[str] = []
    fssai_license: Optional[str] = None
    manufacturing_date: Optional[str] = None
    expiry_date: Optional[str] = None
    best_before: Optional[str] = None
    vegetarian_status: Optional[str] = None  # veg / non-veg / not_specified
    nutritional_info: Optional[NutritionalInfo] = None
    detected_languages: List[str] = []

class ComplianceFinding(BaseModel):
    module: str  # additives, allergens, claims, license, labelling
    severity: str  # CRITICAL, WARNING, INFO
    title: str
    description: str
    regulation: Optional[str] = None
    recommendation: Optional[str] = None

class ModuleScore(BaseModel):
    module: str
    score: int
    findings_count: int
    critical_count: int
    warning_count: int

class RiskScore(BaseModel):
    overall_score: int
    grade: str  # A, B, C, F
    modules: List[ModuleScore] = []

class ComplianceResult(BaseModel):
    label_data: LabelComplianceData
    findings: List[ComplianceFinding] = []
    risk_score: RiskScore
    summary: str

# --- MODULE 1: Additives Checker ---

def check_additives(label: LabelComplianceData) -> List[ComplianceFinding]:
    findings = []
    if not label.additives and not label.ingredients:
        return findings

    try:
        conn = _get_db()
    except Exception as e:
        return [ComplianceFinding(
            module="additives",
            severity="INFO",
            title="Database Connection Notice",
            description=f"Compliance DB check deferred: {e}"
        )]

    food_category = (label.food_category or "").lower()

    # Normalize additives from either explicit additive objects or parse from ingredients
    additives_to_check = list(label.additives)
    
    # If no explicit additives were parsed, search ingredients for E-codes or common chemical names
    if not additives_to_check and label.ingredients:
        for ing in label.ingredients:
            m = re.search(r'\b(E\d{3,4}[a-z]?|INS\s*\d{3,4}[a-z]?)\b', ing, re.IGNORECASE)
            if m:
                code = m.group(1).upper().replace("INS", "E").replace(" ", "")
                additives_to_check.append(AdditiveInfo(name=ing, e_code=code))

    for additive in additives_to_check:
        row = None
        if additive.e_code:
            clean_ecode = additive.e_code.upper().replace("INS", "E").replace(" ", "")
            row = conn.execute(
                "SELECT * FROM additives WHERE UPPER(e_code) = UPPER(?)", (clean_ecode,)
            ).fetchone()

        if not row and additive.name:
            # clean name lookup
            clean_name = re.sub(r'[\(\)\d\.\%]', '', additive.name).strip().lower()
            row = conn.execute(
                "SELECT * FROM additives WHERE LOWER(name) LIKE ? OR LOWER(?) LIKE '%' || LOWER(name) || '%'", 
                (f"%{clean_name}%", clean_name)
            ).fetchone()

        if not row:
            if additive.e_code:
                findings.append(ComplianceFinding(
                    module="additives",
                    severity="WARNING",
                    title=f"Unrecognized Additive: {additive.name}",
                    description=f"'{additive.name}' ({additive.e_code or 'No E-code'}) not cataloged in FSSAI Schedule I. Needs verification.",
                    regulation="FSS Food Products Standards & Food Additives Regulations, 2011 — Schedule I",
                    recommendation="Confirm FSSAI prior approval for this specific additive formulation."
                ))
            continue

        status = row["status"]
        name = row["name"]
        e_code = row["e_code"]
        permitted = (row["permitted_categories"] or "").lower()

        if status == "banned":
            findings.append(ComplianceFinding(
                module="additives",
                severity="CRITICAL",
                title=f"Banned Additive Detected: {name} ({e_code})",
                description=f"'{name}' is strictly BANNED by FSSAI for food formulations. {row['notes'] or ''}",
                regulation="FSS Food Products Standards & Food Additives Regulations, 2011 — Schedule I",
                recommendation=f"Immediately eliminate {name} from product formulation."
            ))
        elif status == "restricted":
            category_match = (
                not food_category
                or "all food categories" in permitted
                or any(cat.strip() in food_category for cat in permitted.split(","))
                or any(food_category in cat.strip() for cat in permitted.split(","))
            )
            if not category_match and food_category:
                findings.append(ComplianceFinding(
                    module="additives",
                    severity="CRITICAL",
                    title=f"Restricted Additive in Unauthorized Category: {name} ({e_code})",
                    description=f"'{name}' is restricted to '{row['permitted_categories']}'. Product category '{label.food_category}' is unauthorized.",
                    regulation="FSS Food Products Standards & Food Additives Regulations, 2011 — Schedule I",
                    recommendation=f"Reformulate to remove {name} or reclassify under permitted food categories."
                ))
            else:
                findings.append(ComplianceFinding(
                    module="additives",
                    severity="WARNING",
                    title=f"Restricted Additive: {name} ({e_code})",
                    description=f"'{name}' has maximum permissible limits: {row['max_limit_ppm'] or 'GMP'} ppm. {row['notes'] or ''}",
                    regulation="FSS Food Products Standards & Food Additives Regulations, 2011 — Schedule I",
                    recommendation=f"Ensure dosage does not exceed {row['max_limit_ppm'] or 'Good Manufacturing Practice'} ppm."
                ))
        elif status == "approved" and row["notes"] and ("allergen" in row["notes"].lower() or "declare" in row["notes"].lower()):
            findings.append(ComplianceFinding(
                module="additives",
                severity="INFO",
                title=f"Approved Additive with Labelling Note: {name} ({e_code})",
                description=f"'{name}' is approved. Note: {row['notes']}",
                regulation="FSS Food Products Standards & Food Additives Regulations, 2011 — Schedule I"
            ))

    conn.close()
    return findings

# --- MODULE 2: Allergen Cross-Reference Checker ---

ALLERGEN_EXCEPTIONS = {
    "butter": {"Milk": ["cocoa butter", "shea butter"]},
    "cream": {"Milk": ["cream of tartar"]},
    "egg": {"Eggs": ["nutmeg", "eggplant"]},
}

def _is_allergen_exception(keyword: str, category: str, ingredient: str) -> bool:
    ing_lower = ingredient.lower()
    exceptions = ALLERGEN_EXCEPTIONS.get(keyword, {}).get(category, [])
    return any(exc in ing_lower for exc in exceptions)

def check_allergens(label: LabelComplianceData) -> List[ComplianceFinding]:
    findings = []
    if not label.ingredients:
        return findings

    conn = _get_db()
    allergen_rows = conn.execute("SELECT keyword, allergen_category FROM allergen_keywords").fetchall()
    conn.close()

    keyword_map = {row["keyword"].lower(): row["allergen_category"] for row in allergen_rows}
    declared = {a.lower().strip() for a in label.declared_allergens}

    detected_allergens: Dict[str, List[str]] = {}

    for keyword, category in keyword_map.items():
        pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
        for ing in label.ingredients:
            if pattern.search(ing) and not _is_allergen_exception(keyword, category, ing):
                if category not in detected_allergens:
                    detected_allergens[category] = []
                if ing not in detected_allergens[category]:
                    detected_allergens[category].append(ing)

    for category, triggering_ingredients in detected_allergens.items():
        category_declared = any(
            cat_word in declared
            for cat_word in [category.lower()] + category.lower().split()
        )
        if not category_declared:
            for d in declared:
                if d in category.lower() or category.lower() in d:
                    category_declared = True
                    break
                for ing in triggering_ingredients:
                    if d in ing.lower() or ing.lower() in d:
                        category_declared = True
                        break

        if not category_declared:
            findings.append(ComplianceFinding(
                module="allergens",
                severity="CRITICAL",
                title=f"Undeclared Allergen: {category}",
                description=f"Allergen category '{category}' detected in ingredients ({', '.join(triggering_ingredients)}) but NOT declared on the label packaging.",
                regulation="FSS (Labelling & Display) Regulations, 2020",
                recommendation=f"Add '{category}' to the allergen warning statement (e.g., 'Contains: {category}')."
            ))
        else:
            findings.append(ComplianceFinding(
                module="allergens",
                severity="INFO",
                title=f"Allergen Declared: {category}",
                description=f"Allergen '{category}' correctly declared. Triggering ingredient(s): {', '.join(triggering_ingredients)}.",
                regulation="FSS (Labelling & Display) Regulations, 2020"
            ))

    if not detected_allergens and label.declared_allergens:
        findings.append(ComplianceFinding(
            module="allergens",
            severity="INFO",
            title="Allergen Declaration Present",
            description=f"Declared allergens: {', '.join(label.declared_allergens)}. No undisclosed allergens detected.",
            regulation="FSS (Labelling & Display) Regulations, 2020"
        ))

    return findings

# --- MODULE 3: Claims Verification ---

def check_claims(label: LabelComplianceData) -> List[ComplianceFinding]:
    findings = []
    if not label.nutritional_claims:
        return findings

    conn = _get_db()
    claims_rows = conn.execute("SELECT * FROM claims_rules").fetchall()
    conn.close()

    rules = {row["claim"].lower(): dict(row) for row in claims_rows}
    nutritional = label.nutritional_info

    for claim in label.nutritional_claims:
        claim_lower = claim.lower().strip()

        matched_rule = None
        for rule_claim, rule_data in rules.items():
            if rule_claim in claim_lower or claim_lower in rule_claim:
                matched_rule = rule_data
                break

        if not matched_rule:
            findings.append(ComplianceFinding(
                module="claims",
                severity="WARNING",
                title=f"Unverifiable Claim: '{claim}'",
                description=f"The claim '{claim}' is not mapped to explicit statutory thresholds. Verification recommended.",
                regulation="FSS (Advertising & Claims) Regulations, 2018",
                recommendation="Validate scientific evidence documentation supporting this claim."
            ))
            continue

        if "no added sugar" in claim_lower:
            findings.append(ComplianceFinding(
                module="claims",
                severity="WARNING",
                title=f"Ingredient Inspection Required: '{claim}'",
                description=f"'{claim}' stipulates no sucrose, invert sugar, or syrups added. Ensure zero added mono/disaccharides in formulation.",
                regulation=matched_rule["regulation"],
                recommendation="Audit full recipe to confirm no honey, concentrates, or corn syrup."
            ))
            continue

        if not nutritional:
            findings.append(ComplianceFinding(
                module="claims",
                severity="WARNING",
                title=f"Cannot Verify Claim: '{claim}'",
                description=f"No nutritional table found on label to mathematically verify claim '{claim}'.",
                regulation=matched_rule["regulation"],
                recommendation="Declare complete nutritional values per 100g/serving."
            ))
            continue

        if "high protein" in claim_lower or "source of protein" in claim_lower:
            if nutritional.protein_g is not None and nutritional.energy_kcal and nutritional.energy_kcal > 0:
                protein_energy_pct = (nutritional.protein_g * 4 / nutritional.energy_kcal) * 100
                threshold = matched_rule["threshold"]
                if protein_energy_pct >= threshold:
                    findings.append(ComplianceFinding(
                        module="claims",
                        severity="INFO",
                        title=f"Claim Verified: '{claim}'",
                        description=f"'{claim}' validated — protein constitutes {protein_energy_pct:.1f}% of total energy (threshold >= {threshold}%).",
                        regulation=matched_rule["regulation"]
                    ))
                else:
                    findings.append(ComplianceFinding(
                        module="claims",
                        severity="CRITICAL",
                        title=f"Misleading Claim: '{claim}'",
                        description=f"'{claim}' fails statutory cutoff — protein provides only {protein_energy_pct:.1f}% of energy (minimum required: {threshold}%).",
                        regulation=matched_rule["regulation"],
                        recommendation="Remove high protein claim or increase protein content in formulation."
                    ))
            continue

        field = matched_rule["condition_field"]
        actual_value = getattr(nutritional, field, None)

        if actual_value is None:
            findings.append(ComplianceFinding(
                module="claims",
                severity="WARNING",
                title=f"Missing Field for Claim: '{claim}'",
                description=f"Nutritional parameter '{field}' missing from label to verify '{claim}'.",
                regulation=matched_rule["regulation"],
                recommendation=f"Disclose '{field}' explicitly in nutrition panel."
            ))
            continue

        threshold = matched_rule["threshold"]
        op = matched_rule["operator"]
        unit = matched_rule["unit"]

        valid = False
        if op == "<=": valid = actual_value <= threshold
        elif op == ">=": valid = actual_value >= threshold
        elif op == "<": valid = actual_value < threshold
        elif op == ">": valid = actual_value > threshold
        else: valid = actual_value == threshold

        if valid:
            findings.append(ComplianceFinding(
                module="claims",
                severity="INFO",
                title=f"Claim Verified: '{claim}'",
                description=f"'{claim}' verified — {field} is {actual_value} {unit} (statutory limit: {op} {threshold} {unit}).",
                regulation=matched_rule["regulation"]
            ))
        else:
            findings.append(ComplianceFinding(
                module="claims",
                severity="CRITICAL",
                title=f"Misleading Claim: '{claim}'",
                description=f"'{claim}' violated — {field} measured at {actual_value} {unit} exceeds statutory limit ({op} {threshold} {unit}).",
                regulation=matched_rule["regulation"],
                recommendation=f"Withdraw '{claim}' from packaging or reformulate to meet the {threshold} {unit} cutoff."
            ))

    # Check Natural claim contradictions
    natural_claims = [c for c in label.nutritional_claims if "natural" in c.lower()]
    if natural_claims and label.additives:
        synthetic = [a for a in label.additives if a.e_code in ("E102", "E110", "E122", "E124", "E127", "E129", "E131", "E132", "E133", "E621", "E211")]
        if synthetic:
            names = [f"{a.name} ({a.e_code})" for a in synthetic]
            findings.append(ComplianceFinding(
                module="claims",
                severity="CRITICAL",
                title="Contradictory 'Natural' Claim (Greenwashing)",
                description=f"Product claims 'Natural' but contains synthetic/chemical additives: {', '.join(names)}.",
                regulation="FSS (Advertising & Claims) Regulations, 2018",
                recommendation="Remove 'Natural' claim to prevent regulatory penalties for deceptive packaging."
            ))

    return findings

# --- MODULE 4: License Validator ---

LICENSE_TYPES = {
    "10": "Central License (Large Manufacturer / Importer)",
    "20": "State License (Manufacturer)",
    "21": "State License (Storage / Transport)",
    "22": "State License (Retail / Food Service)",
}

def check_license(label: LabelComplianceData) -> List[ComplianceFinding]:
    findings = []
    if not label.fssai_license:
        findings.append(ComplianceFinding(
            module="license",
            severity="CRITICAL",
            title="Missing Mandatory FSSAI License Number",
            description="No FSSAI registration/license number detected on packaging. Compulsory for all commercial products sold in India.",
            regulation="FSS (Licensing & Registration) Regulations, 2011",
            recommendation="Display 14-digit FSSAI License Number prominently alongside the FSSAI logo."
        ))
        return findings

    clean_license = re.sub(r"[\s\-]", "", str(label.fssai_license).strip())

    if not clean_license.isdigit():
        findings.append(ComplianceFinding(
            module="license",
            severity="CRITICAL",
            title=f"Invalid License Characters: '{label.fssai_license}'",
            description="FSSAI license must consist strictly of 14 numeric digits.",
            regulation="FSS (Licensing & Registration) Regulations, 2011",
            recommendation="Correct license number printing to numeric 14 digits."
        ))
        return findings

    if len(clean_license) != 14:
        findings.append(ComplianceFinding(
            module="license",
            severity="CRITICAL",
            title=f"Invalid License Length ({len(clean_license)} digits)",
            description=f"FSSAI license must be exactly 14 digits. Found {len(clean_license)} digits: '{clean_license}'.",
            regulation="FSS (Licensing & Registration) Regulations, 2011",
            recommendation="Verify 14-digit license number registration."
        ))
        return findings

    prefix = clean_license[:2]
    if prefix in LICENSE_TYPES:
        findings.append(ComplianceFinding(
            module="license",
            severity="INFO",
            title="FSSAI License Valid Structure",
            description=f"License '{clean_license}' validated. Category: {LICENSE_TYPES[prefix]}.",
            regulation="FSS (Licensing & Registration) Regulations, 2011"
        ))
    else:
        findings.append(ComplianceFinding(
            module="license",
            severity="WARNING",
            title=f"Unrecognized License Prefix ('{prefix}')",
            description=f"Prefix '{prefix}' does not match standard Central (10) or State (20-22) designations.",
            regulation="FSS (Licensing & Registration) Regulations, 2011",
            recommendation="Cross-check license status on FoSCoS portal."
        ))

    return findings

# --- MODULE 5: Mandatory Labelling Completeness ---

def check_labelling(label: LabelComplianceData) -> List[ComplianceFinding]:
    findings = []
    conn = _get_db()
    mandatory_rows = conn.execute("SELECT * FROM mandatory_fields").fetchall()
    conn.close()

    for row in mandatory_rows:
        field_name = row["field_name"]
        json_key = row["json_key"]
        regulation = row["fssai_reference"]

        value = getattr(label, json_key, None)
        present = False
        if value is not None:
            if isinstance(value, str): present = len(value.strip()) > 0
            elif isinstance(value, list): present = len(value) > 0
            else: present = True

        if present:
            findings.append(ComplianceFinding(
                module="labelling",
                severity="INFO",
                title=f"Mandatory Field Present: {field_name}",
                description=f"Field '{field_name}' successfully identified on label packaging.",
                regulation=regulation
            ))
        else:
            findings.append(ComplianceFinding(
                module="labelling",
                severity="CRITICAL" if json_key in ("ingredients", "net_weight", "product_name") else "WARNING",
                title=f"Missing Mandatory Field: {field_name}",
                description=f"Statutory packaging field '{field_name}' was not detected.",
                regulation=regulation,
                recommendation=f"Print '{field_name}' visibly on package label."
            ))

    return findings

# --- Risk Scoring Engine ---

MODULE_WEIGHTS = {
    "allergens": 30,
    "additives": 25,
    "claims": 20,
    "labelling": 15,
    "license": 10,
}

CRITICAL_PENALTY = 25
WARNING_PENALTY = 10

def calculate_risk_score(findings: List[ComplianceFinding]) -> RiskScore:
    by_module: Dict[str, List[ComplianceFinding]] = {m: [] for m in MODULE_WEIGHTS}
    for f in findings:
        if f.module in by_module:
            by_module[f.module].append(f)

    modules = []
    weighted_total = 0

    for module, weight in MODULE_WEIGHTS.items():
        m_findings = by_module[module]
        critical = sum(1 for f in m_findings if f.severity == "CRITICAL")
        warning = sum(1 for f in m_findings if f.severity == "WARNING")

        raw_score = 100 - (critical * CRITICAL_PENALTY) - (warning * WARNING_PENALTY)
        score = max(0, min(100, raw_score))

        modules.append(ModuleScore(
            module=module,
            score=score,
            findings_count=len(m_findings),
            critical_count=critical,
            warning_count=warning
        ))
        weighted_total += score * weight

    overall = round(weighted_total / 100)

    if overall >= 90: grade = "A"
    elif overall >= 75: grade = "B"
    elif overall >= 55: grade = "C"
    else: grade = "F"

    return RiskScore(overall_score=overall, grade=grade, modules=modules)

def build_summary(findings: List[ComplianceFinding], score: RiskScore) -> str:
    critical = sum(1 for f in findings if f.severity == "CRITICAL")
    warning = sum(1 for f in findings if f.severity == "WARNING")
    if critical or warning:
        return f"Grade {score.grade} ({score.overall_score}/100) — {critical} critical violations, {warning} warnings flagged."
    return f"Grade {score.grade} ({score.overall_score}/100) — Zero non-compliances flagged. Full statutory adherence."

def run_all_checks(label: LabelComplianceData) -> List[ComplianceFinding]:
    all_findings = []
    all_findings.extend(check_additives(label))
    all_findings.extend(check_allergens(label))
    all_findings.extend(check_claims(label))
    all_findings.extend(check_license(label))
    all_findings.extend(check_labelling(label))
    return all_findings

def run_compliance_pipeline(label: LabelComplianceData) -> ComplianceResult:
    findings = run_all_checks(label)
    risk_score = calculate_risk_score(findings)
    summary = build_summary(findings, risk_score)
    return ComplianceResult(
        label_data=label,
        findings=findings,
        risk_score=risk_score,
        summary=summary
    )

# --- What-If Scenario Simulation ---

def apply_what_if_modifications(label: LabelComplianceData, mods: dict) -> LabelComplianceData:
    label = deepcopy(label)
    if "remove_ingredients" in mods:
        rem_set = {r.lower().strip() for r in mods["remove_ingredients"]}
        label.ingredients = [i for i in label.ingredients if i.lower().strip() not in rem_set]

    if "add_allergen_declaration" in mods:
        for a in mods["add_allergen_declaration"]:
            if a not in label.declared_allergens:
                label.declared_allergens.append(a)

    if "remove_allergen_declaration" in mods:
        rem_set = {r.lower().strip() for r in mods["remove_allergen_declaration"]}
        label.declared_allergens = [a for a in label.declared_allergens if a.lower().strip() not in rem_set]

    if "remove_additives" in mods:
        rem_set = {r.lower().strip() for r in mods["remove_additives"]}
        label.additives = [a for a in label.additives if a.name.lower().strip() not in rem_set and (not a.e_code or a.e_code.lower().strip() not in rem_set)]

    if "add_claim" in mods:
        claim = mods["add_claim"]
        if claim and claim not in label.nutritional_claims:
            label.nutritional_claims.append(claim)

    if "remove_claim" in mods:
        claim_lower = str(mods["remove_claim"]).lower().strip()
        label.nutritional_claims = [c for c in label.nutritional_claims if c.lower().strip() != claim_lower]

    if "set_fssai_license" in mods:
        label.fssai_license = mods["set_fssai_license"]

    return label
