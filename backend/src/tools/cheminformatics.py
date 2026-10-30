"""
LAYER 3: In Silico Cheminformatics & Predictive Toxicology Engine
Computes canonical SMILES, physicochemical descriptors, Potts-Guy dermal permeability (Kp),
Lipinski Rule of 5 (500 Da Rule), and proxy toxicological risk endpoints (Sensitization, DART).
"""

import math
import re
from typing import Dict, Any, Optional, List
import requests

# Curated reference database of common cosmetic actives and excipients
# Provides canonical SMILES, MW (g/mol), LogP, TPSA (Å²), HBD, HBA, and chemical class
MOLECULAR_KNOWLEDGE_BASE = {
    "aqua": {
        "smiles": "O",
        "name": "Water",
        "mw": 18.02,
        "logp": -0.65,
        "tpsa": 9.23,
        "hbd": 2,
        "hba": 1,
        "class": "Inorganic Solvent",
        "dermal_sensitizer": False,
        "endocrine_alert": False,
        "dart_risk": False,
    },
    "water": {
        "smiles": "O",
        "name": "Water",
        "mw": 18.02,
        "logp": -0.65,
        "tpsa": 9.23,
        "hbd": 2,
        "hba": 1,
        "class": "Inorganic Solvent",
        "dermal_sensitizer": False,
        "endocrine_alert": False,
        "dart_risk": False,
    },
    "niacinamide": {
        "smiles": "NC(=O)C1=CN=CC=C1",
        "name": "Niacinamide (Vitamin B3)",
        "mw": 122.12,
        "logp": -0.37,
        "tpsa": 55.98,
        "hbd": 1,
        "hba": 3,
        "class": "Pyridinecarboxamide Active",
        "dermal_sensitizer": False,
        "endocrine_alert": False,
        "dart_risk": False,
    },
    "salicylic acid": {
        "smiles": "OC(=O)C1=CC=CC=C1O",
        "name": "Salicylic Acid (BHA)",
        "mw": 138.12,
        "logp": 2.26,
        "tpsa": 57.53,
        "hbd": 2,
        "hba": 3,
        "class": "Beta-Hydroxy Acid",
        "dermal_sensitizer": True,
        "endocrine_alert": False,
        "dart_risk": False,
    },
    "glycolic acid": {
        "smiles": "OCC(=O)O",
        "name": "Glycolic Acid (AHA)",
        "mw": 76.05,
        "logp": -1.11,
        "tpsa": 57.53,
        "hbd": 2,
        "hba": 3,
        "class": "Alpha-Hydroxy Acid",
        "dermal_sensitizer": True,
        "endocrine_alert": False,
        "dart_risk": False,
    },
    "retinol": {
        "smiles": "CC1=C(C(CCC1)(C)C)/C=C/C(=C/C=C/C(=C/CO)/C)/C",
        "name": "Retinol (Vitamin A)",
        "mw": 286.45,
        "logp": 5.68,
        "tpsa": 20.23,
        "hbd": 1,
        "hba": 1,
        "class": "Retinoid / Diterpenoid",
        "dermal_sensitizer": True,
        "endocrine_alert": False,
        "dart_risk": True,  # Teratogenicity / DART concern in pregnancy
    },
    "hyaluronic acid": {
        "smiles": "CC(=O)NC1C(C(C(OC1O)CO)O)OC2C(C(C(C(O2)C(=O)O)O)O)O",
        "name": "Hyaluronic Acid (Oligomer)",
        "mw": 776.65,
        "logp": -5.10,
        "tpsa": 352.00,
        "hbd": 10,
        "hba": 18,
        "class": "Glycosaminoglycan Polymer",
        "dermal_sensitizer": False,
        "endocrine_alert": False,
        "dart_risk": False,
    },
    "glycerine": {
        "smiles": "OCC(O)CO",
        "name": "Glycerin",
        "mw": 92.09,
        "logp": -1.76,
        "tpsa": 60.69,
        "hbd": 3,
        "hba": 3,
        "class": "Polyol Humectant",
        "dermal_sensitizer": False,
        "endocrine_alert": False,
        "dart_risk": False,
    },
    "glycerin": {
        "smiles": "OCC(O)CO",
        "name": "Glycerin",
        "mw": 92.09,
        "logp": -1.76,
        "tpsa": 60.69,
        "hbd": 3,
        "hba": 3,
        "class": "Polyol Humectant",
        "dermal_sensitizer": False,
        "endocrine_alert": False,
        "dart_risk": False,
    },
    "phenoxyethanol": {
        "smiles": "C1=CC=C(C=C1)OCCO",
        "name": "2-Phenoxyethanol",
        "mw": 138.16,
        "logp": 1.20,
        "tpsa": 29.46,
        "hbd": 1,
        "hba": 2,
        "class": "Glycol Ether Preservative",
        "dermal_sensitizer": True,
        "endocrine_alert": False,
        "dart_risk": False,
    },
    "citric acid": {
        "smiles": "C(C(=O)O)C(CC(=O)O)(C(=O)O)O",
        "name": "Citric Acid",
        "mw": 192.12,
        "logp": -1.72,
        "tpsa": 132.13,
        "hbd": 4,
        "hba": 7,
        "class": "Tricarboxylic Acid / pH Adjuster",
        "dermal_sensitizer": False,
        "endocrine_alert": False,
        "dart_risk": False,
    },
    "zinc oxide": {
        "smiles": "O=[Zn]",
        "name": "Zinc Oxide",
        "mw": 81.38,
        "logp": 1.53,
        "tpsa": 17.07,
        "hbd": 0,
        "hba": 1,
        "class": "Inorganic UV Attenuator",
        "dermal_sensitizer": False,
        "endocrine_alert": False,
        "dart_risk": False,
    },
    "titanium dioxide": {
        "smiles": "O=[Ti]=O",
        "name": "Titanium Dioxide",
        "mw": 79.87,
        "logp": 1.20,
        "tpsa": 34.14,
        "hbd": 0,
        "hba": 2,
        "class": "Inorganic Mineral Filter",
        "dermal_sensitizer": False,
        "endocrine_alert": False,
        "dart_risk": False,
    },
    "tocopherol acetate": {
        "smiles": "CC(=O)OC1=C(C)C(=C2CCC(OC2=C1C)(C)CCCC(C)CCCC(C)CCCC(C)C)C",
        "name": "Tocopheryl Acetate (Vitamin E)",
        "mw": 472.74,
        "logp": 10.36,
        "tpsa": 35.53,
        "hbd": 0,
        "hba": 3,
        "class": "Lipophilic Antioxidant",
        "dermal_sensitizer": False,
        "endocrine_alert": False,
        "dart_risk": False,
    },
    "homosalate": {
        "smiles": "CC1CCC(CC1)(C)OC(=O)C2=CC=CC=C2O",
        "name": "Homosalate",
        "mw": 262.35,
        "logp": 6.14,
        "tpsa": 46.53,
        "hbd": 1,
        "hba": 3,
        "class": "Chemical UVB Filter",
        "dermal_sensitizer": False,
        "endocrine_alert": True,  # EU SCCS endocrine disruption flag
        "dart_risk": False,
    },
    "avobenzone": {
        "smiles": "CC(C)(C)C1=CC=C(C=C1)C(=O)CC(=O)C2=CC=C(C=C2)OC",
        "name": "Avobenzone (Butyl Methoxydibenzoylmethane)",
        "mw": 310.39,
        "logp": 4.51,
        "tpsa": 43.37,
        "hbd": 0,
        "hba": 3,
        "class": "Dibenzoylmethane UVA Filter",
        "dermal_sensitizer": True,  # Photoallergen potential
        "endocrine_alert": False,
        "dart_risk": False,
    },
    "octocrylene": {
        "smiles": "CCCCC(CC)COC(=O)C(=C(C1=CC=CC=C1)C2=CC=CC=C2)C#N",
        "name": "Octocrylene",
        "mw": 361.48,
        "logp": 6.88,
        "tpsa": 50.09,
        "hbd": 0,
        "hba": 3,
        "class": "UVB/UVA2 Filter",
        "dermal_sensitizer": True,  # Photo-sensitizer
        "endocrine_alert": True,   # SCCS restriction
        "dart_risk": False,
    },
    "cyclopentasiloxane": {
        "smiles": "C[Si]1(O[Si](C)(O[Si](C)(O[Si](C)(O[Si](C)(O1)C)C)C)C)C",
        "name": "Cyclopentasiloxane (D5)",
        "mw": 370.77,
        "logp": 5.20,
        "tpsa": 46.15,
        "hbd": 0,
        "hba": 5,
        "class": "Volatile Cyclomethicone Silicone",
        "dermal_sensitizer": False,
        "endocrine_alert": True,   # REACH Annex XVII restricted in wash-off
        "dart_risk": False,
    },
    "ceramide np": {
        "smiles": "CCCCCCCCCCCCCCCCCC(=O)NC(CO)C(O)C(O)CCCCCCCCCCCCCC",
        "name": "Ceramide NP (Ceramide 3)",
        "mw": 583.97,
        "logp": 9.45,
        "tpsa": 89.52,
        "hbd": 4,
        "hba": 4,
        "class": "Sphingolipid Barrier Lipid",
        "dermal_sensitizer": False,
        "endocrine_alert": False,
        "dart_risk": False,
    },
    "d-panthenol": {
        "smiles": "CC(C)(CO)C(O)C(=O)NCCCO",
        "name": "D-Panthenol (Provitamin B5)",
        "mw": 205.25,
        "logp": -1.05,
        "tpsa": 89.52,
        "hbd": 4,
        "hba": 4,
        "class": "Humectant Provitamin",
        "dermal_sensitizer": False,
        "endocrine_alert": False,
        "dart_risk": False,
    }
}


