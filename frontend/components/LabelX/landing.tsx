"use client";

/**
 * landing.tsx — the overview: typography does the work. A huge
 * sentence-case claim, the golden path played live by the page, the
 * live ledger, the trust ladder, the transports, the proof layer.
 * One device — the hairline — and one accent. Captions and notes set
 * in the house sans (the mono voice is for machine strings).
 */
import { GhostButton, InkButton, Reveal } from "./bits";
import { HeroBot } from "./hero-bot";
import { HeroFabric } from "./hero-fabric";
import type { View } from "./shell";

export function Landing({ onEnter }: { onEnter: (view: View) => void }) {
  // Live stats and ledger have been removed since LabelX is now purely a cosmetic analyzer.

  return (
    <div>
      {/* ------------------------------ hero ------------------------------ */}
      <section aria-label="intro" className="pb-16 pt-6 sm:pt-10">
        <div className="grid items-center gap-10 lg:grid-cols-[minmax(0,1fr)_minmax(0,29rem)] lg:gap-6">
          <div>
            <p className="label-caps">AI-POWERED COSMETIC INGREDIENT ANALYZER</p>
            <h1 className="mt-6 max-w-[15ch] font-display text-[clamp(44px,7.4vw,92px)] font-semibold leading-[0.98] tracking-[-0.035em] text-ink">
              Understand your cosmetics.
              <br />
              <span className="text-inksoft">Instantly.</span>
            </h1>
            <p className="mt-7 max-w-[52ch] text-[17px] leading-relaxed text-inksoft">
              Label Analyzer is an AI-powered tool that helps you understand complex ingredient labels on skincare and cosmetic products. We extract text from product images using OCR and analyze every ingredient against our safety database to help you make safer and more informed decisions.
            </p>
            <div className="mt-9 flex flex-wrap items-center gap-3">
              <InkButton onClick={() => onEnter("upload")} ariaLabel="Analyze a label" arrow className="h-11 px-5 text-[14px]">
                Analyze a Label
              </InkButton>
            </div>
          </div>
          {/* the LabelX bot — the desk's little officer, stamping as it
              orbits. The wool mat is a separate backdrop layer: same
              viewBox, stacked behind, never drawn into the bot itself. */}
          <div className="relative mx-auto w-[min(80vw,340px)] lg:w-full">
            <HeroFabric className="absolute inset-0 h-full w-full" />
            <HeroBot className="relative w-full" />
          </div>
        </div>
      </section>

      {/* ------------------------------ the golden path, live (REMOVED) ------------------------------ */}
      <section aria-label="how it works" className="border-t border-line py-16">
        <h2 className="font-display text-[clamp(24px,3vw,34px)] font-semibold tracking-[-0.025em] text-ink">
          How the analyzer works.
        </h2>
        <div className="mt-8 grid gap-px bg-line md:grid-cols-3">
          {[
            {
              n: "01",
              t: "Extract Text",
              d: "Upload a picture of your cosmetic product label. Our OCR engine accurately extracts all complex ingredient names from the image.",
              code: "extract(image.ocr)",
            },
            {
              n: "02",
              t: "Analyze",
              d: "Each ingredient is matched against our comprehensive safety database, evaluating toxicity, allergens, and skin-type compatibility.",
              code: "analyze(ingredients)",
            },
            {
              n: "03",
              t: "Recommend",
              d: "A final safety score is generated, classifying ingredients as Safe, Caution, or High Risk, with personalized recommendations.",
              code: "recommend(profile)",
            },
          ].map((s, i) => (
            <Reveal key={s.n} delay={i * 80} className="bg-paper">
              <div className="card-lift h-full rounded-[4px] p-5">
                <div className="flex items-baseline justify-between">
                  <span className="font-display text-[19px] font-semibold tracking-[-0.02em] text-ink">{s.t}</span>
                  <span className="font-mono text-[11px] text-inksoft">{s.n}</span>
                </div>
                <p className="mt-2.5 text-[13px] leading-relaxed text-inksoft">{s.d}</p>
                <div className="mt-4 rounded-[4px] bg-ink/[0.05] px-2.5 py-1.5 font-mono text-[11.5px] text-ink">{s.code}</div>
              </div>
            </Reveal>
          ))}
        </div>
      </section>

      {/* ------------------------------ trust ladder ------------------------------ */}
      <section aria-label="safety classifications" className="border-t border-line py-16">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <h2 className="font-display text-[clamp(24px,3vw,34px)] font-semibold tracking-[-0.025em] text-ink">
            Ingredient Classifications.
          </h2>
          <span className="text-[12.5px] text-inksoft">backed by clinical safety databases</span>
        </div>
        <div className="mt-8 grid gap-px bg-line md:grid-cols-3">
          {[
            { id: "safe", label: "safe to use", title: "Safe", blurb: "Clinically proven to be safe for general use without known side effects." },
            { id: "caution", label: "use with care", title: "Caution", blurb: "May cause irritation for sensitive skin types or if used improperly." },
            { id: "high_risk", label: "avoid if possible", title: "High Risk", blurb: "Contains known allergens, endocrine disruptors, or high toxicity levels." },
          ].map((t, i) => {
            return (
              <Reveal key={t.id} delay={i * 80} className="bg-paper">
                <div className="card-lift h-full rounded-[4px] p-5">
                  <div className="label-caps">{t.label}</div>
                  <div className="tnum mt-2 font-display text-[30px] font-semibold tracking-[-0.03em] text-ink">
                    {t.title}
                  </div>
                  <p className="mt-2 text-[13px] leading-relaxed text-inksoft">{t.blurb}</p>
                </div>
              </Reveal>
            );
          })}
        </div>
      </section>



      {/* ------------------------------ built to be judged ------------------------------ */}
      <Reveal>
        <section className="rounded-[4px] border border-line bg-card px-6 py-8" aria-label="proof layer">
          <div className="flex flex-wrap items-baseline justify-between gap-2">
            <h2 className="font-display text-[clamp(24px,3vw,34px)] font-semibold tracking-[-0.025em] text-ink">
              Make informed skincare decisions.
            </h2>
            <span className="label-caps">the analyzer layer</span>
          </div>
          <div className="mt-6 flex flex-wrap gap-2">
            <GhostButton onClick={() => onEnter("analyze")}>try the analyzer</GhostButton>
            <GhostButton onClick={() => onEnter("why")} variant="ink">why it exists</GhostButton>
          </div>
        </section>
      </Reveal>
    </div>
  );
}

function Stat({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <div className="label-caps">{label}</div>
      <div className="mt-1.5">{children}</div>
    </div>
  );
}
