"use client";

import { ShieldAlert, AlertTriangle, CheckCircle, Search, HelpCircle, Flame, Baby, Info } from "lucide-react";

export interface GreenwashingAlertItem {
  claimed_label: string;
  actual_substance_detected: string;
  glycemic_index_or_risk: string;
  deception_mechanism: string;
  regulatory_verdict: string;
}

export interface HierarchyAuditData {
  top_3_ingredients: string[];
  dominant_filler?: string;
  is_sugar_in_top_3: boolean;
  is_palm_oil_in_top_3: boolean;
  is_refined_flour_in_top_3: boolean;
  hierarchy_verdict: string;
  consumer_tip: string;
}

export interface LabelPadhegaReportData {
  hierarchy: HierarchyAuditData;
  greenwashing_alerts: GreenwashingAlertItem[];
  palm_oil_alert?: string | null;
  children_marketing_alert?: string | null;
  summary_verdict: string;
}

interface LabelPadhegaCardProps {
  data?: LabelPadhegaReportData;
}

export function LabelPadhegaCard({ data }: LabelPadhegaCardProps) {
  if (!data) return null;

  const { hierarchy, greenwashing_alerts, palm_oil_alert, children_marketing_alert, summary_verdict } = data;
  const isHighRisk = hierarchy.is_sugar_in_top_3 || hierarchy.is_palm_oil_in_top_3 || hierarchy.is_refined_flour_in_top_3 || greenwashing_alerts.length > 0;

  return (
    <div className="rounded-2xl border border-line bg-paper p-6 shadow-sm space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-line pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-500/10 text-amber-600 dark:text-amber-400 font-bold text-lg">
            🇮🇳
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold text-ink">#LabelPadhegaIndia Deceptive Marketing Buster</h3>
              <span className="rounded-full bg-amber-500/10 px-2 py-0.5 text-[10px] font-semibold text-amber-700 dark:text-amber-300">
                FSSAI Descending Rule
              </span>
            </div>
            <p className="text-xs text-inksoft">
              Unmasking deceptive front-of-pack claims by decoding the raw descending order ingredients list.
            </p>
          </div>
        </div>

        <div className={`px-3 py-1 rounded-full text-xs font-semibold flex items-center gap-1.5 self-start sm:self-auto ${
          isHighRisk ? "bg-red-500/10 text-red-700 dark:text-red-400 border border-red-500/20" : "bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-500/20"
        }`}>
          {isHighRisk ? <AlertTriangle className="h-3.5 w-3.5" /> : <CheckCircle className="h-3.5 w-3.5" />}
          {isHighRisk ? "Deceptive Formulation Detected" : "Honest Whole-Food Base"}
        </div>
      </div>

      {/* 1. Hierarchy Analyzer (Top 3 Ingredients) */}
      <div className="rounded-xl border border-line/60 bg-surface/50 p-4 space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold uppercase tracking-wider text-inksoft flex items-center gap-1.5">
            <Search className="h-3.5 w-3.5 text-accent" />
            Top 3 Dominant Ingredients (~70-80% of volume)
          </span>
          {hierarchy.dominant_filler && (
            <span className="text-[11px] font-bold text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-950/40 px-2 py-0.5 rounded-md border border-red-200 dark:border-red-900/40">
              Primary Mass: {hierarchy.dominant_filler}
            </span>
          )}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
          {hierarchy.top_3_ingredients.map((ing, idx) => {
            const isSuspicious = ing.toLowerCase().includes("sugar") || 
                                ing.toLowerCase().includes("palm") || 
                                ing.toLowerCase().includes("maida") || 
                                ing.toLowerCase().includes("maltodextrin") ||
                                ing.toLowerCase().includes("flour");
            return (
              <div
                key={idx}
                className={`flex items-center gap-2.5 p-2.5 rounded-lg border text-xs ${
                  isSuspicious
                    ? "border-amber-300 dark:border-amber-900/50 bg-amber-50/50 dark:bg-amber-950/20 text-ink"
                    : "border-line bg-paper text-ink"
                }`}
              >
                <span className="flex h-5 w-5 items-center justify-center rounded-full bg-accent/10 text-accent font-bold text-[10px]">
                  #{idx + 1}
                </span>
                <span className="font-semibold truncate">{ing}</span>
              </div>
            );
          })}
        </div>

        <p className="text-xs text-inksoft italic">
          💡 <strong className="text-ink">Consumer Rule:</strong> {hierarchy.consumer_tip}
        </p>
      </div>

      {/* 2. Refined Palmolein Alert */}
      {palm_oil_alert && (
        <div className="flex items-start gap-3 p-3.5 rounded-xl border border-amber-300 dark:border-amber-900/60 bg-amber-50 dark:bg-amber-950/30 text-amber-950 dark:text-amber-200">
          <Flame className="h-4 w-4 text-amber-600 dark:text-amber-400 mt-0.5 shrink-0" />
          <div className="text-xs space-y-1">
            <div className="font-bold">Refined Palmolein Warning</div>
            <p className="text-amber-800 dark:text-amber-300">{palm_oil_alert}</p>
          </div>
        </div>
      )}

      {/* 3. Children Southampton Six Azo Dye Alert */}
      {children_marketing_alert && (
        <div className="flex items-start gap-3 p-3.5 rounded-xl border border-red-300 dark:border-red-900/60 bg-red-50 dark:bg-red-950/30 text-red-950 dark:text-red-200">
          <Baby className="h-4 w-4 text-red-600 dark:text-red-400 mt-0.5 shrink-0" />
          <div className="text-xs space-y-1">
            <div className="font-bold">Pediatric Warning: Southampton Six Azo Dyes</div>
            <p className="text-red-800 dark:text-red-300">{children_marketing_alert}</p>
          </div>
        </div>
      )}

      {/* 4. Greenwashing Contradiction Alerts */}
      {greenwashing_alerts && greenwashing_alerts.length > 0 && (
        <div className="space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-red-600 dark:text-red-400 flex items-center gap-1.5">
            <ShieldAlert className="h-3.5 w-3.5" />
            Front-of-Pack Deceptive Greenwashing Unmasked ({greenwashing_alerts.length})
          </h4>

          <div className="grid grid-cols-1 gap-3">
            {greenwashing_alerts.map((alert, idx) => (
              <div key={idx} className="rounded-xl border border-red-200 dark:border-red-900/40 bg-red-50/40 dark:bg-red-950/20 p-3.5 space-y-2">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="line-through text-xs text-red-600 dark:text-red-400 font-bold bg-red-100 dark:bg-red-900/40 px-2 py-0.5 rounded">
                      Claimed: {alert.claimed_label}
                    </span>
                    <span className="text-xs font-bold text-ink">➡️ Actual: {alert.actual_substance_detected}</span>
                  </div>
                  <span className="text-[11px] font-semibold text-red-700 dark:text-red-300 bg-red-200/50 dark:bg-red-900/50 px-2 py-0.5 rounded">
                    {alert.glycemic_index_or_risk}
                  </span>
                </div>
                <p className="text-xs text-inksoft leading-relaxed">{alert.deception_mechanism}</p>
                <div className="text-[11px] text-red-600 dark:text-red-400 font-medium">
                  ⚖️ <strong>Regulatory Verdict:</strong> {alert.regulatory_verdict}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Summary Banner */}
      <div className="p-3 rounded-lg bg-surface border border-line text-xs flex items-center gap-2 text-ink">
        <Info className="h-4 w-4 text-accent shrink-0" />
        <span>{summary_verdict}</span>
      </div>
    </div>
  );
}
