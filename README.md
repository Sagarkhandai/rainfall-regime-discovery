# 🌧️ Rainfall Atlas — 3D Climate Intelligence Platform

**Unsupervised discovery of rainfall regimes across Australia, with interactive 3D visualizations.**

🔗 **Live demo:** [https://rainfall-atlas-ca-eo9s.onrender.com](https://rainfall-atlas-ca-eo9s.onrender.com)

> ⏳ The demo is hosted on Render's free tier, so the first load may take 30–60 seconds while the server wakes up.

---

## 📖 Project Overview

Rainfall Atlas is an end-to-end unsupervised machine learning project that analyses **10 years of Australian Bureau of Meteorology (BOM) weather observations** to uncover hidden precipitation regimes, without using any labels. The results are presented in an interactive, WebGL-powered web dashboard.

**Dataset:** `weatherAUS.csv`: 145,460 daily records from 49 weather stations across the continent.

### Key Features

- **3D Station Field:** Explore all 49 stations in volumetric space (latitude, longitude, pressure/altitude), with hover probes for temperature, rainfall and pressure.
- **Regime Discovery:** Particle-based visualization of clusters. The discovered regimes are Monsoonal Tropics, Arid Outback, Oceanic Front and Subtropical Convective.
- **Hierarchical Linkage:** A 3D Ward dendrogram showing how observations merge from the continental root down to leaf clusters.
- **PCA Latent Space:** Orbitable 3D projection onto PC1 × PC2 × PC3.
- **Continental Map:** Topographic rainfall contours and station density.
- **Model Registry:** Side-by-side comparison of algorithms with validation metrics, multi-seed stability, seasonal breakdown, Markov transition matrix and a persistent experiment log.
- **Interactive Model Runner:** Choose the algorithm, mode (daily or monthly) and `k` (2–8), then run the model live.

### Algorithms and Methods

| Category | Methods |
|---|---|
| Partition clustering | K-Means (Euclidean), K-Medoids / PAM (Manhattan) |
| Hierarchical clustering | Ward (Euclidean), Complete (Manhattan), Average (Euclidean) |
| Dimensionality reduction | Principal Component Analysis (PCA) |
| Validation | Silhouette Score, Davies-Bouldin Index, Cophenetic Correlation, ARI, NMI |
| Temporal analysis | 1-day Markov transition and persistence matrix |

### 8-Stage ML Pipeline

1. **Historical Ingestion:** load 145,460 BOM weather records
2. **Preprocessing & Imputation:** median imputation, `log1p` on skewed rainfall
3. **Feature Normalization:** `StandardScaler` (23 → 11 features)
4. **Partition Clustering:** multi-restart K-Means and K-Medoids
5. **Hierarchical Linkage:** Ward agglomeration and dendrogram
6. **Validation Indices:** Silhouette and Davies-Bouldin to select `k`
7. **PCA Projection:** reduce to PC1, PC2 and PC3
8. **Climatological Profiling:** map clusters back to physical weather regimes

### Key Results

- Optimal number of clusters: **k = 4**
- Multi-seed stability (mean pairwise ARI): **0.9824**
- Ward cophenetic correlation: **0.84**
- Silhouette peaks mathematically at k = 2 (0.24), but k = 4 gives the most meteorologically meaningful regimes: Tropical Monsoon, Subtropical Maritime, Temperate Mediterranean and Arid Interior.

---

## 🛠️ Tech Stack

- **Backend / ML:** Python, Pandas, NumPy, Scikit-learn, SciPy
- **Frontend:** HTML, CSS, JavaScript, WebGL 2.0 (3D rendering)
- **Deployment:** Render

> 📝 *Adjust this list to match your exact stack (e.g. Flask / FastAPI, Three.js, Plotly).*

---

## ✅ Prerequisites

Make sure you have the following installed:

- **Python 3.9 or higher** ([download](https://www.python.org/downloads/))
- **pip** (comes with Python)
- **Git** ([download](https://git-scm.com/downloads))
- A modern web browser with **WebGL 2.0** support (Chrome, Edge, Firefox or Safari)
- The dataset file **`weatherAUS.csv`** ([Kaggle: Rain in Australia](https://www.kaggle.com/datasets/jsphyg/weather-dataset-rattle-package))

---

## 📦 Installation

**1. Clone the repository**

```bash
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>
```

**2. Create and activate a virtual environment (recommended)**

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Add the dataset**

Download `weatherAUS.csv` and place it in the project's data folder (or the project root, depending on your structure):

```
<your-repo-name>/
├── data/
│   └── weatherAUS.csv
├── app.py
├── requirements.txt
└── README.md
```

---

## ▶️ Execution

**Run the application locally**

```bash
python app.py
```

Then open your browser and go to:

```
http://127.0.0.1:5000
```

*(Use the port shown in your terminal if it differs.)*

**Run with Gunicorn (production-style, same as Render)**

```bash
gunicorn app:app
```

### Using the Dashboard

1. Open the **Model Registry** section.
2. Select an **algorithm** (K-Means, K-Medoids, Ward, Complete or Average).
3. Choose the **mode** (Daily or Monthly) and the number of clusters **k** (2–8).
4. Click **Run Model**.
5. Explore the results in the 3D Regime, Dendrogram, PCA and Map sections.

---

## ☁️ Deployment (Render)

1. Push your code to GitHub.
2. Create a new **Web Service** on [Render](https://render.com) and connect your repository.
3. Set the following:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
4. Deploy and wait for the build to finish.

---

## 📁 Project Structure

```
├── app.py               # Application entry point / API
├── requirements.txt     # Python dependencies
├── data/
│   └── weatherAUS.csv   # BOM weather dataset
├── static/              # CSS, JavaScript, 3D visualization code
├── templates/           # HTML templates
└── README.md
```

> 📝 *Update this tree to match your actual folders and file names.*

---

## 🔮 Future Improvements

- Add more clustering algorithms (DBSCAN, Gaussian Mixture Models)
- Real-time weather data integration
- Rainfall prediction using supervised models
- Exportable reports for experiment runs

---

## 🤝 Contributing

Contributions are welcome! Fork the repo, create a feature branch, and open a pull request.

## 📄 License

This project is licensed under the [MIT License](LICENSE).

## 🙏 Acknowledgements

- [Australian Bureau of Meteorology](http://www.bom.gov.au/) for the original weather data
- [Kaggle "Rain in Australia"](https://www.kaggle.com/datasets/jsphyg/weather-dataset-rattle-package) for the dataset

## 👤 Author

**Sagar Khnadai**
B.Tech CSE, Lovely Professional University

