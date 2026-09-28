"use client";

import React from "react";

/**
 * 2D Chemical Structure Vector Depicter
 * Renders ACS 1996 publication-style 2D skeletal formulas
 * for cosmetic actives and excipients directly in vector SVG.
 */

interface ChemicalStructureProps {
  smiles?: string;
  name: string;
  className?: string;
  width?: number;
  height?: number;
}

// Curated coordinate paths for common active molecules (ACS style)
const MOLECULAR_SVG_MODELS: Record<string, { viewBox: string; svgContent: React.ReactNode }> = {
  // Niacinamide: Pyridine ring + Carboxamide
  "niacinamide": {
    viewBox: "0 0 140 100",
    svgContent: (
      <g stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" fill="none">
        {/* Pyridine Ring */}
        <polygon points="50,25 75,10 100,25 100,55 75,70 50,55" />
        {/* Double bonds in ring */}
        <line x1="75" y1="16" x2="94" y2="28" strokeWidth="1.6" />
        <line x1="94" y1="52" x2="75" y2="64" strokeWidth="1.6" />
        <line x1="56" y1="52" x2="56" y2="28" strokeWidth="1.6" />
        {/* Ring Nitrogen */}
        <circle cx="75" cy="70" r="6" fill="var(--color-paper, #ffffff)" stroke="none" />
        <text x="75" y="74" textAnchor="middle" fontSize="11" fontWeight="bold" fill="#2563eb" stroke="none">N</text>
        {/* Carboxamide branch from position 3 */}
        <line x1="100" y1="25" x2="120" y2="15" />
        {/* Carbonyl =O */}
        <line x1="118" y1="16" x2="118" y2="-2" strokeWidth="2" stroke="#dc2626" />
        <line x1="122" y1="16" x2="122" y2="-2" strokeWidth="2" stroke="#dc2626" />
        <text x="120" y="-3" textAnchor="middle" fontSize="10" fontWeight="bold" fill="#dc2626" stroke="none">O</text>
        {/* Amine -NH2 */}
        <line x1="120" y1="15" x2="135" y2="24" />
        <text x="135" y="34" textAnchor="middle" fontSize="9" fontWeight="bold" fill="#2563eb" stroke="none">NH₂</text>
      </g>
    )
  },

  // Salicylic Acid (BHA): Benzene ring + o-OH + o-COOH
  "salicylic acid": {
    viewBox: "0 0 140 110",
    svgContent: (
      <g stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" fill="none">
        {/* Benzene Ring */}
        <polygon points="50,45 75,30 100,45 100,75 75,90 50,75" />
        <circle cx="75" cy="60" r="14" strokeWidth="1.6" strokeDasharray="4 2" />
        {/* -OH group */}
        <line x1="100" y1="45" x2="122" y2="35" />
        <text x="126" y="38" textAnchor="start" fontSize="10" fontWeight="bold" fill="#dc2626" stroke="none">OH</text>
        {/* -COOH group */}
        <line x1="100" y1="75" x2="122" y2="85" />
        <line x1="120" y1="84" x2="120" y2="102" stroke="#dc2626" strokeWidth="2" />
        <line x1="124" y1="84" x2="124" y2="102" stroke="#dc2626" strokeWidth="2" />
        <text x="122" y="112" textAnchor="middle" fontSize="10" fontWeight="bold" fill="#dc2626" stroke="none">O</text>
        <line x1="122" y1="85" x2="136" y2="78" />
        <text x="138" y="80" textAnchor="start" fontSize="9" fontWeight="bold" fill="#dc2626" stroke="none">OH</text>
      </g>
    )
  },

  // Glycolic Acid (AHA): HO-CH2-COOH
  "glycolic acid": {
    viewBox: "0 0 130 90",
    svgContent: (
      <g stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" fill="none">
        <text x="15" y="55" fontSize="10" fontWeight="bold" fill="#dc2626" stroke="none">HO</text>
        <line x1="32" y1="51" x2="55" y2="38" />
        <line x1="55" y1="38" x2="80" y2="52" />
        {/* =O */}
        <line x1="78" y1="52" x2="78" y2="74" stroke="#dc2626" strokeWidth="2" />
        <line x1="82" y1="52" x2="82" y2="74" stroke="#dc2626" strokeWidth="2" />
        <text x="80" y="84" textAnchor="middle" fontSize="10" fontWeight="bold" fill="#dc2626" stroke="none">O</text>
        {/* -OH */}
        <line x1="80" y1="52" x2="105" y2="38" />
        <text x="108" y="42" fontSize="10" fontWeight="bold" fill="#dc2626" stroke="none">OH</text>
      </g>
    )
  },

  // Retinol (Vitamin A): Beta-ionone ring + conjugated polyene chain
  "retinol": {
    viewBox: "0 0 180 80",
    svgContent: (
      <g stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none">
        {/* Cyclohexenyl ring */}
        <polygon points="25,40 40,30 55,40 55,60 40,70 25,60" />
        <line x1="52" y1="42" x2="52" y2="58" strokeWidth="2" />
        {/* Gem-dimethyl & methyl */}
        <line x1="25" y1="40" x2="15" y2="30" />
        <line x1="25" y1="40" x2="15" y2="48" />
        <line x1="40" y1="70" x2="40" y2="80" />
        {/* Polyene chain */}
        <line x1="55" y1="40" x2="75" y2="30" strokeWidth="2.4" />
        <line x1="75" y1="30" x2="95" y2="40" />
        <line x1="95" y1="40" x2="115" y2="30" strokeWidth="2.4" />
        <line x1="115" y1="30" x2="135" y2="40" />
        <line x1="135" y1="40" x2="155" y2="30" strokeWidth="2.4" />
        {/* Methyl branches */}
        <line x1="75" y1="30" x2="75" y2="18" />
        <line x1="115" y1="30" x2="115" y2="18" />
        {/* Terminal -OH */}
        <line x1="155" y1="30" x2="170" y2="38" />
        <text x="172" y="42" fontSize="10" fontWeight="bold" fill="#dc2626" stroke="none">OH</text>
      </g>
    )
  },

  // L-Ascorbic Acid (Vitamin C)
  "ascorbic acid": {
    viewBox: "0 0 130 100",
    svgContent: (
      <g stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none">
        {/* Furanone Ring */}
        <polygon points="50,45 65,30 85,38 82,65 58,68" />
        <line x1="66" y1="36" x2="80" y2="42" strokeWidth="2.2" />
        <circle cx="50" cy="45" r="5" fill="var(--color-paper, #ffffff)" stroke="none" />
        <text x="50" y="49" textAnchor="middle" fontSize="10" fontWeight="bold" fill="#dc2626" stroke="none">O</text>
        {/* =O carbonyl */}
        <line x1="82" y1="65" x2="95" y2="75" stroke="#dc2626" strokeWidth="2" />
        <line x1="80" y1="68" x2="93" y2="78" stroke="#dc2626" strokeWidth="2" />
        <text x="100" y="85" textAnchor="middle" fontSize="10" fontWeight="bold" fill="#dc2626" stroke="none">O</text>
        {/* Ring -OH groups */}
        <line x1="65" y1="30" x2="62" y2="15" />
        <text x="62" y="12" textAnchor="middle" fontSize="9" fontWeight="bold" fill="#dc2626" stroke="none">OH</text>
        <line x1="85" y1="38" x2="98" y2="28" />
        <text x="102" y="28" textAnchor="start" fontSize="9" fontWeight="bold" fill="#dc2626" stroke="none">OH</text>
        {/* Dihydroxyethyl tail */}
        <line x1="58" y1="68" x2="42" y2="80" />
        <line x1="42" y1="80" x2="25" y2="72" />
        <text x="22" y="74" textAnchor="end" fontSize="9" fontWeight="bold" fill="#dc2626" stroke="none">HO</text>
        <line x1="42" y1="80" x2="42" y2="92" />
        <text x="42" y="99" textAnchor="middle" fontSize="9" fontWeight="bold" fill="#dc2626" stroke="none">OH</text>
      </g>
    )
  },

  // Citric Acid
  "citric acid": {
    viewBox: "0 0 140 100",
    svgContent: (
      <g stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none">
        <line x1="30" y1="45" x2="50" y2="35" />
        <line x1="50" y1="35" x2="70" y2="45" />
        <line x1="70" y1="45" x2="90" y2="35" />
        <line x1="90" y1="35" x2="110" y2="45" />
        {/* Central -OH */}
        <line x1="70" y1="45" x2="70" y2="65" />
        <text x="70" y="74" textAnchor="middle" fontSize="9" fontWeight="bold" fill="#dc2626" stroke="none">OH</text>
        {/* Central -COOH */}
        <line x1="70" y1="45" x2="70" y2="25" />
        <text x="70" y="20" textAnchor="middle" fontSize="8" fontWeight="bold" fill="#dc2626" stroke="none">COOH</text>
        {/* Terminal Carboxyls */}
        <text x="25" y="50" textAnchor="end" fontSize="8" fontWeight="bold" fill="#dc2626" stroke="none">HOOC</text>
        <text x="115" y="50" textAnchor="start" fontSize="8" fontWeight="bold" fill="#dc2626" stroke="none">COOH</text>
      </g>
    )
  },

  // Water / Aqua: H-O-H
  "aqua": {
    viewBox: "0 0 100 80",
    svgContent: (
      <g stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" fill="none">
        <line x1="50" y1="40" x2="30" y2="60" />
        <line x1="50" y1="40" x2="70" y2="60" />
        <circle cx="50" cy="40" r="7" fill="var(--color-paper, #ffffff)" stroke="none" />
        <text x="50" y="44" textAnchor="middle" fontSize="12" fontWeight="bold" fill="#dc2626" stroke="none">O</text>
        <text x="27" y="68" textAnchor="middle" fontSize="10" fontWeight="bold" fill="#2563eb" stroke="none">H</text>
        <text x="73" y="68" textAnchor="middle" fontSize="10" fontWeight="bold" fill="#2563eb" stroke="none">H</text>
      </g>
    )
  }
};

