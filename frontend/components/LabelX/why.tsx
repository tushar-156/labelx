"use client";

import { cn } from "@/lib/utils";
import { GhostButton, InkButton, Reveal, SectionLabel, Stamp, LogoMark } from "./bits";
import type { View } from "./shell";

export const SAFETY_TIERS = {
  SAFE: {
    label: "Safe",
    blurb: "Scientifically proven to be harmless under normal usage.",
  },
  CAUTION: {
    label: "Caution",
    blurb: "May cause irritation for sensitive skin. Patch test recommended.",
  },
  HIGH_RISK: {
    label: "High Risk",
    blurb: "Known allergens, endocrine disruptors, or banned substances.",
  },
} as const;

export function TierChip({ tier }: { tier: keyof typeof SAFETY_TIERS }) {
  const t = SAFETY_TIERS[tier];
  return (
    <span
      className={cn(
        "rounded-[3px] border px-2 py-0.5 font-mono text-[10px] tracking-[0.04em]",
        tier === "SAFE" && "border-[#cfdccf] bg-[#cfdccf]/20 text-[#6f8f79]",
        tier === "CAUTION" && "border-[#f4e6c2] bg-[#f4e6c2]/20 text-[#b99a5e]",
        tier === "HIGH_RISK" && "border-red-200 bg-red-50 text-red-700"
      )}
    >
      {t.label}
    </span>
  );
}

