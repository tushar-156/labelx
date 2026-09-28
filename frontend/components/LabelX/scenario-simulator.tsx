"use client";

import { useState } from "react";
import { Sliders, RefreshCw, Plus, Trash2, CheckCircle, AlertTriangle, ShieldCheck } from "lucide-react";

interface SimulationProps {
  initialLabelData?: any;
  initialScore?: number;
  onSimulationUpdate?: (updatedResult: any) => void;
}

export function ScenarioSimulator({
  initialLabelData,
  initialScore = 75,
  onSimulationUpdate,
}: SimulationProps) {
  const [ingredients, setIngredients] = useState<string[]>(
    initialLabelData?.ingredients || [
      "Water",
      "Sugar",
      "Sodium Benzoate",
      "Citric Acid",
      "Tartrazine",
      "Artificial Flavor",
      "Soy Lecithin"
    ]
  );
  const [removedIngredients, setRemovedIngredients] = useState<Set<string>>(new Set());
  const [declaredAllergens, setDeclaredAllergens] = useState<string[]>(
    initialLabelData?.declared_allergens || ["Soy"]
  );
  const [claims, setClaims] = useState<string[]>(
    initialLabelData?.nutritional_claims || ["All Natural", "High Energy"]
  );
  const [fssaiLicense, setFssaiLicense] = useState<string>(
    initialLabelData?.fssai_license || "10012011000123"
  );
  const [newIngredient, setNewIngredient] = useState("");
  const [newAllergen, setNewAllergen] = useState("");
  const [newClaim, setNewClaim] = useState("");

  const [currentScore, setCurrentScore] = useState<number>(initialScore);
  const [isSimulating, setIsSimulating] = useState(false);
  const [delta, setDelta] = useState<number>(0);
  const [violationsCount, setViolationsCount] = useState<number>(2);

  const toggleRemove = (ing: string) => {
    const next = new Set(removedIngredients);
    if (next.has(ing)) next.delete(ing);
    else next.add(ing);
    setRemovedIngredients(next);
  };

  const addAllergen = () => {
    if (newAllergen.trim() && !declaredAllergens.includes(newAllergen.trim())) {
      setDeclaredAllergens([...declaredAllergens, newAllergen.trim()]);
      setNewAllergen("");
    }
  };

  const removeAllergen = (a: string) => {
    setDeclaredAllergens(declaredAllergens.filter((x) => x !== a));
  };

  const addClaim = () => {
    if (newClaim.trim() && !claims.includes(newClaim.trim())) {
      setClaims([...claims, newClaim.trim()]);
      setNewClaim("");
    }
  };

  const removeClaim = (c: string) => {
    setClaims(claims.filter((x) => x !== c));
  };

  const runSimulation = async () => {
    setIsSimulating(true);
    try {
      const activeIngredients = ingredients.filter((i) => !removedIngredients.has(i));
      const res = await fetch("http://localhost:8000/simulate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          label_data: {
            product_name: initialLabelData?.product_name || "Simulated Product",
            ingredients: activeIngredients,
            declared_allergens: declaredAllergens,
            nutritional_claims: claims,
            fssai_license: fssaiLicense,
            food_category: "Food & Beverage"
          },
          modifications: {
            remove_ingredients: Array.from(removedIngredients),
            add_allergen_declaration: declaredAllergens,
            set_fssai_license: fssaiLicense
          }
        })
      });

      if (res.ok) {
        const data = await res.json();
        const newScore = data.risk_score?.overall_score ?? 85;
        setDelta(newScore - initialScore);
        setCurrentScore(newScore);
        const criticals = data.findings?.filter((f: any) => f.severity === "CRITICAL").length || 0;
        setViolationsCount(criticals);
        if (onSimulationUpdate) onSimulationUpdate(data);
      } else {
        // Local simulation fallback
        let score = initialScore;
        if (removedIngredients.has("Sodium Benzoate") || removedIngredients.has("Tartrazine")) {
          score += 15;
        }
        if (declaredAllergens.includes("Soy") && declaredAllergens.includes("Wheat")) {
          score += 10;
        }
        if (claims.includes("All Natural") && (ingredients.includes("Tartrazine") || ingredients.includes("Sodium Benzoate"))) {
          score -= 15;
        }
        const bounded = Math.min(100, Math.max(20, score));
        setDelta(bounded - initialScore);
        setCurrentScore(bounded);
      }
    } catch {
      // Local fallback calculation
      const bonus = removedIngredients.size * 10;
      const bounded = Math.min(100, initialScore + bonus);
      setDelta(bounded - initialScore);
      setCurrentScore(bounded);
    } finally {
      setIsSimulating(false);
    }
  };

  const resetAll = () => {
    setRemovedIngredients(new Set());
    setDeclaredAllergens(initialLabelData?.declared_allergens || ["Soy"]);
    setClaims(initialLabelData?.nutritional_claims || ["All Natural", "High Energy"]);
    setFssaiLicense(initialLabelData?.fssai_license || "10012011000123");
    setCurrentScore(initialScore);
    setDelta(0);
  };

  return (
    <div className="rounded-xl border border-line bg-card p-5 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line pb-4">
        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
            <Sliders size={18} />
          </div>
          <div>
            <h3 className="text-[15px] font-semibold text-ink">What-If Formulation Simulator</h3>
            <p className="text-[12px] text-inksoft">
              Modify ingredients, allergens, or claims to model real-time regulatory compliance and health deltas.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 rounded-lg bg-paper px-3 py-1.5 border border-line">
            <span className="text-[11px] font-medium text-inksoft uppercase tracking-wider">Score</span>
            <span className="text-[16px] font-bold text-ink">{currentScore}/100</span>
            {delta !== 0 && (
              <span
                className={`text-[12px] font-semibold ${
                  delta > 0 ? "text-emerald-600" : "text-rose-600"
                }`}
              >
                {delta > 0 ? `+${delta}` : delta}
              </span>
            )}
          </div>

          <button
            onClick={resetAll}
            className="flex h-8 items-center gap-1 rounded-md border border-line px-2.5 text-[12px] text-inksoft hover:text-ink hover:bg-paper transition"
          >
            <RefreshCw size={13} /> Reset
          </button>

          <button
            onClick={runSimulation}
            disabled={isSimulating}
            className="flex h-8 items-center gap-1.5 rounded-md bg-ink px-3.5 text-[12px] font-medium text-paper hover:bg-ink/90 transition shadow-sm disabled:opacity-50"
          >
            {isSimulating ? "Recalculating..." : "Run Simulation"}
          </button>
        </div>
      </div>

      <div className="mt-5 grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* Ingredient Formulation Toggle */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-[13px] font-medium text-ink">Ingredient Formulation</h4>
            <span className="text-[11px] text-inksoft">{ingredients.length - removedIngredients.size} active</span>
          </div>
          <div className="max-h-[220px] overflow-y-auto space-y-1.5 pr-1">
            {ingredients.map((ing) => {
              const isRemoved = removedIngredients.has(ing);
              return (
                <div
                  key={ing}
                  onClick={() => toggleRemove(ing)}
                  className={`flex cursor-pointer items-center justify-between rounded-md border px-2.5 py-1.5 text-[12px] transition ${
                    isRemoved
                      ? "border-rose-200 bg-rose-50/50 text-rose-500 line-through dark:border-rose-950 dark:bg-rose-950/20"
                      : "border-line bg-paper text-ink hover:border-inksoft"
                  }`}
                >
                  <span className="truncate">{ing}</span>
                  <span className="text-[10px] font-medium uppercase tracking-wider">
                    {isRemoved ? "Removed" : "Keep"}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Allergen Warnings */}
        <div className="space-y-3">
          <h4 className="text-[13px] font-medium text-ink">Declared Allergens</h4>
          <div className="flex flex-wrap gap-1.5">
            {declaredAllergens.map((a) => (
              <span
                key={a}
                className="flex items-center gap-1 rounded-md bg-amber-500/10 px-2 py-1 text-[11px] font-medium text-amber-700 dark:text-amber-400 border border-amber-200/50"
              >
                {a}
                <button onClick={() => removeAllergen(a)} className="hover:text-rose-600">
                  <Trash2 size={11} />
                </button>
              </span>
            ))}
          </div>

          <div className="flex gap-1.5 pt-2">
            <input
              type="text"
              placeholder="e.g. Peanuts, Milk"
              value={newAllergen}
              onChange={(e) => setNewAllergen(e.target.value)}
              className="h-8 flex-1 rounded-md border border-line bg-paper px-2.5 text-[12px] text-ink placeholder:text-inksoft focus:outline-none focus:border-ink"
            />
            <button
              onClick={addAllergen}
              className="flex h-8 items-center justify-center rounded-md border border-line bg-paper px-2.5 text-[12px] text-ink hover:bg-paper2"
            >
              <Plus size={14} />
            </button>
          </div>
        </div>

        {/* Marketing Claims & FSSAI License */}
        <div className="space-y-3">
          <h4 className="text-[13px] font-medium text-ink">Claims & Regulatory License</h4>
          <div className="space-y-1.5">
            <label className="text-[11px] text-inksoft uppercase tracking-wider">FSSAI 14-Digit License</label>
            <input
              type="text"
              value={fssaiLicense}
              onChange={(e) => setFssaiLicense(e.target.value)}
              className="h-8 w-full rounded-md border border-line bg-paper px-2.5 text-[12px] text-ink font-mono focus:outline-none focus:border-ink"
            />
          </div>

          <div className="pt-2">
            <label className="text-[11px] text-inksoft uppercase tracking-wider">Active Marketing Claims</label>
            <div className="flex flex-wrap gap-1.5 mt-1.5">
              {claims.map((c) => (
                <span
                  key={c}
                  className="flex items-center gap-1 rounded-md bg-sky-500/10 px-2 py-1 text-[11px] font-medium text-sky-700 dark:text-sky-300 border border-sky-200/50"
                >
                  {c}
                  <button onClick={() => removeClaim(c)} className="hover:text-rose-600">
                    <Trash2 size={11} />
                  </button>
                </span>
              ))}
            </div>

            <div className="flex gap-1.5 mt-2">
              <input
                type="text"
                placeholder="e.g. Sugar Free"
                value={newClaim}
                onChange={(e) => setNewClaim(e.target.value)}
                className="h-8 flex-1 rounded-md border border-line bg-paper px-2.5 text-[12px] text-ink placeholder:text-inksoft focus:outline-none focus:border-ink"
              />
              <button
                onClick={addClaim}
                className="flex h-8 items-center justify-center rounded-md border border-line bg-paper px-2.5 text-[12px] text-ink hover:bg-paper2"
              >
                <Plus size={14} />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
