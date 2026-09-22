"use client";

import { useState } from "react";
import { BookOpen, Calendar, Search, X, AlertTriangle, ArrowRight, CheckCircle2 } from "lucide-react";

export interface FoodDiaryItem {
  id?: string;
  timestamp?: string;
  date?: string;
  product_name: string;
  serving_fraction?: number;
  sugar_g?: number;
  sodium_mg?: number;
  saturated_fat_g?: number;
  calories_kcal?: number;
  additives_count?: number;
  additives?: string[];
}

interface FoodDiaryDrawerProps {
  onSelectProduct?: (productName: string) => void;
}

export function FoodDiaryDrawer({ onSelectProduct }: FoodDiaryDrawerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState<FoodDiaryItem[]>([]);
  const [searchQuery, setSearchQuery] = useState("");

  const handleOpen = async () => {
    setIsOpen(true);
    setLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/intake/history");
      if (res.ok) {
        const data = await res.json();
        setLogs(data || []);
      } else {
        // Fallback demo state
        setLogs([
          {
            product_name: "Whole Wheat Multi-Seed Bread",
            date: "2026-11-23",
            timestamp: "14:22",
            sugar_g: 2.1,
            sodium_mg: 180.0,
            saturated_fat_g: 0.5,
            calories_kcal: 140.0,
            additives_count: 0
          },
          {
            product_name: "Crunchy Sweet Potato Crisps",
            date: "2026-11-23",
            timestamp: "11:05",
            sugar_g: 4.2,
            sodium_mg: 210.0,
            saturated_fat_g: 2.0,
            calories_kcal: 180.0,
            additives_count: 1
          }
        ]);
      }
    } catch {
      // Fallback
    } finally {
      setLoading(false);
    }
  };

  const filteredLogs = logs.filter(item =>
    item.product_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (item.date && item.date.includes(searchQuery))
  );

  return (
    <>
      <button
        type="button"
        onClick={handleOpen}
        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-[6px] border border-line2 bg-paper hover:bg-card text-ink text-xs font-medium shadow-2xs hover:border-ink/40 transition-all cursor-pointer"
      >
        <BookOpen className="w-3.5 h-3.5 text-inksoft" />
        <span>Food Diary & Scan History</span>
      </button>

      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs animate-in fade-in duration-200">
          <div className="relative w-full max-w-2xl max-h-[85vh] flex flex-col rounded-[10px] border border-line bg-card shadow-xl overflow-hidden">
            
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-line bg-paper2/50">
              <div className="flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-ink" />
                <div>
                  <h3 className="font-bold text-ink text-sm">
                    Personal Food Diary & Historical Scans
                  </h3>
                  <p className="text-[11px] text-inksoft">
                    Persistent log of evaluated products and nutrient loads
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                className="p-1 rounded text-inksoft hover:text-ink hover:bg-paper transition-colors cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Search Bar */}
            <div className="p-3 border-b border-line/60 bg-paper/40">
              <div className="relative">
                <Search className="absolute left-3 top-2.5 w-3.5 h-3.5 text-inksoft" />
                <input
                  type="text"
                  placeholder="Search past scans by product name or date..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full rounded-[6px] border border-line bg-card pl-9 pr-3 py-1.5 text-xs text-ink placeholder:text-inksoft/60 focus:outline-none focus:border-ink/30"
                />
              </div>
            </div>

            {/* List */}
            <div className="flex-1 overflow-y-auto p-4 space-y-2.5">
              {loading ? (
                <div className="p-8 text-center text-xs text-inksoft">
                  Loading food history...
                </div>
              ) : filteredLogs.length === 0 ? (
                <div className="p-8 text-center text-xs text-inksoft">
                  No food log entries found. Scan food products and click "Log Product into Daily Diary" to record them here.
                </div>
              ) : (
                filteredLogs.map((item, idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-[6px] border border-line2 bg-paper/50 hover:bg-paper2/50 transition-colors flex flex-col sm:flex-row sm:items-center justify-between gap-2"
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-xs text-ink">{item.product_name}</span>
                        {item.date && (
                          <span className="text-[10px] font-mono text-inksoft">
                            {item.date} {item.timestamp || ""}
                          </span>
                        )}
                      </div>
                      <div className="mt-1 flex flex-wrap gap-2 text-[11px] font-mono text-inksoft">
                        <span>Sugar: <strong className="text-ink">{item.sugar_g ?? 0}g</strong></span>
                        <span>•</span>
                        <span>Sodium: <strong className="text-ink">{item.sodium_mg ?? 0}mg</strong></span>
                        <span>•</span>
                        <span>Sat Fat: <strong className="text-ink">{item.saturated_fat_g ?? 0}g</strong></span>
                        <span>•</span>
                        <span>Energy: <strong className="text-ink">{item.calories_kcal ?? 0} kcal</strong></span>
                      </div>
                    </div>

                    <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-card border border-line text-ink w-fit">
                      {item.additives_count ?? 0} additive(s)
                    </span>
                  </div>
                ))
              )}
            </div>

            {/* Footer */}
            <div className="p-3 border-t border-line bg-paper2/50 flex items-center justify-between">
              <span className="text-[11px] text-inksoft font-mono">
                {filteredLogs.length} record(s) logged
              </span>
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                className="px-4 py-1.5 rounded-[6px] bg-ink text-paper text-xs font-semibold hover:bg-ink/90 transition-colors cursor-pointer"
              >
                Done
              </button>
            </div>

          </div>
        </div>
      )}
    </>
  );
}
