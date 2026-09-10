"use client";

import { Activity, Heart, ShieldAlert, Baby, Sparkles, Filter, Droplet } from "lucide-react";

export type DietaryLensId = "all" | "diabetic" | "renal" | "cardiac" | "asthma" | "pediatric" | "clean_label";

interface DietaryLensOption {
  id: DietaryLensId;
  label: string;
  badge: string;
  iconName: string;
  description: string;
  criticalFocus: string[];
}

export const DIETARY_LENSES: DietaryLensOption[] = [
  {
    id: "all",
    label: "Full Spectrum",
    badge: "All Criteria",
    iconName: "Filter",
    description: "Evaluates comprehensive statutory compliance, food fraud, chemical additives, and allergens.",
    criticalFocus: ["FSSAI Schedule I", "Allergens", "Claims Verifier", "Adulteration"]
  },
  {
    id: "diabetic",
    label: "Diabetic & Glycemic",
    badge: "Glycemic Impact",
    iconName: "Activity",
    description: "Strict surveillance of hidden sugars, maltodextrin (GI 110-185), high-fructose corn syrup, and refined starches.",
    criticalFocus: ["Hidden Sugars", "Maltodextrin", "Invert Syrup", "Total Carbs"]
  },
  {
    id: "renal",
    label: "Renal & Kidney",
    badge: "Electrolyte Load",
    iconName: "Droplet",
    description: "Monitors potassium sorbate (E202), sodium benzoates, synthetic phosphates, and excessive mineral burdens.",
    criticalFocus: ["Potassium Sorbate", "Sodium Load", "Phosphates", "Heavy Preservatives"]
  },
  {
    id: "cardiac",
    label: "Cardiac & Hypertension",
    badge: "Vascular Risk",
    iconName: "Heart",
    description: "Audits sodium chloride density, hydrogenated vegetable oils (trans fats), palmolein, and synthetic antioxidants.",
    criticalFocus: ["Sodium > 400mg", "Palmolein", "TBHQ (E319)", "Trans Fatty Acids"]
  },
  {
    id: "asthma",
    label: "Respiratory & Asthma",
    badge: "Bronchospasm Triggers",
    iconName: "ShieldAlert",
    description: "Screens for sulfur dioxide (E220-E228), sulfites, sodium benzoates (E211), and azo colorants (Tartrazine E102).",
    criticalFocus: ["Sulfites (E220-228)", "Benzoates (E211)", "Tartrazine (E102)", "Salicylates"]
  },
  {
    id: "pediatric",
    label: "Pediatric & Kids",
    badge: "Child Development",
    iconName: "Baby",
    description: "Enforces WHO Southampton Six bans: artificial colorants, excessive caffeine, and intense non-nutritive sweeteners.",
    criticalFocus: ["Southampton Six Azo Dyes", "Aspartame", "Sucralose", "Caffeine"]
  },
  {
    id: "clean_label",
    label: "100% Clean Label",
    badge: "NOVA 1-2 Only",
    iconName: "Sparkles",
    description: "Zero tolerance for artificial preservatives, synthetic emulsifiers, INS codes, or ultra-processed ingredients.",
    criticalFocus: ["Zero E-Codes", "Zero Emulsifiers", "Zero Artificial Flavor", "NOVA Group 1-2"]
  }
];

interface DietaryLensesToolbarProps {
  activeLens: DietaryLensId;
  onSelectLens: (lens: DietaryLensId) => void;
}

export function DietaryLensesToolbar({ activeLens, onSelectLens }: DietaryLensesToolbarProps) {
  const current = DIETARY_LENSES.find(l => l.id === activeLens) || DIETARY_LENSES[0];

  return (
    <div className="rounded-[8px] border border-line bg-paper2/50 p-3 shadow-xs">
      <div className="flex items-center justify-between mb-2">
        <span className="font-mono text-[11px] font-semibold uppercase tracking-wider text-ink flex items-center gap-1.5">
          <Filter className="w-3.5 h-3.5 text-inksoft" />
          Specialized Health & Pathology Lenses
        </span>
        <span className="text-[10px] text-inksoft font-mono">1-Click Diagnostic Filter</span>
      </div>

      {/* Lens Chips */}
      <div className="flex flex-wrap gap-1.5">
        {DIETARY_LENSES.map(lens => {
          const isSelected = activeLens === lens.id;
          return (
            <button
              key={lens.id}
              type="button"
              onClick={() => onSelectLens(lens.id)}
              className={`px-2.5 py-1 rounded-[6px] text-xs font-medium transition-all cursor-pointer flex items-center gap-1.5 border ${
                isSelected
                  ? "bg-ink text-paper border-ink shadow-xs"
                  : "bg-card text-inksoft border-line hover:text-ink hover:border-ink/40 hover:bg-paper"
              }`}
            >
              <span>{lens.label}</span>
              <span className={`text-[10px] px-1.5 py-0.2 rounded font-mono ${
                isSelected ? "bg-paper/20 text-paper" : "bg-paper2 text-inksoft"
              }`}>
                {lens.badge}
              </span>
            </button>
          );
        })}
      </div>

      {/* Active Lens Description & High Priority Targets */}
      <div className="mt-2.5 p-2 rounded bg-card/80 border border-line/60 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
        <div className="text-ink">
          <span className="font-semibold text-ink">{current.label} Lens: </span>
          <span className="text-inksoft">{current.description}</span>
        </div>
        <div className="flex items-center gap-1 shrink-0 flex-wrap">
          <span className="text-[10px] uppercase font-mono font-bold text-inksoft mr-1">Focus:</span>
          {current.criticalFocus.map((f, i) => (
            <span key={i} className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-paper border border-line text-ink">
              {f}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
