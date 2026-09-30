"use client";

import { ShieldAlert, CheckCircle2, XCircle, AlertCircle, Info } from "lucide-react";

interface AllergenRow {
  category: string;
  detected: boolean;
  declared: boolean;
  triggering_ingredients?: string[];
  severity: "CRITICAL" | "INFO" | "WARNING";
}

interface AllergenMatrixProps {
  findings?: any[];
  declaredAllergens?: string[];
  ingredients?: string[];
}

const CORE_ALLERGEN_CATEGORIES = [
  "Milk & Dairy",
  "Eggs",
  "Peanuts",
  "Tree Nuts (Almonds, Cashews, Walnuts)",
  "Soybeans",
  "Wheat & Gluten",
  "Fish",
  "Crustacean Shellfish"
];

export function AllergenMatrix({ findings = [], declaredAllergens = [], ingredients = [] }: AllergenMatrixProps) {
  // Parse allergen findings from compliance pipeline
  const allergenFindings = findings.filter((f) => f.module === "allergens");

  // Build matrix rows
  const rows: AllergenRow[] = CORE_ALLERGEN_CATEGORIES.map((cat) => {
    const cleanCat = cat.split(" ")[0].toLowerCase();
    
    // Check if detected in findings
    const undeclaredFinding = allergenFindings.find(
      (f) => f.title.toLowerCase().includes("undeclared") && f.title.toLowerCase().includes(cleanCat)
    );
    const declaredFinding = allergenFindings.find(
      (f) => f.title.toLowerCase().includes("declared") && f.title.toLowerCase().includes(cleanCat)
    );

    const isDeclared = declaredAllergens.some((d) => d.toLowerCase().includes(cleanCat)) || !!declaredFinding;
    const isDetected = !!undeclaredFinding || !!declaredFinding;

    let triggering: string[] = [];
    if (undeclaredFinding) {
      triggering = [undeclaredFinding.description.split("(")[1]?.split(")")[0] || "Found in ingredients"];
    } else if (declaredFinding) {
      triggering = [declaredFinding.description.split(":")[1]?.trim() || "Declared on label"];
    }

    return {
      category: cat,
      detected: isDetected,
      declared: isDeclared,
      triggering_ingredients: triggering,
      severity: isDetected && !isDeclared ? "CRITICAL" : "INFO"
    };
  });

  const criticalCount = rows.filter((r) => r.detected && !r.declared).length;

  return (
    <div className="rounded-xl border border-line bg-card p-5 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line pb-4">
        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-amber-500/10 text-amber-600 dark:text-amber-400">
            <ShieldAlert size={18} />
          </div>
          <div>
            <h3 className="text-[15px] font-semibold text-ink">Detected vs. Declared Allergen Matrix</h3>
            <p className="text-[12px] text-inksoft">
              Cross-references packaging ingredients against the statutory 8 core allergen classes to catch undeclared allergens.
            </p>
          </div>
        </div>

        {criticalCount > 0 ? (
          <span className="flex items-center gap-1.5 rounded-full bg-rose-500/10 px-3 py-1 text-[11px] font-semibold text-rose-600 dark:text-rose-400 border border-rose-200 dark:border-rose-900">
            <AlertCircle size={13} /> {criticalCount} Undeclared Allergen{criticalCount > 1 ? "s" : ""}
          </span>
        ) : (
          <span className="flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-3 py-1 text-[11px] font-semibold text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-900">
            <CheckCircle2 size={13} /> Full Allergen Compliance
          </span>
        )}
      </div>

      <div className="mt-4 overflow-x-auto">
        <table className="w-full text-left text-[12px]">
          <thead>
            <tr className="border-b border-line text-inksoft">
              <th className="py-2.5 px-3 font-medium uppercase tracking-wider">Allergen Group</th>
              <th className="py-2.5 px-3 font-medium uppercase tracking-wider text-center">Detected in Formula</th>
              <th className="py-2.5 px-3 font-medium uppercase tracking-wider text-center">Declared on Package</th>
              <th className="py-2.5 px-3 font-medium uppercase tracking-wider text-center">Compliance Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line/60">
            {rows.map((row) => (
              <tr key={row.category} className="hover:bg-paper/40 transition">
                <td className="py-3 px-3">
                  <div className="font-medium text-ink">{row.category}</div>
                  {row.triggering_ingredients && row.triggering_ingredients.length > 0 && row.detected && (
                    <div className="text-[11px] text-inksoft truncate max-w-[280px]">
                      Source: {row.triggering_ingredients.join(", ")}
                    </div>
                  )}
                </td>
                <td className="py-3 px-3 text-center">
                  {row.detected ? (
                    <span className="inline-flex items-center gap-1 font-semibold text-amber-600 dark:text-amber-400">
                      <AlertCircle size={14} /> Detected
                    </span>
                  ) : (
                    <span className="text-inksoft">—</span>
                  )}
                </td>
                <td className="py-3 px-3 text-center">
                  {row.declared ? (
                    <span className="inline-flex items-center gap-1 font-semibold text-emerald-600 dark:text-emerald-400">
                      <CheckCircle2 size={14} /> Declared
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 font-semibold text-inksoft">
                      <XCircle size={14} /> Not Listed
                    </span>
                  )}
                </td>
                <td className="py-3 px-3 text-center">
                  {row.detected && !row.declared ? (
                    <span className="inline-block rounded-full bg-rose-500/10 px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider text-rose-600 border border-rose-200 dark:border-rose-900">
                      CRITICAL VIOLATION
                    </span>
                  ) : row.detected && row.declared ? (
                    <span className="inline-block rounded-full bg-emerald-500/10 px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider text-emerald-600 border border-emerald-200 dark:border-emerald-900">
                      COMPLIANT
                    </span>
                  ) : (
                    <span className="inline-block rounded-full bg-paper px-2.5 py-0.5 text-[10px] font-medium text-inksoft border border-line">
                      CLEAR
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
