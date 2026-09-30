"use client";

import React, { useState } from "react";
import { Layers, AlertTriangle, ShieldCheck, CheckCircle2, Plus, Trash2, ArrowRight } from "lucide-react";
import { GhostButton, InkButton, SectionLabel } from "./bits";

interface ProductInput {
  name: string;
  ingredients: string;
}

const ROUTINE_PRESETS = [
  {
    title: "Preset 1: Retinol + AHA/BHA (Barrier Rupture Clash)",
    products: [
      { name: "Step 1: Glycolic Acid Exfoliating Toner", ingredients: "Water, Glycolic Acid, Glycerin, Sodium Hydroxide, Aloe Vera" },
      { name: "Step 2: 1% Pure Retinol Night Serum", ingredients: "Squalane, Retinol, Caprylic Triglyceride, BHT" }
    ]
  },
  {
    title: "Preset 2: Vitamin C + Niacinamide (pH Hydrolysis Alert)",
    products: [
      { name: "Step 1: 15% L-Ascorbic Acid Vitamin C", ingredients: "Aqua, Ascorbic Acid, Ethoxydiglycol, Ferulic Acid" },
      { name: "Step 2: 10% Niacinamide Barrier Serum", ingredients: "Water, Niacinamide, Zinc PCA, Panthenol" }
    ]
  },
  {
    title: "Preset 3: Gentle Barrier Recovery Routine (100% Safe)",
    products: [
      { name: "Step 1: Hydrating Ceramide Cleanser", ingredients: "Water, Glycerin, Cetearyl Alcohol, Ceramide NP, Hyaluronic Acid" },
      { name: "Step 2: Mineral SPF 50 Barrier Cream", ingredients: "Zinc Oxide, Caprylic Triglyceride, Squalane, Tocopherol" }
    ]
  }
];

