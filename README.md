# RAINFALL ATLAS v2.6
### Natural Rainfall Regime Discovery from Historical Observations
**3D Scientific Climate Intelligence Platform**

---

## 1. Overview

**Rainfall Atlas** is a full-stack, scientific climate intelligence and unsupervised machine learning web application. It discovers natural precipitation and synoptic climate regimes across Australia using 10 years of historical Bureau of Meteorology (BOM) observations (**145,460 daily records**, 49 continental monitoring posts, 2007–2017).

The platform integrates:
- **FastAPI** backend with asynchronous lifespan caching and RESTful endpoints.
- **Unsupervised Machine Learning**: Euclidean K-Means, Manhattan K-Medoids (PAM/CLARA), and 5 Hierarchical Agglomerative configurations (Ward, Complete, and Average linkages with Euclidean and Manhattan metrics).
- **PCA Dimensionality Reduction**: Standardized 3D projection onto PC1 (thermal), PC2 (moisture), and PC3 (barometric) explaining ~75% of synoptic variance.
- **Scientific Validation & Honest Metrics**: Multi-seed stability ($ARI \approx 0.9824$), multi-$K$ ($K=2..8$) evaluation, Cophenetic Correlation, and cross-model comparison on a common stratified sample ($N=1,500$) with Adjusted Rand Index (ARI) and Normalized Mutual Information (NMI).
- **Markov Temporal Synoptic Dynamics**: Strict consecutive-day calendar pairs ($\Delta t = 1$ day) calculating single-day regime persistence and Southern Hemisphere seasonal distributions.
- **Persistent Experiment Registry**: Automatic logging of all benchmark and custom runs to `outputs/experiments_registry.json` and `.csv`.
- **Six 3D WebGL / Three.js Visualizations**: Atmospheric Earth globe, 3D volumetric station landscape, 2,500-particle regime convergence field, 3D Ward hierarchical dendrogram tree, 3D PCA latent scatter space with eigenvector axes, and 3D extruded Australian continental topography with precipitation columns.

---

## 2. Quick Start

### One-Click Launch (Windows)
Double-click or run:
```cmd
start.bat
```
This automatically:
1. Verifies Python 3.10+ installation.
2. Checks all required scientific packages (`fastapi`, `uvicorn`, `scikit-learn`, `scipy`, `pandas`, `numpy`).
3. Boots the Uvicorn server on `http://127.0.0.1:8000`.
4. Automatically opens the interactive 3D web application in your default browser.

### Manual Launch (Command Line / PowerShell)
```powershell
# 1. Install dependencies
pip install -r backend/requirements.txt

# 2. Run backend test suite
python backend/tests/test_backend.py
python backend/tests/test_endpoints.py

# 3. Start server
python run.py
```
Navigate to:
- **Interactive Application:** `http://127.0.0.1:8000`
- **Swagger API Documentation:** `http://127.0.0.1:8000/docs`
- **ReDoc Technical Reference:** `http://127.0.0.1:8000/redoc`

---

## 3. Architecture & File Structure

```text
RAINFALL-ATLAS/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── endpoints.py         # RESTful API router (clustering, pca, dendrogram, experiments)
│   │   ├── core/
│   │   │   ├── config.py            # Global paths, model defaults, and configurations
│   │   │   └── constants.py         # 49 BOM stations coordinates, elevations & color palettes
│   │   ├── preprocessing/
│   │   │   ├── data_loader.py       # Safe CSV loading, observation_id assignment, skewness audit
│   │   │   └── pipeline.py          # Imputation, StandardScaler, log1p, daily & location_monthly aggregation
│   │   ├── algorithms/
│   │   │   ├── kmeans.py            # Euclidean K-Means, multi-K evaluate (K=2..8), multi-seed stability
│   │   │   ├── kmedoids.py          # Manhattan CLARA/PAM medoid optimization, SAD & native medoid dispersion
│   │   │   ├── hierarchical.py      # Ward, Complete, Average linkages (Euclidean & Manhattan), SciPy dendrogram
│   │   │   ├── pca.py               # 3D PCA projection, feature loadings, explained variance ratios
│   │   │   └── comparison.py        # Common stratified sample ARI & NMI cross-model congruence matrix
│   │   ├── services/
│   │   │   ├── clustering_service.py# Lifecycle coordinator, active model state, experiment registration
│   │   │   ├── experiment_registry.py# Persistent run logger to disk (JSON & CSV)
│   │   │   ├── profiling_service.py # Dynamic meteorological regime naming grounded in physical data
│   │   │   ├── geography_service.py # Station distributions, continental proportions & geo-coordinates
│   │   │   └── temporal_service.py  # Seasonal breakdown & strict consecutive-day Markov persistence
│   │   └── main.py                  # FastAPI application with CORS & static file mount
│   ├── tests/
│   │   ├── test_backend.py          # Core ML algorithm & data processing test suite
│   │   └── test_endpoints.py        # API endpoint handler integration test suite
│   └── requirements.txt             # Verified Python dependencies
│
├── static/
│   └── index.html                   # Integrated 3D Stitch frontend with interactive controls & live API client
│
├── data/
│   └── weatherAUS.csv               # 145,460 BOM historical records (2007–2017)
│
├── outputs/
│   ├── experiments_registry.json    # Persistent experiment ledger
│   ├── experiments_registry.csv     # Persistent experiment spreadsheet
│   ├── figures/
│   ├── tables/
│   └── models/
│
├── code.html                        # Original Stitch frontend (preserved reference)
├── DESIGN.md                        # Stitch design specification (preserved reference)
├── screen.png                       # Reference UI screenshot
├── run.py                           # Cross-platform Python launcher
├── start.bat                        # One-click Windows starter script
└── README.md
```

