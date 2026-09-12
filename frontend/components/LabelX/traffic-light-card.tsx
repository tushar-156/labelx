"use client";

import { Activity, ShieldCheck, AlertTriangle, AlertOctagon, CheckCircle2 } from "lucide-react";

export interface TrafficLightBadge {
  nutrient: string;
  value: number;
  unit: string;
  rating: "LOW" | "MODERATE" | "HIGH" | "UNKNOWN" | string;
  color: "GREEN" | "AMBER" | "RED" | "GRAY" | string;
  reference_intake_pct: number;
  threshold_explanation: string;
}

export interface TrafficLightReportData {
  badges: TrafficLightBadge[];
  overall_healthiness: "HEALTHY" | "BALANCED" | "CAUTION" | "UNHEALTHY" | string;
  high_count: number;
  moderate_count: number;
  low_count: number;
  summary: string;
}

interface TrafficLightCardProps {
  report?: TrafficLightReportData;
}

export function TrafficLightCard({ report }: TrafficLightCardProps) {
  if (!report || !report.badges || report.badges.length === 0) {
    return null;
  }

  const getBadgeStyle = (color: string) => {
    switch (color) {
      case "GREEN":
        return {
          pill: "bg-emerald-500 text-white",
          border: "border-emerald-500/40 bg-emerald-50/50 dark:bg-emerald-950/20 text-emerald-900 dark:text-emerald-200",
          dot: "bg-emerald-500"
        };
      case "AMBER":
        return {
          pill: "bg-amber-500 text-white",
          border: "border-amber-500/40 bg-amber-50/50 dark:bg-amber-950/20 text-amber-900 dark:text-amber-200",
          dot: "bg-amber-500"
        };
      case "RED":
        return {
          pill: "bg-red-500 text-white",
          border: "border-red-500/40 bg-red-50/60 dark:bg-red-950/30 text-red-900 dark:text-red-200",
          dot: "bg-red-500"
        };
      default:
        return {
          pill: "bg-gray-400 text-white",
          border: "border-line bg-paper text-inksoft",
          dot: "bg-gray-400"
        };
    }
  };

  return (
    <div className="rounded-[8px] border border-line bg-card p-4 shadow-sm">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-line pb-2.5 mb-3">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-ink" />
          <h4 className="text-[13px] font-bold tracking-tight text-ink uppercase">
            UK FSA & WHO Front-of-Pack Traffic Light Rating
          </h4>
        </div>
        <div className="flex items-center gap-1.5 font-mono text-[10px]">
          <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 dark:bg-emerald-900/60 dark:text-emerald-200 font-bold">
            {report.low_count} Low
          </span>
          <span className="px-2 py-0.5 rounded bg-amber-100 text-amber-800 dark:bg-amber-900/60 dark:text-amber-200 font-bold">
            {report.moderate_count} Med
          </span>
          <span className="px-2 py-0.5 rounded bg-red-100 text-red-800 dark:bg-red-900/60 dark:text-red-200 font-bold">
            {report.high_count} High
          </span>
        </div>
      </div>

      <p className="text-[12px] text-inksoft mb-4">
        Statutory front-of-pack traffic lights per 100g serving according to UK Food Standards Agency and European Commission criteria:
      </p>

      {/* Traffic Light 5-Pillar Badges */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 mb-4">
        {report.badges.map((b, idx) => {
          const style = getBadgeStyle(b.color);
          return (
            <div
              key={idx}
              className={`rounded-[8px] border ${style.border} p-3 flex flex-col items-center justify-between text-center gap-1.5 shadow-2xs`}
            >
              <span className="text-[11px] uppercase tracking-wider font-semibold opacity-90">
                {b.nutrient}
              </span>

              <div className="my-1">
                <span className="text-xl font-bold font-display tracking-tight block">
                  {b.value}{b.unit}
                </span>
                <span className="text-[10px] font-mono opacity-80">
                  {b.reference_intake_pct}% RI*
                </span>
              </div>

              <div className={`w-full py-0.5 rounded-[4px] text-[10px] font-bold uppercase tracking-wider ${style.pill}`}>
                {b.rating}
              </div>

              <span className="text-[9px] opacity-75 line-clamp-2 mt-0.5">
                {b.threshold_explanation}
              </span>
            </div>
          );
        })}
      </div>

      {/* Summary Footer */}
      <div className="p-2.5 rounded bg-paper2/70 border border-line/60 flex items-center justify-between gap-2 text-xs">
        <span className="text-ink">
          <strong className="text-ink font-semibold">Evaluation: </strong>
          {report.summary}
        </span>
        <span className="text-[10px] text-inksoft font-mono shrink-0">
          *RI = Adult Reference Intake
        </span>
      </div>
    </div>
  );
}
