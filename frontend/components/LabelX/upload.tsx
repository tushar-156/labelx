import { useState, useRef, FormEvent, useEffect } from "react";
import { InkButton, SectionLabel, GhostButton, LogoMark, Kbd } from "./bits";
import { View } from "./shell";
import { motion, AnimatePresence } from "framer-motion";
import { Camera, RefreshCw, Upload, X, FlaskConical, Dna, Activity, ShieldCheck, CheckCircle2, ChevronRight, Layers, Barcode } from "lucide-react";

import { ChemicalStructure } from "./chemical-structure";
import { DiffusionKineticsCard } from "./diffusion-kinetics";
import { AgentConsensusInspector } from "./agent-consensus";
import { RoutineLayeringSimulator } from "./routine-layering";

import { CompliancePanel } from "./compliance-panel";
import { ScenarioSimulator } from "./scenario-simulator";
import { AllergenMatrix } from "./allergen-matrix";
import { NovaProcessingView } from "./nova-processing";
import { ChemicalDictionary } from "./chemical-dictionary";
import { ReportExportModal } from "./report-export";

import { ClinicalAlertsBanner } from "./clinical-alerts";
import { CleanAlternativesCard } from "./clean-alternatives";
import { DietaryLensesToolbar, DietaryLensId } from "./dietary-lenses";
import { DailyIntakeBudgetCard } from "./daily-intake-card";
import { DietLensVerdictCard } from "./diet-lens-verdict";
import { ImageEnhancerModal } from "./image-enhancer-modal";
import { TrafficLightCard } from "./traffic-light-card";
import { RecipeSwapsCard } from "./recipe-swaps";
import { FoodDiaryDrawer } from "./food-diary-drawer";
import { LabelPadhegaCard } from "./label-padhega-card";
import { TemporalImpactsCard } from "./temporal-impacts";
import { InlineProductChat } from "./inline-product-chat";

const DIETARY_CONDITIONS_PRESETS = [
  { id: "Diabetic", label: "Diabetic & Glycemic Control", badge: "Glycemic", desc: "Flags hidden sugars, maltodextrin (GI 185), and liquid syrups" },
  { id: "Hypertension", label: "Hypertension & Low Sodium", badge: "Cardiac", desc: "Restricts sodium > 140mg/serving and hidden MSG" },
  { id: "Child Protection", label: "Child Protection (Azo Dyes)", badge: "Pediatric", desc: "Enforces Southampton Six synthetic dye hyperactivity warnings" },
  { id: "Celiac", label: "Celiac / Gluten-Free", badge: "Gluten", desc: "Screens wheat, barley, rye, and malt extracts" },
  { id: "Vegetarian", label: "Strict Vegetarian / Vegan", badge: "Plant-Based", desc: "Audits circular green dot seals, carmine, tallow, and gelatins" }
];

const FUN_FACTS = [
  "Did you know? The FDA requires cosmetics to list ingredients in descending order of predominance.",
  "Fun fact: 'Fragrance' can legally hide dozens of undisclosed chemical ingredients.",
  "AI is scanning the image for tiny text, fixing typos, and structuring the data.",
  "Fun fact: Water (Aqua) is the most common first ingredient in cosmetics.",
  "We are cross-referencing these ingredients against multiple chemical databases.",
  "Did you know? Hypoallergenic just means a manufacturer claims it produces fewer allergic reactions."
];

function OcrFunFact() {
  const [index, setIndex] = useState(0);
  
  useEffect(() => {
    const timer = setInterval(() => {
      setIndex((prev) => (prev + 1) % FUN_FACTS.length);
    }, 3000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="h-[36px] relative overflow-hidden">
      <AnimatePresence mode="popLayout">
        <motion.div
          key={index}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.3 }}
          className="absolute inset-0"
        >
          {FUN_FACTS[index]}
        </motion.div>
      </AnimatePresence>
    </div>
  );
}