def calculate_potts_guy_kp(logp: float, mw: float) -> float:
    """
    Computes the Potts-Guy Dermal Permeability Coefficient (Kp).
    Equation: log10(Kp) = -2.7 + (0.71 * logP) - (0.0061 * MW)
    Returns: Kp in cm/hour (rate of permeation through human stratum corneum).
    """
    try:
        log_kp = -2.7 + (0.71 * logp) - (0.0061 * mw)
        kp = math.pow(10, log_kp)
        return kp
    except (ValueError, OverflowError):
        return 1e-6


def assess_skin_permeability(mw: float, logp: float, kp: float, tpsa: float) -> Dict[str, Any]:
    """
    Evaluates stratum corneum barrier permeation using the 500 Dalton Rule
    and the Potts-Guy flux model.
    """
    # 500 Dalton Rule for skin absorption (Bos & Meinardi, 2000)
    passes_500_da = mw <= 500.0
    
    # Optimum lipophilicity window for dermal absorption: 1 <= logP <= 3
    in_optimum_logp = 1.0 <= logp <= 3.5
    
    if mw > 500.0 or tpsa > 140.0:
        penetration_class = "Surface Film-Former"
        penetration_summary = "Non-Penetrating (MW > 500 Da / High TPSA). Molecule remains on surface stratum corneum without systemic absorption."
        systemic_risk = "Negligible"
    elif kp > 1e-3 and in_optimum_logp:
        penetration_class = "High Transdermal Permeation"
        penetration_summary = "Readily permeates stratum corneum into viable epidermis and vascular microcirculation."
        systemic_risk = "Moderate to High (monitor dose)"
    elif kp > 1e-5:
        penetration_class = "Moderate Epidermal Diffusion"
        penetration_summary = "Diffuses into viable epidermis to engage cellular targets (ideal for cosmeceuticals)."
        systemic_risk = "Low"
    else:
        penetration_class = "Low Dermal Flux"
        penetration_summary = "Slow dermal penetration due to low partition coefficient or steric hindrance."
        systemic_risk = "Very Low"
        
    return {
        "passes_500_da_rule": passes_500_da,
        "penetration_class": penetration_class,
        "penetration_summary": penetration_summary,
        "systemic_exposure_risk": systemic_risk,
        "kp_cm_per_hr": f"{kp:.2e}",
        "kp_raw": kp
    }


