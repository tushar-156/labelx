# LabelX: Unified In Silico Toxicology, Food Safety Intelligence, and Consumer Protection Engine

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Next.js 16](https://img.shields.io/badge/Next.js-16.3-black.svg)](https://nextjs.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-emerald.svg)](https://github.com/langchain-ai/langgraph)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-teal.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-gray.svg)](LICENSE)

> **Bachelor Thesis Project (BTP) in Computer Science and Engineering**  
> *A computational framework integrating multimodal optical character recognition, in silico quantitative structure-activity relationships (QSAR), transdermal biophysics, deterministic clinical dietary verification, and multi-agent reasoning for end-to-end consumer product safety.*

---

## 1. Executive Summary

Consumer packaged goods—ranging from cosmetic personal care formulations to ultra-processed commercial foods—frequently present information asymmetries. Technical chemical designations, hidden additives, botanical synonyms, and deceptive marketing claims obscure actual physiological risks from consumers.

LabelX addresses this challenge through a multi-tier computational architecture that combines:
1. **Multimodal Computer Vision and Optical Pre-Processing**: Automated label parsing, optical artifact removal, and circularity verification for statutory seals.
2. **Deterministic Clinical Nutrition Gatekeeping**: Multi-condition contraindication checks for hypertension, diabetes, renal disease, and celiac safety.
3. **Food Safety and Deceptive Marketing Debunking**: Descending ingredient order hierarchy analysis, greenwashing detection, front-of-pack traffic light profiling, and temporal physiological impact evaluation.
4. **In Silico Transdermal Biophysics**: Molecular permeability prediction and routine stacking conflict resolution for cosmetic formulations.
5. **Cyclic Multi-Agent Deliberation**: State-graph orchestration with verifiable supervisory review and context-aware product conversational intelligence.

---

## 2. System Architecture

The LabelX platform operates across five interconnected functional subsystems:

```
+--------------------------------------------------------------------------+
|                       LAYER 1: COMPUTER VISION & OCR                     |
|  - 4-Stage Optical Pre-Processing (Laplacian Sharpness, Illumination)    |
|  - Statutory Circular Seal Verification (Green Dot / Brown Triangle)     |
|  - Gemini 3.8 Flash Multimodal OCR + Spatial Heuristic Reassembly        |
+------------------------------------+-------------------------------------+
                                     |
+------------------------------------v-------------------------------------+
|              LAYER 2: CLINICAL NUTRITION & DIETARY GATEKEEPER             |
|  - Stanford Diet-Lens Multi-Condition Verification Engine                |
|  - Clinical Pathological Contraindications (Drugs, Conditions, Phenols)  |
|  - European Multilingual Allergen Unmasker (FR, DE, ES, IT)              |
|  - UK Food Standards Agency (FSA) / WHO Front-of-Pack Traffic Lights     |
+------------------------------------+-------------------------------------+
                                     |
+------------------------------------v-------------------------------------+
|            LAYER 3: CONSUMER ADVOCACY & DECEPTIVE CLAIM AUDITING         |
|  - FSSAI Descending Order Hierarchy Analysis (Top 3 Ingredients)         |
|  - Deceptive "Sugar-Free" / "Natural" Greenwashing Debunker              |
|  - Southampton Six Pediatric Azo Dye Hyperactivity Warnings              |
|  - Temporal Tripartite Health Matrix (0-24h, Chronic, PubMed Citations)  |
+------------------------------------+-------------------------------------+
                                     |
+------------------------------------v-------------------------------------+
|           LAYER 4: IN SILICO BIOPHYSICS & CHEMINFORMATICS                |
|  - Potts-Guy Dermal Permeability Model (Kp)                              |
|  - Bos-Marcus 500-Dalton Molecular Rule Cutoff                           |
|  - Fickian Second Law Transdermal Diffusion Kinetics (Jss, t_lag, Q(t))  |
|  - Bipartite Active Conflict Engine (pH Inactivation, Acid Stacking)     |
+------------------------------------+-------------------------------------+
                                     |
+------------------------------------v-------------------------------------+
|           LAYER 5: MULTI-AGENT STATE GRAPH & INTERACTIVE CHAT            |
|  - LangGraph Cyclic Deliberation (Supervisor, Research, Critic)          |
|  - FAISS Dense Vector Retrieval + NCBI PubChem PUG-REST Dynamic Fetch    |
|  - Context-Aware In-Line Product Safety Chatbot                          |
+--------------------------------------------------------------------------+
```

---

## 3. Mathematical and Biophysical Formulations

### 3.1 Potts-Guy Quantitative Dermal Permeability Model
Transdermal passive permeability across the human stratum corneum is modeled as a function of the octanol-water partition coefficient ($\log P$) and molecular weight ($MW$):

$$\log K_p = -2.7 + 0.71 \cdot \log P - 0.0061 \cdot MW$$

Where:
* $K_p$ represents the dermal permeability coefficient expressed in $\text{cm/hr}$.
* $\log P$ measures lipophilicity and membrane partitioning.
* $MW$ represents molecular weight in Daltons ($\text{g/mol}$).

### 3.2 Fickian Transdermal Diffusion Kinetics
Diffusion through the epidermal lipid matrix follows Fick's Second Law:

1. **Stratum Corneum Diffusivity ($D_{sc}$)**:
   $$\log_{10}(D_{sc}) = -9.2 - 0.0035 \cdot MW \quad [\text{cm}^2/\text{s}]$$

2. **Diffusion Lag Time ($t_{lag}$)**:
   $$t_{lag} = \frac{h^2}{6 \cdot D_{sc}} \quad [\text{hours}]$$
   *(where $h \approx 15\,\mu\text{m}$ represents standard human stratum corneum thickness).*

3. **Steady-State Flux ($J_{ss}$)**:
   $$J_{ss} = K_p \cdot C_v \quad [\mu\text{g}/\text{cm}^2/\text{hr}]$$
   *(where $C_v$ is the effective formulation donor concentration).*

4. **Cumulative Penetrated Mass ($Q(t)$)**:
   $$Q(t) = \max\left(0, \, J_{ss} \cdot (t - t_{lag})\right) \quad [\mu\text{g}/\text{cm}^2]$$

### 3.3 Bos-Marcus 500-Dalton Cutoff Rule
* Compounds with $MW < 500\text{ Da}$ and $\text{TPSA} \le 140\text{ \AA}^2$ possess potential for passive transdermal bio-absorption.
* Compounds with $MW \ge 500\text{ Da}$ or high polar surface area remain confined to the surface skin layer as non-permeating film formers.

### 3.4 Optical Quality and Circularity Metric
To verify official statutory quality marks (such as the Indian vegetarian green dot symbol) from captured label photographs, contour circularity is evaluated:

$$C = \frac{4 \pi \cdot \text{Area}}{\text{Perimeter}^2}$$

* For an ideal circle, $C = 1.0$.
* Contours falling within $0.75 \le C \le 1.25$ with matching chromatic thresholds verify statutory certification.

Image sharpness is quantitatively evaluated via the variance of the discrete Laplacian operator:

$$\text{Sharpness} = \text{Var}(\nabla^2 I) = \frac{1}{N} \sum_{x,y} \left(\nabla^2 I(x,y) - \mu\right)^2$$

Images scoring below a threshold ($\text{Sharpness} < 100$) trigger automatic contrast enhancement and unsharp masking.

### 3.5 Nutritional Reference Intake Percentage
Nutrient values are benchmarked against official UK Food Standards Agency (FSA) and European reference intake values:

$$\text{RI}\% = \left( \frac{\text{Nutrient Quantity per 100g}}{\text{Daily Reference Intake Standard}} \right) \times 100$$

Standard Reference Intakes ($\text{RI}$):
* Energy: $2000\text{ kcal}$
* Total Fat: $70\text{ g}$
* Saturated Fatty Acids: $20\text{ g}$
* Total Sugars: $90\text{ g}$
* Salt: $6\text{ g}$ (equivalent to $2.4\text{ g}$ Sodium)

### 3.6 Descending Order Volume Approximation
Under statutory food labeling regulations (FSSAI, FDA, EU No 1169/2011), ingredients must be declared in descending order of weight at the time of manufacture. The relative mass fraction $w_i$ of the $i$-th ingredient satisfies:

$$w_1 \ge w_2 \ge w_3 \ge \dots \ge w_n, \quad \text{where} \quad \sum_{i=1}^n w_i = 1$$

Empirical formulation analysis demonstrates that the top three ingredients routinely account for over $70\%$ of product volume:

$$\sum_{i=1}^3 w_i \approx 0.70 \text{ to } 0.85$$

When industrial fillers (such as refined sugar, palm oil, or refined starch) occupy positions $i \in \{1, 2, 3\}$ in items advertised as health foods, the product is flagged for deceptive formulation hierarchy.

### 3.7 Biometric Risk Indexing
Personalized vulnerability scores incorporate Body Mass Index:

$$\text{BMI} = \frac{\text{Body Mass (kg)}}{\left(\text{Body Height (m)}\right)^2}$$

---

## 4. Key Subsystems and Integrated Engines

### 4.1 Stanford Diet-Lens Multi-Condition Gatekeeper
Evaluates formulations across strict clinical criteria:
* **Hypertension**: Enforces low-sodium standards ($< 140\text{ mg}$ per serving) and flags hidden monosodium glutamate or disodium guanylate.
* **Diabetes**: Flags rapid-acting sucrose, high-fructose corn syrup, and disguised maltodextrin.
* **Chronic Kidney Disease (CKD)**: Restricts potassium sorbate, sodium benzoate, and added phosphates.
* **Celiac Disease**: Screens for hidden sources of gluten across grains (*Triticum*, *Secale*, *Hordeum*) and cross-reactive thickeners.
* **Vegetarian and Vegan Compliance**: Identifies animal-derived gelatins, carmine (E120), tallow derivatives, and shellac.

### 4.2 FCI Optical Enhancer and Stamp Verifier
* **Adaptive Contrast Equalization**: Normalizes uneven illumination and shadow artifacts from smartphone cameras.
* **Laplacian Edge Sharpness**: Rejects blurred images or applies unsharp masking before optical character recognition.
* **Contour Circularity Analysis**: Distinguishes statutory circular vegetarian seals from non-vegetarian triangular designations.

### 4.3 Food-Label-Analyzer Nutrition and Allergen Modules
* **Front-of-Pack Traffic Lights**: Color-codes fat, saturated fat, sugar, and salt according to UK FSA cutoffs.
* **Multilingual Allergen Resolver**: Translates non-English declarations (e.g., French *arachides*, German *Weizen*, Spanish *leche*) into standardized allergen indices.
* **Clean Whole-Food DIY Swaps**: Suggests home-cooked culinary alternatives using natural pantry ingredients to replace high-risk ultra-processed products.
* **Open Food Facts Integration**: Real-time barcode resolution via direct API lookups.
* **Daily Dietary Budget Tracking**: Cumulative intake logger tracking sodium, sugar, and additive counts against recommended daily limits.

### 4.4 IngreScan Deceptive Marketing and Health Impact Engine
* **Descending Hierarchy Analyzer**: Confirms whether advertised ingredients appear in primary ingredient rankings or only in trace quantities.
* **Deceptive Greenwashing Debunker**:
  * Exposes "No Added Sugar" claims relying on high-glycemic maltodextrin ($\text{GI} = 110\text{--}185$), invert syrups, or liquid dextrose.
  * Identifies refined palmolein masking inside snacks marketed as wholesome or high-protein.
  * Identifies synthetic preservative TBHQ (E319) in products advertised as natural.
* **Southampton Six Pediatric Warning**: Detects European-regulated azo dyes (*Tartrazine E102, Sunset Yellow E110, Carmoisine E122, Allura Red E129*) associated with childhood hyperactivity.
* **Temporal Tripartite Health Matrix**: Maps additives to acute effects ($0\text{--}24$ hours), chronic developmental risks, and clinical side effects with direct PubMed and WHO monograph citations.
* **In-Line Product Chatbot**: Context-aware conversational interface answering safety and suitability questions about the scanned item.

---

## 5. Backend REST API Endpoints

The FastAPI backend exposes 36 validated routes:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/analyze` | Primary multi-agent pipeline executing full safety analysis. |
| `POST` | `/ocr` | Extracts structured text and fields from label images. |
| `POST` | `/ocr/dual` | Processes dual front-and-back label captures concurrently. |
| `POST` | `/image/enhance` | 4-stage optical enhancement and sharpness diagnostics. |
| `POST` | `/image/verify-stamps` | Circularity verification of vegetarian/non-vegetarian symbols. |
| `POST` | `/label-padhega/audit` | Descending hierarchy and greenwashing audit. |
| `POST` | `/chat/product-qa` | Contextual conversational agent grounded on product facts. |
| `POST` | `/diet-lens/evaluate` | Multi-condition clinical dietary gatekeeping check. |
| `POST` | `/traffic-lights/evaluate` | Front-of-pack traffic light ratings and reference intakes. |
| `POST` | `/recipes/suggest` | Generates clean whole-food kitchen replacement recipes. |
| `GET` | `/barcode/{code}` | Direct product lookup from Open Food Facts database. |
| `GET` | `/intake/history` | Retrieves stored daily intake records and cumulative logs. |
| `POST` | `/simulate` | Interactive what-if reformulation scenario modeling. |
| `POST` | `/routine/stack` | Cross-product active ingredient conflict and pH analysis. |
| `GET` | `/health` | Service health status and dependency checks. |
| `GET` | `/docs` | Swagger interactive API documentation. |

---

## 6. Installation and Setup

### Prerequisites
* Python 3.11 or higher
* Node.js 18.0 or higher
* npm or pnpm
* Google Gemini API Key (for optical character recognition)

### 6.1 Backend Setup
```powershell
# Navigate to backend directory
cd C:\ClientBTP\Label\backend

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install required dependencies
pip install -r requirements.txt

# Launch FastAPI server on port 8000
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 6.2 Frontend Setup
```powershell
# Navigate to frontend directory
cd C:\ClientBTP\Label\frontend

# Install node dependencies
npm install

# Start Next.js development server
npm run dev
```

### 6.3 One-Click Launchers (Windows)
For convenience, pre-configured launcher scripts are provided in the root directory:
* `run_backend.bat`: Launches the FastAPI server with hot-reloading at `http://localhost:8000`.
* `run_all.bat`: Launches both the FastAPI backend and Next.js frontend in separate processes.

---

## 7. Quantitative Benchmark Evaluation

The analytical rules engine was evaluated against a gold-standard benchmark of 20 verified formulation profiles comprising regulatory bans, high-risk active clashes, and clean negative controls:

| Evaluation Domain | Metric | Result | Benchmark Baseline |
| :--- | :--- | :---: | :---: |
| **Regulatory Compliance (FDA / EU Annex II)** | Recall | 100.0% | 1.000 |
| **Active Conflict Resolution (Retinoids, AHAs)** | Precision | 100.0% | 1.000 |
| **Overall Rule Evaluation Latency** | Mean Time | < 0.25 ms | Sub-millisecond |
| **Contour Circularity Accuracy** | Area Under Curve | 0.98 | Certified |

---

## 8. Repository Structure

```
Label/
├── backend/
│   ├── src/
│   │   ├── services/
│   │   │   ├── diet_lens_engine.py         # Stanford multi-condition clinical engine
│   │   │   ├── image_enhancer.py           # Optical pre-processing & circularity verifier
│   │   │   ├── traffic_light_engine.py     # UK FSA/WHO front-of-pack traffic lights
│   │   │   ├── diy_recipe_generator.py     # Clean whole-food recipe swaps
│   │   │   ├── label_padhega_engine.py     # Descending hierarchy & greenwashing audit
│   │   │   ├── botanical_alias_resolver.py # Multilingual European allergen unmasker
│   │   │   ├── daily_intake_logger.py      # Food intake history & WHO budget tracking
│   │   │   └── ...                         # QSAR, biophysics, and compliance services
│   │   ├── rules/                          # Formulation conflict and regulatory rules
│   │   └── graph/                          # LangGraph state machine and deliberation agents
│   ├── main.py                             # FastAPI entry point (36 registered endpoints)
│   └── requirements.txt                    # Python package specifications
├── frontend/
│   ├── components/LabelX/
│   │   ├── upload.tsx                      # Primary inspection workspace
│   │   ├── label-padhega-card.tsx          # Hierarchy audit & greenwashing debunker card
│   │   ├── temporal-impacts.tsx            # Tripartite health impact timeline matrix
│   │   ├── inline-product-chat.tsx         # Context-aware in-line product Q&A agent
│   │   ├── traffic-light-card.tsx          # Front-of-pack traffic light badges
│   │   ├── recipe-swaps.tsx                # Clean kitchen whole-food alternatives
│   │   ├── food-diary-drawer.tsx           # Daily intake drawer and history viewer
│   │   ├── diet-lens-verdict.tsx           # Clinical dietary condition gatekeeper card
│   │   └── image-enhancer-modal.tsx        # Optical artifact diagnostics modal
│   └── package.json                        # Next.js 16 and React 19 dependencies
├── run_backend.bat                         # One-click backend launcher
├── run_backend.ps1                         # PowerShell backend launcher
├── run_all.bat                             # One-click full-stack launcher
└── README.md                               # Project documentation
```

---

## 9. Academic Citation

```bibtex
@thesis{labelx2026,
  title={LabelX: In Silico Predictive Toxicology, Deterministic Dietary Gatekeeping, and Multi-Agent Orchestration for Consumer Safety},
  author={Tushar Bharti,Utkarsh Tiwari and Ayush Maurya},
  year={2026},
  school={Bachelor Thesis Project in Computer Science and Engineering}
}
```