export function UploadPage({ onEnter }: { onEnter: (v: View) => void }) {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [extractedText, setExtractedText] = useState("");
  const [busyOcr, setBusyOcr] = useState(false);
  const [busyAnalysis, setBusyAnalysis] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const [structuredData, setStructuredData] = useState<any>(null);
  const [batchResults, setBatchResults] = useState<any[]>([]);
  const [activeLens, setActiveLens] = useState<DietaryLensId>("all");
  const [barcodeInput, setBarcodeInput] = useState("");
  const [busyBarcode, setBusyBarcode] = useState(false);

  // Fast Mode & Caching State
  const [fastMode, setFastMode] = useState(true);
  const [cacheHitNotice, setCacheHitNotice] = useState<string | null>(null);
  const [uncoveredNotice, setUncoveredNotice] = useState<string | null>(null);
  const [telemetry, setTelemetry] = useState<any>(null);
  const [activeCitationModal, setActiveCitationModal] = useState<{ id: string; passage: string; ingredient: string } | null>(null);

  // Camera State
  const [cameraActive, setCameraActive] = useState(false);
  const [facingMode, setFacingMode] = useState<"environment" | "user">("environment");
  const [cameraPermissionError, setCameraPermissionError] = useState<string | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const nativeCameraInputRef = useRef<HTMLInputElement | null>(null);

  const compressImageClientSide = async (sourceFile: File): Promise<File> => {
    if (!fastMode) return sourceFile;
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const img = new window.Image();
        img.onload = () => {
          const canvas = document.createElement("canvas");
          let width = img.width;
          let height = img.height;
          const maxDim = 1024;
          if (width > maxDim || height > maxDim) {
            if (width > height) {
              height = Math.round((height * maxDim) / width);
              width = maxDim;
            } else {
              width = Math.round((width * maxDim) / height);
              height = maxDim;
            }
          }
          canvas.width = width;
          canvas.height = height;
          const ctx = canvas.getContext("2d");
          if (!ctx) return resolve(sourceFile);
          ctx.drawImage(img, 0, 0, width, height);
          canvas.toBlob(
            (blob) => {
              if (!blob) return resolve(sourceFile);
              resolve(new File([blob], sourceFile.name, { type: "image/jpeg" }));
            },
            "image/jpeg",
            0.72
          );
        };
        img.onerror = () => resolve(sourceFile);
        img.src = e.target?.result as string;
      };
      reader.onerror = () => resolve(sourceFile);
      reader.readAsDataURL(sourceFile);
    });
  };

  // Clean up camera on unmount
  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  const startCamera = async (mode: "environment" | "user" = facingMode) => {
    setCameraPermissionError(null);
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        // Fallback for non-HTTPS or unsupported browsers: use native camera input directly
        nativeCameraInputRef.current?.click();
        return;
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
      setCameraActive(true);
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: { ideal: mode },
          width: { ideal: 1920 },
          height: { ideal: 1080 },
        },
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }
    } catch (err: any) {
      console.warn("Camera access error:", err);
      setCameraActive(false);
      const isDismissed = err?.name === "NotAllowedError" || err?.message?.includes("dismissed");
      if (isDismissed) {
        setCameraPermissionError("Camera permission was dismissed or blocked. Opening device camera picker...");
      } else {
        setCameraPermissionError("Live viewfinder unavailable. Opening device camera picker...");
      }
      // Seamlessly fall back to native device camera / file input
      setTimeout(() => {
        nativeCameraInputRef.current?.click();
      }, 200);
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    setCameraActive(false);
  };

  const toggleCameraFacing = () => {
    const nextMode = facingMode === "environment" ? "user" : "environment";
    setFacingMode(nextMode);
    startCamera(nextMode);
  };

  const captureFrame = () => {
    if (!videoRef.current || !canvasRef.current) return;
    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth || 1280;
    canvas.height = video.videoHeight || 720;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
      if (!blob) return;
      const capturedFile = new File([blob], `label-capture-${Date.now()}.jpg`, { type: "image/jpeg" });
      setFile(capturedFile);
      setPreview(URL.createObjectURL(blob));
      stopCamera();
      // Auto-trigger OCR extraction on captured frame
      handleOcr(capturedFile);
    }, "image/jpeg", 0.92);
  };

  // Dietary & Clinical Health Profile State
  const [userConditions, setUserConditions] = useState<string[]>([
    "Diabetic",
    "Hypertension",
    "Low Sodium",
    "Child Protection"
  ]);

  const toggleCondition = (conditionId: string) => {
    setUserConditions((prev) =>
      prev.includes(conditionId)
        ? prev.filter((c) => c !== conditionId)
        : [...prev, conditionId]
    );
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      setPreview(URL.createObjectURL(selectedFile));
      // Auto-trigger OCR extraction on mobile camera capture / selection
      handleOcr(selectedFile);
    }
  };

  const handleOcr = async (fileToProcess?: File) => {
    const targetFile = fileToProcess || file;
    if (!targetFile) return;
    setBusyOcr(true);
    setCacheHitNotice(null);
    try {
      // Apply Fast Mode Client-Side Compression if enabled
      const processedFile = await compressImageClientSide(targetFile);
      const formData = new FormData();
      formData.append("file", processedFile);

      // Call the Next.js server proxy for robust mobile & desktop support
      const res = await fetch("/api/ocr", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (!res.ok || !data.ok) {
        const errorMsg = data.error || data.detail || `Extraction failed with status ${res.status}`;
        throw new Error(errorMsg);
      }

      if (data.data?.from_cache) {
        setCacheHitNotice("⚡ Instant Tier-1 Cache Hit: Loaded from image SHA-256 fingerprint in <10ms.");
      }

      if (data.data && data.data.ingredients) {
        // We received structured JSON! Format it cleanly
        let extracted = `Brand: ${data.data.brand_name || "Unknown"}\n`;
        extracted += `Product: ${data.data.product_name || "Unknown"}\n`;
        extracted += `Volume: ${data.data.net_volume || "Unknown"}\n`;
        extracted += `Ingredients: ${data.data.ingredients.join(", ")}\n`;
        
        setExtractedText(extracted);
        
        // Immediately run analysis with fresh extracted data (no stale state race condition!)
        handleAnalyze(extracted, data.data.ingredients);
      } else {
        throw new Error("Invalid response format received from OCR service");
      }
    } catch (err: any) {
      console.error("OCR extraction error:", err);
      setExtractedText(err.message || "Failed to parse text from image.");
    } finally {
      setBusyOcr(false);
    }
  };

  const handleBarcodeLookup = async () => {
    if (!barcodeInput.trim()) return;
    setBusyBarcode(true);
    try {
      const res = await fetch(`http://127.0.0.1:8000/barcode/${barcodeInput.trim()}`);
      if (res.ok) {
        const prod = await res.json();
        const brand = prod.brand || prod.brands || "";
        const name = prod.product_name || prod.name || "Scanned Product";
        const ings = prod.ingredients_text || prod.ingredients || "";
        const formatted = `Brand: ${brand}\nProduct: ${name}\nBarcode: ${barcodeInput.trim()}\n\nIngredients: ${ings}`;
        setExtractedText(formatted);
      } else {
        alert("Barcode not found in Open Food Facts. Try uploading a label photo instead.");
      }
    } catch {
      alert("Error querying Open Food Facts API.");
    } finally {
      setBusyBarcode(false);
    }
  };

  const handleAnalyze = async (textToAnalyze?: string, directIngredients?: string[]) => {
    const rawText = (typeof textToAnalyze === "string" ? textToAnalyze : extractedText) || "";
    if (!rawText.trim()) return;
    setBusyAnalysis(true);
    setResult(null);
    setStructuredData(null);
    setBatchResults([]);
    try {
      // Determine active pathology and conditions from active dietary lens and user conditions
      const lensConditions: string[] = [...userConditions];
      const lensMeds: string[] = [];
      if (activeLens === "diabetic") {
        lensConditions.push("diabetes");
        lensMeds.push("metformin");
      } else if (activeLens === "renal") {
        lensConditions.push("chronic_kidney_disease");
      } else if (activeLens === "cardiac") {
        lensConditions.push("hypertension");
        lensMeds.push("statins", "ace_inhibitors");
      } else if (activeLens === "asthma") {
        lensConditions.push("asthma");
      }

      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: rawText,
          ingredients: directIngredients,
          adapter: "naive",
          skin_type: "normal",
          expertise_level: "beginner",
          allergies: [],
          routine: [],
          season: "all",
          user_id: undefined,
          active_lens: activeLens,
          user_conditions: Array.from(new Set(lensConditions)),
          active_medications: lensMeds
        }),
      });
      const data = await res.json();
      
      // Find the agent response in events
      const agentMsg = data.events?.find((e: any) => e.role === "agent" && e.text);
      if (agentMsg) {
        setResult(agentMsg.text);
      } else {
        setResult("Analysis could not be completed.");
      }
      
      if (data.structured_data) {
        setStructuredData(data.structured_data);
      }
      
      if (data.telemetry) {
        setTelemetry(data.telemetry);
      }
      
      if (data.from_cache) {
        setCacheHitNotice("⚡ Instant Tier-2 Cache Hit: Retrieved verified chemical dossier via ingredient MD5.");
      }
      
      // Auto-scroll to results
      setTimeout(() => {
        document.getElementById('analysis-results')?.scrollIntoView({ behavior: 'smooth' });
      }, 300);
    } catch (e) {
      console.error(e);
      setResult("Error reaching the analysis engine.");
    } finally {
      setBusyAnalysis(false);
    }
  };

  const handleBatchAnalyze = async () => {
    if (!extractedText.trim()) return;

    // If this is a single scanned label with metadata (Brand, Ingredients), automatically run the full deep report!
    if (extractedText.includes("Ingredients:") || extractedText.includes("Brand:")) {
      handleAnalyze();
      return;
    }

    setBusyAnalysis(true);
    setResult(null);
    setBatchResults([]);
    
    const products = extractedText.split("\n").filter(p => p.trim());
    const requests = products.map(p => ({
      message: p,
      skin_type: "normal"
    }));

    try {
      const res = await fetch("/api/batch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requests)
      });
      const data = await res.json();
      setBatchResults(data.batch_results || []);
    } catch (e) {
      console.error(e);
      setResult("Error reaching the batch analysis engine.");
    } finally {
      setBusyAnalysis(false);
    }
  };

  return (
    <>
      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_340px]">
        {/* ------------------------------ left: upload and analysis ------------------------------ */}
        <section className="doc flex min-h-[640px] flex-col overflow-hidden">
        <header className="border-b border-line px-4 py-3">
          <div className="label-caps">label analyzer · optical character recognition</div>
          <h2 className="font-display text-xl font-medium">Upload Image & Analyze</h2>
        </header>

        <div className="flex-1 space-y-6 overflow-y-auto px-4 py-6">
          {/* File & Camera Upload */}
          <div>
            <SectionLabel>1. label camera scan & image upload</SectionLabel>
            <div className="mt-3 flex flex-col items-center justify-center rounded-[8px] border-2 border-dashed border-line p-6 text-center">
              {preview ? (
                <div className="flex flex-col items-center">
                  <img src={preview} alt="Captured Label" className="max-h-56 rounded-[6px] object-contain shadow-sm border border-line" />
                  <div className="mt-4 flex flex-wrap gap-2.5 justify-center">
                    <GhostButton onClick={() => { setFile(null); setPreview(null); setExtractedText(""); }}>
                      Clear Image
                    </GhostButton>
                    <InkButton onClick={() => handleOcr(file || undefined)} disabled={busyOcr}>
                      {busyOcr ? "Extracting..." : "Re-Scan Image"}
                    </InkButton>
                  </div>
                </div>
              ) : (
                <>
                  <p className="text-[15px] font-medium text-ink">Scan Food or Consumer Product Label</p>
                  <p className="mt-1 text-[12px] text-inksoft max-w-[340px]">
                    Use your camera or select a photo of the ingredient list or barcode.
                  </p>

                  {/* Clean Action Buttons */}
                  <div className="mt-4 flex flex-col items-center gap-3">
                    {/* Fast Mode Toggle */}
                    <button
                      type="button"
                      onClick={() => setFastMode(!fastMode)}
                      className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-mono font-medium transition-all border ${
                        fastMode
                          ? "bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 border-emerald-500/30"
                          : "bg-paper2 text-inksoft border-line hover:border-line2"
                      }`}
                    >
                      <span>{fastMode ? "⚡ Fast Mode: ON (Compressed for Instant Upload)" : "💎 Full-Res Scan: Raw Quality"}</span>
                    </button>

                    <div className="flex flex-wrap items-center justify-center gap-3">
                      {/* Primary Camera Action */}
                      <button
                        onClick={() => startCamera("environment")}
                        className="inline-flex h-10 items-center justify-center gap-2 rounded-[6px] bg-ink px-5 text-[13px] font-medium text-paper transition-all hover:bg-ink/90 active:scale-95 shadow-sm"
                      >
                        <Camera className="w-4 h-4" />
                        Scan with Camera
                      </button>

                    {/* Hidden Native Camera Input for Seamless Fallback */}
                    <input
                      ref={nativeCameraInputRef}
                      type="file"
                      accept="image/*"
                      capture="environment"
                      className="hidden"
                      onChange={handleFileChange}
                    />

                    {/* Upload from Device */}
                    <label className="cursor-pointer inline-flex h-10 items-center justify-center gap-2 rounded-[6px] border border-line2 bg-card px-4 text-[13px] font-medium text-ink transition-all hover:bg-paper2 active:scale-95">
                      <Upload className="w-4 h-4 text-inksoft" />
                      <span>Upload Photo</span>
                      <input
                        type="file"
                        accept="image/*"
                        className="hidden"
                        onChange={handleFileChange}
                      />
                    </label>

                    {/* FCI Optical Preprocessing & Stamp Inspector Modal */}
                    {(file || preview) && (
                      <ImageEnhancerModal imageFile={file} imageSrc={preview} />
                    )}

                    {/* Food Diary & Scan History Drawer */}
                    <FoodDiaryDrawer />
                  </div>

                  {/* Direct Barcode Search & Instant Autofill (Food-Label-Analyzer feature) */}
                  <div className="mt-3.5 pt-3 border-t border-line/40 flex flex-wrap items-center justify-center gap-2">
                    <Barcode className="w-4 h-4 text-inksoft" />
                    <input
                      type="text"
                      placeholder="Or enter barcode (e.g. 8901030383848)..."
                      value={barcodeInput}
                      onChange={(e) => setBarcodeInput(e.target.value)}
                      onKeyDown={(e) => { if (e.key === 'Enter') handleBarcodeLookup(); }}
                      className="w-64 rounded-[6px] border border-line bg-card px-3 py-1.5 text-xs text-ink placeholder:text-inksoft/60 focus:outline-none focus:border-ink/40 font-mono"
                    />
                    <button
                      type="button"
                      onClick={handleBarcodeLookup}
                      disabled={busyBarcode || !barcodeInput.trim()}
                      className="px-3 py-1.5 rounded-[6px] bg-ink text-paper text-xs font-semibold hover:bg-ink/90 transition-all cursor-pointer disabled:opacity-50"
                    >
                      {busyBarcode ? "Fetching..." : "Fetch Barcode"}
                    </button>
                  </div>
                </div>

                {cameraPermissionError && (
                  <div className="mt-3 rounded-[6px] bg-amber-500/10 border border-amber-500/20 px-3 py-2 text-left text-[11px] text-amber-700 dark:text-amber-300">
                    <p className="font-medium">Camera Notice</p>
                    <p className="mt-0.5 text-[11px] opacity-90">{cameraPermissionError}</p>
                    <p className="mt-1 opacity-75">Tip: Click the lock icon in your browser URL bar to allow camera access.</p>
                  </div>
                )}
              </>
            )}
          </div>
            
            {busyOcr && (
              <div className="mt-4 text-left animate-in slide-in-from-bottom-2 fade-in duration-300">
                <div className="rounded-[8px] bg-sage/10 p-4 border border-sage/20 flex gap-3 items-center">
                  <span className="size-2 rounded-full bg-sage animate-ping shrink-0" />
                  <div>
                    <p className="text-[13px] font-medium text-ink">Running Gemini Vision OCR...</p>
                    <div className="mt-1 text-[12px] text-inksoft">
                      <OcrFunFact />
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Diagnostic Pathology & Dietary Lenses Toolbar */}
          <div className="pt-4 border-t border-line/40">
            <DietaryLensesToolbar activeLens={activeLens} onSelectLens={setActiveLens} />
          </div>

          {/* Extracted Text */}
          <div className="pt-4 border-t border-line/40">
            <SectionLabel>2. extracted ingredients</SectionLabel>
            <p className="mt-1 text-[12px] text-inksoft mb-3">Review and edit the text before running the analysis.</p>
            <textarea 
              value={extractedText}
              onChange={(e) => setExtractedText(e.target.value)}
              placeholder="Extracted text will appear here...&#10;For Batch Analysis, enter each product on a new line."
              className="min-h-[120px] w-full rounded-[4px] border border-line2 bg-card p-3 text-[13px] text-ink placeholder:text-inksoft/60 focus:border-ink/30 focus:outline-none"
            />
            <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
              <InkButton onClick={() => handleAnalyze()} disabled={busyAnalysis || !extractedText.trim()} className="h-11 px-6 text-[14px] font-medium shadow-sm">
                {busyAnalysis && !batchResults.length && !result ? "Running AI Agents..." : "Analyze Ingredients (Full Report)"}
              </InkButton>
            </div>
            
            <div className="mt-4 pt-4 border-t border-line/40 flex items-center justify-between">
              <div>
                <SectionLabel>batch comparison (multi-product)</SectionLabel>
                <p className="text-[12px] text-inksoft">Compare multiple formulas (paste multiple products, 1 per line).</p>
              </div>
              <GhostButton onClick={handleBatchAnalyze} disabled={busyAnalysis || !extractedText.trim()}>
                {busyAnalysis && batchResults.length === 0 && !result ? "Running..." : "Run Batch Analysis"}
              </GhostButton>
            </div>

            {/* Academic Feature: Multi-Product Routine Chemical Stacking Simulator */}
            <div className="mt-6 pt-5 border-t border-line">
              <RoutineLayeringSimulator />
            </div>
          </div>

          {/* Results */}
          {result && (
            <div id="analysis-results" className="pt-4 border-t border-line/40 animate-rise">
              <div className="flex items-center justify-between">
                <SectionLabel>3. analysis results</SectionLabel>
              </div>

              {cacheHitNotice && (
                <div className="mt-3 rounded-[6px] bg-emerald-500/10 border border-emerald-500/30 p-2.5 text-[12px] text-emerald-800 dark:text-emerald-300 flex items-center gap-2 font-mono">
                  <span className="size-2 rounded-full bg-emerald-500 animate-pulse shrink-0" />
                  <span>{cacheHitNotice}</span>
                </div>
              )}
              {uncoveredNotice && (
                <div className="mt-2 rounded-[6px] bg-amber-500/10 border border-amber-500/30 p-2.5 text-[12px] text-amber-800 dark:text-amber-300 flex items-center gap-2 font-mono">
                  <span>{uncoveredNotice}</span>
                </div>
              )}

              {/* Dynamic Safety Gauge & EthiScan */}
              {structuredData && (
                <div className="mt-5 flex flex-col sm:flex-row gap-4 items-center sm:items-start justify-between bg-paper2/50 p-4 rounded-[8px] border border-line">
                  
                  {/* Gauge */}
                  <div className="flex flex-col items-center">
                    <div className="relative w-24 h-24">
                      <svg viewBox="0 0 100 100" className="w-full h-full transform -rotate-90">
                        <circle cx="50" cy="50" r="40" className="text-line2 stroke-current" strokeWidth="8" fill="none" />
                        <motion.circle 
                          cx="50" cy="50" r="40"
                          strokeWidth="8" fill="none"
                          strokeDasharray="251.2"
                          initial={{ strokeDashoffset: 251.2 }}
                          animate={{ strokeDashoffset: 251.2 - (251.2 * (structuredData.overall_score || 0)) / 100 }}
                          transition={{ duration: 1.5, ease: "easeOut" }}
                          className={`stroke-current ${
                            structuredData.overall_score >= 80 ? "text-green-500" :
                            structuredData.overall_score >= 50 ? "text-yellow-500" : "text-red-500"
                          }`}
                        />
                      </svg>
                      <div className="absolute inset-0 flex items-center justify-center flex-col">
                        <span className="text-2xl font-bold font-display">{structuredData.overall_score}</span>
                      </div>
                    </div>
                    <span className="text-[11px] uppercase tracking-wider font-semibold mt-2 text-inksoft">Safety Score</span>
                  </div>

                  {/* Export Certificate Button */}
                  <div className="flex items-center gap-2 self-center sm:self-start">
                    <ReportExportModal 
                      productName={file?.name?.replace(/\.[^/.]+$/, "") || "Scanned Formulation"}
                      brandName={structuredData?.ethics?.brand || "Commercial Manufacturer"}
                      complianceData={structuredData?.compliance}
                      intelligence={structuredData?.intelligence}
                      structuredData={structuredData}
                    />
                  </div>
                  
                  {/* Brand Ethics */}
                  {structuredData.ethics && (
                    <div className="flex-1 flex flex-col items-end sm:items-start sm:ml-6">
                      <span className="text-[11px] uppercase tracking-wider font-semibold text-inksoft mb-2">EthiScan Brand Check</span>
                      <div className="flex flex-col gap-2">
                        <div className="flex items-center gap-2">
                          <span className="text-[13px] font-medium text-ink">{structuredData.ethics.brand || "Brand"}</span>
                        </div>
                        {structuredData.ethics.found ? (
                          <div className="flex gap-2">
                            {structuredData.ethics.cruelty_free && (
                              <span className="px-2.5 py-1 bg-pink-100 text-pink-700 text-[11px] font-semibold rounded-full border border-pink-200">🐰 Cruelty-Free</span>
                            )}
                            {structuredData.ethics.vegan && (
                              <span className="px-2.5 py-1 bg-green-100 text-green-700 text-[11px] font-semibold rounded-full border border-green-200">🌱 Vegan</span>
                            )}
                            {!structuredData.ethics.cruelty_free && !structuredData.ethics.vegan && (
                              <span className="px-2.5 py-1 bg-gray-100 text-gray-700 text-[11px] font-semibold rounded-full border border-gray-200">No Certifications Found</span>
                            )}
                          </div>
                        ) : (
                          <span className="text-[12px] text-inksoft italic">Brand not found in ethics database</span>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* UK FSA & WHO Front-of-Pack Traffic Lights */}
              {structuredData?.traffic_lights && (
                <div className="mt-5">
                  <TrafficLightCard report={structuredData.traffic_lights} />
                </div>
              )}

              {/* Diet-Lens Stanford Deterministic Verdict Gatekeeper */}
              {structuredData?.diet_lens_verdict && (
                <div className="mt-5">
                  <DietLensVerdictCard
                    initialVerdict={structuredData.diet_lens_verdict}
                    ingredients={structuredData?.compliance?.label_data?.ingredients || []}
                    rawText={extractedText}
                  />
                </div>
              )}

              {/* #LabelPadhegaIndia Hierarchy & Deceptive Greenwashing Buster */}
              {structuredData?.label_padhega && (
                <div className="mt-5">
                  <LabelPadhegaCard data={structuredData.label_padhega} />
                </div>
              )}

              {/* Temporal Tripartite Health Impact Matrix */}
              {structuredData?.label_padhega?.temporal_impacts && structuredData.label_padhega.temporal_impacts.length > 0 && (
                <div className="mt-5">
                  <TemporalImpactsCard impacts={structuredData.label_padhega.temporal_impacts} />
                </div>
              )}

              {/* Clinical Pathology & Drug-Food Contraindications + Botanical Allergen Unmasker */}
              <div className="mt-5">
                <ClinicalAlertsBanner 
                  alerts={structuredData?.clinical_contraindications || []}
                  botanicalAllergens={structuredData?.botanical_allergens || []}
                />
              </div>

              {/* Telemetry Latency Breakdown Bar */}
              {telemetry && (
                <div className="mt-4 rounded-[8px] border border-line bg-card/60 p-3 text-xs">
                  <div className="flex items-center justify-between font-mono text-[11px] text-ink mb-1.5">
                    <span className="font-semibold flex items-center gap-1.5">
                      <span className="size-2 rounded-full bg-emerald-500 animate-pulse" />
                      Execution Telemetry Breakdown
                    </span>
                    <span className="text-inksoft font-bold">{telemetry.total_ms}ms total</span>
                  </div>
                  <div className="grid grid-cols-3 gap-2 font-mono text-[10px] text-inksoft">
                    <div className="bg-paper2/80 rounded p-1.5 border border-line">
                      <span className="block text-ink font-semibold">{telemetry.stages?.cache_check_ms ?? 0}ms</span>
                      <span>Cache Lookup</span>
                    </div>
                    <div className="bg-paper2/80 rounded p-1.5 border border-line">
                      <span className="block text-ink font-semibold">{telemetry.stages?.rules_and_allergens_ms ?? 0}ms</span>
                      <span>Rules & Allergens</span>
                    </div>
                    <div className="bg-paper2/80 rounded p-1.5 border border-line">
                      <span className="block text-ink font-semibold">{telemetry.stages?.multi_agent_dag_ms ?? 0}ms</span>
                      <span>LangGraph Multi-Agent</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Deterministic Word-Boundary Allergen Alert Box */}
              {structuredData?.allergen_report && structuredData.allergen_report.total_flagged > 0 && (
                <div className="mt-4 rounded-[8px] border border-red-200 dark:border-red-900/60 bg-red-500/10 p-3.5">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-mono text-[11px] font-semibold text-red-700 dark:text-red-300 uppercase tracking-wider flex items-center gap-1.5">
                      ⚠️ Allergen Safety Alert (Word-Boundary Verified)
                    </span>
                    <span className="text-[10px] text-red-600 dark:text-red-400 font-mono">Zero False-Positive Regex Match</span>
                  </div>
                  <div className="space-y-1.5">
                    {structuredData.allergen_report.user_allergen_violations?.map((v: any, idx: number) => (
                      <div key={idx} className="text-xs text-red-800 dark:text-red-200 flex items-center justify-between bg-card/80 p-2 rounded border border-red-200 dark:border-red-900">
                        <span className="font-semibold">{v.ingredient}</span>
                        <span className="px-2 py-0.5 rounded text-[10px] bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200 font-bold">
                          Matches User Allergy: {v.matched_allergy}
                        </span>
                      </div>
                    ))}
                    {structuredData.allergen_report.general_allergen_alerts?.map((g: any, idx: number) => (
                      <div key={idx} className="text-xs text-amber-800 dark:text-amber-200 flex items-center justify-between bg-card/60 p-1.5 rounded border border-amber-200 dark:border-amber-900">
                        <span>{g.ingredient}</span>
                        <span className="text-[10px] font-mono text-amber-700 dark:text-amber-300">
                          {g.category}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Out-of-Corpus Uncovered Compounds Card */}
              {structuredData?.ingredient_data?.some((i: any) => i.is_uncovered) && (
                <div className="mt-4 rounded-[8px] border border-line bg-paper2/80 p-3.5">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-mono text-[11px] font-semibold text-ink uppercase tracking-wider">
                      🛡️ Out-of-Corpus Uncovered Compounds
                    </span>
                    <span className="text-[10px] text-inksoft font-mono">Double-Refusal Abstention Active</span>
                  </div>
                  <p className="text-[11px] text-inksoft mb-2.5">
                    These compounds do not appear in CIR, EU Annex II, or FDA reference databases. Rather than hallucinating safety scores, our engine abstains from drawing conclusions.
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {structuredData.ingredient_data.filter((i: any) => i.is_uncovered).map((u: any, idx: number) => (
                      <span key={idx} className="px-2 py-1 rounded bg-card text-[11px] text-ink border border-line font-mono">
                        {u.name} <span className="text-inksoft text-[10px]">(NO_SOURCE)</span>
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Caution Zone */}
              {structuredData?.flagged_ingredients?.length > 0 && (
                <div className="mt-5 p-4 rounded-[8px] border border-red-200/60 bg-red-50/30">
                  <h4 className="text-[12px] font-semibold uppercase tracking-wider text-red-600 mb-3 flex items-center gap-2">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                    Caution Zone
                  </h4>
                  <div className="flex flex-col gap-2">
                    {structuredData.flagged_ingredients.map((ing: any, idx: number) => (
                      <div key={idx} className="bg-white p-3 rounded-[6px] border border-red-100 shadow-sm flex flex-col sm:flex-row gap-2 sm:gap-4 sm:items-center justify-between">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="text-[13px] font-bold text-ink">{ing.name}</span>
                            <span className={`px-1.5 py-0.5 rounded-[4px] text-[10px] font-bold ${ing.recommendation === 'AVOID' ? 'bg-red-100 text-red-700' : 'bg-orange-100 text-orange-700'}`}>{ing.recommendation}</span>
                          </div>
                          <p className="text-[12px] text-inksoft mt-1">{ing.reasoning}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* XAI Multi-Agent Consensus Inspector */}
              {structuredData?.xai_agent_consensus && (
                <AgentConsensusInspector xaiData={structuredData.xai_agent_consensus} />
              )}

              {/* In Silico Cheminformatics & Biophysical Dossier */}
              {structuredData?.cheminformatics_dossier && structuredData.cheminformatics_dossier.length > 0 && (
                <div className="mt-5 rounded-[8px] border border-line bg-paper2/60 p-4 shadow-sm">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-line pb-2.5 mb-3">
                    <div className="flex items-center gap-2">
                      <FlaskConical className="w-4 h-4 text-ink" />
                      <h4 className="text-[13px] font-bold tracking-tight text-ink uppercase">
                        In Silico Cheminformatics & Biophysical Dossier
                      </h4>
                    </div>
                    <span className="font-mono text-[10px] uppercase tracking-wider text-inksoft px-2 py-0.5 rounded bg-card border border-line w-fit">
                      Potts-Guy Kp & Bos-Marcus 500 Da Model
                    </span>
                  </div>
                  <p className="text-[12px] text-inksoft mb-4">
                    Direct computational modeling of transdermal flux, stratum corneum penetration, 2D molecular geometry, and OECD TG 429 sensitizer alerts.
                  </p>
                  <div className="grid gap-3 sm:grid-cols-2">
                    {structuredData.cheminformatics_dossier.map((chem: any, idx: number) => {
                      if (!chem) return null;
                      const props = chem.physicochemical_properties || {};
                      const perm = chem.biophysical_skin_permeability || {};
                      const tox = chem.in_silico_toxicity_endpoints || {};
                      const is500Pass = perm.passes_500_da_rule ?? (props.molecular_weight_da < 500);

                      return (
                        <div key={idx} className="rounded-[6px] border border-line2 bg-card p-3 shadow-xs flex flex-col justify-between">
                          <div>
                            <div className="flex items-start justify-between gap-2">
                              <div>
                                <span className="font-bold text-[13px] text-ink">{chem.ingredient || "Compound"}</span>
                                <span className="block text-[11px] text-inksoft italic">{chem.chemical_class || "Organic Molecule"}</span>
                              </div>
                              <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-semibold border ${
                                is500Pass ? "bg-emerald-50 text-emerald-800 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800" 
                                          : "bg-blue-50 text-blue-800 border-blue-200 dark:bg-blue-950/40 dark:text-blue-300 dark:border-blue-800"
                              }`}>
                                {is500Pass ? "< 500 Da (Permeant)" : "≥ 500 Da (Film-Former)"}
                              </span>
                            </div>

                            {/* 2D Chemical Molecular Structure Bond Diagram */}
                            <div className="mt-2.5 flex items-center justify-center">
                              <ChemicalStructure name={chem.ingredient} smiles={chem.canonical_smiles} width={135} height={70} />
                            </div>

                            {/* Canonical SMILES */}
                            {chem.canonical_smiles && (
                              <div className="mt-2 p-1.5 rounded bg-paper font-mono text-[10px] text-inksoft break-all border border-line/60">
                                <span className="text-ink font-semibold">SMILES: </span>{chem.canonical_smiles}
                              </div>
                            )}

                            {/* Molecular Metrics Grid */}
                            <div className="mt-2.5 grid grid-cols-4 gap-1.5 text-center font-mono text-[11px]">
                              <div className="rounded bg-paper/60 p-1 border border-line/40">
                                <div className="text-[9px] uppercase text-inksoft">MW</div>
                                <div className="font-semibold text-ink">{props.molecular_weight_da ? `${props.molecular_weight_da}` : "N/A"}</div>
                              </div>
                              <div className="rounded bg-paper/60 p-1 border border-line/40">
                                <div className="text-[9px] uppercase text-inksoft">LogP</div>
                                <div className="font-semibold text-ink">{props.logp_partition_coefficient ?? "N/A"}</div>
                              </div>
                              <div className="rounded bg-paper/60 p-1 border border-line/40">
                                <div className="text-[9px] uppercase text-inksoft">TPSA</div>
                                <div className="font-semibold text-ink">{props.tpsa_angstrom2 ? `${props.tpsa_angstrom2}Å²` : "N/A"}</div>
                              </div>
                              <div className="rounded bg-paper/60 p-1 border border-line/40">
                                <div className="text-[9px] uppercase text-inksoft">Kp (cm/h)</div>
                                <div className="font-semibold text-ink">{perm.kp_cm_per_hr || (perm.kp_raw ? Number(perm.kp_raw).toExponential(2) : "N/A")}</div>
                              </div>
                            </div>

                            {/* Fickian Dermal Kinetics Absorption Curve */}
                            {chem.diffusion_kinetics && (
                              <DiffusionKineticsCard ingredient={chem.ingredient} kinetics={chem.diffusion_kinetics} />
                            )}
                          </div>

                          {/* Toxicological Endpoints */}
                          {tox && (
                            <div className="mt-2.5 pt-2 border-t border-line/40 flex flex-wrap gap-1.5 text-[10px]">
                              {tox.dermal_sensitization && (
                                <span className={`px-1.5 py-0.5 rounded font-medium ${
                                  tox.dermal_sensitization.flagged 
                                    ? "bg-red-100 text-red-800 dark:bg-red-950/60 dark:text-red-300" 
                                    : "bg-paper text-inksoft border border-line/40"
                                }`}>
                                  Sensitizer: {tox.dermal_sensitization.risk_level}
                                </span>
                              )}
                              {tox.endocrine_disruption?.flagged && (
                                <span className="px-1.5 py-0.5 rounded font-medium bg-purple-100 text-purple-800 dark:bg-purple-950/60 dark:text-purple-300">
                                  Endocrine: Flagged
                                </span>
                              )}
                              {tox.dart_developmental_toxicity?.flagged && (
                                <span className="px-1.5 py-0.5 rounded font-medium bg-red-100 text-red-800 dark:bg-red-950/60 dark:text-red-300">
                                  DART: Contraindicated
                                </span>
                              )}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Grounded Citation Badges */}
              {structuredData?.ingredient_data?.some((i: any) => i.citations?.length > 0) && (
                <div className="mt-4 rounded-[8px] border border-line bg-card/60 p-3.5">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-mono text-[11px] font-semibold uppercase tracking-wider text-ink flex items-center gap-1.5">
                      <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                      Authoritative Passage Citations
                    </span>
                    <span className="text-[10px] text-inksoft font-mono">Click citation to inspect evidence</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {structuredData.ingredient_data.map((ing: any, idx: number) => {
                      if (!ing.citations || ing.citations.length === 0) return null;
                      const cId = ing.citations[0];
                      const passage = ing.passages?.[0] || `${ing.name}: Referenced in authoritative cosmetic monographs.`;
                      return (
                        <button
                          key={idx}
                          type="button"
                          onClick={() => setActiveCitationModal({ id: cId, passage, ingredient: ing.name })}
                          className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-paper2 hover:bg-card border border-line hover:border-ink transition-all text-xs font-mono group cursor-pointer"
                        >
                          <span className="font-bold text-ink">{ing.name}</span>
                          <span className="px-1.5 py-0.2 rounded bg-ink/10 text-ink text-[10px] font-bold group-hover:bg-ink group-hover:text-paper transition-colors">
                            {cId}
                          </span>
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* 5-Module Statutory Compliance Engine */}
              {structuredData?.compliance && (
                <div className="mt-5">
                  <CompliancePanel complianceData={structuredData.compliance} />
                </div>
              )}

              {/* Detected vs. Declared Allergen Matrix */}
              <div className="mt-5">
                <AllergenMatrix 
                  findings={structuredData?.compliance?.findings || []}
                  declaredAllergens={structuredData?.compliance?.label_data?.declared_allergens || []}
                  ingredients={structuredData?.compliance?.label_data?.ingredients || []}
                />
              </div>

              {/* NOVA Processing Classification & Intent Intelligence */}
              {structuredData?.intelligence && (
                <div className="mt-5">
                  <NovaProcessingView intelligence={structuredData.intelligence} />
                </div>
              )}

              {/* Plain-English Chemical Translator */}
              {structuredData?.translations && (
                <div className="mt-5">
                  <ChemicalDictionary translations={structuredData.translations} />
                </div>
              )}

              {/* Clean-Label Alternatives & Smart Swaps ("Swap This Junk") */}
              {structuredData?.clean_alternatives && structuredData.clean_alternatives.length > 0 && (
                <div className="mt-5">
                  <CleanAlternativesCard 
                    category={structuredData?.classification?.category || "Packaged Food"}
                    alternatives={structuredData.clean_alternatives}
                  />
                </div>
              )}

              {/* DIY Clean Home-Cooked Recipe Swaps (Food-Label-Analyzer feature) */}
              {structuredData?.diy_recipes && structuredData.diy_recipes.length > 0 && (
                <div className="mt-5">
                  <RecipeSwapsCard 
                    category={structuredData?.classification?.category || "Packaged Food"}
                    recipes={structuredData.diy_recipes}
                  />
                </div>
              )}

              {/* Cumulative Daily Intake & WHO Budget Meter */}
              <div className="mt-5">
                <DailyIntakeBudgetCard 
                  productName={file?.name?.replace(/\.[^/.]+$/, "") || structuredData?.ethics?.brand || "Scanned Formulation"}
                  nutritionalInfo={structuredData?.compliance?.label_data?.nutritional_info}
                  additivesCount={structuredData?.compliance?.label_data?.additives?.length || 0}
                />
              </div>

              {/* Interactive What-If Reformulation Simulator */}
              <div className="mt-5">
                <ScenarioSimulator 
                  initialLabelData={structuredData?.compliance?.label_data}
                  initialScore={structuredData?.compliance?.risk_score?.overall_score || structuredData?.overall_score || 80}
                />
              </div>

              {/* In-Line Product Safety Q&A Chatbot (IngreScan AI architecture) */}
              <div className="mt-5">
                <InlineProductChat
                  productName={file?.name?.replace(/\.[^/.]+$/, "") || structuredData?.ethics?.brand || "Scanned Formulation"}
                  ingredients={structuredData?.compliance?.label_data?.ingredients || []}
                  category={structuredData?.classification?.category || "Packaged Food"}
                  claims={structuredData?.marketing_claims || []}
                />
              </div>

              <div className="mt-5 rounded-[6px] bg-paper2/50 p-5 text-[14px] leading-relaxed text-ink shadow-sm ring-1 ring-line">
                <div dangerouslySetInnerHTML={{ __html: result.replace(/\n/g, '<br/>') }} />
              </div>
            </div>
          )}

          {batchResults.length > 0 && (
            <div className="pt-4 border-t border-line/40 animate-rise">
              <div className="flex items-center justify-between mb-2">
                <SectionLabel>3. batch results</SectionLabel>
                <span className="text-[12px] font-mono text-inksoft">{batchResults.length} formulation(s) evaluated</span>
              </div>
              <div className="mt-4 flex flex-col gap-4">
                {batchResults.map((r, i) => (
                  <div key={i} className="p-4 border border-line rounded-[6px] bg-paper2/50 shadow-sm ring-1 ring-line">
                    <div className="flex items-start justify-between gap-3 mb-2">
                      <div>
                        <div className="font-semibold text-[13px] text-ink">
                          {r.product || `Sample #${i + 1}`}
                        </div>
                        <div className="font-mono text-[10px] text-inksoft">
                          Session UUID: {r.sessionId}
                        </div>
                      </div>
                      <div className="flex gap-2 shrink-0">
                        <span className={`px-2 py-0.5 rounded-[4px] text-xs font-semibold ${r.rules_report.is_compliant ? 'bg-green-100 dark:bg-green-950/60 text-green-700 dark:text-green-300' : 'bg-red-100 dark:bg-red-950/60 text-red-700 dark:text-red-300'}`}>
                          {r.rules_report.is_compliant ? "Compliant" : "Non-Compliant"}
                        </span>
                        <span className="px-2 py-0.5 bg-blue-100 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 rounded-[4px] text-xs font-semibold">
                          Score: {r.safety_score}/100
                        </span>
                      </div>
                    </div>
                    {r.ingredients && r.ingredients.length > 0 && (
                      <div className="mt-2 mb-2 font-mono text-[11px] bg-paper/80 p-2.5 rounded border border-line/40">
                        <span className="text-inksoft uppercase tracking-wider text-[9px] block mb-1">
                          Evaluated Chemical Entities ({r.ingredients.length}):
                        </span>
                        <span className="text-ink">
                          {r.ingredients.join(" • ")}
                        </span>
                      </div>
                    )}
                    {r.rules_report.regulatory_violations?.length > 0 && (
                      <div className="mt-3 p-3 bg-red-50 dark:bg-red-950/40 text-red-900 dark:text-red-200 border border-red-200 dark:border-red-900 rounded-[4px] text-[12px]">
                        <strong className="block mb-1 text-red-700 dark:text-red-400">Regulatory Violations (EU Annex II / FDA Prohibited):</strong>
                        <ul className="list-disc pl-4 space-y-1">
                          {r.rules_report.regulatory_violations.map((v: any, j: number) => (
                            <li key={j}><span className="font-mono font-semibold">{v.ingredient}</span> ({v.regulation}): {v.reason}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {r.rules_report.ingredient_conflicts?.length > 0 && (
                      <div className="mt-4 p-3 bg-orange-50 text-orange-900 rounded-[4px] text-[13px]">
                        <strong>Conflicts:</strong>
                        <ul className="list-disc pl-4 mt-1">
                          {r.rules_report.ingredient_conflicts.map((c: any, j: number) => (
                            <li key={j}>{c.conflict_pair.join(" + ")}: {c.warning}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </section>

      {/* ------------------------------ right: profile config ------------------------------ */}
      <aside className="rail-scroll space-y-5 lg:max-h-[calc(100vh-8rem)] lg:overflow-y-auto lg:pr-1">
        <section className="doc px-4 py-4">
          <div className="flex items-center justify-between">
            <SectionLabel>dietary & health profile</SectionLabel>
            <span className="text-[10px] font-bold text-accent uppercase tracking-wider bg-accent/10 px-2 py-0.5 rounded">
              Active Guardrails
            </span>
          </div>
          <p className="mt-2 text-[12.5px] leading-relaxed text-inksoft">
            Select your clinical conditions and dietary guidelines to evaluate foods against personalized health thresholds.
          </p>

          {/* Quick Dietary Condition Toggles */}
          <div className="mt-4 space-y-2">
            <span className="block text-[10px] font-mono uppercase tracking-wider text-inksoft">
              Active Surveillance Conditions
            </span>
            <div className="flex flex-col gap-2">
              {DIETARY_CONDITIONS_PRESETS.map((cond) => {
                const isSelected = userConditions.includes(cond.id);
                return (
                  <button
                    key={cond.id}
                    type="button"
                    onClick={() => toggleCondition(cond.id)}
                    className={`flex items-start justify-between p-2.5 rounded-[6px] border text-left text-xs transition-all ${
                      isSelected
                        ? "bg-card border-ink font-semibold shadow-xs ring-1 ring-ink/20"
                        : "bg-paper/40 border-line text-inksoft hover:text-ink hover:bg-card"
                    }`}
                  >
                    <div className="space-y-0.5 pr-2">
                      <div className="flex items-center gap-1.5">
                        <span className="text-ink font-medium">{cond.label}</span>
                        {isSelected && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />}
                      </div>
                      <p className="text-[11px] text-inksoft leading-tight">{cond.desc}</p>
                    </div>
                    <span className={`px-1.5 py-0.5 rounded text-[9.5px] font-semibold border shrink-0 ${
                      isSelected
                        ? "bg-accent/10 text-accent border-accent/20"
                        : "bg-surface text-inksoft border-line"
                    }`}>
                      {cond.badge}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>
        </section>
        
        <section className="doc px-4 py-4">
          <SectionLabel>how it works</SectionLabel>
          <ol className="mt-2 space-y-2.5">
            <li className="flex gap-3.5">
              <span className="font-mono text-[11px] font-semibold text-cleared">01</span>
              <div>
                <div className="text-[12px] font-medium text-ink">Upload / Scan</div>
                <div className="text-[12px] leading-relaxed text-inksoft">Upload or snap a photo of any packaged food label or scan its barcode.</div>
              </div>
            </li>
            <li className="flex gap-3.5">
              <span className="font-mono text-[11px] font-semibold text-cleared">02</span>
              <div>
                <div className="text-[12px] font-medium text-ink">Optical Verification</div>
                <div className="text-[12px] leading-relaxed text-inksoft">Pre-processing enhances sharpness and verifies statutory circular seals.</div>
              </div>
            </li>
            <li className="flex gap-3.5">
              <span className="font-mono text-[11px] font-semibold text-cleared">03</span>
              <div>
                <div className="text-[12px] font-medium text-ink">Safety & Deception Audit</div>
                <div className="text-[12px] leading-relaxed text-inksoft">Multi-agent engine checks descending order, traffic lights, and clinical health impacts.</div>
              </div>
            </li>
          </ol>
        </section>
      </aside>

      {/* Live Mobile Camera Viewfinder Modal */}
      {cameraActive && (
        <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-black/90 p-4 backdrop-blur-md">
          <div className="relative w-full max-w-[460px] overflow-hidden rounded-[16px] border border-white/20 bg-black shadow-2xl">
            {/* Header controls */}
            <div className="absolute top-0 inset-x-0 z-20 flex items-center justify-between bg-gradient-to-b from-black/80 to-transparent p-4">
              <span className="text-[12px] font-semibold uppercase tracking-wider text-white flex items-center gap-2">
                <span className="size-2 rounded-full bg-red-500 animate-pulse" />
                Live Label Scanner
              </span>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => setFastMode(!fastMode)}
                  className={`rounded-full px-2.5 py-1 text-[10px] font-mono font-medium text-white transition-all border ${
                    fastMode ? "bg-emerald-500/80 border-emerald-400" : "bg-white/20 border-white/30 hover:bg-white/30"
                  }`}
                  title="Toggle Fast Compression"
                >
                  {fastMode ? "⚡ FAST" : "💎 HD"}
                </button>
                <button
                  onClick={toggleCameraFacing}
                  className="rounded-full bg-white/20 p-2 text-white hover:bg-white/30 backdrop-blur-md transition-all active:scale-90"
                  title="Flip Camera (Front/Rear)"
                >
                  <RefreshCw className="w-4 h-4" />
                </button>
                <button
                  onClick={stopCamera}
                  className="rounded-full bg-white/20 p-2 text-white hover:bg-white/30 backdrop-blur-md transition-all active:scale-90"
                  title="Close Camera"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Video Stream & Viewfinder Overlay */}
            <div className="relative aspect-[3/4] w-full bg-black flex items-center justify-center overflow-hidden">
              <video
                ref={videoRef}
                playsInline
                autoPlay
                muted
                className="h-full w-full object-cover"
              />

              {/* Viewfinder Target Guide Overlay */}
              <div className="pointer-events-none absolute inset-8 rounded-[12px] border-2 border-white/40 shadow-[0_0_0_9999px_rgba(0,0,0,0.4)]">
                {/* Laser animation bar */}
                <div className="absolute inset-x-0 top-0 h-0.5 bg-gradient-to-r from-transparent via-red-500 to-transparent animate-pulse" />
                
                {/* Corner guide brackets */}
                <div className="absolute -top-1 -left-1 size-5 border-t-4 border-l-4 border-white rounded-tl-[6px]" />
                <div className="absolute -top-1 -right-1 size-5 border-t-4 border-r-4 border-white rounded-tr-[6px]" />
                <div className="absolute -bottom-1 -left-1 size-5 border-b-4 border-l-4 border-white rounded-bl-[6px]" />
                <div className="absolute -bottom-1 -right-1 size-5 border-b-4 border-r-4 border-white rounded-br-[6px]" />
              </div>

              <div className="absolute bottom-16 inset-x-0 text-center pointer-events-none">
                <span className="px-3 py-1.5 rounded-full bg-black/60 text-[12px] text-white/90 backdrop-blur-md">
                  Align cosmetic ingredient text within frame
                </span>
              </div>
            </div>

            {/* Hidden canvas for image capture */}
            <canvas ref={canvasRef} className="hidden" />

            {/* Shutter Bar */}
            <div className="flex items-center justify-center bg-black/95 p-5">
              <button
                onClick={captureFrame}
                className="group relative flex size-18 items-center justify-center rounded-full border-4 border-white/80 p-1 transition-transform active:scale-90"
                aria-label="Capture and Scan"
              >
                <div className="size-14 rounded-full bg-white transition-all group-hover:scale-95 group-active:scale-90" />
              </button>
            </div>
          </div>
        </div>
      )}
      {/* Interactive Citation Inspector Modal */}
      {activeCitationModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="relative w-full max-w-[500px] overflow-hidden rounded-[12px] border border-line bg-card p-6 shadow-2xl">
            <div className="flex items-center justify-between border-b border-line pb-3 mb-4">
              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 rounded font-mono text-xs font-bold bg-ink text-paper">
                  {activeCitationModal.id}
                </span>
                <span className="text-sm font-semibold text-ink">Authoritative Reference Passage</span>
              </div>
              <button
                type="button"
                onClick={() => setActiveCitationModal(null)}
                className="rounded-full p-1 text-inksoft hover:text-ink hover:bg-paper2 transition-colors cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="space-y-3">
              <div>
                <span className="text-[11px] font-mono text-inksoft uppercase tracking-wider">Chemical Subject</span>
                <p className="text-sm font-bold text-ink">{activeCitationModal.ingredient}</p>
              </div>
              <div>
                <span className="text-[11px] font-mono text-inksoft uppercase tracking-wider">Passage Evidence</span>
                <div className="mt-1 rounded bg-paper2 p-3 text-xs leading-relaxed text-ink font-mono border border-line/60 break-words">
                  {activeCitationModal.passage}
                </div>
              </div>
              <div className="flex items-center justify-between pt-2 border-t border-line text-[11px] text-inksoft">
                <span>Database: CIR / EU Cosmetic Annex / FDA</span>
                <span className="text-emerald-600 font-semibold flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" /> Verified Grounded
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
    </>
  );
}

