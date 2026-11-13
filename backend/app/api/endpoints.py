from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Query

from app.core.json_util import sanitize_for_json
from app.preprocessing.data_loader import DataLoader
from app.services.clustering_service import ClusteringService
from app.schemas.schemas import (
    DatasetSummaryResponse,
    PreprocessingConfigRequest,
    PreprocessingSummaryResponse,
    KMeansRequest,
    KMedoidsRequest,
    HierarchicalRequest,
    SelectModelRequest,
    ModelMetricSummary,
    ClusterProfileItem,
    PCAResponse,
    DendrogramResponse,
    GeographyResponse,
    TemporalResponse,
    ModelComparisonResponse,
    ExperimentItem
)

router = APIRouter()
clustering_service = ClusteringService.get_instance()

# -------------------------------------------------------------
# 1. Dataset Endpoints
# -------------------------------------------------------------
@router.get("/health")
def get_health():
    return {
        "status": "healthy",
        "service": "Rainfall Atlas API",
        "version": "2.4.0",
        "cache_initialized": clustering_service.X_scaled is not None
    }

@router.get("/dataset/summary", response_model=DatasetSummaryResponse)
def get_dataset_summary():
    try:
        summary = DataLoader.get_dataset_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dataset/features")
def get_dataset_features():
    summary = DataLoader.get_dataset_summary()
    return {
        "columns": summary["columns"],
        "missing_percentages": summary["missing_percentages"],
        "core_features_recommended": [
            'MinTemp', 'MaxTemp', 'Rainfall', 'WindSpeed9am', 'WindSpeed3pm',
            'Humidity9am', 'Humidity3pm', 'Pressure9am', 'Pressure3pm', 'Temp9am', 'Temp3pm'
        ],
        "excluded_leakage_features": ['RainTomorrow', 'RainToday']
    }

@router.get("/dataset/quality")
def get_dataset_quality():
    summary = DataLoader.get_dataset_summary()
    return {
        "total_observations": summary["total_observations"],
        "complete_core_rows": summary["complete_core_rows"],
        "complete_rate_pct": round(summary["complete_core_rows"] / summary["total_observations"] * 100, 2),
        "duplicate_records": summary["duplicate_records"],
        "rainfall_skewness": summary["rainfall_distribution"].get("skewness", 9.84),
        "zero_rainfall_pct": summary["rainfall_distribution"].get("zero_rain_pct", 62.62),
        "missing_breakdown": summary["missing_percentages"]
    }

# -------------------------------------------------------------
# 2. Preprocessing Endpoints
# -------------------------------------------------------------
@router.post("/preprocessing/configure", response_model=PreprocessingSummaryResponse)
def configure_preprocessing(config: PreprocessingConfigRequest):
    try:
        clustering_service.initialize_and_warm_cache(
            features=config.features,
            use_log_rainfall=config.use_log_rainfall,
            observation_unit=config.observation_unit
        )
        return clustering_service.pipeline.get_pipeline_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to configure preprocessing: {str(e)}")

@router.get("/preprocessing/summary", response_model=PreprocessingSummaryResponse)
def get_preprocessing_summary():
    if clustering_service.pipeline is None:
        raise HTTPException(status_code=400, detail="Preprocessing pipeline not yet initialized.")
    return clustering_service.pipeline.get_pipeline_summary()

# -------------------------------------------------------------
# 3. Clustering Endpoints
# -------------------------------------------------------------
@router.post("/clustering/kmeans")
def run_kmeans(req: KMeansRequest):
    try:
        res = clustering_service.run_custom_kmeans(k=req.k, random_state=req.random_state)
        # Exclude large raw labels from response, return metrics and centroids
        clean_res = {k: v for k, v in res.items() if k != "labels"}
        return sanitize_for_json(clean_res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"K-Means execution failed: {str(e)}")

@router.get("/clustering/kmeans/evaluate")
def evaluate_kmeans_range(
    k_min: int = Query(2, ge=2, le=10),
    k_max: int = Query(8, ge=2, le=10),
    random_state: int = Query(42)
):
    try:
        return sanitize_for_json(clustering_service.evaluate_kmeans_range(k_min=k_min, k_max=k_max, random_state=random_state))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"K-Means evaluation failed: {str(e)}")

@router.get("/clustering/kmeans/stability")
def evaluate_kmeans_stability(
    k: int = Query(4, ge=2, le=10)
):
    try:
        return sanitize_for_json(clustering_service.evaluate_kmeans_stability(k=k))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"K-Means stability analysis failed: {str(e)}")

@router.post("/clustering/kmedoids")
def run_kmedoids(req: KMedoidsRequest):
    try:
        res = clustering_service.run_custom_kmedoids(k=req.k, random_state=req.random_state)
        clean_res = {k: v for k, v in res.items() if k != "labels"}
        return sanitize_for_json(clean_res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"K-Medoids execution failed: {str(e)}")

