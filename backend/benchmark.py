"""
BENCHMARKING SUITE & QUANTITATIVE EVALUATION ENGINE
Computes Precision, Recall, F1-Score, and Confusion Matrix across curated
gold-standard cosmetic formulations (FDA Banned, EU Annex II, and Active Chemical Clashes).
Generates publication-ready LaTeX tables for BTP thesis inclusion.
"""

import os
import json
import time
from typing import List, Dict, Any

from src.rules.rules_engine import analyze_formulation, analyze_routine_stacking
from src.tools.cheminformatics import get_cheminformatics_dossier

# Curated Gold-Standard Ground Truth Benchmark Dataset (25 Formulations)
BENCHMARK_DATASET = [
    # Category 1: Negative Controls (100% Safe / Compliant Formulations)
    {
        "id": "SAFE_01",
        "name": "Gentle Ceramide Hydrating Cleanser",
        "ingredients": ["Water", "Glycerin", "Cetearyl Alcohol", "Ceramide NP", "Hyaluronic Acid", "Phenoxyethanol"],
        "ground_truth_violation": False,
        "ground_truth_conflict": False
    },
    {
        "id": "SAFE_02",
        "name": "Niacinamide Barrier Serum",
        "ingredients": ["Aqua", "Niacinamide", "Zinc PCA", "Panthenol", "Allantoin", "Ethylhexylglycerin"],
        "ground_truth_violation": False,
        "ground_truth_conflict": False
    },
    {
        "id": "SAFE_03",
        "name": "Squalane Nourishing Facial Oil",
        "ingredients": ["Squalane", "Tocopherol", "Helianthus Annuus Seed Oil"],
        "ground_truth_violation": False,
        "ground_truth_conflict": False
    },
    {
        "id": "SAFE_04",
        "name": "Centella Soothing Gel Cream",
        "ingredients": ["Centella Asiatica Extract", "Madecassoside", "Glycerin", "Butylene Glycol", "Carbomer"],
        "ground_truth_violation": False,
        "ground_truth_conflict": False
    },
    {
        "id": "SAFE_05",
        "name": "Mineral SPF 50 Physical Sunscreen",
        "ingredients": ["Zinc Oxide", "Titanium Dioxide", "Caprylic Triglyceride", "Silica", "Polyglyceryl-3 Polyricinoleate"],
        "ground_truth_violation": False,
        "ground_truth_conflict": False
    },

    # Category 2: FDA Prohibited Substances (Ground Truth Violations)
    {
        "id": "FDA_01",
        "name": "Illegal Antiseptic Cream with Bithionol",
        "ingredients": ["Water", "Petrolatum", "Bithionol", "Cetyl Alcohol", "Fragrance"],
        "ground_truth_violation": True,
        "ground_truth_conflict": False
    },
    {
        "id": "FDA_02",
        "name": "Skin Bleaching Cream with Mercury Compounds",
        "ingredients": ["Aqua", "Stearic Acid", "Mercury Compounds", "Mineral Oil", "Methylparaben"],
        "ground_truth_violation": True,
        "ground_truth_conflict": False
    },
    {
        "id": "FDA_03",
        "name": "Contaminated Cleanser with Chloroform",
        "ingredients": ["Water", "Sodium Laureth Sulfate", "Chloroform", "Cocamidopropyl Betaine"],
        "ground_truth_violation": True,
        "ground_truth_conflict": False
    },
    {
        "id": "FDA_04",
        "name": "Banned Surgical Scrub with Hexachlorophene",
        "ingredients": ["Hexachlorophene", "Propylene Glycol", "Sodium Hydroxide", "Water"],
        "ground_truth_violation": True,
        "ground_truth_conflict": False
    },
    {
        "id": "FDA_05",
        "name": "Aerosol Hairspray with Methylene Chloride",
        "ingredients": ["Alcohol Denat", "Methylene Chloride", "Acrylates Copolymer", "Aminomethyl Propanol"],
        "ground_truth_violation": True,
        "ground_truth_conflict": False
    },

    # Category 3: EU Annex II Prohibited Substances
    {
        "id": "EU_01",
        "name": "Unregulated Lightening Cream with Hydroquinone",
        "ingredients": ["Aqua", "Glyceryl Stearate", "Hydroquinone", "Dimethicone", "Sodium Sulfite"],
        "ground_truth_violation": True,
        "ground_truth_conflict": False
    },
    {
        "id": "EU_02",
        "name": "Preserved Lotion with Methyldibromo Glutaronitrile",
        "ingredients": ["Water", "Glycerin", "Methyldibromo Glutaronitrile", "Cetearyl Glucoside"],
        "ground_truth_violation": True,
        "ground_truth_conflict": False
    },
    {
        "id": "EU_03",
        "name": "Allergenic Fragrance with Lyral",
        "ingredients": ["Alcohol", "Parfum", "Lyral", "Aqua", "BHT"],
        "ground_truth_violation": True,
        "ground_truth_conflict": False
    },
    {
        "id": "EU_04",
        "name": "Oakmoss Formulation with Atranol",
        "ingredients": ["Aqua", "Caprylic Triglyceride", "Atranol", "Xanthan Gum"],
        "ground_truth_violation": True,
        "ground_truth_conflict": False
    },
    {
        "id": "EU_05",
        "name": "Banned Fragrance Compound Chloroatranol",
        "ingredients": ["Dipropylene Glycol", "Fragrance", "Chloroatranol", "Triethyl Citrate"],
        "ground_truth_violation": True,
        "ground_truth_conflict": False
    },

    # Category 4: Active Chemical Conflict Formulations (Ground Truth Conflicts)
    {
        "id": "CONFLICT_01",
        "name": "High-Risk Peeling Night Solution",
        "ingredients": ["Aqua", "Retinol", "Glycolic Acid", "Glycerin", "Sodium Hydroxide"],
        "ground_truth_violation": False,
        "ground_truth_conflict": True
    },
    {
        "id": "CONFLICT_02",
        "name": "Dual Exfoliating Acne Treatment",
        "ingredients": ["Water", "Salicylic Acid", "Retinol", "Butylene Glycol", "Phenoxyethanol"],
        "ground_truth_violation": False,
        "ground_truth_conflict": True
    },
    {
        "id": "CONFLICT_03",
        "name": "Oxidative Inactivation Duo",
        "ingredients": ["Benzoyl Peroxide", "Retinol", "Carbomer", "Disodium EDTA"],
        "ground_truth_violation": False,
        "ground_truth_conflict": True
    },
    {
        "id": "CONFLICT_04",
        "name": "Simultaneous Retinoid & Direct Vitamin C",
        "ingredients": ["Water", "Ascorbic Acid", "Retinol", "Ferulic Acid", "Ethoxydiglycol"],
        "ground_truth_violation": False,
        "ground_truth_conflict": True
    },
    {
        "id": "CONFLICT_05",
        "name": "Acidic Hydrolysis Flushing Mixture",
        "ingredients": ["Aqua", "L-Ascorbic Acid", "Niacinamide", "Propanediol", "Sodium Hyaluronate"],
        "ground_truth_violation": False,
        "ground_truth_conflict": True
    }
]


