"use client";

import { useId, useState } from "react";
import { cn } from "@/lib/utils";
import { DeskHead, GhostButton, InkButton, Reveal } from "./bits";
import type { View } from "./shell";

function FeltGrain() {
  const id = `ag-grain-${useId().replace(/:/g, "")}`;
  return (
    <svg aria-hidden className="pointer-events-none absolute inset-0 h-full w-full">
      <filter id={id}>
        <feTurbulence type="fractalNoise" baseFrequency="0.55" numOctaves="3" stitchTiles="stitch" />
        <feColorMatrix type="saturate" values="0" />
      </filter>
      <rect width="100%" height="100%" filter={`url(#${id})`} opacity="0.05" style={{ mixBlendMode: "overlay" }} />
    </svg>
  );
}

function AgentsFabric({ className }: { className?: string }) {
  const uid = useId().replace(/:/g, "");
  const mat = `af-mat-${uid}`;
  const weave = `af-weave-${uid}`;
  const dyeM = `af-dm-${uid}`;
  const dyeC = `af-dc-${uid}`;
  const soft = `af-soft-${uid}`;
  return (
    <svg aria-hidden viewBox="0 0 340 340" className={cn("select-none", className)}>
      <defs>
        <clipPath id={mat}>
          <rect x="6" y="6" width="328" height="328" rx="14" />
        </clipPath>
        <pattern id={weave} width="8" height="8" patternUnits="userSpaceOnUse">
          <path d="M0 4H8" stroke="var(--ink)" strokeOpacity="0.05" strokeWidth="1" />
          <path d="M4 0V8" stroke="var(--ink)" strokeOpacity="0.035" strokeWidth="1" />
        </pattern>
        <radialGradient id={dyeM} cx="0.5" cy="0.5" r="0.5">
          <stop offset="0" stopColor="var(--ink)" stopOpacity="0.07" />
          <stop offset="1" stopColor="var(--ink)" stopOpacity="0" />
        </radialGradient>
        <radialGradient id={dyeC} cx="0.5" cy="0.5" r="0.5">
          <stop offset="0" stopColor="var(--band)" stopOpacity="0.14" />
          <stop offset="1" stopColor="var(--band)" stopOpacity="0" />
        </radialGradient>
        <filter id={soft} x="-40%" y="-40%" width="180%" height="180%">
          <feGaussianBlur stdDeviation="18" />
        </filter>
      </defs>

      <rect x="6" y="16" width="328" height="328" rx="14" fill="var(--ink)" opacity="0.12" />
      <g clipPath={`url(#${mat})`}>
        <rect x="6" y="6" width="328" height="328" fill="var(--paper2)" />
        <rect x="6" y="6" width="328" height="328" fill={`url(#${weave})`} />
        <ellipse cx="100" cy="110" rx="150" ry="120" fill={`url(#${dyeM})`} />
        <ellipse cx="240" cy="235" rx="160" ry="130" fill={`url(#${dyeC})`} />
        <ellipse
          cx="170"
          cy="205"
          rx="150"
          ry="18"
          fill="var(--ink)"
          opacity="0.05"
          filter={`url(#${soft})`}
          transform="rotate(-38 170 205)"
        />
        <ellipse cx="120" cy="90" rx="140" ry="44" fill="#ffffff" opacity="0.1" filter={`url(#${soft})`} />
      </g>

      <g strokeLinecap="round">
        <line x1="58" y1="74.5" x2="282" y2="270.5" stroke="var(--line-strong)" strokeOpacity="0.4" strokeWidth="1.6" strokeDasharray="0.5 11" />
        <line x1="58" y1="69.5" x2="282" y2="265.5" stroke="var(--line-strong)" strokeWidth="2" strokeDasharray="0.5 11" />
        <path d="M166 166 q 11 6 7 17" fill="none" stroke="var(--line-strong)" strokeWidth="1.4" opacity="0.55" />
        <path d="M247 108 q -9 7 -4 16" fill="none" stroke="var(--line-strong)" strokeWidth="1.2" opacity="0.4" />
      </g>

      <rect x="15" y="15" width="310" height="310" rx="9" fill="none" stroke="var(--ink)" strokeOpacity="0.25" strokeWidth="1.3" strokeDasharray="4 4" />

      <g stroke="var(--ink)" strokeOpacity="0.35" strokeWidth="1.5" strokeLinecap="round" fill="none">
        <path d="M21 21l7 7M28 21l-7 7" />
        <path d="M312 21l7 7M319 21l-7 7" />
        <path d="M21 312l7 7M28 312l-7 7" />
        <path d="M312 312l7 7M319 312l-7 7" />
      </g>
    </svg>
  );
}

