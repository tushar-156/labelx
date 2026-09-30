"use client";

import { useState } from "react";
import { ShieldCheck, AlertTriangle, AlertOctagon, Info, CheckCircle2, ChevronRight, FileCheck } from "lucide-react";

interface CompliancePanelProps {
  complianceData?: any;
}

export function CompliancePanel({ complianceData }: CompliancePanelProps) {
  const [activeFilter, setActiveFilter] = useState<"ALL" | "CRITICAL" | "WARNING" | "INFO">("ALL");

  const riskScore = complianceData?.risk_score || {
    overall_score: 84,
    grade: "B",
    modules: [
      { module: "allergens", score: 85, findings_count: 2, critical_count: 0, warning_count: 1 },
      { module: "additives", score: 75, findings_count: 3, critical_count: 1, warning_count: 1 },
      { module: "claims", score: 90, findings_count: 1, critical_count: 0, warning_count: 0 },
      { module: "labelling", score: 95, findings_count: 5, critical_count: 0, warning_count: 0 },
      { module: "license", score: 100, findings_count: 1, critical_count: 0, warning_count: 0 }
    ]
  };

  const findings = complianceData?.findings || [
    {
      module: "additives",
      severity: "CRITICAL",
      title: "Restricted Additive: TBHQ (E319)",
      description: "TBHQ detected in fried snack base. Maximum permissible limit is 200 ppm under FSSAI Schedule I.",
      regulation: "FSS (Food Products Standards & Food Additives) Regulations, 2011 — Schedule I",
      recommendation: "Ensure dosage does not exceed statutory threshold or substitute with tocopherols."
    },
    {
      module: "allergens",
      severity: "WARNING",
      title: "Undeclared Allergen Warning: Soy",
      description: "Soy Lecithin (E322) present in formulation but allergen disclaimer is missing from front panel.",
      regulation: "FSS (Labelling & Display) Regulations, 2020",
      recommendation: "Print 'Contains: Soy' in bold type in the allergen advisory statement."
    },
    {
      module: "claims",
      severity: "INFO",
      title: "Claim Verified: High Protein",
      description: "Protein provides 22.4% of total caloric value, satisfying the >= 20% statutory threshold.",
      regulation: "FSS (Advertising & Claims) Regulations, 2018"
    },
    {
      module: "license",
      severity: "INFO",
      title: "FSSAI License Verified: 10012011000123",
      description: "Valid 14-digit Central Manufacturing License registration format.",
      regulation: "FSS (Licensing & Registration) Regulations, 2011"
    }
  ];

  const filteredFindings = findings.filter((f: any) => {
    if (activeFilter === "ALL") return true;
    return f.severity === activeFilter;
  });

  const getScoreColor = (score: number) => {
    if (score >= 90) return "text-emerald-500 stroke-emerald-500";
    if (score >= 75) return "text-sky-500 stroke-sky-500";
    if (score >= 55) return "text-amber-500 stroke-amber-500";
    return "text-rose-500 stroke-rose-500";
  };

  const getGradeBadge = (grade: string) => {
    const map: Record<string, string> = {
      A: "bg-emerald-500/10 text-emerald-600 border-emerald-300 dark:border-emerald-800",
      B: "bg-sky-500/10 text-sky-600 border-sky-300 dark:border-sky-800",
      C: "bg-amber-500/10 text-amber-600 border-amber-300 dark:border-amber-800",
      F: "bg-rose-500/10 text-rose-600 border-rose-300 dark:border-rose-800"
    };
    return map[grade] || map.B;
  };

  return (
    <div className="rounded-xl border border-line bg-card p-5 shadow-sm space-y-6">
      {/* Top Header & Circular Gauge */}
      <div className="flex flex-col md:flex-row items-center justify-between gap-6 border-b border-line pb-6">
        <div className="flex items-center gap-4">
          {/* Animated Gauge */}
          <div className="relative flex h-24 w-24 shrink-0 items-center justify-center">
            <svg className="h-full w-full -rotate-90 transform" viewBox="0 0 36 36">
              <path
                className="stroke-line"
                strokeWidth="3.5"
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
              <path
                className={`transition-all duration-1000 ease-out ${getScoreColor(riskScore.overall_score)}`}
                strokeDasharray={`${riskScore.overall_score}, 100`}
                strokeWidth="3.5"
                strokeLinecap="round"
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
            </svg>
            <div className="absolute flex flex-col items-center">
              <span className="text-[20px] font-bold text-ink leading-none">{riskScore.overall_score}</span>
              <span className="text-[9px] uppercase tracking-wider text-inksoft">/ 100</span>
            </div>
          </div>

          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-[17px] font-bold text-ink">5-Module Regulatory Compliance Engine</h3>
              <span className={`rounded-md border px-2 py-0.5 text-[11px] font-bold ${getGradeBadge(riskScore.grade)}`}>
                Grade {riskScore.grade}
              </span>
            </div>
            <p className="mt-1 text-[13px] text-inksoft">
              {complianceData?.summary || "Automated audit against statutory FSSAI and international food packaging regulations."}
            </p>
          </div>
        </div>

        {/* Severity Filter Pills */}
        <div className="flex items-center gap-1.5 self-start md:self-center">
          {(["ALL", "CRITICAL", "WARNING", "INFO"] as const).map((filter) => (
            <button
              key={filter}
              onClick={() => setActiveFilter(filter)}
              className={`h-8 rounded-md px-3 text-[11px] font-medium transition ${
                activeFilter === filter
                  ? "bg-ink text-paper"
                  : "border border-line bg-paper text-inksoft hover:text-ink"
              }`}
            >
              {filter}
            </button>
          ))}
        </div>
      </div>

      {/* Module Score Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
        {riskScore.modules?.map((m: any) => (
          <div key={m.module} className="rounded-lg border border-line bg-paper p-3">
            <div className="flex items-center justify-between text-[11px] text-inksoft font-medium uppercase tracking-wider">
              <span>{m.module}</span>
              <span className="font-bold text-ink">{m.score}%</span>
            </div>
            <div className="mt-2 h-1.5 w-full rounded-full bg-line overflow-hidden">
              <div
                className={`h-full rounded-full ${
                  m.score >= 80 ? "bg-emerald-500" : m.score >= 60 ? "bg-amber-500" : "bg-rose-500"
                }`}
                style={{ width: `${m.score}%` }}
              />
            </div>
            <div className="mt-2 flex items-center justify-between text-[10px] text-inksoft">
              <span>{m.critical_count} critical</span>
              <span>{m.warning_count} warnings</span>
            </div>
          </div>
        ))}
      </div>

      {/* Flagged Findings List */}
      <div className="space-y-2.5">
        <h4 className="text-[13px] font-medium text-ink">Statutory Audit Findings ({filteredFindings.length})</h4>
        {filteredFindings.length === 0 ? (
          <div className="rounded-lg border border-line bg-paper p-4 text-center text-[12px] text-inksoft">
            No issues found under the '{activeFilter}' filter.
          </div>
        ) : (
          filteredFindings.map((finding: any, idx: number) => {
            const isCrit = finding.severity === "CRITICAL";
            const isWarn = finding.severity === "WARNING";
            return (
              <div
                key={idx}
                className={`rounded-lg border p-3.5 text-[12px] transition ${
                  isCrit
                    ? "border-rose-200 bg-rose-50/40 dark:border-rose-950 dark:bg-rose-950/20"
                    : isWarn
                    ? "border-amber-200 bg-amber-50/40 dark:border-amber-950 dark:bg-amber-950/20"
                    : "border-line bg-paper"
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-2.5">
                    {isCrit ? (
                      <AlertOctagon size={16} className="text-rose-600 mt-0.5 shrink-0" />
                    ) : isWarn ? (
                      <AlertTriangle size={16} className="text-amber-600 mt-0.5 shrink-0" />
                    ) : (
                      <CheckCircle2 size={16} className="text-emerald-600 mt-0.5 shrink-0" />
                    )}
                    <div>
                      <h5 className="font-semibold text-ink">{finding.title}</h5>
                      <p className="mt-0.5 text-inksoft">{finding.description}</p>
                      {finding.regulation && (
                        <div className="mt-1.5 flex items-center gap-1 text-[11px] font-mono text-inksoft">
                          <FileCheck size={12} />
                          <span>{finding.regulation}</span>
                        </div>
                      )}
                    </div>
                  </div>

                  <span
                    className={`shrink-0 rounded-full px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider ${
                      isCrit
                        ? "bg-rose-500/10 text-rose-600 border border-rose-300"
                        : isWarn
                        ? "bg-amber-500/10 text-amber-600 border border-amber-300"
                        : "bg-emerald-500/10 text-emerald-600 border border-emerald-300"
                    }`}
                  >
                    {finding.severity}
                  </span>
                </div>

                {finding.recommendation && (
                  <div className="mt-2.5 rounded border border-line bg-card/60 p-2 text-[11px] text-ink">
                    <span className="font-semibold text-ink">Recommendation: </span>
                    {finding.recommendation}
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