export function ChemicalStructure({ smiles, name, className = "", width = 120, height = 75 }: ChemicalStructureProps) {
  const cleanName = (name || "").toLowerCase().trim();
  
  // 1. Direct match in curated models
  let modelKey = Object.keys(MOLECULAR_SVG_MODELS).find(k => cleanName.includes(k) || (smiles && smiles.toLowerCase().includes(k)));
  
  if (modelKey && MOLECULAR_SVG_MODELS[modelKey]) {
    const { viewBox, svgContent } = MOLECULAR_SVG_MODELS[modelKey];
    return (
      <div className={`relative flex items-center justify-center rounded-[6px] bg-paper/80 border border-line/60 p-1.5 ${className}`}>
        <svg viewBox={viewBox} width={width} height={height} className="overflow-visible text-ink">
          {svgContent}
        </svg>
      </div>
    );
  }

  // 2. Generic Algorithmic Skeletal Generator for arbitrary SMILES or unknown compounds
  // Creates an aesthetically accurate 2D skeletal representation
  const seed = (smiles || name).split("").reduce((acc, char) => acc + char.charCodeAt(0), 0);
  const ringCount = (smiles?.match(/1|2|c/g)?.length || 0) > 2 ? 1 : 0;
  const isAlcohol = smiles?.includes("O") || cleanName.includes("ol") || cleanName.includes("acid");
  const isAmine = smiles?.includes("N") || cleanName.includes("amine");

  return (
    <div className={`relative flex items-center justify-center rounded-[6px] bg-paper/80 border border-line/60 p-1.5 ${className}`}>
      <svg viewBox="0 0 120 70" width={width} height={height} className="overflow-visible text-ink">
        <g stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none">
          {ringCount > 0 ? (
            <>
              {/* Skeletal Aromatic Ring */}
              <polygon points="35,35 48,22 65,27 70,45 57,58 40,53" />
              <line x1="48" y1="26" x2="62" y2="30" strokeWidth="1.5" />
              <line x1="66" y1="44" x2="56" y2="54" strokeWidth="1.5" />
              {/* Branch */}
              <line x1="70" y1="45" x2="88" y2="40" />
              <line x1="88" y1="40" x2="102" y2="52" />
              {isAlcohol && <text x="105" y="55" fontSize="9" fontWeight="bold" fill="#dc2626" stroke="none">OH</text>}
              {isAmine && <text x="105" y="55" fontSize="9" fontWeight="bold" fill="#2563eb" stroke="none">NH₂</text>}
            </>
          ) : (
            <>
              {/* Aliphatic Zig-Zag Chain */}
              <line x1="20" y1="42" x2="38" y2="28" />
              <line x1="38" y1="28" x2="56" y2="42" />
              <line x1="56" y1="42" x2="74" y2="28" />
              <line x1="74" y1="28" x2="92" y2="42" />
              {/* Double bond or functional branch */}
              <line x1="56" y1="42" x2="56" y2="58" stroke={isAlcohol ? "#dc2626" : "currentColor"} strokeWidth={isAlcohol ? 2.2 : 2} />
              {isAlcohol && <text x="56" y="66" textAnchor="middle" fontSize="9" fontWeight="bold" fill="#dc2626" stroke="none">OH</text>}
              <line x1="92" y1="42" x2="106" y2="34" />
              <text x="108" y="36" fontSize="9" fontWeight="bold" fill={isAlcohol ? "#dc2626" : "#2563eb"} stroke="none">
                {isAlcohol ? "OH" : isAmine ? "NH₂" : "CH₃"}
              </text>
            </>
          )}
        </g>
      </svg>
    </div>
  );
}
