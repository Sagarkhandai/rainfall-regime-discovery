import os
import json
import csv
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd

from app.core.json_util import sanitize_for_json

class ExperimentRegistry:
    _instance = None
    
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path(__file__).resolve().parent.parent.parent.parent / "outputs"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.json_path = self.output_dir / "experiments_registry.json"
        self.csv_path = self.output_dir / "experiments_registry.csv"
        self.experiments: List[Dict[str, Any]] = []
        self._load_from_disk()

    @classmethod
    def get_instance(cls) -> "ExperimentRegistry":
        if cls._instance is None:
            cls._instance = ExperimentRegistry()
        return cls._instance

    def _load_from_disk(self):
        if self.json_path.exists():
            try:
                with open(self.json_path, "r", encoding="utf-8") as f:
                    self.experiments = json.load(f)
            except Exception as e:
                print(f"[ExperimentRegistry] Warning loading existing registry: {e}")
                self.experiments = []

    def save_to_disk(self):
        try:
            # 1. Save JSON
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(self.experiments, f, indent=2)

            # 2. Save CSV summary table
            if self.experiments:
                flattened = []
                for exp in self.experiments:
                    flattened.append({
                        "experiment_id": exp.get("experiment_id"),
                        "timestamp": exp.get("timestamp"),
                        "observation_unit": exp.get("observation_unit"),
                        "algorithm": exp.get("algorithm"),
                        "distance_metric": exp.get("distance_metric"),
                        "linkage": exp.get("linkage", "N/A"),
                        "k": exp.get("k"),
                        "feature_count": exp.get("feature_count"),
                        "objective_metric": exp.get("objective_metric"),
                        "objective_value": exp.get("objective_value"),
                        "silhouette_score": exp.get("silhouette_score"),
                        "davies_bouldin_index": exp.get("davies_bouldin_index"),
                        "balance_ratio": exp.get("balance_ratio"),
                        "runtime_seconds": exp.get("runtime_seconds"),
                        "status": exp.get("status", "COMPLETED")
                    })
                df_exp = pd.DataFrame(flattened)
                df_exp.to_csv(self.csv_path, index=False)
        except Exception as e:
            print(f"[ExperimentRegistry] Warning saving registry: {e}")

    def register(
        self,
        algorithm: str,
        k: int,
        distance_metric: str,
        linkage: str = "N/A",
        observation_unit: str = "daily",
        feature_names: Optional[List[str]] = None,
        random_state: int = 42,
        objective_metric: str = "WCSS",
        objective_value: float = 0.0,
        silhouette_score: float = 0.0,
        davies_bouldin_index: float = 0.0,
        balance_ratio: float = 0.0,
        cluster_sizes: Optional[Dict[str, int]] = None,
        runtime_seconds: float = 0.0,
        sample_size: Optional[int] = None,
        stability_summary: Optional[Dict[str, Any]] = None,
        status: str = "COMPLETED",
        error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        exp_id = f"EXP_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{len(self.experiments)+1:03d}"
        
        record = sanitize_for_json({
            "experiment_id": exp_id,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "dataset_version": "weatherAUS.csv (145,460 BOM records)",
            "observation_unit": observation_unit,
            "algorithm": algorithm,
            "distance_metric": distance_metric,
            "linkage": linkage,
            "k": k,
            "feature_names": feature_names or [],
            "feature_count": len(feature_names) if feature_names else 0,
            "preprocessing": "SimpleImputer(median) + StandardScaler",
            "random_state": random_state,
            "sample_size": sample_size,
            "objective_metric": objective_metric,
            "objective_value": round(float(objective_value), 2) if objective_value is not None else None,
            "silhouette_score": round(float(silhouette_score), 4) if silhouette_score is not None else None,
            "davies_bouldin_index": round(float(davies_bouldin_index), 4) if davies_bouldin_index is not None else None,
            "balance_ratio": round(float(balance_ratio), 4) if balance_ratio is not None else None,
            "cluster_sizes": cluster_sizes or {},
            "runtime_seconds": round(float(runtime_seconds), 4),
            "stability_summary": stability_summary,
            "status": status,
            "error_message": error_message
        })

        self.experiments.append(record)
        self.save_to_disk()
        return record

    def get_all(self) -> List[Dict[str, Any]]:
        return self.experiments

    def get_by_id(self, exp_id: str) -> Optional[Dict[str, Any]]:
        for exp in self.experiments:
            if exp.get("experiment_id") == exp_id:
                return exp
        return None