function Stitch({ inset = 6, className, rx = 3 }: { inset?: number; className?: string; rx?: number }) {
  return (
    <div aria-hidden className="pointer-events-none absolute" style={{ inset }}>
      <svg width="100%" height="100%" className="block">
        <rect
          x="0.75"
          y="0.75"
          width="99.5%"
          height="99.5%"
          rx={rx}
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeDasharray="0.5 11"
          strokeLinecap="round"
          className={className}
        />
      </svg>
    </div>
  );
}

function CornerTack({ className }: { className?: string }) {
  return (
    <svg
      aria-hidden
      viewBox="0 0 12 12"
      className={cn("pointer-events-none absolute size-3", className)}
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
    >
      <path d="M2 2l8 8M10 2l-8 8" />
    </svg>
  );
}

function Nameplate({ name, thread }: { name: string; thread: string }) {
  return (
    <span className="relative inline-flex items-center border border-line bg-paper2 px-3.5 py-1.5">
      <Stitch inset={3} className={thread} rx={1} />
      <span className="label-caps relative">{name}</span>
    </span>
  );
}

const DESK_SKILLS = [
  "extracts ingredients from dark/curved labels",
  "cleans distorted optical characters into strings",
  "splits comma-separated compound names",
  "floats on every page — ready to scan",
];

const COCO_SKILLS = [
  "cross-references extracted strings",
  "maps trade names to canonical INCI",
  "queries global toxicity databases",
  "computes final safety scores — 0 latency",
];

const HANDOFF: { tag: string; text: string; loud?: boolean }[] = [
  { tag: "user", text: "uploads image of moisturizer back label", loud: true },
  { tag: "vision", text: "extracted: 'water, glycerin, phenoxyethanol, red-40'" },
  { tag: "bus", text: "parsed strings sent over the wire — the handoff" },
  { tag: "engine", text: "phenoxythenol mapped -> CAUTION. red-40 mapped -> HIGH RISK." },
];

function SkillLog({ lines }: { lines: string[] }) {
  return (
    <ul className="mt-5 space-y-2">
      {lines.map((s) => (
        <li key={s} className="flex gap-2.5 font-mono text-[11.5px] leading-relaxed text-inksoft">
          <span aria-hidden className="shrink-0 text-ink/50">
            [ok]
          </span>
          {s}
        </li>
      ))}
    </ul>
  );
}

