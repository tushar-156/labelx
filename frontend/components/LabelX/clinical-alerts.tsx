"use client";

import { useState } from "react";
import { AlertOctagon, AlertTriangle, Pill, ShieldAlert, HeartPulse, Stethoscope, ChevronDown, ChevronUp, Leaf } from "lucide-react";

interface ClinicalAlertItem {
  ingredient: string;
  condition?: string;
  medication?: string;
  risk_level: "CONTRAINDICATED" | "HIGH_RISK" | "MODERATE_CAUTION" | "MONITOR";
  clinical_mechanism: string;
  recommended_action: string;
  authority_guideline: string;
}

interface BotanicalAllergenItem {
  detected_alias: string;
  root_allergen: string;
  scientific_taxa?: string;
  confidence: number;
  clinical_note: string;
}

interface ClinicalAlertsProps {
  alerts?: ClinicalAlertItem[];
  botanicalAllergens?: BotanicalAllergenItem[];
}

export function ClinicalAlertsBanner({ alerts = [], botanicalAllergens = [] }: ClinicalAlertsProps) {
  const [expanded, setExpanded] = useState(true);

  const hasAlerts = alerts && alerts.length > 0;
  const hasBotanicals = botanicalAllergens && botanicalAllergens.length > 0;

  if (!hasAlerts && !hasBotanicals) {
    return (
      <div className="rounded-[8px] border border-emerald-500/20 bg-emerald-50/50 dark:bg-emerald-950/20 p-3.5 flex items-center justify-between text-xs text-emerald-800 dark:text-emerald-300">
        <div className="flex items-center gap-2">
          <HeartPulse className="w-4 h-4 text-emerald-600 shrink-0" />
          <span className="font-medium">
            Clinical Safety Audit: No critical drug-food contraindications or concealed botanical allergens detected for your active medical profile.
          </span>
        </div>
      </div>
    );
  }

  const criticalCount = alerts.filter(a => a.risk_level === "CONTRAINDICATED" || a.risk_level === "HIGH_RISK").length;

  return (
    <div className={`rounded-[8px] border ${criticalCount > 0 ? "border-red-500/40 bg-red-50/60 dark:bg-red-950/30" : "border-amber-500/40 bg-amber-50/60 dark:bg-amber-950/30"} p-4 shadow-sm`}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <div className={`p-2 rounded-[6px] ${criticalCount > 0 ? "bg-red-500 text-white" : "bg-amber-500 text-white"} shrink-0 mt-0.5`}>
            {criticalCount > 0 ? <AlertOctagon className="w-5 h-5" /> : <AlertTriangle className="w-5 h-5" />}
          </div>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h3 className="text-[14px] font-bold text-ink tracking-tight flex items-center gap-1.5">
                Clinical Pathology & Drug-Food Contraindication Alerts
              </h3>
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                criticalCount > 0 ? "bg-red-100 text-red-800 dark:bg-red-900/60 dark:text-red-200" : "bg-amber-100 text-amber-800 dark:bg-amber-900/60 dark:text-amber-200"
              }`}>
                {criticalCount > 0 ? `${criticalCount} Severe Interaction(s)` : `${alerts.length} Cautionary Alert(s)`}
              </span>
            </div>
            <p className="text-[12px] text-inksoft mt-1">
              Cross-referenced against clinical pharmacological evidence, FDA Drug-Food Interaction Monographs, and Latin botanical taxonomy.
            </p>
          </div>
        </div>

        <button
          onClick={() => setExpanded(!expanded)}
          className="text-inksoft hover:text-ink p-1 rounded hover:bg-paper2 transition-colors cursor-pointer"
          title={expanded ? "Collapse alerts" : "Expand alerts"}
        >
          {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
      </div>

      {expanded && (
        <div className="mt-4 space-y-3 pt-3 border-t border-line/40">
          {/* Botanical / INCI Allergen Unmasker */}
          {hasBotanicals && (
            <div className="rounded-[6px] border border-amber-500/30 bg-card p-3">
              <div className="flex items-center gap-2 mb-2 text-amber-800 dark:text-amber-300 font-semibold text-xs">
                <Leaf className="w-3.5 h-3.5" />
                <span>Botanical / Latin Allergen Unmasker ({botanicalAllergens.length} Concealed Ingredients Discovered)</span>
              </div>
              <div className="space-y-2">
                {botanicalAllergens.map((b, idx) => (
                  <div key={idx} className="p-2 rounded bg-paper2/70 border border-line text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div>
                      <span className="font-bold text-ink italic">{b.detected_alias}</span>
                      <span className="mx-1 text-inksoft">→</span>
                      <span className="font-bold text-red-700 dark:text-red-400 uppercase tracking-wide">
                        Contains Root Allergen: {b.root_allergen}
                      </span>
                      {b.scientific_taxa && (
                        <span className="block text-[11px] text-inksoft font-mono">Taxonomy: {b.scientific_taxa}</span>
                      )}
                    </div>
                    <span className="text-[11px] text-inksoft max-w-sm sm:text-right">
                      {b.clinical_note}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Clinical Alerts List */}
          {alerts.map((a, idx) => {
            const isSevere = a.risk_level === "CONTRAINDICATED" || a.risk_level === "HIGH_RISK";
            return (
              <div
                key={idx}
                className={`p-3.5 rounded-[6px] border ${
                  isSevere ? "border-red-500/30 bg-card" : "border-amber-500/30 bg-card"
                } flex flex-col gap-2`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-bold text-[13px] text-ink">{a.ingredient}</span>
                    {a.condition && (
                      <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-blue-50 text-blue-700 dark:bg-blue-950/40 dark:text-blue-300 border border-blue-200 dark:border-blue-800">
                        Condition: {a.condition}
                      </span>
                    )}
                    {a.medication && (
                      <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-purple-50 text-purple-700 dark:bg-purple-950/40 dark:text-purple-300 border border-purple-200 dark:border-purple-800 flex items-center gap-1">
                        <Pill className="w-2.5 h-2.5" />
                        Drug Interaction: {a.medication}
                      </span>
                    )}
                  </div>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold tracking-wider ${
                      isSevere
                        ? "bg-red-500 text-white"
                        : "bg-amber-100 text-amber-800 dark:bg-amber-900/60 dark:text-amber-200"
                    }`}
                  >
                    {a.risk_level}
                  </span>
                </div>

                <p className="text-[12px] text-ink leading-relaxed">
                  <span className="font-semibold text-inksoft">Clinical Mechanism: </span>
                  {a.clinical_mechanism}
                </p>

                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pt-2 border-t border-line/40 text-[11px]">
                  <div className="text-red-700 dark:text-red-400 font-medium">
                    <span className="text-inksoft font-normal">Action: </span>
                    {a.recommended_action}
                  </div>
                  <div className="text-inksoft font-mono italic">
                    Monograph: {a.authority_guideline}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
