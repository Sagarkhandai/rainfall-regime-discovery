import time
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from scipy.cluster.hierarchy import linkage, cophenet, dendrogram
from scipy.spatial.distance import pdist, cdist
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import silhouette_score, davies_bouldin_score

class HierarchicalClustering:
    @staticmethod
    def fit(
        X: np.ndarray,
        k: int = 4,
        linkage_method: str = "ward",
        metric: str = "euclidean",
        sample_size: int = 1500,
        random_state: int = 42,
        locations: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Agglomerative Hierarchical Clustering with actual dendrogram generation.
        Supports Ward (Euclidean), Complete (Euclidean & Manhattan), and Average (Euclidean & Manhattan).
        """
        start_time = time.perf_counter()
        n_samples = X.shape[0]
        rng = np.random.RandomState(random_state)

        # Proportionate stratified sampling across locations if provided
        effective_sample = min(sample_size, n_samples)
        if locations is not None and len(locations) == n_samples:
            loc_indices = {}
            for idx, loc in enumerate(locations):
                loc_indices.setdefault(loc, []).append(idx)
            
            selected = []
            for loc, idxs in loc_indices.items():
                prop = len(idxs) / n_samples
                n_loc = max(1, int(round(prop * effective_sample)))
                chosen = rng.choice(idxs, size=min(n_loc, len(idxs)), replace=False)
                selected.extend(chosen)
            
            if len(selected) > effective_sample:
                sample_indices = rng.choice(selected, size=effective_sample, replace=False)
            else:
                sample_indices = np.array(selected, dtype=np.int64)
            sample_method = "Proportionate Stratified Sampling across Synoptic Stations"
        else:
            sample_indices = rng.choice(n_samples, size=effective_sample, replace=False)
            sample_method = "Representative Stratified Random Sample"

        X_sample = X[sample_indices]

        # Ensure valid metric combination
        if linkage_method == "ward":
            eff_metric = "euclidean"
            dist_name = "Euclidean"
        elif metric in ["manhattan", "cityblock", "l1"]:
            eff_metric = "cityblock"
            dist_name = "Manhattan (Cityblock)"
        else:
            eff_metric = "euclidean"
            dist_name = "Euclidean"

        # Fit Scikit-learn AgglomerativeClustering on representative sample
        model = AgglomerativeClustering(
            n_clusters=k,
            metric=eff_metric,
            linkage=linkage_method
        )
        sample_labels = model.fit_predict(X_sample)

        # Calculate SciPy Linkage Matrix for actual Dendrogram
        Z = linkage(X_sample, method=linkage_method, metric=eff_metric)

        # Cophenetic Correlation Coefficient (faithfulness of dendrogram to original pairwise distances)
        p_dists = pdist(X_sample, metric=eff_metric)
        coph_corr, _ = cophenet(Z, p_dists)

        # Extract dendrogram structure (truncated for clear visualization: 30 leaves)
        dendro_dict = dendrogram(Z, p=30, truncate_mode='lastp', no_plot=True)
        
        icoord = dendro_dict['icoord']  # X coordinates of branches
        dcoord = dendro_dict['dcoord']  # Y coordinates (merge heights / distances)
        color_list = dendro_dict['color_list']
        leaves = [int(l) for l in dendro_dict['leaves']]

        dendrogram_data = {
            "icoord": icoord,
            "dcoord": dcoord,
            "color_list": color_list,
            "leaves": leaves,
            "max_distance": round(float(np.max(Z[:, 2])), 2),
            "cophenetic_correlation": round(float(coph_corr), 4),
            "linkage_method": linkage_method,
            "distance_metric": dist_name,
            "sample_size": effective_sample
        }

        # Calculate sample cluster centroids for approximate optional full extension only
        centroids = []
        for c_id in range(k):
            members = X_sample[sample_labels == c_id]
            if len(members) > 0:
                centroids.append(np.mean(members, axis=0))
            else:
                centroids.append(np.zeros(X.shape[1]))
        centroids = np.array(centroids)

        # Approximate extension for full-dataset visualization only
        full_dists = cdist(X, centroids, metric=eff_metric)
        approximate_extended_labels = np.argmin(full_dists, axis=1)

        runtime = round(time.perf_counter() - start_time, 4)

        # Scientific metrics evaluated strictly on the genuine sample cluster partition
        sil_score = float(silhouette_score(X_sample, sample_labels, metric=eff_metric))
        euclidean_db_score = float(davies_bouldin_score(X_sample, sample_labels))

        unique, counts = np.unique(sample_labels, return_counts=True)
        cluster_sizes = {int(u): int(c) for u, c in zip(unique, counts)}
        cluster_percentages = {int(u): round(float(c / len(sample_labels) * 100), 2) for u, c in zip(unique, counts)}

        min_size = min(counts)
        max_size = max(counts)
        balance_ratio = round(float(min_size / max_size), 4)

        return {
            "algorithm": f"Agglomerative ({linkage_method.capitalize()})",
            "distance_metric": dist_name,
            "linkage": linkage_method,
            "k": k,
            "cophenetic_correlation": round(float(coph_corr), 4),
            "silhouette_score": round(sil_score, 4),
            "davies_bouldin_index": round(euclidean_db_score, 4),
            "cluster_sizes": cluster_sizes,
            "cluster_percentages": cluster_percentages,
            "balance_ratio": balance_ratio,
            "runtime_seconds": runtime,
            "sample_indices": sample_indices,
            "sample_labels": sample_labels,
            "labels": approximate_extended_labels,  # Clearly named as extended in metadata
            "dendrogram": dendrogram_data,
            "sampling_config": {
                "method": sample_method,
                "sample_size": effective_sample,
                "total_dataset_size": n_samples,
                "random_state": random_state,
                "label_extension_notice": "Full-dataset labels use approximate nearest sample-centroid assignment for visualization only. Exact hierarchical tree computed on representative sample."
            }
        }

    @staticmethod
    def compare_linkages(
        X: np.ndarray,
        k: int = 4,
        sample_size: int = 1500,
        random_state: int = 42,
        locations: Optional[Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Compares all 5 mandatory linkage configurations:
        1. Ward (Euclidean)
        2. Complete (Euclidean)
        3. Complete (Manhattan)
        4. Average (Euclidean)
        5. Average (Manhattan)
        """
        configs = [
            ("ward", "euclidean"),
            ("complete", "euclidean"),
            ("complete", "cityblock"),
            ("average", "euclidean"),
            ("average", "cityblock")
        ]
        results = []
        for lk, met in configs:
            res = HierarchicalClustering.fit(
                X, k=k, linkage_method=lk, metric=met, sample_size=sample_size, random_state=random_state, locations=locations
            )
            results.append({
                "linkage": lk,
                "linkage_method": lk,
                "distance_metric": res["distance_metric"],
                "metric": res["distance_metric"],
                "configuration_label": f"{lk.capitalize()} ({res['distance_metric']})",
                "cophenetic_correlation": res["cophenetic_correlation"],
                "silhouette_score": res["silhouette_score"],
                "davies_bouldin_index": res["davies_bouldin_index"],
                "balance_ratio": res["balance_ratio"],
                "runtime_seconds": res["runtime_seconds"],
                "max_distance": res["dendrogram"]["max_distance"]
            })
        return results