export function WhyPage({ onEnter }: { onEnter: (v: View) => void }) {
  return (
    <div>
      {/* ------------------------------ the claim ------------------------------ */}
      <section aria-label="why Label Analyzer exists" className="pb-16 pt-4 text-center sm:pt-8">
        <p className="label-caps">why Label Analyzer exists</p>
        <h1 className="mx-auto mt-7 max-w-[24ch] text-balance font-display text-[clamp(32px,4.8vw,56px)] font-semibold leading-[1.08] tracking-[-0.03em] text-ink">
          Cosmetic labels are designed to be confusing.
        </h1>
        <div className="mx-auto mt-9 max-w-[60ch] space-y-5 text-left text-[16px] leading-[1.75] text-inksoft">
          <p>
            Chemical names are long, complex, and impossible to memorize. Brands hide behind complex 
            INCI (International Nomenclature of Cosmetic Ingredients) nomenclature. You look at the back 
            of a bottle and see 30 different compounds, but the only question that matters is —{" "}
            <em className="text-ink not-italic underline decoration-cleared/40 decoration-1 underline-offset-4">
              is this actually safe for my body?
            </em>{" "}
            — and currently, figuring that out requires a degree in biochemistry.
          </p>
          <p>
            AI breaks that asymmetry. A machine parsing a label is fast, tireless, and literate — it 
            can extract every compound in milliseconds, cross-reference it against global safety databases, 
            and flag endocrine disruptors or known carcinogens instantly. The consumer finally gets to 
            see the truth behind the marketing. The label is no longer a wall.
          </p>
          <p>
            The industry answer on the horizon — cleaner branding and "green" marketing — moves the wall, 
            it does not remove it. If we can instantly parse ingredients, the question stops being{" "}
            <em className="text-ink not-italic">is this brand trustworthy?</em> and
            becomes{" "}
            <em className="text-ink not-italic">what is the provable scientific consensus on these chemicals?</em> 
            That question has an old, solved shape. It is the question the Label Analyzer answers a thousand times a day.
          </p>
        </div>
      </section>

      {/* ------------------------------ the principle ------------------------------ */}
      <Reveal>
        <section className="rounded-[4px] border border-line bg-card px-6 py-8 sm:px-8 sm:py-9" aria-label="the principle">
          <SectionLabel>the principle — truth over marketing</SectionLabel>
          <p className="mt-4 max-w-[62ch] text-[15px] leading-[1.8] text-inksoft">
            Label Analyzer never asks the brand whether it is honest. It extracts the raw ingredient manifest, 
            checks it against the FDA and global safety rules, stamps what passes, and flags what does not — 
            every decision written down. We apply exactly that protocol to personal care: the user does not 
            rely on trust. They get a{" "}
            <span className="font-semibold text-ink">scientific safety profile</span> — a clear 
            breakdown that says exactly what is inside, matched to their skin type — and every chemical 
            is checked against clinical literature in plain, auditable code.
          </p>
          <div className="mt-6 grid gap-px bg-line md:grid-cols-3">
            {[
              {
                t: "extracted",
                d: "Vision models accurately parse distorted, curved, or poorly lit ingredient lists directly from the bottle.",
              },
              {
                t: "cross-referenced",
                d: "Every extracted chemical is mapped to its INCI standard name and queried against a global safety database.",
              },
              {
                t: "personalized",
                d: "Safety scores aren't generic. Ingredients are evaluated based on your specific skin type and known sensitivities.",
              },
            ].map((p) => (
              <div key={p.t} className="bg-card px-4 py-4">
                <div className="font-mono text-[11px] uppercase tracking-[0.1em] text-cleared">{p.t}</div>
                <p className="mt-2 text-[13px] leading-relaxed text-inksoft">{p.d}</p>
              </div>
            ))}
          </div>
          <div className="mt-5 flex flex-wrap items-center gap-2.5">
            <span className="font-mono text-[10.5px] uppercase tracking-[0.1em] text-inksoft">safety ratings:</span>
            {(["SAFE", "CAUTION", "HIGH_RISK"] as const).map((t) => (
              <TierChip key={t} tier={t} />
            ))}
            <span className="text-[12.5px] text-inksoft">
              clear, scientific, and unwavering
            </span>
          </div>
        </section>
      </Reveal>

      {/* ------------------------------ the architecture ------------------------------ */}
      <Reveal>
        <section aria-label="architecture" className="py-20">
          <div className="flex flex-wrap items-end justify-between gap-3">
            <h2 className="font-display text-[clamp(24px,3vw,34px)] font-semibold tracking-[-0.025em] text-ink">
              One picture, complete clarity.
            </h2>
            <span className="text-[12.5px] text-inksoft">
              the full analysis pipeline lives in ARCHITECTURE.md
            </span>
          </div>

          <ArchFlow />

          {/* the four moves, in order */}
          <div className="mt-3 grid gap-px bg-line md:grid-cols-4">
            {[
              ["01", "the upload", "The user snaps a photo of the back of their cosmetic product. The image is pre-processed for clarity and contrast."],
              ["02", "the extraction", "A vision model extracts the raw text. Comma-separated strings are split, cleaned, and normalized to standard chemical names."],
              ["03", "the safety gate", "Each ingredient is queried against our global safety database. Toxicity, comedogenic ratings, and allergen warnings are pulled instantly."],
              ["04", "the final profile", "A beautiful, color-coded safety profile is generated. The user instantly sees what's safe, what's risky, and why."],
            ].map(([n, t, d]) => (
              <div key={n} className="card-lift rounded-[4px] bg-card px-4 py-3.5">
                <div className="flex items-baseline gap-2.5">
                  <span className="font-mono text-[10px] text-inksoft">{n}</span>
                  <span className="text-[14px] font-medium text-ink">{t}</span>
                </div>
                <p className="mt-1.5 text-[12.5px] leading-relaxed text-inksoft">{d}</p>
              </div>
            ))}
          </div>
        </section>
      </Reveal>

      {/* ------------------------------ the database ------------------------------ */}
      <Reveal>
        <section aria-label="the database" className="pb-20">
          <h2 className="font-display text-[clamp(24px,3vw,34px)] font-semibold tracking-[-0.025em] text-ink">
            The safety database.
          </h2>
          <p className="mt-4 max-w-[62ch] text-[15px] leading-[1.8] text-inksoft">
            We hold ourselves to the highest scientific bar — every safety rating is 
            explainable and backed by clinical literature. If an ingredient is flagged, 
            it points to the exact compound and reason. Here is what we scan, how we classify, 
            and the work order for what comes next.
          </p>

          <div className="mt-8 grid gap-4 lg:grid-cols-2">
            <PatchCard
              stamp={<Stamp kind="cleared" animate={false}>scanned · verified</Stamp>}
              items={[
                "Live at LabelX.srivtx.xyz — real OCR extraction (simulated:false in /api/health); the vision pipeline is executed locally.",
                "Both sides of the counter: consumer scanner + global safety database, one shared truth.",
                "10-check safety pipeline mapping synonyms to canonical INCI names.",
                "Safety ratings (Safe / Caution / High Risk) and a human review desk for disputed compounds.",
                "Hash-chained JSONL database — the audit trail is immutable; tamper probe detects mutation.",
                "Channel metric (scans − API serving cost) with the at-1M projection, assumptions declared.",
                "The developer API — the analysis engine published for outside integrations: a REAL REST API at /api/analyze.",
              ]}
              dot="bg-cleared"
            />
            <PatchCard
              stamp={<Stamp kind="held" animate={false}>simulated · labeled · code-ready</Stamp>}
              items={[
                "The simulation fallback — on a fresh clone or a sandboxed runner with no keys set, the OCR degrades to a loudly-labeled in-process simulation.",
                "The LLM brain — optional by design. The deterministic rules brain runs everything by default so every demo replays bit-for-bit.",
              ]}
              dot="bg-held"
            />
          </div>

          <div className="mt-6 rounded-[4px] border border-dashed border-ink/15 bg-paper2/40 px-5 py-5 sm:px-6">
            <div className="flex flex-wrap items-center gap-3">
              <Stamp kind="held" animate={false}>on the desk · next</Stamp>
              <span className="text-[12.5px] text-inksoft">
                the build order, in the open
              </span>
            </div>
            <div className="mt-4 grid gap-2.5 sm:grid-cols-2">
              {[
                ["01", "the persistent database", "Move the JSONL database to a volume-backed host so state survives restarts."],
                ["02", "pregnancy safety mode", "A new analysis mode that specifically flags ingredients known to be harmful during pregnancy."],
                ["03", "vegan & cruelty-free", "Cross-referencing brand parent companies against PETA's cruelty-free registries."],
              ].map(([n, t, d]) => (
                <div key={n} className="flex items-start gap-3 rounded-[3px] bg-ink/[0.03] px-3 py-2.5">
                  <span className="mt-px shrink-0 rounded-[3px] border border-line bg-card px-1.5 py-0.5 font-mono text-[9.5px] text-inksoft">
                    {n}
                  </span>
                  <div>
                    <span className="text-[13px] font-medium text-ink">{t}</span>
                    <p className="mt-0.5 text-[12px] leading-relaxed text-inksoft">{d}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      </Reveal>

      {/* ------------------------------ where to go ------------------------------ */}
      <Reveal>
        <section className="flex flex-wrap items-center gap-3 border-t border-line pt-8" aria-label="continue">
          <InkButton onClick={() => onEnter("analyze")} arrow>
            scan a product
          </InkButton>
        </section>
      </Reveal>
    </div>
  );
}

function ArchFlow() {
  return (
    <div className="doc mt-6">
      <div className="flex items-center justify-between border-b border-line px-4 py-2.5">
        <span className="label-caps">the flow — one scan, end to end</span>
        <span className="hidden text-[11.5px] text-inksoft sm:block">hover any box · every one is code you can open</span>
      </div>
      <div className="space-y-3 p-4">
        <div className="flex flex-col gap-2 lg:flex-row lg:items-stretch lg:gap-2.5">
          <FlowCard title="user side" flex="lg:flex-[1.05]">
            <FlowRow left="camera" right="human · snaps the photo" />
            <FlowRow left="upload" right="image → pixels → bytes" />
            <FlowRow left="crop" right="detects text regions" />
            <div className="mt-2.5 rounded-[4px] border border-cleared/35 bg-cleared/10 px-2.5 py-1.5 font-mono text-[10px] uppercase tracking-[0.08em] text-cleared">
              image enhancement — human in the loop
            </div>
          </FlowCard>
          <FlowArrow />
          <FlowCard title="the engine" flex="lg:flex-[1.25]" accent>
            <div className="flex items-center gap-2.5 pb-2">
              <LogoMark size={14} className="text-ink" />
              <span className="font-mono text-[10.5px] text-inksoft">extract() — pipeline</span>
            </div>
            {[
              "optical character recognition",
              "comma-separated string split",
              "regex cleanup & normalization",
              "synonym mapping to INCI",
              "database query",
              "≥ 1 High Risk → Flag Product",
            ].map((s) => (
              <div key={s} className="flex items-center gap-2.5 rounded-[3px] bg-ink/[0.04] px-2.5 py-1.5">
                <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-cleared" aria-hidden />
                <span className="text-[12px] text-ink">{s}</span>
              </div>
            ))}
          </FlowCard>
          <FlowArrow />
          <FlowCard title="database" flex="lg:flex-[0.55]">
            <FlowRow left="query" right="development" />
            <FlowRow left="or" right="cached simulation" />
            <p className="mt-2 text-[11.5px] leading-relaxed text-inksoft">the source of truth</p>
          </FlowCard>
          <FlowArrow />
          <FlowCard title="analytics side" flex="lg:flex-[1]">
            <FlowRow left="dashboard" right="scans · anomalies" />
            <FlowRow left="ingredient logs" right="click any row" />
            <FlowRow left="toxic flags" right="12 · all caught" />
          </FlowCard>
        </div>

        <div className="rounded-[4px] border border-line bg-paper2/40 px-4 py-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <span className="font-mono text-[11px] uppercase tracking-[0.14em] text-ink">
              hash-chained database — the audit trail is immutable
            </span>
            <span className="text-[11.5px] text-inksoft">every compound, every scan, every flag</span>
          </div>
          <div className="mt-2.5 flex flex-wrap items-center gap-1.5">
            {Array.from({ length: 12 }, (_, i) => (
              <span key={i} className="flex items-center gap-1.5">
                <span className="rounded-[3px] border border-line bg-card px-1.5 py-0.5 font-mono text-[9.5px] text-inksoft">
                  #{i + 1}
                </span>
                {i < 11 && <span className="text-[10px] text-inksoft/60">→</span>}
              </span>
            ))}
          </div>
          <p className="mt-2 text-[11.5px] text-inksoft">
            safe ratings, warnings, every flag · tamper with a byte and the check fails · review scan-by-scan from the dashboard
          </p>
        </div>
      </div>
    </div>
  );
}

function FlowCard({
  title,
  children,
  flex,
  accent,
}: {
  title: string;
  children: React.ReactNode;
  flex?: string;
  accent?: boolean;
}) {
  return (
    <div className={cn("card-lift rounded-[4px] border bg-card px-3.5 py-3", accent ? "border-ink/25" : "border-line", flex)}>
      <div className="label-caps mb-2.5">{title}</div>
      <div className="space-y-1.5">{children}</div>
    </div>
  );
}

function FlowRow({ left, right }: { left: string; right: string }) {
  return (
    <div className="flex items-baseline justify-between gap-3 rounded-[3px] bg-ink/[0.04] px-2.5 py-1.5">
      <span className="font-mono text-[10px] uppercase tracking-[0.08em] text-ink">{left}</span>
      <span className="text-right text-[11.5px] text-inksoft">{right}</span>
    </div>
  );
}

function PatchCard({
  stamp,
  items,
  dot,
}: {
  stamp: React.ReactNode;
  items: string[];
  dot: string;
}) {
  return (
    <div className="rounded-[4px] border border-line bg-paper2/50 p-[7px]">
      <div className="h-full rounded-[3px] border border-dashed border-ink/15 px-5 py-5">
        {stamp}
        <ul className="mt-4 space-y-2.5 text-[12.5px] leading-relaxed text-inksoft">
          {items.map((s) => (
            <li key={s} className="flex gap-2.5">
              <span className={cn("mt-[7px] h-1 w-1 shrink-0 rounded-full", dot)} aria-hidden />
              <span>{s}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

function FlowArrow() {
  return (
    <div className="flex items-center justify-center py-0.5 lg:py-0" aria-hidden>
      <span className="font-mono text-[13px] text-inksoft/60 lg:hidden">↓</span>
      <span className="hidden font-mono text-[13px] text-inksoft/60 lg:inline">→</span>
    </div>
  );
}
