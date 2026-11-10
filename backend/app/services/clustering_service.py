from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd

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
from app.services.experiment_registry import ExperimentRegistry

class ClusteringService:
    _instance = None

    def __init__(self):
        self.raw_df: Optional[pd.DataFrame] = None
        self.processed_df: Optional[pd.DataFrame] = None
        self.X_scaled: Optional[np.ndarray] = None
        self.pipeline: Optional[PreprocessingPipeline] = None
        self.registry: ExperimentRegistry = ExperimentRegistry.get_instance()

        # Cache of fitted models and analytics
        self.models_cache: Dict[str, Dict[str, Any]] = {}
        self.active_model_key: str = "kmeans_k4"
        self.active_profiles: Optional[List[Dict[str, Any]]] = None
        self.active_pca: Optional[Dict[str, Any]] = None
        self.active_geography: Optional[Dict[str, Any]] = None
        self.active_temporal: Optional[Dict[str, Any]] = None
        self.comparison_cache: Optional[Dict[str, Any]] = None
        self.kmeans_eval_cache: Dict[Any, Any] = {}
        self.kmeans_stability_cache: Dict[Any, Any] = {}
        self.hierarchical_linkages_cache: Dict[Any, Any] = {}

    @classmethod
    def get_instance(cls) -> "ClusteringService":
        if cls._instance is None:
            cls._instance = ClusteringService()
        return cls._instance

    def initialize_and_warm_cache(
        self,
        features: Optional[List[str]] = None,
        use_log_rainfall: bool = True,
        observation_unit: str = "daily"
    ):
        """
        Runs initial data loading, preprocessing, baseline models (K-Means, K-Medoids, Hierarchical),
        and caches the primary analytics for instantaneous response.
        """
        print("[ClusteringService] Initializing data and warming cache...")
        self.models_cache = {}
        self.kmeans_eval_cache = {}
        self.kmeans_stability_cache = {}
        self.hierarchical_linkages_cache = {}
        self.raw_df = DataLoader.load_raw_dataset()
        self.pipeline = PreprocessingPipeline(
            features=features,
            use_log_rainfall=use_log_rainfall,
            observation_unit=observation_unit
        )
        self.X_scaled, self.processed_df = self.pipeline.fit_transform(self.raw_df)

        # 1. Fit Primary Baseline: K-Means (k=4)
        print("[ClusteringService] Fitting K-Means (k=4)...")
        km4 = KMeansClustering.fit_single(self.X_scaled, k=4, random_state=42)
        self.models_cache["kmeans_k4"] = km4
        self.registry.register(
            algorithm="K-Means",
            k=4,
            distance_metric="Squared Euclidean",
            observation_unit=self.pipeline.observation_unit,
            feature_names=self.pipeline.fitted_feature_names,
            objective_metric="WCSS (Inertia)",
            objective_value=km4["wcss"],
            silhouette_score=km4["silhouette_score"],
            davies_bouldin_index=km4["davies_bouldin_index"],
            balance_ratio=km4["balance_ratio"],
            cluster_sizes=km4["cluster_sizes"],
            runtime_seconds=km4["runtime_seconds"]
        )

        # 2. Fit K-Medoids Manhattan (k=4) via CLARA
        print("[ClusteringService] Fitting K-Medoids Manhattan (k=4)...")
        kmed4 = ManhattanKMedoids.fit(self.X_scaled, k=4, num_samples=2, sample_size=800, random_state=42)
        self.models_cache["kmedoids_k4"] = kmed4
        self.registry.register(
            algorithm="K-Medoids (CLARA / PAM)",
            k=4,
            distance_metric="Manhattan (L1 / Cityblock)",
            observation_unit=self.pipeline.observation_unit,
            feature_names=self.pipeline.fitted_feature_names,
            objective_metric="Manhattan Cost (SAD)",
            objective_value=kmed4["manhattan_cost_sad"],
            silhouette_score=kmed4["silhouette_score"],
            davies_bouldin_index=kmed4["davies_bouldin_index"],
            balance_ratio=kmed4["balance_ratio"],
            cluster_sizes=kmed4["cluster_sizes"],
            runtime_seconds=kmed4["runtime_seconds"],
            sample_size=kmed4["sampling_config"]["sample_size"]
        )

        # 3. Fit Hierarchical Ward (k=4)
        print("[ClusteringService] Fitting Hierarchical Ward (k=4)...")
        hier_ward = HierarchicalClustering.fit(
            self.X_scaled, k=4, linkage_method="ward", metric="euclidean", sample_size=800, random_state=42,
            locations=self.raw_df['Location'] if 'Location' in self.raw_df.columns else None
        )
        self.models_cache["hierarchical_ward_k4"] = hier_ward
        self.registry.register(
            algorithm="Agglomerative Hierarchical",
            k=4,
            distance_metric="Euclidean",
            linkage="ward",
            observation_unit=self.pipeline.observation_unit,
            feature_names=self.pipeline.fitted_feature_names,
            objective_metric="Cophenetic Correlation",
            objective_value=hier_ward["cophenetic_correlation"],
            silhouette_score=hier_ward["silhouette_score"],
            davies_bouldin_index=hier_ward["davies_bouldin_index"],
            balance_ratio=hier_ward["balance_ratio"],
            cluster_sizes=hier_ward["cluster_sizes"],
            runtime_seconds=hier_ward["runtime_seconds"],
            sample_size=hier_ward["sampling_config"]["sample_size"]
        )

        # 4. Compute Model Comparison Matrix
        print("[ClusteringService] Computing multi-model comparison matrix...")
        self.comparison_cache = ModelComparison.compare_models([
            km4, kmed4, hier_ward
        ])

        # 5. Set Active Model to K-Means k=4 and generate all downstream analytics
        self.set_active_model("kmeans_k4")

        # 6. Pre-warm K-Means evaluation, stability, and hierarchical linkages
        print("[ClusteringService] Pre-computing K-Means evaluation (k=2..8)...")
        self.evaluate_kmeans_range(k_min=2, k_max=8, random_state=42)
        print("[ClusteringService] Pre-computing K-Means stability (k=4)...")
        self.evaluate_kmeans_stability(k=4)
        print("[ClusteringService] Pre-computing Hierarchical 5-linkages (k=4)...")
        self.compare_hierarchical_linkages(k=4, sample_size=1500, random_state=42)
        print("[ClusteringService] Cache warming complete. Ready for high-throughput serving.")

    def set_active_model(self, model_key: str):
        if model_key not in self.models_cache:
            raise KeyError(f"Model key '{model_key}' not found in cache.")

        self.active_model_key = model_key
        model = self.models_cache[model_key]
        labels = model["labels"]

        # Ensure downstream metadata matches observation unit (daily vs monthly)
        active_df = self.processed_df if (self.pipeline and self.pipeline.observation_unit == "location_monthly") else self.raw_df

        # 1. Cluster Profiles
        self.active_profiles = ProfilingService.profile_clusters(active_df, labels)

        # 2. PCA Coordinates
        self.active_pca = PCAReduction.compute(
            X=self.X_scaled,
            feature_names=self.pipeline.fitted_feature_names,
            labels=labels,
            metadata_df=active_df,
            max_scatter_points=2500,
            random_state=42
        )

        # 3. Geography Analysis
        self.active_geography = GeographyService.analyze_geography(
            active_df, labels, self.active_profiles
        )

        # 4. Temporal Analysis
        self.active_temporal = TemporalService.analyze_temporal(
            active_df, labels, self.active_profiles
        )

    def run_custom_kmeans(self, k: int, random_state: int = 42) -> Dict[str, Any]:
        key = f"kmeans_k{k}_s{random_state}"
        if key not in self.models_cache:
            res = KMeansClustering.fit_single(self.X_scaled, k=k, random_state=random_state)
            self.models_cache[key] = res
            self.registry.register(
                algorithm="K-Means",
                k=k,
                distance_metric="Squared Euclidean",
                observation_unit=self.pipeline.observation_unit if self.pipeline else "daily",
                feature_names=self.pipeline.fitted_feature_names if self.pipeline else [],
                objective_metric="WCSS (Inertia)",
                objective_value=res["wcss"],
                silhouette_score=res["silhouette_score"],
                davies_bouldin_index=res["davies_bouldin_index"],
                balance_ratio=res["balance_ratio"],
                cluster_sizes=res["cluster_sizes"],
                runtime_seconds=res["runtime_seconds"]
            )
            self.comparison_cache = ModelComparison.compare_models(list(self.models_cache.values()))
        self.set_active_model(key)
        return self.models_cache[key]

    def run_custom_kmedoids(self, k: int, random_state: int = 42) -> Dict[str, Any]:
        key = f"kmedoids_k{k}_s{random_state}"
        if key not in self.models_cache:
            res = ManhattanKMedoids.fit(self.X_scaled, k=k, num_samples=3, sample_size=1000, random_state=random_state)
            self.models_cache[key] = res
            self.registry.register(
                algorithm="K-Medoids (CLARA / PAM)",
                k=k,
                distance_metric="Manhattan (L1 / Cityblock)",
                observation_unit=self.pipeline.observation_unit if self.pipeline else "daily",
                feature_names=self.pipeline.fitted_feature_names if self.pipeline else [],
                objective_metric="Manhattan Cost (SAD)",
                objective_value=res["manhattan_cost_sad"],
                silhouette_score=res["silhouette_score"],
                davies_bouldin_index=res["davies_bouldin_index"],
                balance_ratio=res["balance_ratio"],
                cluster_sizes=res["cluster_sizes"],
                runtime_seconds=res["runtime_seconds"],
                sample_size=res["sampling_config"]["sample_size"]
            )
            self.comparison_cache = ModelComparison.compare_models(list(self.models_cache.values()))
        self.set_active_model(key)
        return self.models_cache[key]

    def run_custom_hierarchical(self, k: int, linkage_method: str = "ward", metric: str = "euclidean", random_state: int = 42) -> Dict[str, Any]:
        key = f"hierarchical_{linkage_method}_{metric}_k{k}_s{random_state}"
        if key not in self.models_cache:
            res = HierarchicalClustering.fit(
                self.X_scaled, k=k, linkage_method=linkage_method, metric=metric, sample_size=1000, random_state=random_state,
                locations=self.raw_df['Location'] if (self.raw_df is not None and 'Location' in self.raw_df.columns) else None
            )
            self.models_cache[key] = res
            self.registry.register(
                algorithm=f"Agglomerative ({linkage_method.capitalize()})",
                k=k,
                distance_metric=res["distance_metric"],
                linkage=linkage_method,
                observation_unit=self.pipeline.observation_unit if self.pipeline else "daily",
                feature_names=self.pipeline.fitted_feature_names if self.pipeline else [],
                objective_metric="Cophenetic Correlation",
                objective_value=res["cophenetic_correlation"],
                silhouette_score=res["silhouette_score"],
                davies_bouldin_index=res["davies_bouldin_index"],
                balance_ratio=res["balance_ratio"],
                cluster_sizes=res["cluster_sizes"],
                runtime_seconds=res["runtime_seconds"],
                sample_size=res["sampling_config"]["sample_size"]
            )
            self.comparison_cache = ModelComparison.compare_models(list(self.models_cache.values()))
        self.set_active_model(key)
        return self.models_cache[key]

    def evaluate_kmeans_range(self, k_min: int = 2, k_max: int = 8, random_state: int = 42) -> Dict[str, Any]:
        key = (k_min, k_max, random_state)
        if key not in self.kmeans_eval_cache:
            self.kmeans_eval_cache[key] = KMeansClustering.evaluate_range(self.X_scaled, k_min=k_min, k_max=k_max, random_state=random_state)
        return self.kmeans_eval_cache[key]

    def evaluate_kmeans_stability(self, k: int = 4, seeds: Optional[List[int]] = None) -> Dict[str, Any]:
        seeds_tuple = tuple(seeds) if seeds else (42, 101, 7, 2024, 99)
        key = (k, seeds_tuple)
        if key not in self.kmeans_stability_cache:
            self.kmeans_stability_cache[key] = KMeansClustering.evaluate_stability(self.X_scaled, k=k, seeds=list(seeds_tuple))
        return self.kmeans_stability_cache[key]

    def compare_hierarchical_linkages(self, k: int = 4, sample_size: int = 1500, random_state: int = 42) -> List[Dict[str, Any]]:
        key = (k, sample_size, random_state)
        if key not in self.hierarchical_linkages_cache:
            self.hierarchical_linkages_cache[key] = HierarchicalClustering.compare_linkages(
                self.X_scaled, k=k, sample_size=sample_size, random_state=random_state,
                locations=self.raw_df['Location'] if (self.raw_df is not None and 'Location' in self.raw_df.columns) else None
            )
        return self.hierarchical_linkages_cache[key]