def run_benchmark():
    print("=" * 70)
    print("🚀 RUNNING QUANTITATIVE BENCHMARK EVALUATION (BTP DEFENSE SUITE)")
    print(f"📊 Total Ground-Truth Formulations Tested: {len(BENCHMARK_DATASET)}")
    print("=" * 70)

    start_time = time.time()

    # Metrics for Regulatory Violation Detection (Binary Classification)
    tp_v = 0
    fp_v = 0
    tn_v = 0
    fn_v = 0

    # Metrics for Ingredient Conflict Detection
    tp_c = 0
    fp_c = 0
    tn_c = 0
    fn_c = 0

    # Latencies
    latencies = []

    for test_case in BENCHMARK_DATASET:
        t0 = time.time()
        report = analyze_formulation(test_case["ingredients"])
        latencies.append((time.time() - t0) * 1000)

        pred_violation = len(report["regulatory_violations"]) > 0
        actual_violation = test_case["ground_truth_violation"]

        if pred_violation and actual_violation:
            tp_v += 1
        elif pred_violation and not actual_violation:
            fp_v += 1
        elif not pred_violation and actual_violation:
            fn_v += 1
        else:
            tn_v += 1

        pred_conflict = len(report["ingredient_conflicts"]) > 0
        actual_conflict = test_case["ground_truth_conflict"]

        if pred_conflict and actual_conflict:
            tp_c += 1
        elif pred_conflict and not actual_conflict:
            fp_c += 1
        elif not pred_conflict and actual_conflict:
            fn_c += 1
        else:
            tn_c += 1

    total_time = time.time() - start_time

    # Calculate Quantitative Metrics
    def calc_metrics(tp, fp, tn, fn):
        accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) else 0.0
        precision = tp / (tp + fp) if (tp + fp) else 1.0
        recall = tp / (tp + fn) if (tp + fn) else 1.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) else 0.0
        return accuracy, precision, recall, f1

    acc_v, prec_v, rec_v, f1_v = calc_metrics(tp_v, fp_v, tn_v, fn_v)
    acc_c, prec_c, rec_c, f1_c = calc_metrics(tp_c, fp_c, tn_c, fn_c)
    avg_latency = sum(latencies) / len(latencies)

    print(f"\n[1] REGULATORY VIOLATIONS (EU Annex II & FDA Lists):")
    print(f"    - True Positives:  {tp_v} | False Positives: {fp_v}")
    print(f"    - True Negatives:  {tn_v} | False Negatives: {fn_v}")
    print(f"    - Accuracy:  {acc_v:.1%}")
    print(f"    - Precision: {prec_v:.1%}")
    print(f"    - Recall:    {rec_v:.1%}")
    print(f"    - F1-Score:  {f1_v:.3f}")

    print(f"\n[2] ACTIVE CHEMICAL CONFLICT DETECTION:")
    print(f"    - True Positives:  {tp_c} | False Positives: {fp_c}")
    print(f"    - True Negatives:  {tn_c} | False Negatives: {fn_c}")
    print(f"    - Accuracy:  {acc_c:.1%}")
    print(f"    - Precision: {prec_c:.1%}")
    print(f"    - Recall:    {rec_c:.1%}")
    print(f"    - F1-Score:  {f1_c:.3f}")

    print(f"\n[3] COMPUTATIONAL PERFORMANCE:")
    print(f"    - Mean Rule Execution Latency: {avg_latency:.2f} ms")
    print(f"    - Total Benchmark Run Time:     {total_time:.3f} s")

    # Generate Publication-Ready LaTeX Table for Thesis
    latex_table = f"""% Auto-generated Benchmark Evaluation Table for Thesis Report
\\begin{{table}}[htbp]
\\centering
\\caption{{Quantitative Evaluation of the Deterministic Regulatory \\& Chemical Interaction Engine}}
\\label{{tab:benchmark_results}}
\\begin{{tabular}}{{lccccr}}
\\hline
\\textbf{{Evaluation Task}} & \\textbf{{Accuracy}} & \\textbf{{Precision}} & \\textbf{{Recall}} & \\textbf{{$F_1$-Score}} & \\textbf{{Mean Latency}} \\\\
\\hline
Regulatory Violations (FDA/EU) & {acc_v:.1%} & {prec_v:.1%} & {rec_v:.1%} & {f1_v:.3f} & {avg_latency:.2f}\\,ms \\\\
Active Conflict Detection & {acc_c:.1%} & {prec_c:.1%} & {rec_c:.1%} & {f1_c:.3f} & {avg_latency:.2f}\\,ms \\\\
\\hline
\\textbf{{Overall Pipeline Performance}} & \\textbf{{{((acc_v + acc_c)/2):.1%}}} & \\textbf{{{((prec_v + prec_c)/2):.1%}}} & \\textbf{{{((rec_v + rec_c)/2):.1%}}} & \\textbf{{{((f1_v + f1_c)/2):.3f}}} & \\textbf{{{avg_latency:.2f}\\,ms}} \\\\
\\hline
\\end{{tabular}}
\\end{{table}}
"""

    out_latex_path = os.path.join(os.path.dirname(__file__), "benchmark_latex_table.tex")
    with open(out_latex_path, "w", encoding="utf-8") as f:
        f.write(latex_table)

    print(f"\n✅ Publication LaTeX Table saved to: {out_latex_path}")
    print("=" * 70)


if __name__ == "__main__":
    run_benchmark()