export function RoutineLayeringSimulator() {
  const [products, setProducts] = useState<ProductInput[]>([
    { name: "Product A (Toner/Exfoliant)", ingredients: "Water, Glycolic Acid, Glycerin" },
    { name: "Product B (Active Treatment)", ingredients: "Squalane, Retinol, Tocopherol" }
  ]);
  const [busy, setBusy] = useState(false);
  const [report, setReport] = useState<any>(null);

  const loadPreset = (preset: typeof ROUTINE_PRESETS[0]) => {
    setProducts(preset.products);
    setReport(null);
  };

  const addProduct = () => {
    if (products.length >= 4) return;
    setProducts([...products, { name: `Product ${String.fromCharCode(65 + products.length)}`, ingredients: "" }]);
  };

  const removeProduct = (idx: number) => {
    if (products.length <= 2) return;
    setProducts(products.filter((_, i) => i !== idx));
  };

  const updateProduct = (idx: number, field: "name" | "ingredients", value: string) => {
    const updated = [...products];
    updated[idx][field] = value;
    setProducts(updated);
  };

  const runRoutineAnalysis = async () => {
    setBusy(true);
    setReport(null);
    try {
      const payload = {
        products: products.map((p) => ({
          name: p.name.trim() || "Cosmetic Formulation",
          ingredients: p.ingredients.split(",").map((i) => i.trim()).filter((i) => i.length > 0)
        }))
      };

      const res = await fetch("/api/routine", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data.ok && data.data) {
        setReport(data.data);
      }
    } catch (err) {
      console.error("Routine analysis error:", err);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="rounded-[8px] border border-line bg-paper2/50 p-4 shadow-sm">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-line pb-3 mb-4">
        <div>
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-ink" />
            <h3 className="text-[14px] font-bold uppercase tracking-tight text-ink">
              Multi-Product Chemical Layering & Routine Conflict Graph
            </h3>
          </div>
          <p className="mt-1 text-[12px] text-inksoft">
            Simulate cross-product active clashes, cumulative active overdoses, and pH incompatibility across your skincare stack.
          </p>
        </div>
        <span className="font-mono text-[10px] uppercase tracking-wider text-inksoft px-2 py-0.5 rounded bg-card border border-line shrink-0">
          Topological Conflict Engine
        </span>
      </div>

      {/* Preset Evaluation Buttons */}
      <div className="mb-4">
        <span className="block font-mono text-[10px] uppercase tracking-wider text-inksoft mb-1.5">
          1-Click Academic Evaluation Presets:
        </span>
        <div className="flex flex-wrap gap-2">
          {ROUTINE_PRESETS.map((preset, idx) => (
            <button
              key={idx}
              onClick={() => loadPreset(preset)}
              className="px-2.5 py-1 text-left rounded-[4px] border border-line bg-card hover:bg-paper text-[11px] font-medium text-ink transition-colors"
            >
              {preset.title.split(":")[0]}
            </button>
          ))}
        </div>
      </div>

      {/* Products Input Cards */}
      <div className="grid gap-3 sm:grid-cols-2 mb-4">
        {products.map((p, idx) => (
          <div key={idx} className="rounded-[6px] border border-line2 bg-card p-3 shadow-xs flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-2">
                <input
                  type="text"
                  value={p.name}
                  onChange={(e) => updateProduct(idx, "name", e.target.value)}
                  className="font-semibold text-[12.5px] text-ink bg-transparent border-b border-transparent focus:border-line focus:outline-none w-full"
                  placeholder="Product Name"
                />
                {products.length > 2 && (
                  <button onClick={() => removeProduct(idx)} className="text-inksoft hover:text-red-500 ml-2" title="Remove Product">
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
              <textarea
                value={p.ingredients}
                onChange={(e) => updateProduct(idx, "ingredients", e.target.value)}
                placeholder="Comma-separated ingredients (e.g. Water, Glycolic Acid, Glycerin)"
                className="w-full min-h-[60px] rounded-[4px] border border-line bg-paper/60 p-2 text-[12px] text-ink font-mono focus:border-ink/30 focus:outline-none resize-none"
              />
            </div>
          </div>
        ))}
      </div>

      <div className="flex items-center justify-between gap-3 pt-2 border-t border-line/60">
        {products.length < 4 ? (
          <GhostButton onClick={addProduct} className="h-9 text-[12px]">
            <Plus className="w-3.5 h-3.5 mr-1" /> Add Layer Product
          </GhostButton>
        ) : <div />}
        <InkButton onClick={runRoutineAnalysis} disabled={busy} className="h-9 px-5 text-[12px]">
          {busy ? "Evaluating Layering..." : "Simulate Routine Layering Risk"}
        </InkButton>
      </div>

      {/* Routine Layering Results */}
      {report && (
        <div className="mt-5 pt-4 border-t border-line animate-rise">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 p-3.5 rounded-[8px] bg-card border border-line">
            <div className="flex items-center gap-3">
              <div className={`size-12 rounded-full flex items-center justify-center font-bold text-lg font-display border ${
                report.routine_safety_score >= 80 ? "bg-emerald-50 text-emerald-700 border-emerald-300" :
                report.routine_safety_score >= 50 ? "bg-amber-50 text-amber-700 border-amber-300" :
                "bg-red-50 text-red-700 border-red-300"
              }`}>
                {report.routine_safety_score}
              </div>
              <div>
                <h4 className="font-semibold text-[13px] text-ink">
                  Routine Safety Index: {report.is_safe_to_layer ? "Safe to Layer" : "Adverse Chemical Conflicts Detected"}
                </h4>
                <p className="text-[11px] text-inksoft">
                  Evaluated {report.products_evaluated} simultaneous formulations across the stratum corneum barrier.
                </p>
              </div>
            </div>
            <span className={`px-2.5 py-1 rounded-full text-[11px] font-semibold border ${
              report.is_safe_to_layer ? "bg-emerald-100 text-emerald-800 border-emerald-200" : "bg-red-100 text-red-800 border-red-200"
            }`}>
              {report.is_safe_to_layer ? "✅ Compatible Routine" : "⚠️ High Layering Hazard"}
            </span>
          </div>

          {/* Cross-Product Clash Warnings */}
          {report.cross_product_conflicts && report.cross_product_conflicts.length > 0 && (
            <div className="mt-3 p-3.5 rounded-[6px] border border-red-200 bg-red-50/40 dark:bg-red-950/20">
              <h5 className="font-bold text-[12px] uppercase text-red-700 dark:text-red-300 flex items-center gap-1.5 mb-2">
                <AlertTriangle className="w-4 h-4" /> Cross-Product Active Interferences:
              </h5>
              <div className="space-y-2">
                {report.cross_product_conflicts.map((c: any, i: number) => (
                  <div key={i} className="p-2.5 rounded bg-card border border-red-100 dark:border-red-900 text-[12px]">
                    <div className="flex items-center gap-1.5 font-bold text-red-600 dark:text-red-400">
                      <span>{c.product_a}</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                      <span>{c.product_b}</span>
                      <span className="ml-auto font-mono text-[10px] uppercase px-1.5 py-0.5 rounded bg-red-100 dark:bg-red-900/50 text-red-800 dark:text-red-300">
                        {c.conflict_pair.join(" + ").toUpperCase()}
                      </span>
                    </div>
                    <p className="mt-1 text-inksoft text-[11.5px]">{c.warning}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Active Stacking Alerts */}
          {report.stacking_overdose_alerts && report.stacking_overdose_alerts.length > 0 && (
            <div className="mt-3 p-3.5 rounded-[6px] border border-amber-200 bg-amber-50/40 dark:bg-amber-950/20 text-[12px]">
              <h5 className="font-bold text-[12px] uppercase text-amber-800 dark:text-amber-300 flex items-center gap-1.5 mb-2">
                <AlertTriangle className="w-4 h-4" /> Cumulative Active Overdose Warning:
              </h5>
              {report.stacking_overdose_alerts.map((alert: any, i: number) => (
                <div key={i} className="p-2 rounded bg-card border border-amber-100 text-[11.5px] text-inksoft mb-1.5">
                  <span className="font-bold text-ink">{alert.active}: </span>
                  {alert.warning}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
