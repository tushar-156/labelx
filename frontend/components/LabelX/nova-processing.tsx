"use client";

import { Layers, Target, Scale, HelpCircle, Check, X, AlertCircle } from "lucide-react";

interface NovaProps {
  intelligence?: any;
}

export function NovaProcessingView({ intelligence }: NovaProps) {
  const nova = intelligence?.nova || {
    group: 4,
    tier_name: "Ultra-Processed (UPF)",
    color: "red",
    description: "Industrial formulations made mostly from substances derived from foods and synthetic additives.",
    upf_markers: ["Maltodextrin", "Sodium Benzoate (E211)", "Artificial Flavor", "Tartrazine (E102)"]
  };

  const intent = intelligence?.intent || {
    intent: "Parent Checking Child Nutrition & Toxicity",
    rationale: "Evaluating safety for pediatric metabolism, hyperactive colorant risks (Southampton 6), and sugar spikes.",
    suitability: "Acceptable with Moderation",
    priority_nutrients: ["Added Sugar", "Synthetic Azo Dyes (E102, E110)", "Dietary Fiber"]
  };

  const tradeoffs = intelligence?.tradeoffs || {
    positive_aspects: [
      "Convenient shelf-stable caloric energy source.",
      "Fortified with essential Vitamin C (Ascorbic Acid)."
    ],
    negative_aspects: [
      "Ultra-processed footprint with chemical preservative (E211).",
      "Contains artificial dye (E102) requiring hyperactivity cautionary advisory in EU."
    ],
    consumer_tradeoff_summary: "High sensory and shelf-life convenience, but carries multiple synthetic additives and refined carbohydrates.",
    verdict: "Fair",
    frequency_recommendation: "Occasional Treat (1-2 times/week)"
  };

  const uncertainty = intelligence?.uncertainty || {
    has_gaps: false,
    confidence_score: 0.92,
    flags: [],
    recommendation: "All key statutory nutritional values identified with high confidence."
  };

  const getGroupBadgeColor = (group: number) => {
    switch (group) {
      case 1: return "bg-emerald-500/10 text-emerald-600 border-emerald-300 dark:border-emerald-800";
      case 2: return "bg-teal-500/10 text-teal-600 border-teal-300 dark:border-teal-800";
      case 3: return "bg-amber-500/10 text-amber-600 border-amber-300 dark:border-amber-800";
      default: return "bg-rose-500/10 text-rose-600 border-rose-300 dark:border-rose-800";
    }
  };

  return (
    <div className="rounded-xl border border-line bg-card p-5 shadow-sm space-y-5">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line pb-4">
        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-500/10 text-indigo-600 dark:text-indigo-400">
            <Layers size={18} />
          </div>
          <div>
            <h3 className="text-[15px] font-semibold text-ink">NOVA Processing & Consumer Intent Intelligence</h3>
            <p className="text-[12px] text-inksoft">
              Classifies industrial processing depth (NOVA Groups 1-4) and matches formulation against buyer intent.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[11px] font-medium text-inksoft uppercase tracking-wider">Frequency:</span>
          <span className="rounded-md bg-paper px-2.5 py-1 text-[11px] font-bold text-ink border border-line">
            {tradeoffs.frequency_recommendation}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* NOVA Classification */}
        <div className="rounded-lg border border-line bg-paper p-4 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-medium text-inksoft uppercase tracking-wider">NOVA Classification</span>
            <span className={`rounded-full border px-2.5 py-0.5 text-[11px] font-bold ${getGroupBadgeColor(nova.group)}`}>
              NOVA Group {nova.group}: {nova.tier_name}
            </span>
          </div>

          <p className="text-[12px] text-ink">{nova.description}</p>

          {nova.upf_markers && nova.upf_markers.length > 0 && (
            <div className="pt-2 border-t border-line/60">
              <span className="text-[11px] font-medium text-inksoft">Detected UPF Cosmetic Additives:</span>
              <div className="flex flex-wrap gap-1.5 mt-1.5">
                {nova.upf_markers.map((marker: string) => (
                  <span
                    key={marker}
                    className="rounded bg-rose-500/10 px-2 py-0.5 text-[11px] font-medium text-rose-600 border border-rose-200/50"
                  >
                    {marker}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Consumer Intent */}
        <div className="rounded-lg border border-line bg-paper p-4 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-medium text-inksoft uppercase tracking-wider">Inferred Consumer Intent</span>
            <span className="rounded-full bg-indigo-500/10 px-2.5 py-0.5 text-[11px] font-bold text-indigo-600 border border-indigo-200">
              {intent.suitability}
            </span>
          </div>

          <h4 className="text-[13px] font-semibold text-ink flex items-center gap-1.5">
            <Target size={14} className="text-indigo-500" />
            {intent.intent}
          </h4>

          <p className="text-[12px] text-inksoft">{intent.rationale}</p>

          {intent.priority_nutrients && (
            <div className="pt-2 border-t border-line/60">
              <span className="text-[11px] font-medium text-inksoft">Priority Nutrients Monitored:</span>
              <div className="flex flex-wrap gap-1 mt-1">
                {intent.priority_nutrients.map((n: string) => (
                  <span key={n} className="rounded bg-paper2 px-2 py-0.5 text-[10px] text-ink font-medium">
                    {n}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Balanced Nutritional Trade-Offs */}
      <div className="rounded-lg border border-line bg-paper p-4 space-y-3">
        <div className="flex items-center justify-between">
          <h4 className="text-[13px] font-semibold text-ink flex items-center gap-1.5">
            <Scale size={15} className="text-emerald-500" />
            Objective Nutritional Trade-Offs
          </h4>
          <span className="text-[11px] font-bold text-ink">Verdict: {tradeoffs.verdict}</span>
        </div>

        <p className="text-[12px] text-inksoft italic">{tradeoffs.consumer_tradeoff_summary}</p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
          <div className="rounded-md border border-emerald-200/60 bg-emerald-50/20 dark:bg-emerald-950/10 p-2.5 space-y-1">
            <span className="text-[11px] font-semibold text-emerald-700 dark:text-emerald-400 flex items-center gap-1">
              <Check size={12} /> Positive Attributes
            </span>
            <ul className="text-[11px] text-ink space-y-1 pl-1">
              {tradeoffs.positive_aspects?.map((p: string, i: number) => (
                <li key={i}>• {p}</li>
              ))}
            </ul>
          </div>

          <div className="rounded-md border border-rose-200/60 bg-rose-50/20 dark:bg-rose-950/10 p-2.5 space-y-1">
            <span className="text-[11px] font-semibold text-rose-700 dark:text-rose-400 flex items-center gap-1">
              <X size={12} /> Nutritional Trade-Offs / Risks
            </span>
            <ul className="text-[11px] text-ink space-y-1 pl-1">
              {tradeoffs.negative_aspects?.map((n: string, i: number) => (
                <li key={i}>• {n}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Uncertainty & Data-Gap Reporting */}
      {uncertainty.has_gaps && (
        <div className="flex items-start gap-2.5 rounded-lg border border-amber-200 bg-amber-50/50 dark:border-amber-900 dark:bg-amber-950/20 p-3 text-[12px]">
          <AlertCircle size={16} className="text-amber-600 mt-0.5 shrink-0" />
          <div>
            <div className="font-semibold text-amber-800 dark:text-amber-300">
              Data-Gap Audit (Confidence: {(uncertainty.confidence_score * 100).toFixed(0)}%)
            </div>
            <p className="mt-0.5 text-amber-700 dark:text-amber-400">
              {uncertainty.recommendation}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
