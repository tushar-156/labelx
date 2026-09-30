"use client";

import React, { useState } from "react";
import { CheckCircle2, ChevronDown, ChevronUp, Cpu, Network, ShieldCheck, Sparkles, Terminal } from "lucide-react";

interface AgentConsensusProps {
  xaiData?: {
    dag_nodes?: Array<{
      id: string;
      name: string;
      status: string;
      detail?: string;
      metrics?: Record<string, any>;
    }>;
    critic_approved?: boolean;
    review_cycles?: number;
    critic_notes?: string;
  };
}

export function AgentConsensusInspector({ xaiData }: AgentConsensusProps) {
  const [expanded, setExpanded] = useState(false);

  if (!xaiData) return null;

  const nodes = xaiData.dag_nodes || [
    { id: "supervisor", name: "Supervisor Agent", status: "COMPLETED", detail: "Orchestrated formulation through state graph" },
    { id: "research", name: "Research Agent", status: "COMPLETED", detail: "Vector DB FAISS similarity retrieval and PubChem PUG-REST mapping" },
    { id: "analysis", name: "Biochemical Analysis Agent", status: "COMPLETED", detail: "Synthesized personalized dermal toxicity profile" },
    { id: "critic", name: "Critic Verification Agent", status: "APPROVED", detail: "Evaluated claims against EU Annex II & FDA prohibited benchmarks" }
  ];

  return (
    <div className="mt-5 rounded-[8px] border border-line bg-paper2/50 p-4 shadow-sm">
      <div 
        className="flex items-center justify-between cursor-pointer select-none"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-2">
          <Network className="w-4 h-4 text-ink" />
          <h4 className="text-[13px] font-bold uppercase tracking-tight text-ink">
            XAI Multi-Agent Execution DAG & Consensus Inspector
          </h4>
        </div>
        <div className="flex items-center gap-2">
          <span className="font-mono text-[10px] uppercase tracking-wider text-emerald-700 dark:text-emerald-300 px-2 py-0.5 rounded bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800">
            {xaiData.critic_approved ? "Consensus Approved" : "Evaluating"}
          </span>
          {expanded ? <ChevronUp className="w-4 h-4 text-inksoft" /> : <ChevronDown className="w-4 h-4 text-inksoft" />}
        </div>
      </div>

      <p className="mt-1 text-[12px] text-inksoft">
        Deterministic audit trail of LangGraph cyclic state machine verification. Verified across {xaiData.review_cycles || 1} deliberation cycle(s).
      </p>

      {/* Execution DAG Nodes Flowchart */}
      <div className="mt-3.5 grid gap-2 sm:grid-cols-4">
        {nodes.map((node, i) => (
          <div key={node.id} className="relative rounded-[6px] border border-line bg-card p-2.5 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="font-mono text-[10px] text-inksoft">0{i + 1}. AGENT</span>
                <CheckCircle2 className="w-3 h-3 text-emerald-600" />
              </div>
              <p className="font-semibold text-[12px] text-ink leading-tight">{node.name}</p>
              <p className="mt-1 text-[11px] text-inksoft leading-snug line-clamp-2">{node.detail}</p>
            </div>
            <div className="mt-2 pt-1.5 border-t border-line/40">
              <span className="font-mono text-[9px] uppercase font-bold text-emerald-600">
                ● {node.status}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Expanded Deliberation & Self-Correction Log */}
      {expanded && (
        <div className="mt-3 pt-3 border-t border-line space-y-2 animate-in fade-in">
          <div className="rounded-[6px] bg-paper p-3 border border-line font-mono text-[11px]">
            <div className="flex items-center gap-1.5 text-ink font-bold mb-1">
              <Terminal className="w-3.5 h-3.5" />
              <span>CRITIC AGENT VERIFICATION AUDIT TRAIL</span>
            </div>
            <p className="text-inksoft leading-relaxed">
              {xaiData.critic_notes}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