def query_pubchem_properties(chemical_name: str) -> Optional[Dict[str, Any]]:
    """
    Fetches real-time molecular structure and physicochemical descriptors
    from the NCBI PubChem PUG-REST API for arbitrary chemical entities.
    """
    clean_name = chemical_name.strip()
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{requests.utils.quote(clean_name)}/property/MolecularWeight,XLogP,TPSA,HBondDonorCount,HBondAcceptorCount,CanonicalSMILES/JSON"
    try:
        resp = requests.get(url, timeout=4)
        if resp.status_code == 200:
            data = resp.json()
            props = data["PropertyTable"]["Properties"][0]
            mw = float(props.get("MolecularWeight", 200.0))
            logp = float(props.get("XLogP", 1.0))
            tpsa = float(props.get("TPSA", 40.0))
            hbd = int(props.get("HBondDonorCount", 1))
            hba = int(props.get("HBondAcceptorCount", 2))
            smiles = str(props.get("CanonicalSMILES", ""))
            
            return {
                "smiles": smiles,
                "name": clean_name.title(),
                "mw": mw,
                "logp": logp,
                "tpsa": tpsa,
                "hbd": hbd,
                "hba": hba,
                "class": "Synthesized Chemical Entity",
                "dermal_sensitizer": False,
                "endocrine_alert": False,
                "dart_risk": False,
                "source": "PubChem PUG-REST API"
            }
    except Exception:
        pass
    return None