@router.post("/clustering/hierarchical")
def run_hierarchical(req: HierarchicalRequest):
    try:
        res = clustering_service.run_custom_hierarchical(
            k=req.k, linkage_method=req.linkage, metric=getattr(req, 'metric', 'euclidean') or 'euclidean', random_state=req.random_state
        )
        clean_res = {k: v for k, v in res.items() if k not in ["labels", "sample_labels", "sample_indices"]}
        return sanitize_for_json(clean_res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hierarchical execution failed: {str(e)}")

@router.get("/clustering/hierarchical/compare_linkages")
def compare_hierarchical_linkages(
    k: int = Query(4, ge=2, le=10),
    sample_size: int = Query(1500, ge=100, le=5000),
    random_state: int = Query(42)
):
    try:
        return sanitize_for_json(clustering_service.compare_hierarchical_linkages(k=k, sample_size=sample_size, random_state=random_state))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hierarchical linkage comparison failed: {str(e)}")

@router.post("/clustering/select")
def select_active_model(req: SelectModelRequest):
    try:
        clustering_service.set_active_model(req.model_key)
        return {
            "status": "success",
            "active_model_key": req.model_key,
            "message": f"Active model switched to {req.model_key}"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/clustering/compare", response_model=ModelComparisonResponse)
@router.post("/clustering/compare", response_model=ModelComparisonResponse)
def get_model_comparison():
    if clustering_service.comparison_cache is None:
        raise HTTPException(status_code=400, detail="Comparison cache not ready.")
    return clustering_service.comparison_cache

# -------------------------------------------------------------
# 4. Results Endpoints
# -------------------------------------------------------------
@router.get("/results/metrics")
def get_active_metrics():
    model = clustering_service.models_cache.get(clustering_service.active_model_key)
    if not model:
        raise HTTPException(status_code=404, detail="Active model metrics not found.")
    return sanitize_for_json({
        "active_model_key": clustering_service.active_model_key,
        "algorithm": model.get("algorithm"),
        "distance_metric": model.get("distance_metric"),
        "linkage": model.get("linkage", "N/A"),
        "k": model.get("k"),
        "silhouette_score": model.get("silhouette_score"),
        "davies_bouldin_index": model.get("davies_bouldin_index"),
        "wcss": model.get("wcss"),
        "manhattan_cost_sad": model.get("manhattan_cost_sad"),
        "cophenetic_correlation": model.get("cophenetic_correlation"),
        "balance_ratio": model.get("balance_ratio"),
        "cluster_sizes": model.get("cluster_sizes"),
        "cluster_percentages": model.get("cluster_percentages"),
        "runtime_seconds": model.get("runtime_seconds")
    })

@router.get("/results/clusters")
def get_active_clusters():
    return sanitize_for_json({
        "active_model_key": clustering_service.active_model_key,
        "profiles": clustering_service.active_profiles
    })

@router.get("/results/profiles", response_model=List[ClusterProfileItem])
def get_cluster_profiles():
    if clustering_service.active_profiles is None:
        raise HTTPException(status_code=400, detail="Active profiles not available.")
    return sanitize_for_json(clustering_service.active_profiles)

@router.get("/results/pca", response_model=PCAResponse)
def get_pca_projection():
    if clustering_service.active_pca is None:
        raise HTTPException(status_code=400, detail="PCA data not ready.")
    return sanitize_for_json(clustering_service.active_pca)

@router.get("/results/dendrogram", response_model=DendrogramResponse)
def get_dendrogram():
    # If active model has a dendrogram, return it
    active_model = clustering_service.models_cache.get(clustering_service.active_model_key)
    if active_model and "dendrogram" in active_model:
        return sanitize_for_json(active_model["dendrogram"])

    # Otherwise look up default or any cached hierarchical dendrogram
    hier_model = clustering_service.models_cache.get("hierarchical_ward_k4")
    if hier_model and "dendrogram" in hier_model:
        return sanitize_for_json(hier_model["dendrogram"])

    for model in clustering_service.models_cache.values():
        if "dendrogram" in model:
            return sanitize_for_json(model["dendrogram"])

    raise HTTPException(status_code=404, detail="Hierarchical dendrogram not found.")

@router.get("/results/geography", response_model=GeographyResponse)
def get_geography_analysis():
    if clustering_service.active_geography is None:
        raise HTTPException(status_code=400, detail="Geography analysis not ready.")
    return clustering_service.active_geography

@router.get("/results/temporal", response_model=TemporalResponse)
def get_temporal_analysis():
    if clustering_service.active_temporal is None:
        raise HTTPException(status_code=400, detail="Temporal analysis not ready.")
    return clustering_service.active_temporal

# -------------------------------------------------------------
# 5. Experiment Registry Endpoints
# -------------------------------------------------------------
@router.get("/experiments", response_model=List[ExperimentItem])
def get_registered_experiments():
    try:
        return clustering_service.registry.get_all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch experiments: {str(e)}")

@router.get("/experiments/{exp_id}")
def get_experiment_details(exp_id: str):
    exp = clustering_service.registry.get_by_id(exp_id)
    if not exp:
        raise HTTPException(status_code=404, detail=f"Experiment '{exp_id}' not found.")
    return exp

