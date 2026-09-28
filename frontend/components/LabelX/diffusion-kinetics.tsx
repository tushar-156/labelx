"use client";

import React from "react";
import { Activity } from "lucide-react";

interface DiffusionKineticsProps {
  ingredient: string;
  kinetics?: {
    diffusivity_d_sc_cm2_per_hr?: string;
    lag_time_hours?: number;
    steady_state_flux_j_ss?: number;
    absorption_profile_24h?: Array<{ hour: number; absorbed_ug_per_cm2: number }>;
    kinetic_classification?: string;
  };
}

export function DiffusionKineticsCard({ ingredient, kinetics }: DiffusionKineticsProps) {
  if (!kinetics || !kinetics.absorption_profile_24h || kinetics.absorption_profile_24h.length === 0) {
    return null;
  }

  const profile = kinetics.absorption_profile_24h;
  const maxAbsorbed = Math.max(...profile.map((p) => p.absorbed_ug_per_cm2), 1.0);
  const width = 240;
  const height = 70;
  const padding = 10;

  // Calculate SVG line points
  const points = profile.map((p) => {
    const x = padding + (p.hour / 24) * (width - 2 * padding);
    const y = height - padding - (p.absorbed_ug_per_cm2 / maxAbsorbed) * (height - 2 * padding);
    return `${x},${y}`;
  }).join(" ");

  return (
    <div className="mt-3 rounded-[6px] border border-line/60 bg-paper/60 p-2.5">
      <div className="flex items-center justify-between mb-1.5">
        <div className="flex items-center gap-1.5">
          <Activity className="w-3.5 h-3.5 text-ink" />
          <span className="font-mono text-[10px] uppercase font-bold tracking-wider text-ink">
            Fickian Dermal Kinetics (24h Flux)
          </span>
        </div>
        <span className="font-mono text-[9px] px-1.5 py-0.2 rounded bg-card border border-line text-inksoft">
          {kinetics.kinetic_classification || "Kinetic Profile"}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-2 my-2 text-[10px] font-mono">
        <div>
          <span className="text-inksoft">Lag Time (t_lag): </span>
          <span className="font-semibold text-ink">{kinetics.lag_time_hours} hrs</span>
        </div>
        <div>
          <span className="text-inksoft">Steady Flux (J_ss): </span>
          <span className="font-semibold text-ink">{kinetics.steady_state_flux_j_ss} µg/cm²/h</span>
        </div>
      </div>

      {/* SVG 24-Hour Absorption Curve */}
      <div className="relative w-full overflow-hidden rounded bg-card/60 p-1 border border-line/40">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-14 overflow-visible">
          {/* Grid lines */}
          <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} stroke="currentColor" strokeOpacity="0.15" strokeWidth="1" />
          <line x1={padding} y1={padding} x2={padding} y2={height - padding} stroke="currentColor" strokeOpacity="0.15" strokeWidth="1" />
          
          {/* Area fill under curve */}
          <polygon
            points={`${padding},${height - padding} ${points} ${width - padding},${height - padding}`}
            fill="#2563eb"
            fillOpacity="0.1"
          />

          {/* Kinetic Curve */}
          <polyline
            points={points}
            fill="none"
            stroke="#2563eb"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Hour Marks */}
          <text x={padding} y={height - 1} fontSize="7" fill="currentColor" opacity="0.5" fontFamily="monospace">0h</text>
          <text x={width / 2} y={height - 1} textAnchor="middle" fontSize="7" fill="currentColor" opacity="0.5" fontFamily="monospace">12h</text>
          <text x={width - padding} y={height - 1} textAnchor="end" fontSize="7" fill="currentColor" opacity="0.5" fontFamily="monospace">24h</text>
        </svg>
      </div>
    </div>
  );
}
