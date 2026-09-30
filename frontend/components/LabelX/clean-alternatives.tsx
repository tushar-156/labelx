"use client";

import { useState } from "react";
import { Sparkles, ArrowRight, ShieldCheck, CheckCircle2, ChevronRight, RefreshCw, ThumbsUp } from "lucide-react";

interface CleanAlt {
  name: string;
  brand: string;
  category: string;
  nova_group: number;
  health_score: number;
  why_cleaner: string;
  swapped_out_additives: string[];
}

interface CleanAlternativesProps {
  category?: string;
  alternatives?: CleanAlt[];
}

export function CleanAlternativesCard({ category = "Packaged Food", alternatives = [] }: CleanAlternativesProps) {
  const [selectedAlt, setSelectedAlt] = useState<number>(0);

  if (!alternatives || alternatives.length === 0) {
    return null;
  }

  const active = alternatives[selectedAlt] || alternatives[0];

  return (
    <div className="rounded-[8px] border border-emerald-500/30 bg-paper2/60 p-4 shadow-sm">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-line pb-2.5 mb-3">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
          <h4 className="text-[13px] font-bold tracking-tight text-ink uppercase">
            Clean-Label Alternatives & Smart Swaps ("Swap This Junk")
          </h4>
        </div>
        <span className="font-mono text-[10px] uppercase tracking-wider text-emerald-700 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-950/40 px-2 py-0.5 rounded border border-emerald-300 dark:border-emerald-800 w-fit">
          Category: {category}
        </span>
      </div>

      <p className="text-[12px] text-inksoft mb-4">
        Evidence-backed healthier substitutes containing zero ultra-processed industrial additives, harmful preservatives, or hidden trans fats.
      </p>

      {/* Tabs for Alternatives */}
      <div className="flex flex-wrap gap-2 mb-4">
        {alternatives.map((alt, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => setSelectedAlt(idx)}
            className={`px-3 py-1.5 rounded-[6px] text-xs font-medium transition-all cursor-pointer flex items-center gap-1.5 border ${
              selectedAlt === idx
                ? "bg-card text-ink border-emerald-500 shadow-xs"
                : "bg-paper text-inksoft border-line hover:text-ink hover:bg-paper2"
            }`}
          >
            <span>{alt.brand}</span>
            <span className="text-[10px] px-1.5 py-0.2 rounded bg-emerald-100 text-emerald-800 dark:bg-emerald-900/60 dark:text-emerald-200 font-bold">
              {alt.health_score}/100
            </span>
          </button>
        ))}
      </div>

      {/* Active Alternative Spotlight Card */}
      <div className="rounded-[6px] border border-line2 bg-card p-4">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <span className="font-bold text-[14px] text-ink">{active.name}</span>
              <span className="text-[12px] text-inksoft">by {active.brand}</span>
            </div>
            <div className="mt-1 flex items-center gap-2">
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-50 text-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                NOVA Group {active.nova_group} ({active.nova_group <= 2 ? "Minimally Processed" : "Processed"})
              </span>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-ink text-paper">
                Score: {active.health_score}/100
              </span>
            </div>
          </div>

          <div className="text-right sm:self-start">
            <span className="text-[11px] uppercase tracking-wider font-semibold text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
              <ThumbsUp className="w-3.5 h-3.5" />
              Nutritional Upgrade
            </span>
          </div>
        </div>

        {/* Why It's Cleaner */}
        <div className="mt-3 p-2.5 rounded bg-paper font-sans text-xs text-ink leading-relaxed border border-line/60">
          <span className="font-semibold text-emerald-700 dark:text-emerald-400">Why It's Better: </span>
          {active.why_cleaner}
        </div>

        {/* Swapped Out Additives */}
        {active.swapped_out_additives && active.swapped_out_additives.length > 0 && (
          <div className="mt-3">
            <span className="text-[11px] font-semibold text-inksoft uppercase tracking-wider block mb-1.5">
              Harmful Ingredients Eliminated vs Traditional Brands:
            </span>
            <div className="flex flex-wrap gap-1.5">
              {active.swapped_out_additives.map((add, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono bg-red-50 text-red-700 dark:bg-red-950/40 dark:text-red-300 border border-red-200 dark:border-red-900"
                >
                  <span className="text-red-500 font-bold">✕</span> {add}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
