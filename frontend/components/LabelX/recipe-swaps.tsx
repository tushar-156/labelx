"use client";

import { useState } from "react";
import { ChefHat, Clock, Users, Sparkles, Check, ChevronDown, ChevronUp, Utensils } from "lucide-react";

export interface DIYRecipe {
  title: string;
  prep_time_minutes: number;
  cook_time_minutes: number;
  servings: number;
  difficulty: string;
  target_craving: string;
  ingredients: string[];
  instructions: string[];
  why_healthier: string;
  eliminated_industrial_additives: string[];
}

interface RecipeSwapsProps {
  recipes?: DIYRecipe[];
  category?: string;
}

export function RecipeSwapsCard({ recipes = [], category = "Packaged Snack" }: RecipeSwapsProps) {
  const [expandedIndex, setExpandedIndex] = useState<number>(0);

  if (!recipes || recipes.length === 0) {
    return null;
  }

  return (
    <div className="rounded-[8px] border border-line bg-paper2/50 p-4 shadow-sm">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-line pb-2.5 mb-3">
        <div className="flex items-center gap-2">
          <ChefHat className="w-4 h-4 text-ink" />
          <h4 className="text-[13px] font-bold tracking-tight text-ink uppercase">
            "Cook It Yourself Clean" DIY Whole-Food Recipe Swaps
          </h4>
        </div>
        <span className="font-mono text-[10px] uppercase tracking-wider text-emerald-700 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-950/40 px-2 py-0.5 rounded border border-emerald-300 dark:border-emerald-800 w-fit">
          100% Ultra-Processed Free
        </span>
      </div>

      <p className="text-[12px] text-inksoft mb-4">
        Simple homemade whole-food alternatives crafted by nutritionists to satisfy the same cravings without commercial additives, hydrogenated oils, or synthetic flavor enhancers:
      </p>

      {/* Recipe Cards List */}
      <div className="space-y-3">
        {recipes.map((rec, idx) => {
          const isExpanded = expandedIndex === idx;
          return (
            <div key={idx} className="rounded-[6px] border border-line2 bg-card overflow-hidden">
              <div
                onClick={() => setExpandedIndex(isExpanded ? -1 : idx)}
                className="p-3.5 flex items-start justify-between gap-3 cursor-pointer hover:bg-paper2/50 transition-colors"
              >
                <div>
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-bold text-[13px] text-ink">{rec.title}</span>
                    <span className="px-2 py-0.2 rounded text-[10px] font-mono bg-paper border border-line text-inksoft">
                      Craving: {rec.target_craving}
                    </span>
                  </div>
                  <div className="mt-1 flex items-center gap-3 text-[11px] text-inksoft font-mono">
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3" /> {rec.prep_time_minutes + rec.cook_time_minutes} mins total
                    </span>
                    <span className="flex items-center gap-1">
                      <Users className="w-3 h-3" /> {rec.servings} serving(s)
                    </span>
                    <span className="text-emerald-600 font-semibold">
                      {rec.difficulty}
                    </span>
                  </div>
                </div>

                <button
                  type="button"
                  className="text-inksoft p-1 rounded hover:bg-paper"
                >
                  {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                </button>
              </div>

              {isExpanded && (
                <div className="p-3.5 pt-0 border-t border-line/40 space-y-3 mt-1 text-xs">
                  {/* Why it's healthier */}
                  <div className="p-2.5 rounded bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-500/20 text-emerald-900 dark:text-emerald-200">
                    <strong className="font-semibold">Nutritional Advantage: </strong>
                    {rec.why_healthier}
                  </div>

                  <div className="grid gap-3 sm:grid-cols-2">
                    {/* Ingredients */}
                    <div>
                      <span className="text-[11px] font-semibold text-inksoft uppercase tracking-wider block mb-1.5">
                        Clean Kitchen Ingredients:
                      </span>
                      <ul className="space-y-1">
                        {rec.ingredients.map((ing, i) => (
                          <li key={i} className="text-ink flex items-start gap-1.5">
                            <span className="text-emerald-600 font-bold">•</span>
                            <span>{ing}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Step-by-step instructions */}
                    <div>
                      <span className="text-[11px] font-semibold text-inksoft uppercase tracking-wider block mb-1.5">
                        Preparation Steps:
                      </span>
                      <ol className="space-y-1 list-decimal list-inside text-ink leading-relaxed">
                        {rec.instructions.map((step, i) => (
                          <li key={i} className="pl-1">
                            <span>{step}</span>
                          </li>
                        ))}
                      </ol>
                    </div>
                  </div>

                  {/* Additives Eliminated */}
                  {rec.eliminated_industrial_additives && rec.eliminated_industrial_additives.length > 0 && (
                    <div className="pt-2 border-t border-line/40">
                      <span className="text-[10px] uppercase font-mono text-inksoft mr-1">
                        Eliminated Industrial Toxins:
                      </span>
                      <div className="inline-flex flex-wrap gap-1 mt-1">
                        {rec.eliminated_industrial_additives.map((add, i) => (
                          <span key={i} className="px-1.5 py-0.2 rounded text-[10px] font-mono bg-red-50 text-red-700 dark:bg-red-950/40 dark:text-red-300 border border-red-200 dark:border-red-900">
                            ✕ {add}
                          </span>
                        ))}
                      </div>
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
