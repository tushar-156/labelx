"use client";

import { useState } from "react";
import { Clock, Calendar, AlertCircle, BookOpen, ChevronDown, ChevronUp, ShieldAlert } from "lucide-react";

export interface TemporalHealthImpactItem {
  ingredient_name: string;
  scientific_name_or_e_code: string;
  category: string;
  risk_level: "Safe" | "Low" | "Moderate" | "High" | "Severe" | string;
  short_term_effects: string;
  long_term_effects: string;
  documented_side_effects: string;
  sources: string[];
}

interface TemporalImpactsCardProps {
  impacts?: TemporalHealthImpactItem[];
}

export function TemporalImpactsCard({ impacts }: TemporalImpactsCardProps) {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(0);

  if (!impacts || impacts.length === 0) return null;

  const getRiskBadge = (risk: string) => {
    switch (risk.toLowerCase()) {
      case "severe":
        return "bg-red-500/15 text-red-700 dark:text-red-400 border border-red-500/30";
      case "high":
        return "bg-amber-500/15 text-amber-700 dark:text-amber-400 border border-amber-500/30";
      case "moderate":
        return "bg-yellow-500/15 text-yellow-700 dark:text-yellow-400 border border-yellow-500/30";
      default:
        return "bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 border border-emerald-500/30";
    }
  };

  return (
    <div className="rounded-2xl border border-line bg-paper p-6 shadow-sm space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-line pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-bold text-ink">Temporal Tripartite Health Impact Matrix</h3>
            <span className="rounded-full bg-accent/10 px-2 py-0.5 text-[10px] font-semibold text-accent">
              0-24h vs Chronic Timeline
            </span>
          </div>
          <p className="text-xs text-inksoft">
            Evidence-backed physiological breakdown comparing acute postprandial effects against long-term toxicological risk.
          </p>
        </div>
        <div className="text-xs font-semibold text-inksoft">
          {impacts.length} Flagged Additive{impacts.length > 1 ? "s" : ""}
        </div>
      </div>

      <div className="space-y-3">
        {impacts.map((item, idx) => {
          const isExpanded = expandedIndex === idx;
          return (
            <div
              key={idx}
              className="rounded-xl border border-line bg-surface/40 overflow-hidden transition-all duration-200"
            >
              {/* Header Toggle */}
              <button
                type="button"
                onClick={() => setExpandedIndex(isExpanded ? null : idx)}
                className="w-full flex items-center justify-between p-4 text-left hover:bg-surface/80 transition-colors"
              >
                <div className="flex flex-wrap items-center gap-2.5">
                  <span className="text-sm font-bold text-ink">{item.ingredient_name}</span>
                  <span className="text-xs text-inksoft">({item.scientific_name_or_e_code})</span>
                  <span className="text-[11px] text-inksoft hidden md:inline">• {item.category}</span>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  <span className={`text-[11px] font-bold px-2 py-0.5 rounded-full ${getRiskBadge(item.risk_level)}`}>
                    {item.risk_level} Risk
                  </span>
                  {isExpanded ? (
                    <ChevronUp className="h-4 w-4 text-inksoft" />
                  ) : (
                    <ChevronDown className="h-4 w-4 text-inksoft" />
                  )}
                </div>
              </button>

              {/* Collapsible Tripartite Content */}
              {isExpanded && (
                <div className="p-4 pt-1 border-t border-line/60 bg-paper/60 space-y-4 text-xs">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-2">
                    {/* Short-Term (0-24h) */}
                    <div className="p-3 rounded-lg border border-line bg-surface/50 space-y-1.5">
                      <div className="flex items-center gap-1.5 font-bold text-ink text-[11px] uppercase tracking-wider">
                        <Clock className="h-3.5 w-3.5 text-amber-500" />
                        Short-Term (0 - 24 Hours)
                      </div>
                      <p className="text-inksoft leading-relaxed">{item.short_term_effects}</p>
                    </div>

                    {/* Long-Term (Chronic) */}
                    <div className="p-3 rounded-lg border border-line bg-surface/50 space-y-1.5">
                      <div className="flex items-center gap-1.5 font-bold text-ink text-[11px] uppercase tracking-wider">
                        <Calendar className="h-3.5 w-3.5 text-red-500" />
                        Long-Term (Chronic Risks)
                      </div>
                      <p className="text-inksoft leading-relaxed">{item.long_term_effects}</p>
                    </div>

                    {/* Documented Side Effects */}
                    <div className="p-3 rounded-lg border border-line bg-surface/50 space-y-1.5">
                      <div className="flex items-center gap-1.5 font-bold text-ink text-[11px] uppercase tracking-wider">
                        <AlertCircle className="h-3.5 w-3.5 text-accent" />
                        Clinical Side Effects
                      </div>
                      <p className="text-inksoft leading-relaxed">{item.documented_side_effects}</p>
                    </div>
                  </div>

                  {/* Sources / PubMed Citations */}
                  {item.sources && item.sources.length > 0 && (
                    <div className="flex flex-wrap items-center gap-2 pt-1 border-t border-line/40">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-inksoft flex items-center gap-1">
                        <BookOpen className="h-3 w-3" />
                        Authoritative Citations:
                      </span>
                      {item.sources.map((src, sIdx) => (
                        <span
                          key={sIdx}
                          className="text-[10px] font-medium px-2 py-0.5 rounded bg-surface border border-line text-inksoft"
                        >
                          {src}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
