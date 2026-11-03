from typing import Dict, Any, List
import numpy as np
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

from app.core.json_util import sanitize_for_json

class ModelComparison:
    @staticmethod
    def compare_models(model_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Builds a comprehensive model comparison matrix including ARI and NMI.
        """
        comparison_table = []
        labels_map = {}

        for idx, res in enumerate(model_results):
            model_key = f"{res.get('algorithm')} (k={res.get('k')})"
            entry = {
                "id": idx,
                "model_key": model_key,
                "algorithm": res.get("algorithm"),
                "distance_metric": res.get("distance_metric"),
                "linkage": res.get("linkage", "N/A"),
                "k": res.get("k"),
                "silhouette_score": res.get("silhouette_score"),
                "davies_bouldin_index": res.get("davies_bouldin_index"),
                "objective_metric_name": "WCSS (Inertia)" if "wcss" in res else ("Manhattan Cost (SAD)" if "manhattan_cost_sad" in res else "Linkage Height"),
                "objective_metric_value": res.get("wcss") or res.get("manhattan_cost_sad") or res.get("cophenetic_correlation"),
                "balance_ratio": res.get("balance_ratio"),
                "cluster_sizes": res.get("cluster_sizes"),
                "runtime_seconds": res.get("runtime_seconds")
            }
            comparison_table.append(entry)
            if "labels" in res:
                labels_map[model_key] = res["labels"]

        # Determine common evaluation sample across models for fair ARI & NMI
        common_indices = None
        for res in model_results:
            if "sample_indices" in res:
                common_indices = res["sample_indices"]
                break

        # Build evaluation labels on identical common observations
        eval_labels_map = {}
        for idx, res in enumerate(model_results):
            model_key = f"{res.get('algorithm')} (k={res.get('k')})"
            if "sample_labels" in res:
                eval_labels_map[model_key] = np.array(res["sample_labels"])
            elif "labels" in res:
                all_lbls = np.array(res["labels"])
                if common_indices is not None and len(all_lbls) > len(common_indices):
                    eval_labels_map[model_key] = all_lbls[common_indices]
                else:
                    eval_labels_map[model_key] = all_lbls

        # Label-invariant pairwise similarity matrix (ARI and NMI) on identical observations
        model_names = list(eval_labels_map.keys())
        ari_matrix = {}
        nmi_matrix = {}

        for m1 in model_names:
            ari_matrix[m1] = {}
            nmi_matrix[m1] = {}
            for m2 in model_names:
                ari = float(adjusted_rand_score(eval_labels_map[m1], eval_labels_map[m2]))
                nmi = float(normalized_mutual_info_score(eval_labels_map[m1], eval_labels_map[m2]))
                ari_matrix[m1][m2] = round(ari, 4)
                nmi_matrix[m1][m2] = round(nmi, 4)

        sample_note = (
            f"ARI and NMI are evaluated strictly on the identical common stratified sample (N={len(common_indices)}) "
            "where genuine hierarchical clustering was performed."
            if common_indices is not None else
            "ARI and NMI are evaluated on the shared observation partition."
        )

        return sanitize_for_json({
            "comparison_table": comparison_table,
            "models_count": len(comparison_table),
            "common_sample_size": len(common_indices) if common_indices is not None else None,
            "pairwise_ari": ari_matrix,
            "pairwise_nmi": nmi_matrix,
            "evaluation_notes": [
                sample_note,
                "Adjusted Rand Index (ARI) evaluates label-invariant clustering agreement [-1 to +1].",
                "Normalized Mutual Information (NMI) evaluates shared cluster information [0 to 1].",
                "Standard K-Means minimizes squared Euclidean distance (WCSS).",
                "K-Medoids minimizes L1 Manhattan distance Sum of Absolute Deviations (SAD)."
            ]
        })

