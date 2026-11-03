from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.config import settings
from app.services.clustering_service import ClusteringService
from app.api.endpoints import router as api_router

STATIC_DIR = Path(__file__).resolve().parent.parent.parent / "static"
INDEX_HTML = STATIC_DIR / "index.html"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load dataset and warm analytical cache
    print("=" * 60)
    print("RAINFALL ATLAS · 3D CLIMATE INTELLIGENCE PLATFORM")
    print("Backend API Bootstrapping & Cache Warmup")
    print("=" * 60)
    service = ClusteringService.get_instance()
    service.initialize_and_warm_cache()
    print("[OK] All models fitted and analytical cache warmed successfully.")
    yield
    print("Rainfall Atlas Backend Shutting Down.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Natural Rainfall Regime Discovery from Historical Patterns · 3D Climate Intelligence Platform",
    version="2.4.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def root():
    if INDEX_HTML.exists():
        return FileResponse(INDEX_HTML)
    return {
        "title": settings.PROJECT_NAME,
        "status": "online",
        "api_docs": "/docs"
    }

@app.get("/api/info")
def api_info():
    return {
        "title": settings.PROJECT_NAME,
        "status": "online",
        "api_docs": "/docs",
        "endpoints": {
            "dataset_summary": f"{settings.API_V1_STR}/dataset/summary",
            "cluster_profiles": f"{settings.API_V1_STR}/results/profiles",
            "pca_projection": f"{settings.API_V1_STR}/results/pca",
            "dendrogram": f"{settings.API_V1_STR}/results/dendrogram",
            "geography": f"{settings.API_V1_STR}/results/geography",
            "temporal": f"{settings.API_V1_STR}/results/temporal",
            "model_comparison": f"{settings.API_V1_STR}/clustering/compare"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