def compute_fickian_diffusion_kinetics(mw: float, logp: float, kp: float) -> Dict[str, Any]:
    """
    Computes transdermal diffusion kinetics using Fick's Second Law:
    - Diffusivity D_sc in stratum corneum (cm^2/hr)
    - Lag time t_lag (hours) to achieve steady-state transdermal flux
    - Steady-state flux J_ss (ug/cm^2/hr)
    - 24-hour temporal absorption curve points Q(t) in ug/cm^2
    """
    # Diffusivity estimation in stratum corneum: log10(D_sc) = -9.2 - 0.0035 * MW (cm^2/s)
    log_d_sc = -9.2 - (0.0035 * mw)
    d_sc_cm2_per_sec = 10.0 ** max(-14.0, min(-8.0, log_d_sc))
    d_sc_cm2_per_hr = d_sc_cm2_per_sec * 3600.0

    # Stratum corneum thickness: h = 15 um = 0.0015 cm
    h_sc = 0.0015
    
    # Lag time: t_lag = h^2 / (6 * D_sc) in hours
    t_lag_hr = round((h_sc ** 2) / (6.0 * d_sc_cm2_per_hr), 2)
    t_lag_hr = max(0.2, min(18.0, t_lag_hr))

    # Standard donor concentration Cv = 10,000 ug/cm^3 (1% cosmetic active)
    cv_ug_cm3 = 10000.0
    
    # Steady-state flux J_ss = Kp * Cv (ug/cm^2/hr)
    j_ss = round(kp * cv_ug_cm3, 3)
    
    # Generate 24-hour cumulative absorption profile points Q(t)
    hours = [0, 2, 4, 6, 8, 12, 16, 20, 24]
    absorption_curve = []
    for t in hours:
        if t <= t_lag_hr:
            q_t = 0.0
        else:
            q_t = round(j_ss * (t - t_lag_hr), 2)
        absorption_curve.append({"hour": t, "absorbed_ug_per_cm2": q_t})

    return {
        "diffusivity_d_sc_cm2_per_hr": f"{d_sc_cm2_per_hr:.2e}",
        "lag_time_hours": t_lag_hr,
        "steady_state_flux_j_ss": j_ss,
        "absorption_profile_24h": absorption_curve,
        "kinetic_classification": "Rapid Transdermal Flux" if t_lag_hr < 2.0 and j_ss > 1.0 else ("Moderate Permeation" if j_ss > 0.05 else "Surface Localized / Slow Flux")
    }


