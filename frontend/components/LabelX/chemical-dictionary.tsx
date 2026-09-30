"use client";

import { useState } from "react";
import { BookOpen, AlertOctagon, Sparkles, MinusCircle, ChevronDown, ChevronUp } from "lucide-react";

interface ChemicalDictionaryProps {
  translations?: {
    harmful?: any[];
    beneficial?: any[];
    neutral?: any[];
  };
}

export function ChemicalDictionary({ translations }: ChemicalDictionaryProps) {
  const [activeTab, setActiveTab] = useState<"harmful" | "beneficial" | "neutral">("harmful");
  const [expandedItem, setExpandedItem] = useState<string | null>(null);

  const harmfulList = translations?.harmful || [
    {
      name: "INS 211 / Sodium Benzoate",
      original_code: "E211",
      category: "harmful",
      common_name: "Sodium Benzoate (Synthetic Preservative)",
      simple_explanation: "A chemical preservative used to prevent mold and yeast in acidic beverages and sauces.",
      potential_risks: "Can react with Vitamin C (Ascorbic Acid) to form benzene, a known carcinogen. May trigger hyperactivity in children."
    },
    {
      name: "TBHQ",
      original_code: "E319",
      category: "harmful",
      common_name: "TBHQ (Petroleum-Derived Antioxidant)",
      simple_explanation: "A synthetic petroleum byproduct used to prevent industrial vegetable oils from turning rancid.",
      potential_risks: "Linked to cellular oxidative stress and potential immune system disruptions in long-term rodent studies."
    },
    {
      name: "Maltodextrin",
      original_code: null,
      category: "harmful",
      common_name: "Maltodextrin (Refined Starch Bulking Agent)",
      simple_explanation: "A highly processed white powder with an exceptionally high glycemic index (110).",
      potential_risks: "Causes rapid blood glucose spikes higher than table sugar; alters gut bacterial diversity."
    }
  ];

  const beneficialList = translations?.beneficial || [
    {
      name: "Curcumin",
      original_code: "E100",
      category: "beneficial",
      common_name: "Curcumin (Turmeric Extract)",
      simple_explanation: "The active natural polyphenol extracted from turmeric root.",
      health_benefits: "Potent anti-inflammatory and cellular antioxidant properties supporting vascular health."
    },
    {
      name: "Ascorbic Acid",
      original_code: "E300",
      category: "beneficial",
      common_name: "Vitamin C",
      simple_explanation: "Pure Vitamin C, an essential antioxidant protecting against oxidation.",
      health_benefits: "Supports immune function, collagen synthesis, and neutralizes free radicals."
    }
  ];

  const neutralList = translations?.neutral || [
    {
      name: "Guar Gum",
      original_code: "E412",
      category: "neutral",
      common_name: "Guar Gum (Natural Plant Soluble Fiber)",
      simple_explanation: "A water-soluble dietary fiber extracted from guar beans used as a natural thickener.",
      health_benefits: "Acts as a prebiotic fiber; safe for general consumption in standard quantities."
    },
    {
      name: "Citric Acid",
      original_code: "E330",
      category: "neutral",
      common_name: "Citric Acid",
      simple_explanation: "A natural fruit acid providing sour tartness and adjusting acidity.",
      health_benefits: "Standard non-toxic buffering agent."
    }
  ];

  const currentList =
    activeTab === "harmful" ? harmfulList : activeTab === "beneficial" ? beneficialList : neutralList;

  const toggleExpand = (name: string) => {
    setExpandedItem(expandedItem === name ? null : name);
  };

  return (
    <div className="rounded-xl border border-line bg-card p-5 shadow-sm space-y-4">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line pb-4">
        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-teal-500/10 text-teal-600 dark:text-teal-400">
            <BookOpen size={18} />
          </div>
          <div>
            <h3 className="text-[15px] font-semibold text-ink">Plain-English Chemical Translator</h3>
            <p className="text-[12px] text-inksoft">
              Translates cryptic chemical numbers (INS, E-codes, chemical additives) into transparent layman explanations.
            </p>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex items-center gap-1 rounded-lg border border-line bg-paper p-1">
          <button
            onClick={() => setActiveTab("harmful")}
            className={`flex items-center gap-1.5 rounded-md px-3 py-1 text-[11px] font-medium transition ${
              activeTab === "harmful"
                ? "bg-rose-500 text-white shadow-sm"
                : "text-inksoft hover:text-ink"
            }`}
          >
            <AlertOctagon size={12} />
            Harmful ({harmfulList.length})
          </button>
          <button
            onClick={() => setActiveTab("beneficial")}
            className={`flex items-center gap-1.5 rounded-md px-3 py-1 text-[11px] font-medium transition ${
              activeTab === "beneficial"
                ? "bg-emerald-600 text-white shadow-sm"
                : "text-inksoft hover:text-ink"
            }`}
          >
            <Sparkles size={12} />
            Beneficial ({beneficialList.length})
          </button>
          <button
            onClick={() => setActiveTab("neutral")}
            className={`flex items-center gap-1.5 rounded-md px-3 py-1 text-[11px] font-medium transition ${
              activeTab === "neutral"
                ? "bg-ink text-paper shadow-sm"
                : "text-inksoft hover:text-ink"
            }`}
          >
            <MinusCircle size={12} />
            Neutral ({neutralList.length})
          </button>
        </div>
      </div>

      {/* Chemical Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {currentList.length === 0 ? (
          <div className="col-span-2 rounded-lg border border-line bg-paper p-5 text-center text-[12px] text-inksoft">
            No ingredients classified in this category for this product.
          </div>
        ) : (
          currentList.map((item: any, i: number) => {
            const isExpanded = expandedItem === item.name;
            return (
              <div
                key={i}
                className="rounded-lg border border-line bg-paper p-3.5 space-y-2 hover:border-inksoft transition cursor-pointer"
                onClick={() => toggleExpand(item.name)}
              >
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <div className="flex items-center gap-1.5">
                      <span className="font-semibold text-ink text-[13px]">{item.common_name || item.name}</span>
                      {item.original_code && (
                        <span className="rounded bg-paper2 px-1.5 py-0.5 text-[10px] font-mono font-bold text-ink">
                          {item.original_code}
                        </span>
                      )}
                    </div>
                    <span className="text-[11px] text-inksoft">Found as: {item.name}</span>
                  </div>

                  <button className="text-inksoft hover:text-ink">
                    {isExpanded ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
                  </button>
                </div>

                <p className="text-[12px] text-ink leading-relaxed">{item.simple_explanation}</p>

                {item.potential_risks && (
                  <div className="rounded bg-rose-500/10 border border-rose-200/60 p-2 text-[11px] text-rose-700 dark:text-rose-300">
                    <span className="font-semibold">Why to avoid: </span>
                    {item.potential_risks}
                  </div>
                )}

                {item.health_benefits && (
                  <div className="rounded bg-emerald-500/10 border border-emerald-200/60 p-2 text-[11px] text-emerald-700 dark:text-emerald-300">
                    <span className="font-semibold">Health Benefit: </span>
                    {item.health_benefits}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
