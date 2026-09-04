import { LabelXApp } from "@/components/LabelX/shell";

/**
 * LabelX — both sides of the agentic counter, in one route.
 * Overview → Agent Playground (buyer side) → Control Room (merchant side).
 * All state lives behind /api/*; the ledger is the only source of truth.
 */
export default function Home() {
  return <LabelXApp />;
}
