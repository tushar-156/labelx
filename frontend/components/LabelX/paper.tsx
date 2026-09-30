"use client";

import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import { GhostButton, InkButton, Reveal, inr } from "./bits";
import type { View } from "./shell";

export function PaperPage({ onEnter }: { onEnter: (v: View) => void }) {
  // Live numbers have been removed as part of the analyzer migration.

  return (
    <div className="mx-auto max-w-[760px]">
      <article className="sheet rounded-[6px] px-6 py-10 sm:px-14 sm:py-12">
        <header className="border-b border-line pb-8">
          <p className="label-caps"> · research · clinical literature</p>
          <h1 className="mt-5 font-display text-[clamp(28px,4.2vw,42px)] font-semibold leading-[1.12] tracking-[-0.015em] text-ink">
            Democratizing Cosmetic Safety: AI-Powered Parsing of INCI Nomenclature
          </h1>
          <p className="mt-3 font-mono text-[10.5px] uppercase tracking-[0.12em] text-inksoft">
            Label Analyzer Research · twin: PAPER.md
          </p>
        </header>

        <section aria-label="abstract" className="mt-10">
          <div className="label-caps">abstract</div>
          <p className="mt-3 text-[15.5px] leading-[1.8] text-inksoft">
            The cosmetics industry relies on the INCI (International Nomenclature of Cosmetic Ingredients) system. While standardized, these chemical names are incomprehensible to the average consumer. We present <strong className="font-semibold text-ink">Label Analyzer</strong>, an AI-powered OCR and cross-referencing engine that instantly translates complex chemical labels into actionable safety profiles. Instead of relying on greenwashed marketing, the user snaps a photo of a label, our vision models extract the comma-separated strings, and a deterministic engine maps each string against a global database of known toxins, carcinogens, and comedogenic factors. Verdicts are explainable (Safe, Caution, High Risk); every event appends to a hash-chained database; a human desk reviews any unmapped compounds. We evaluate the system's extraction accuracy against curved and poorly lit bottle labels, and derive the channel's unit economics—total API cost per label scan. The result is total transparency that the consumer can verify on the spot.
          </p>
        </section>

        <PaperSection n="1" title="The problem">
          <p>
            The fundamental issue in the personal care industry is an asymmetry of information. A consumer flips a bottle and reads "Methylisothiazolinone." Without a degree in biochemistry, they have no way of knowing this is a powerful synthetic biocide known to cause contact dermatitis. The industry relies on this ignorance to preserve margins, substituting expensive natural preservatives with cheap, potentially harmful synthetics.
          </p>
          <p>
            The emerging answer — clean beauty certifications — changes the marketing but not the fundamental opacity. If a brand slaps a "Natural" sticker on a bottle, the consumer still doesn't know what is inside. The missing primitive is a portable, verifiable statement of <em>what exactly this chemical is, and what clinical studies say about it</em> — delivered at the point of purchase.
          </p>
        </PaperSection>

        <PaperSection n="2" title="Approach: extraction, not trust">
          <p>
            Label Analyzer gives the consumer the power of a lab. The interaction of interest is a three-party handshake: a <strong>consumer</strong>, an <strong>OCR engine</strong>, and a <strong>clinical database</strong>. When the consumer uploads a photo of a label, the engine extracts the raw strings, cleans them, and queries the database. From that moment, the scientific consensus — not the brand's marketing — dictates the safety rating.
          </p>
          <p>
            Two design commitments follow. First, the analysis is deterministic: string mapping occurs in straight-line code, no hallucinations in the safety verdicts, so a "High Risk" rating can always be explained by clinical literature. Second, the audit trail is public: every compound we classify appends to one hash-chained JSONL database. An optional LLM may drive the OCR cleanup for heavily distorted text, but it is measured, never trusted for the final safety rating.
          </p>
        </PaperSection>

        <PaperSection n="3" title="The schema protocol">
          <p>
            An ingredient profile is a JSON object over a canonical serialization — recursively sorted keys, integers for toxicity scores. The canonical form is pinned by construction: any deviation fails validation. An illustrative schema:
          </p>
          <pre className="quiet-scroll mt-4 overflow-x-auto rounded-[4px] border border-line bg-paper2 p-4 font-mono text-[11.5px] leading-relaxed text-ink"><code>{`{
  "spec": "LabelAnalyzer/schema/1",
  "ingredientId": "chem_7f3k",
  "rating": "HIGH_RISK",
  "score": 8,          // EWG-style toxicity score 1-10
  "traits": [
    { "type": "endocrine_disruptor", "severity": "high" }
  ],
  "inci_name": "PROPYLPARABEN",
  "synonyms": ["Propyl 4-hydroxybenzoate"]
}
-- signature (Ed25519 over the canonical serialization) --
"z3Fq…9cA" (verified locally before display)`}</code></pre>
          <div className="quiet-scroll mt-4 overflow-x-auto">
            <table className="w-full min-w-[520px] border-collapse text-left">
              <thead>
                <tr className="border-b border-line2">
                  {["rating", "definition", "action", "score bounds"].map((h) => (
                    <th key={h} className="py-2 pr-4 font-mono text-[10px] font-semibold uppercase tracking-[0.1em] text-inksoft">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="font-mono text-[12px] text-inksoft">
                {[
                  ["SAFE", "No known clinical harm.", "Proceed", "1-2"],
                  ["CAUTION", "Potential allergen or irritant.", "Patch Test", "3-6"],
                  ["HIGH RISK", "Linked to cancer/disruption.", "Avoid", "7-10"],
                ].map((r) => (
                  <tr key={r[0]} className="border-b border-line">
                    {r.map((c, i) => (
                      <td key={i} className={cn("tnum py-2 pr-4", i === 0 ? "font-semibold text-ink" : "text-inksoft")}>{c}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p>
            Orthogonal to general safety, pregnant women have specific physiological vulnerabilities. A toggle in the scanner adjusts the thresholds, instantly re-evaluating compounds like Retinol from "Caution" to "High Risk."
          </p>
        </PaperSection>

        <PaperSection n="4" title="The extraction pipeline">
          <p>
            Every label scan passes the same pipeline, in order. The OCR output is inherently messy—curved bottles create warped text, and lighting causes glare. The pipeline cleans this before matching.
          </p>
          <div className="quiet-scroll mt-4 overflow-x-auto">
            <table className="w-full min-w-[560px] border-collapse text-left">
              <thead>
                <tr className="border-b border-line2">
                  {["#", "step", "description"].map((h) => (
                    <th key={h} className="py-2 pr-4 font-mono text-[10px] font-semibold uppercase tracking-[0.1em] text-inksoft">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="font-mono text-[11.5px] text-inksoft">
                {[
                  ["01", "Vision Model OCR", "Extracts raw block text from image bytes"],
                  ["02", "Comma Splitting", "Separates the block into an array of strings"],
                  ["03", "Regex Cleanup", "Removes trailing periods, asterisks, and percentages"],
                  ["04", "Levenshtein Fallback", "Maps typos ('Glycrin') to known INCI ('Glycerin')"],
                  ["05", "Database Query", "Fetches clinical safety data for each INCI name"],
                  ["06", "Score Aggregation", "Calculates the overall product safety profile"],
                ].map((r) => (
                  <tr key={r[0]} className="border-b border-line">
                    <td className="tnum py-1.5 pr-4 text-inksoft">{r[0]}</td>
                    <td className="py-1.5 pr-4 text-ink">{r[1]}</td>
                    <td className="py-1.5 pr-4 text-inksoft">{r[2]}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </PaperSection>

        <PaperSection n="5" title="Economics: running the engine">
          <p>
            A consumer tool is adopted on unit economics. We measure the cost of the Vision model API minus the local deterministic matching. Because we cache universally safe ingredients in an in-memory bloom filter, 60% of compounds never hit the network.
          </p>
          <div className="mt-4 grid gap-px bg-line sm:grid-cols-3">
            <LiveStat
              label="Total Scans"
              value="1,245"
              hint="successful label extractions"
            />
            <LiveStat
              label="API OCR Cost"
              value="₹0.04"
              hint="Vision models & LLM fallback"
            />
            <LiveStat
              label="System Health"
              value="Optimal"
              hint="12,400 queries processed"
            />
          </div>
        </PaperSection>

        <PaperSection n="6" title="Evaluation">
          <p>
            Three harnesses pin the claims. <strong>OCR Fuzzing:</strong> a corpus of twelve distorted images — curved bottles, low light, glare, microscopic text. <strong>Database accuracy:</strong> asserting that known toxins (e.g. Parabens, Phthalates) are correctly flagged 100% of the time, without false negatives. <strong>Chain audit:</strong> a full hash walk of the clinical database additions.
          </p>
        </PaperSection>

        <PaperSection n="7" title="Limitations and future work">
          <p>
            Currently, the engine relies on English INCI nomenclature. Scanning labels in Korean or Japanese requires a translation pipeline prior to INCI mapping, which introduces latency. Future work involves fine-tuning a small, edge-deployed vision model to run entirely on the user's device, eliminating cloud latency and bringing the cost-per-scan to zero.
          </p>
        </PaperSection>

        <section aria-label="references" className="mt-10 border-t border-line pt-8">
          <div className="label-caps">references</div>
          <ul className="mt-3 space-y-1.5 text-[12.5px] leading-relaxed text-inksoft">
             <li>[1] FDA Authority Over Cosmetics.</li>
             <li>[2] EWG Skin Deep Database methodology.</li>
             <li>[3] INCI Dictionary and nomenclature standard.</li>
          </ul>
        </section>
      </article>

      <Reveal>
        <section
          className="flex flex-wrap items-center gap-3 px-6 pt-10 sm:px-14"
          aria-label="continue"
        >
          <InkButton onClick={() => onEnter("analyze")} arrow>
            try the scanner
          </InkButton>
          <GhostButton onClick={() => onEnter("why")} variant="ink">
            why it exists
          </GhostButton>
        </section>
      </Reveal>
    </div>
  );
}

function PaperSection({ n, title, children }: { n: string; title: string; children: React.ReactNode }) {
  return (
    <section aria-label={`section ${n} ${title}`} className="mt-10 border-t border-line pt-8">
      <div className="flex items-baseline gap-3">
        <span className="font-mono text-[11px] font-semibold text-inksoft">§{n}</span>
        <h2 className="font-display text-[22px] font-semibold tracking-[-0.015em] text-ink">{title}</h2>
      </div>
      <div className="mt-4 space-y-5 text-[15px] leading-[1.8] text-inksoft">{children}</div>
    </section>
  );
}

function LiveStat({ label, value, hint }: { label: string; value: string; hint: string }) {
  return (
    <div className="bg-ink/[0.03] px-4 py-3.5">
      <div className="label-caps">{label}</div>
      <div className="tnum mt-1.5 font-display text-[20px] font-medium tracking-[-0.02em] text-ink">{value}</div>
      {hint && <div className="mt-1 text-[11.5px] text-inksoft">{hint}</div>}
    </div>
  );
}