export function AgentsPage({ onEnter }: { onEnter: (v: View) => void }) {
  const [summoning, setSummoning] = useState(false);
  const [said, setSaid] = useState<string | null>(null);
  const [ping, setPing] = useState(false);

  const summon = async () => {
    if (summoning) return;
    setSummoning(true);
    setSaid("initializing vision model…");
    try {
      await new Promise(r => setTimeout(r, 1500));
      setSaid(`extracting compounds — found 24 ingredients`);
      setPing(true);
      setTimeout(() => setPing(false), 950);
    } catch {
      setSaid("the extraction failed — try again.");
    } finally {
      setSummoning(false);
    }
  };

  return (
    <div>
      <section aria-label="the science" className="pb-16 pt-6 sm:pt-10">
        <div className="grid items-center gap-10 lg:grid-cols-[minmax(0,1fr)_minmax(0,29rem)] lg:gap-6">
          <div>
            <p className="label-caps">the science · two engines · zero latency</p>
            <h1 className="mt-6 max-w-[16ch] font-display text-[clamp(40px,6vw,72px)] font-semibold leading-[0.98] tracking-[-0.035em] text-ink">
              Vision extracts.
              <br />
              <span className="text-inksoft">Engine analyzes.</span>
            </h1>
            <p className="mt-7 max-w-[52ch] text-[17px] leading-relaxed text-inksoft">
              Two powerful pipelines share one processor. The vision model extracts 
              distorted text from curved bottles; the database engine cross-references 
              every compound instantly. Run a test extraction below.
            </p>
            <div className="mt-9 flex flex-wrap items-center gap-3">
              <InkButton onClick={summon} disabled={summoning} ariaLabel="test extraction" arrow className="h-11 px-5 text-[14px]">
                {summoning ? "Initializing…" : "Test extraction"}
              </InkButton>
              <GhostButton onClick={() => onEnter("analyze")} ariaLabel="open the scanner" variant="ink" className="h-11 px-5">
                Open scanner
              </GhostButton>
            </div>
            <p aria-live="polite" className="mt-4 min-h-[20px] font-mono text-[11.5px] leading-relaxed text-inksoft">
              {said ?? "the pipeline is ready — press test and watch it run"}
            </p>
          </div>

          <div className="relative mx-auto w-[min(80vw,340px)] lg:w-full">
            <AgentsFabric className="absolute inset-0 h-full w-full" />
            <div className="relative aspect-square">
              <div className="absolute left-[4%] top-[6%]">
                <DeskHead size={120} className="text-ink" />
              </div>
              <div className="absolute bottom-[4%] right-[4%]">
                <DeskHead size={120} className="text-ink opacity-50" />
              </div>
              <span className="absolute left-1/2 top-1/2 flex size-12 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full border border-line-strong bg-card font-mono text-[9px] uppercase tracking-[0.08em] text-inksoft">
                bus
                {ping && <span className="wire-packet absolute inset-0 rounded-full border-2 border-line-strong" />}
              </span>
            </div>
          </div>
        </div>
      </section>

      <Reveal>
        <section aria-label="what they can do" className="border-t border-line py-16">
          <div className="flex flex-wrap items-end justify-between gap-3">
            <h2 className="font-display text-[clamp(24px,3vw,34px)] font-semibold tracking-[-0.025em] text-ink">
              The dual pipeline.
            </h2>
            <span className="text-[12.5px] text-inksoft">OCR and database queries · ~300ms total</span>
          </div>

          <div className="relative mt-8 rounded-[4px] border border-line bg-card transition-colors duration-150 hover:border-line-strong">
            <Stitch inset={5} className="text-inksoft/70" rx={3} />
            <CornerTack className="left-1.5 top-1.5 text-inksoft" />
            <CornerTack className="right-1.5 top-1.5 text-inksoft" />
            <CornerTack className="bottom-1.5 left-1.5 text-inksoft" />
            <CornerTack className="bottom-1.5 right-1.5 text-inksoft" />

            <div className="relative grid md:grid-cols-[1fr_auto_1fr]">
              <div className="p-7 transition-colors duration-150 hover:bg-card-hover">
                <FeltGrain />
                <div className="relative flex items-center justify-center py-4">
                  <DeskHead size={96} className="text-ink" />
                </div>
                <div className="relative mt-3 flex items-center justify-center gap-1.5 text-[10.5px] text-inksoft">
                  <span aria-hidden className="h-1 w-1 rounded-full bg-cleared/80" />
                  gpu bound
                </div>
                <div className="relative mt-5 flex justify-center">
                  <Nameplate name="vision" thread="text-ink/40" />
                </div>
                <div className="relative">
                  <SkillLog lines={DESK_SKILLS} />
                </div>
              </div>

              <div aria-hidden className="relative hidden w-14 shrink-0 md:block">
                <svg className="absolute inset-0 h-full w-full">
                  <line
                    x1="50%"
                    y1="0"
                    x2="50%"
                    y2="100%"
                    stroke="var(--band)"
                    strokeOpacity="0.55"
                    strokeWidth="1.5"
                    strokeDasharray="0.5 11"
                    strokeLinecap="round"
                  />
                </svg>
                <span className="absolute left-1/2 top-1/2 flex size-12 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full border border-line-strong bg-card font-mono text-[9px] uppercase tracking-[0.08em] text-inksoft">
                  bus
                </span>
              </div>
              <div aria-hidden className="relative h-12 md:hidden">
                <svg className="absolute inset-0 h-full w-full">
                  <line
                    x1="0"
                    y1="50%"
                    x2="100%"
                    y2="50%"
                    stroke="var(--band)"
                    strokeOpacity="0.55"
                    strokeWidth="1.5"
                    strokeDasharray="0.5 11"
                    strokeLinecap="round"
                  />
                </svg>
                <span className="absolute left-1/2 top-1/2 flex size-12 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full border border-line-strong bg-card font-mono text-[9px] uppercase tracking-[0.08em] text-inksoft">
                  bus
                </span>
              </div>

              <div className="p-7 transition-colors duration-150 hover:bg-card-hover">
                <FeltGrain />
                <div aria-hidden className="pointer-events-none absolute -right-12 -top-12 size-48 rounded-full bg-band-ink blur-3xl" />
                <div aria-hidden className="pointer-events-none absolute -bottom-16 left-6 size-36 rounded-full bg-band-ink/70 blur-3xl" />
                <div className="relative flex items-center justify-center py-4">
                  <DeskHead size={96} className="text-ink opacity-50" />
                </div>
                <div className="relative mt-3 flex items-center justify-center gap-1.5 text-[10.5px] text-inksoft">
                  <span aria-hidden className="h-1 w-1 rounded-full bg-inksoft/40" />
                  io bound
                </div>
                <div className="relative mt-5 flex justify-center">
                  <Nameplate name="engine" thread="text-ink/40" />
                </div>
                <div className="relative">
                  <SkillLog lines={COCO_SKILLS} />
                </div>
              </div>
            </div>

            <div className="relative flex flex-wrap items-center gap-x-3 gap-y-1 border-t border-line px-5 py-2.5 font-mono text-[9.5px] uppercase tracking-[0.1em] text-inksoft">
              <span>vision · text extractor</span>
              <span aria-hidden className="text-ink/30">·····</span>
              <span>engine · safety mapping</span>
              <span aria-hidden className="text-ink/30">·····</span>
              <span>shared bus · executed in parallel</span>
            </div>
          </div>
        </section>
      </Reveal>

      <Reveal>
        <section aria-label="the handoff" className="border-t border-line py-16">
          <div className="flex flex-wrap items-end justify-between gap-3">
            <h2 className="font-display text-[clamp(24px,3vw,34px)] font-semibold tracking-[-0.025em] text-ink">
              The extraction handoff.
            </h2>
            <span className="text-[12.5px] text-inksoft">one image, four beats — as the processor sees it</span>
          </div>
          <div className="card-lift mt-8 rounded-[4px] border border-line bg-card p-6">
            <div className="divide-y divide-line">
              {HANDOFF.map((l) => (
                <div key={l.tag} className="flex items-baseline gap-3 py-2.5 first:pt-0 last:pb-0">
                  <span className="w-16 shrink-0 font-mono text-[10.5px] uppercase tracking-[0.08em] text-ink/60">
                    [{l.tag}]
                  </span>
                  <span className={cn("font-mono text-[12px] leading-relaxed", l.loud ? "text-ink" : "text-inksoft")}>
                    {l.text}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </section>
      </Reveal>

      <Reveal>
        <section aria-label="how it stays fast" className="border-t border-line py-16">
          <h2 className="font-display text-[clamp(24px,3vw,34px)] font-semibold tracking-[-0.025em] text-ink">
            How it stays fast.
          </h2>
          <div className="mt-8 grid gap-px bg-line md:grid-cols-2">
            <Reveal delay={0} className="bg-paper">
              <div className="card-lift h-full rounded-[4px] p-5">
                <div className="flex items-baseline justify-between">
                  <span className="font-display text-[19px] font-semibold tracking-[-0.02em] text-ink">Local matching</span>
                  <span className="font-mono text-[11px] text-inksoft">01</span>
                </div>
                <p className="mt-2.5 text-[13.5px] leading-relaxed text-inksoft">
                  Every extracted string is cross-referenced locally against an in-memory 
                  bloom filter before making a database call. If the ingredient is universally 
                  safe (like Water/Aqua), it never hits the network.
                </p>
                <div className="mt-4 rounded-[4px] bg-ink/[0.05] px-2.5 py-1.5 font-mono text-[11.5px] text-ink">
                  checkBloomFilter("aqua") // true, skip network
                </div>
              </div>
            </Reveal>
            <Reveal delay={80} className="bg-paper">
              <div className="card-lift h-full rounded-[4px] p-5">
                <div className="flex items-baseline justify-between">
                  <span className="font-display text-[19px] font-semibold tracking-[-0.02em] text-ink">The LLM, on a leash</span>
                  <span className="font-mono text-[11px] text-inksoft">02</span>
                </div>
                <p className="mt-2.5 text-[13.5px] leading-relaxed text-inksoft">
                  Only heavily distorted or misspelled ingredients reach a large language model. 
                  95% of ingredients map directly via Levenshtein distance, keeping 
                  the pipeline cheap, deterministic, and instant.
                </p>
                <div className="mt-4 rounded-[4px] bg-ink/[0.05] px-2.5 py-1.5 font-mono text-[11.5px] text-ink">
                  matchINCI("pheenoxythnaol") // handled by fallback LLM
                </div>
              </div>
            </Reveal>
          </div>
        </section>
      </Reveal>

      <p className="pb-16 text-[13px] leading-relaxed text-inksoft">
        The scanner floats on every page — click the black head to begin extraction.
      </p>
    </div>
  );
}