---

## 4. Scientific Methodology & Algorithms

1. **Dataset Integrity & Ingestion**:
   - `weatherAUS.csv` contains 145,460 observations across 49 synoptic stations from 2007-11-01 to 2017-06-25.
   - Stable sequential `observation_id` (0..145459) tracks provenance throughout preprocessing and downsampling.
   - Skewness is formally audited: positive skewness of `9.84` and `62.62%` zero-rain dry days.

2. **Preprocessing & Leakage Prevention**:
   - Strictly excludes `RainTomorrow` and categorical targets from clustering feature vectors.
   - Continuous features: `MinTemp`, `MaxTemp`, `Rainfall`, `WindGustSpeed`, `WindSpeed9am`, `WindSpeed3pm`, `Humidity9am`, `Humidity3pm`, `Pressure9am`, `Pressure3pm`, `Temp9am`, `Temp3pm`.
   - Log transformation: `log1p(Rainfall) = ln(1 + Rainfall)` dampens extreme outlier precipitation events.
   - Standard scaling: transforms all continuous features to zero mean and unit variance.
   - Observation units: supports both **Daily Observations** (145,460 rows) and **Location-Monthly Aggregations** (4,786 rows with unique `agg_id`).

3. **Partition Clustering**:
   - **K-Means (Euclidean)**: Minimizes Within-Cluster Sum of Squares (WCSS). Includes range evaluation ($K=2..8$) on a single consistent validation sample ($N=2,000$) and 5-seed stability validation ($ARI \approx 0.9824$).
   - **K-Medoids (Manhattan)**: Minimizes Sum of Absolute Deviations (SAD) using L1 Cityblock distance via PAM/CLARA medoid selection. Features a native Manhattan Medoid Separation Index (MSI).

4. **Hierarchical Agglomeration**:
   - Evaluated on a proportionate stratified sample across all 49 synoptic locations ($N=1,500$).
   - 5 Linkage and Metric configurations:
     - Ward (Euclidean) — Minimizes within-cluster variance increase.
     - Complete Linkage (Euclidean)
     - Complete Linkage (Manhattan)
     - Average Linkage (Euclidean)
     - Average Linkage (Manhattan)
   - Real SciPy linkage matrix, Cophenetic Correlation Coefficient, and dendrogram branch coordinates.

5. **Cross-Model Alignment**:
   - Adjusted Rand Index (ARI) and Normalized Mutual Information (NMI) are calculated strictly on the **exact same common stratified sample** ($N=1,500$) across K-Means, K-Medoids, and Hierarchical models.

6. **Markov Temporal Dynamics**:
   - Single-day regime transitions enforce the **consecutive-day rule**: only records separated by exactly 1 calendar day ($\Delta t = 1$) within the same station are evaluated.
   - Southern Hemisphere seasonal breakdown: Summer (DJF), Autumn (MAM), Winter (JJA), Spring (SON).

---

## 5. 3D WebGL Visualization Suite

The application includes six real-time Three.js scenes designed to the Stitch visual specification:

1. **Atmospheric Earth Globe** (`#hero-earth-container`):
   - Phased Phong globe with specular highlights, graticule wireframe lines, and Australian continental dot matrix.
   - Animated halo atmospheric glow and falling precipitation stream particles.
2. **Spatial Weather Landscape** (`#threejs-container-DATA_FIELD`):
   - 49 synoptic station cylinders plotted in [Latitude, Longitude, Barometric Altitude] 3D space with rainfall isohyet bases.
3. **Regime Equilibrium Convergence Field** (`#particle-cluster-container`):
   - 2,500 particles cycling along sine/cosine orbital trajectories toward 4 centroid beacon towers.
   - Ground isometric grid and mouse parallax tilt interaction.
4. **3D Hierarchical Discovery Tree** (`#tree-container`):
   - 3D branching lineage of the Ward hierarchical dendrogram from Root Node through Macro Bifurcation to 48 observation leaf clusters.
   - Isometric grid at $y=-5.8$ and interactive camera parallax.
5. **3D PCA Latent Space** (`#pca-3d-container`):
   - 1,800 latent observations plotted in standardized PC1 × PC2 × PC3 space.
   - Bounding box wireframe, orthogonal axis lines (PC1 Cyan, PC2 Turquoise, PC3 Glacier), 3 eigenvector arrow helpers, 4 cluster core spheres, and toggle controls.
6. **3D Topographic Australian Terrain** (`#threejs-container-AU_GEO`):
   - Extruded Australian landmass shape with wireframe edges and the Great Dividing Range ridge tube.
   - 9 primary synoptic city markers with vertical rainfall pillars, emitter heads, and animated orographic clouds.

---

## 6. Verification & Test Suite

Run the full automated test suite anytime:

```powershell
# Core algorithms & ML pipelines
python backend/tests/test_backend.py

# FastAPI endpoints & data integrity
python backend/tests/test_endpoints.py
```

All tests execute on the local dataset without mocks or synthetic fabrication.

---

## 7. Public Deployment (GitHub + Render)

See [DEPLOYMENT.md](DEPLOYMENT.md) for the exact GitHub publishing steps and Render configuration. This project includes a `render.yaml` Blueprint and a pinned `.python-version` file. The hosted dashboard uses same-origin `/api` requests so the frontend works behind the public Render URL.
#   r a i n f a l l - r e g i m e - d i s c o v e r y  
 