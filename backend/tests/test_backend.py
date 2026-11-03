import numpy as np
import pandas as pd
from pathlib import Path
import sys

# Ensure backend root is in python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.preprocessing.data_loader import DataLoader
from app.preprocessing.pipeline import PreprocessingPipeline
from app.algorithms.kmeans import KMeansClustering
from app.algorithms.kmedoids import ManhattanKMedoids
from app.algorithms.hierarchical import HierarchicalClustering
from app.algorithms.pca import PCAReduction
from app.algorithms.comparison import ModelComparison
from app.services.profiling_service import ProfilingService
from app.services.geography_service import GeographyService
from app.services.temporal_service import TemporalService

def test_data_loader_and_summary():
    df = DataLoader.load_raw_dataset()
    assert df is not None
    assert len(df) == 145460
    assert "Rainfall" in df.columns
    assert "Location" in df.columns

    summary = DataLoader.get_dataset_summary(df)
    assert summary["total_observations"] == 145460
    assert summary["unique_locations"] == 49
    assert summary["date_range"]["min"] == "2007-11-01"
    assert "rainfall_distribution" in summary
    assert summary["rainfall_distribution"]["mean"] > 0

def test_preprocessing_pipeline():
    df = DataLoader.load_raw_dataset()
    pipeline = PreprocessingPipeline(use_log_rainfall=True)
    X_scaled, processed_df = pipeline.fit_transform(df)

    assert X_scaled.shape[0] == 145460
    assert X_scaled.shape[1] == len(pipeline.fitted_feature_names)
    assert not np.isnan(X_scaled).any(), "Scaled feature matrix contains NaNs!"
    assert "RainTomorrow" not in pipeline.fitted_feature_names
    assert "RainToday" not in pipeline.fitted_feature_names

    # Check zero mean and unit variance
    means = np.mean(X_scaled, axis=0)
    stds = np.std(X_scaled, axis=0)
    np.testing.assert_allclose(means, 0.0, atol=1e-2)
    np.testing.assert_allclose(stds, 1.0, atol=1e-2)

def test_kmeans_and_stability():
    df = DataLoader.load_raw_dataset()
    pipeline = PreprocessingPipeline(use_log_rainfall=True)
    X_scaled, _ = pipeline.fit_transform(df)

    res = KMeansClustering.fit_single(X_scaled, k=4, random_state=42)
    assert res["algorithm"] == "K-Means"
    assert res["wcss"] > 0
    assert 0 <= res["silhouette_score"] <= 1.0
    assert res["davies_bouldin_index"] > 0
    assert len(res["labels"]) == 145460
    assert len(res["centroids"]) == 4

    stability = KMeansClustering.evaluate_stability(X_scaled, k=4, seeds=[42, 101])
    assert "wcss_mean" in stability
    assert "mean_pairwise_ari" in stability
    assert stability["mean_pairwise_ari"] > 0.5

def test_manhattan_kmedoids_clara():
    df = DataLoader.load_raw_dataset()
    pipeline = PreprocessingPipeline(use_log_rainfall=True)
    X_scaled, _ = pipeline.fit_transform(df)

    res = ManhattanKMedoids.fit(X_scaled, k=4, num_samples=2, sample_size=500, random_state=42)
    assert res["algorithm"] == "K-Medoids (CLARA / PAM)"
    assert res["distance_metric"] == "Manhattan (L1 / Cityblock)"
    assert res["manhattan_cost_sad"] > 0
    assert len(res["medoids"]) == 4
    assert len(res["labels"]) == 145460

def test_hierarchical_clustering_and_dendrogram():
    df = DataLoader.load_raw_dataset()
    pipeline = PreprocessingPipeline(use_log_rainfall=True)
    X_scaled, _ = pipeline.fit_transform(df)

    res = HierarchicalClustering.fit(X_scaled, k=4, linkage_method="ward", sample_size=500, random_state=42)
    assert "Agglomerative" in res["algorithm"]
    assert res["cophenetic_correlation"] > 0
    assert "dendrogram" in res
    assert "icoord" in res["dendrogram"]
    assert "dcoord" in res["dendrogram"]
    assert len(res["labels"]) == 145460

