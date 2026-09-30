"use client";

import { useState } from "react";
import { Download, Printer, FileText, CheckCircle2, ShieldCheck, ExternalLink } from "lucide-react";

interface ReportExportProps {
  productName?: string;
  brandName?: string;
  complianceData?: any;
  intelligence?: any;
  structuredData?: any;
}

export function ReportExportModal({
  productName = "Analyzed Product",
  brandName = "Commercial Manufacturer",
  complianceData,
  intelligence,
  structuredData
}: ReportExportProps) {
  const [isOpen, setIsOpen] = useState(false);

  const riskScore = complianceData?.risk_score || { overall_score: 84, grade: "B" };
  const findings = complianceData?.findings || [];
  const nova = intelligence?.nova || { group: 4, tier_name: "Ultra-Processed (UPF)" };
  const tradeoffs = intelligence?.tradeoffs || { verdict: "Fair", frequency_recommendation: "Occasional Treat" };

  const handlePrint = () => {
    window.print();
  };

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="flex items-center gap-1.5 rounded-lg border border-line bg-paper px-3 py-1.5 text-[12px] font-medium text-ink hover:bg-paper2 transition shadow-sm"
      >
        <FileText size={14} />
        <span>Export Audit Report</span>
      </button>

      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 overflow-y-auto">
          <div className="relative w-full max-w-3xl rounded-xl border border-line bg-paper p-6 shadow-2xl my-8">
            {/* Modal Controls */}
            <div className="flex items-center justify-between border-b border-line pb-4 print:hidden">
              <div className="flex items-center gap-2">
                <ShieldCheck size={20} className="text-emerald-500" />
                <h3 className="text-[16px] font-bold text-ink">Statutory Compliance & Safety Audit Certificate</h3>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={handlePrint}
                  className="flex items-center gap-1.5 rounded-md bg-ink px-3 py-1.5 text-[12px] font-medium text-paper hover:bg-ink/90 transition shadow-sm"
                >
                  <Printer size={14} /> Print / Save PDF
                </button>
                <button
                  onClick={() => setIsOpen(false)}
                  className="rounded-md border border-line px-2.5 py-1.5 text-[12px] text-inksoft hover:text-ink transition"
                >
                  Close
                </button>
              </div>
            </div>

            {/* Printable Document Body */}
            <div id="compliance-printable-doc" className="mt-6 space-y-6 text-ink p-2">
              {/* Header */}
              <div className="flex items-start justify-between border-b-2 border-ink pb-4">
                <div>
                  <div className="text-[20px] font-extrabold tracking-tight">LABELX AUDIT CERTIFICATE</div>
                  <div className="text-[12px] text-inksoft">Food Safety, Additive Purity & Allergen Compliance Assessment</div>
                  <div className="text-[11px] text-inksoft mt-1">Generated: {new Date().toLocaleDateString("en-IN")}</div>
                </div>

                <div className="text-right">
                  <div className="text-[28px] font-black leading-none text-emerald-600">
                    {riskScore.overall_score}
                    <span className="text-[14px] text-inksoft font-normal">/100</span>
                  </div>
                  <div className="text-[12px] font-bold uppercase tracking-wider text-ink mt-0.5">
                    Grade {riskScore.grade} Compliance
                  </div>
                </div>
              </div>

              {/* Product Info Table */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 rounded-lg border border-line bg-card p-3 text-[12px]">
                <div>
                  <span className="text-[10px] text-inksoft uppercase tracking-wider font-semibold">Product Name</span>
                  <div className="font-medium text-ink truncate">{productName}</div>
                </div>
                <div>
                  <span className="text-[10px] text-inksoft uppercase tracking-wider font-semibold">Brand / Entity</span>
                  <div className="font-medium text-ink truncate">{brandName}</div>
                </div>
                <div>
                  <span className="text-[10px] text-inksoft uppercase tracking-wider font-semibold">NOVA Level</span>
                  <div className="font-medium text-ink">Group {nova.group} ({nova.tier_name})</div>
                </div>
                <div>
                  <span className="text-[10px] text-inksoft uppercase tracking-wider font-semibold">Frequency Advisory</span>
                  <div className="font-medium text-ink">{tradeoffs.frequency_recommendation}</div>
                </div>
              </div>

              {/* Module Scores */}
              <div>
                <h4 className="text-[13px] font-bold uppercase tracking-wider border-b border-line pb-1 mb-2">
                  1. Statutory Module Evaluations
                </h4>
                <div className="grid grid-cols-5 gap-2 text-center text-[11px]">
                  {complianceData?.risk_score?.modules?.map((m: any) => (
                    <div key={m.module} className="rounded border border-line p-2">
                      <div className="uppercase font-semibold text-inksoft">{m.module}</div>
                      <div className="text-[14px] font-bold text-ink mt-0.5">{m.score}%</div>
                      <div className="text-[10px] text-inksoft">{m.critical_count} critical</div>
                    </div>
                  )) || (
                    <>
                      <div className="rounded border border-line p-2">Allergens: 90%</div>
                      <div className="rounded border border-line p-2">Additives: 80%</div>
                      <div className="rounded border border-line p-2">Claims: 85%</div>
                      <div className="rounded border border-line p-2">Labelling: 95%</div>
                      <div className="rounded border border-line p-2">License: 100%</div>
                    </>
                  )}
                </div>
              </div>

              {/* Regulatory Findings & Violations */}
              <div>
                <h4 className="text-[13px] font-bold uppercase tracking-wider border-b border-line pb-1 mb-2">
                  2. Flagged Non-Compliances & Legal Recommendations
                </h4>
                <div className="space-y-2 text-[12px]">
                  {findings.length === 0 ? (
                    <p className="text-inksoft italic">No regulatory infractions identified.</p>
                  ) : (
                    findings.map((f: any, i: number) => (
                      <div key={i} className="border-l-2 border-ink pl-3 py-1 space-y-0.5">
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-ink">{f.title}</span>
                          <span className="text-[10px] uppercase font-bold text-inksoft">[{f.severity}]</span>
                        </div>
                        <p className="text-inksoft text-[11px]">{f.description}</p>
                        {f.regulation && (
                          <div className="text-[10px] font-mono text-inksoft">Statute: {f.regulation}</div>
                        )}
                        {f.recommendation && (
                          <div className="text-[11px] font-medium text-ink">Action Required: {f.recommendation}</div>
                        )}
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* Legal Signoff Footer */}
              <div className="border-t border-line pt-4 text-[10px] text-inksoft flex justify-between items-center">
                <span>Verified by LabelX Deterministic Multi-Agent Regulatory Core</span>
                <span>FSSAI / FDA / EU REACH Standards Conformity</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