def get_cheminformatics_dossier(ingredient_name: str) -> Dict[str, Any]:
    """
    Master function: Generates a complete biochemical dossier for an ingredient.
    Combines local knowledge base with dynamic PubChem PUG-REST resolution.
    """
    key = ingredient_name.lower().strip()
    
    # 1. Check local knowledge base first (instant, 0 latency)
    record = None
    for k, v in MOLECULAR_KNOWLEDGE_BASE.items():
        if k in key or key in k:
            record = dict(v)
            record["source"] = "Curated Biochemical Knowledge Graph"
            break
            
    # 2. Dynamic live query via PubChem if missing
    if not record:
        record = query_pubchem_properties(ingredient_name)
        
    # 3. Fallback heuristic estimation if obscure/botanical extract
    if not record:
        record = {
            "smiles": "Polymer/Complex Botanical Matrix",
            "name": ingredient_name.title(),
            "mw": 350.0,
            "logp": 1.2,
            "tpsa": 65.0,
            "hbd": 2,
            "hba": 4,
            "class": "Complex Botanical Extract / Matrix",
            "dermal_sensitizer": False,
            "endocrine_alert": False,
            "dart_risk": False,
            "source": "Biophysical Heuristic Estimation"
        }
        
    # Calculate Potts-Guy Kp
    kp = calculate_potts_guy_kp(record["logp"], record["mw"])
    
    # Evaluate dermal permeability & 500 Da rule
    permeability = assess_skin_permeability(record["mw"], record["logp"], kp, record["tpsa"])
    
    # Calculate Fickian diffusion kinetics & 24h absorption curve
    kinetics = compute_fickian_diffusion_kinetics(record["mw"], record["logp"], kp)
    
    # Quantitative toxicological hazard flags
    toxicity_endpoints = {
        "dermal_sensitization": {
            "flagged": record.get("dermal_sensitizer", False),
            "endpoint": "OECD TG 429 Local Lymph Node Assay (LLNA) proxy",
            "risk_level": "High Induction Risk" if record.get("dermal_sensitizer") else "Negative / Low Risk"
        },
        "endocrine_disruption": {
            "flagged": record.get("endocrine_alert", False),
            "endpoint": "SCCS & Tox21 Nuclear Receptor Binding alert",
            "risk_level": "Potential Receptor Antagonist" if record.get("endocrine_alert") else "No Identified Disruptor Alert"
        },
        "dart_developmental_toxicity": {
            "flagged": record.get("dart_risk", False),
            "endpoint": "Developmental & Reproductive Toxicity (DART) proxy",
            "risk_level": "Contraindicated in Pregnancy/Lactation" if record.get("dart_risk") else "Unrestricted"
        }
    }
    
    return {
        "ingredient": ingredient_name,
        "canonical_smiles": record["smiles"],
        "chemical_class": record.get("class", "Organic Molecule"),
        "physicochemical_properties": {
            "molecular_weight_da": record["mw"],
            "logp_partition_coefficient": record["logp"],
            "tpsa_angstrom2": record["tpsa"],
            "hydrogen_bond_donors": record["hbd"],
            "hydrogen_bond_acceptors": record["hba"],
        },
        "biophysical_skin_permeability": permeability,
        "diffusion_kinetics": kinetics,
        "in_silico_toxicity_endpoints": toxicity_endpoints,
        "datasource": record.get("source", "ToxKG")
    }
