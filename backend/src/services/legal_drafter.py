"""
Consumer Forum / 'Jago Grahak Jago' Automated Legal Draft Generator
Generates a formal legal complaint draft for the National Consumer Helpline / District Consumer Disputes Redressal Commission
when misleading marketing claims, economic food adulteration, or FSSAI regulatory violations are detected.
Ported & enhanced from OpenLabel-AI-Pipeline.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

def generate_consumer_complaint_draft(
    product_name: str,
    brand_name: str,
    category: str,
    misleading_claims: List[Dict[str, str]],
    adulteration_alerts: List[Dict[str, Any]],
    regulatory_violations: List[Dict[str, Any]],
    user_name: str = "[CONSUMER NAME]",
    purchase_location: str = "[RETAIL STORE / E-COMMERCE PLATFORM]"
) -> Optional[Dict[str, Any]]:
    """
    Evaluates whether a formal complaint is warranted.
    If yes, formats a structured legal complaint notice ready for filing.
    """
    has_misleading = any(c.get("verdict") == "misleading" for c in misleading_claims)
    has_adulteration = len(adulteration_alerts) > 0
    has_regulatory = len(regulatory_violations) > 0

    if not (has_misleading or has_adulteration or has_regulatory):
        return {
            "legal_draft_available": False,
            "reason": "No actionable regulatory violations or unfair trade practices detected."
        }

    date_str = datetime.now().strftime("%B %d, %Y")

    # Compile Evidence Items
    evidence_points = []
    if has_misleading:
        for c in misleading_claims:
            if c.get("verdict") == "misleading":
                evidence_points.append(f"- Deceptive Claim: '{c.get('claim')}' vs Chemical Reality: {c.get('truth')}")

    if has_adulteration:
        for a in adulteration_alerts:
            evidence_points.append(f"- Adulteration Flag ({a.get('title')}): {a.get('message')} [Ingredient: {a.get('ingredient')}]")

    if has_regulatory:
        for r in regulatory_violations:
            evidence_points.append(f"- Regulatory Breach ({r.get('regulation', 'FSSAI')}): {r.get('reason')} [Ingredient: {r.get('ingredient')}]")

    evidence_text = "\n".join(evidence_points)

    legal_notice = f"""BEFORE THE HON'BLE DISTRICT CONSUMER DISPUTES REDRESSAL COMMISSION
(Filed under Section 35 of the Consumer Protection Act, 2019)

COMPLAINANT:
{user_name}
Address: [Consumer Residential Address]
Email / Contact: [Consumer Contact Details]

VERSUS

OPPOSITE PARTY:
{brand_name or '[MANUFACTURER / BRAND NAME]'}
Marketed / Manufactured by: {brand_name or '[COMPANY NAME]'}
Product: {product_name or '[PRODUCT NAME]'} ({category})
Purchase Point: {purchase_location}

DATE: {date_str}

SUBJECT: FORMAL COMPLAINT AGAINST UNFAIR TRADE PRACTICE AND MISLEADING LABELLING UNDER SECTION 2(47) & SECTION 89 OF THE CONSUMER PROTECTION ACT, 2019 AND FSSAI LABELLING REGULATIONS

RESPECTFULLY SHEWETH:

1. THE COMPLAINANT is a bona fide consumer who purchased the product "{product_name}" believing the front-of-package marketing representations and claims.

2. UNFAIR TRADE PRACTICE & DECEPTIVE CLAIMS:
The Opposite Party has engaged in deliberate deceptive marketing by asserting false attributes on the primary display panel while concealing contraindicated chemical constituents in fine print:
{evidence_text}

3. STATUTORY BREACHES:
   a. Violation of Section 2(47) of the Consumer Protection Act, 2019 (Misleading representation regarding the standard, quality, or grade of goods).
   b. Violation of Section 89 of the Consumer Protection Act, 2019 (Penal action for false or misleading advertisement prejudicial to consumer interest).
   c. Violation of Food Safety and Standards (Packaging and Labelling) Regulations / Drugs & Cosmetics Rules regarding mandatory truthful disclosures.

4. RELIEFS PRAYED FOR:
   a. Direct the Opposite Party to recall all packaging carrying the misleading claim and issue corrective disclosures.
   b. Refund the purchase price along with statutory interest.
   c. Direct the Opposite Party to deposit a penalty into the Consumer Welfare Fund for mass consumer deception.
   d. Award exemplary damages and costs of litigation to the Complainant.

VERIFICATION:
I, {user_name}, do hereby verify that the contents of paragraphs 1 to 4 are true and correct to my knowledge based on laboratory/algorithmic label verification.

DEPONENT
[Signature / National Consumer Helpline Docket]
"""

    return {
        "legal_draft_available": True,
        "summary": f"Formal consumer forum complaint drafted citing {len(evidence_points)} actionable statutory violation(s).",
        "legal_draft_text": legal_notice.strip(),
        "acts_cited": [
            "Consumer Protection Act 2019 Section 2(47)",
            "Consumer Protection Act 2019 Section 89",
            "FSSAI Food Safety and Standards (Packaging & Labelling) Regulations"
        ]
    }