def test_pca_reduction():
    df = DataLoader.load_raw_dataset()
    pipeline = PreprocessingPipeline(use_log_rainfall=True)
    X_scaled, _ = pipeline.fit_transform(df)
    km = KMeansClustering.fit_single(X_scaled, k=4, random_state=42)

    pca_res = PCAReduction.compute(
        X_scaled,
        feature_names=pipeline.fitted_feature_names,
        labels=km["labels"],
        metadata_df=df,
        max_scatter_points=500
    )
    assert len(pca_res["explained_variance_ratio"]) == 3
    assert pca_res["total_variance_captured"] > 50.0
    assert len(pca_res["points"]) == 500
    assert "pc1" in pca_res["points"][0]
    assert "pc2" in pca_res["points"][0]
    assert "pc3" in pca_res["points"][0]
    assert "eigenvectors" in pca_res

def test_profiling_and_geography_and_temporal():
    df = DataLoader.load_raw_dataset()
    pipeline = PreprocessingPipeline(use_log_rainfall=True)
    X_scaled, _ = pipeline.fit_transform(df)
    km = KMeansClustering.fit_single(X_scaled, k=4, random_state=42)

    profiles = ProfilingService.profile_clusters(df, km["labels"])
    assert len(profiles) == 4
    for p in profiles:
        assert "regime_number" in p
        assert "title" in p
        assert "metrics" in p

    geo = GeographyService.analyze_geography(df, km["labels"], profiles)
    assert geo["total_stations"] == 49
    assert len(geo["continental_distribution"]) == 4

    temp = TemporalService.analyze_temporal(df, km["labels"], profiles)
    assert len(temp["monthly_distribution"]) == 12
    assert len(temp["seasonal_distribution"]) == 4
    assert len(temp["yearly_distribution"]) >= 10
    assert "transition_matrix" in temp

def test_model_comparison_matrix():
    df = DataLoader.load_raw_dataset()
    pipeline = PreprocessingPipeline(use_log_rainfall=True)
    X_scaled, _ = pipeline.fit_transform(df)

    km = KMeansClustering.fit_single(X_scaled, k=4, random_state=42)
    kmed = ManhattanKMedoids.fit(X_scaled, k=4, num_samples=2, sample_size=500, random_state=42)

    comp = ModelComparison.compare_models([km, kmed])
    assert comp["models_count"] == 2
    assert "pairwise_ari" in comp
    assert "pairwise_nmi" in comp

if __name__ == "__main__":
    print("Running test_data_loader_and_summary()...")
    test_data_loader_and_summary()
    print("[PASS] test_data_loader_and_summary passed!")

    print("Running test_preprocessing_pipeline()...")
    test_preprocessing_pipeline()
    print("[PASS] test_preprocessing_pipeline passed!")

    print("Running test_kmeans_and_stability()...")
    test_kmeans_and_stability()
    print("[PASS] test_kmeans_and_stability passed!")

    print("Running test_manhattan_kmedoids_clara()...")
    test_manhattan_kmedoids_clara()
    print("[PASS] test_manhattan_kmedoids_clara passed!")

    print("Running test_hierarchical_clustering_and_dendrogram()...")
    test_hierarchical_clustering_and_dendrogram()
    print("[PASS] test_hierarchical_clustering_and_dendrogram passed!")

    print("Running test_pca_reduction()...")
    test_pca_reduction()
    print("[PASS] test_pca_reduction passed!")

    print("Running test_profiling_and_geography_and_temporal()...")
    test_profiling_and_geography_and_temporal()
    print("[PASS] test_profiling_and_geography_and_temporal passed!")

    print("Running test_model_comparison_matrix()...")
    test_model_comparison_matrix()
    print("[PASS] test_model_comparison_matrix passed!")

    print("\nALL BACKEND ALGORITHMS AND SERVICES PASSED VALIDATION!")
