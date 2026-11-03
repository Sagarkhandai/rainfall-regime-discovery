import time
from typing import Dict, Any, List, Optional
import numpy as np
from scipy.spatial.distance import cdist
from sklearn.metrics import silhouette_score, davies_bouldin_score

class ManhattanKMedoids:
    """
    K-Medoids partitioning using L1 Manhattan (cityblock) distance via CLARA
    (Clustering Large Applications, Kaufman & Rousseeuw 1990).
    
    Avoids $O(N^2)$ memory footprint by extracting representative subsamples,
    performing exact PAM medoid optimization within subsamples using L1 distance,
    and evaluating the total Manhattan Sum of Absolute Deviations (SAD) across the dataset.
    """

    @staticmethod
    def fit(
        X: np.ndarray,
        k: int = 4,
        num_samples: int = 5,
        sample_size: int = 1500,
        random_state: int = 42,
        eval_sample_size: int = 1500
    ) -> Dict[str, Any]:
        start_time = time.perf_counter()
        rng = np.random.RandomState(random_state)
        n_samples = X.shape[0]

        best_cost = float('inf')
        best_medoids = None
        best_medoid_indices = None

        effective_sample_size = min(sample_size, n_samples)

        # Multiple CLARA sampling iterations
        for sample_iter in range(num_samples):
            sub_indices = rng.choice(n_samples, size=effective_sample_size, replace=False)
            sub_X = X[sub_indices]

            # Initialize medoids with k-medoids++ heuristic or random selection from sample
            init_indices = rng.choice(effective_sample_size, size=k, replace=False)
            medoids = sub_X[init_indices].copy()

            # PAM optimization phase on the representative subsample
            for it in range(15):
                # Distance to medoids using L1 cityblock / Manhattan metric
                sub_dists = cdist(sub_X, medoids, metric='cityblock')
                sub_labels = np.argmin(sub_dists, axis=1)

                new_medoids = medoids.copy()
                improved = False

                for cluster_id in range(k):
                    cluster_members = sub_X[sub_labels == cluster_id]
                    if len(cluster_members) > 0:
                        # Find member with minimum sum of Manhattan distances to all other members in cluster
                        intra_dist = cdist(cluster_members, cluster_members, metric='cityblock').sum(axis=1)
                        best_medoid_candidate = cluster_members[np.argmin(intra_dist)]
                        if not np.array_equal(best_medoid_candidate, medoids[cluster_id]):
                            new_medoids[cluster_id] = best_medoid_candidate
                            improved = True

                medoids = new_medoids
                if not improved:
                    break

            # Evaluate Manhattan cost on a representative evaluation batch (5,000 points)
            eval_eval_size = min(5000, n_samples)
            eval_sample_idx = rng.choice(n_samples, size=eval_eval_size, replace=False)
            eval_dists = cdist(X[eval_sample_idx], medoids, metric='cityblock')
            total_manhattan_cost = float(np.sum(np.min(eval_dists, axis=1))) * (n_samples / eval_eval_size)

            if total_manhattan_cost < best_cost:
                best_cost = total_manhattan_cost
                best_medoids = medoids.copy()

        # Final assignment across all observations using optimal medoids in fast chunks
        labels = np.zeros(n_samples, dtype=np.int32)
        chunk_size = 50000
        for start_idx in range(0, n_samples, chunk_size):
            end_idx = min(start_idx + chunk_size, n_samples)
            chunk_dists = cdist(X[start_idx:end_idx], best_medoids, metric='cityblock')
            labels[start_idx:end_idx] = np.argmin(chunk_dists, axis=1)

        runtime = round(time.perf_counter() - start_time, 4)

        # Silhouette & Davies-Bouldin evaluation
        if n_samples > eval_sample_size:
            eval_idx = rng.choice(n_samples, size=eval_sample_size, replace=False)
            eval_X = X[eval_idx]
            eval_lbls = labels[eval_idx]
        else:
            eval_X = X
            eval_lbls = labels

        # Native Manhattan Silhouette Score (using L1 cityblock distance)
        manhattan_sil = float(silhouette_score(eval_X, eval_lbls, metric='cityblock'))
        
        # Supplementary Euclidean Davies-Bouldin diagnostic
        euclidean_dbi = float(davies_bouldin_score(eval_X, eval_lbls))

        # Native Manhattan Medoid Dispersion/Separation Index (L1 analogue of Davies-Bouldin)
        S = []
        for i in range(k):
            members = eval_X[eval_lbls == i]
            s_i = float(np.mean(np.sum(np.abs(members - best_medoids[i]), axis=1))) if len(members) > 0 else 0.0
            S.append(s_i)

        R = []
        for i in range(k):
            r_candidates = []
            for j in range(k):
                if i != j:
                    med_dist = float(np.sum(np.abs(best_medoids[i] - best_medoids[j])))
                    if med_dist > 1e-6:
                        r_candidates.append((S[i] + S[j]) / med_dist)
            R.append(max(r_candidates) if r_candidates else 0.0)
        manhattan_msi = round(float(np.mean(R)), 4) if R else 0.0

        unique, counts = np.unique(labels, return_counts=True)
        cluster_sizes = {int(u): int(c) for u, c in zip(unique, counts)}
        cluster_percentages = {int(u): round(float(c / n_samples * 100), 2) for u, c in zip(unique, counts)}

        min_size = min(counts)
        max_size = max(counts)
        balance_ratio = round(float(min_size / max_size), 4)

        return {
            "algorithm": "K-Medoids (CLARA / PAM)",
            "distance_metric": "Manhattan (L1 / Cityblock)",
            "k": k,
            "manhattan_cost_sad": round(best_cost, 2),  # Sum of Absolute Deviations (SAD)
            "silhouette_score": round(manhattan_sil, 4),  # Native Manhattan Silhouette
            "manhattan_silhouette": round(manhattan_sil, 4),
            "manhattan_dispersion_index": manhattan_msi,  # Native L1 Medoid Separation Index
            "davies_bouldin_index": round(euclidean_dbi, 4),  # Labeled as Euclidean diagnostic
            "euclidean_davies_bouldin_index": round(euclidean_dbi, 4),
            "cluster_sizes": cluster_sizes,
            "cluster_percentages": cluster_percentages,
            "balance_ratio": balance_ratio,
            "runtime_seconds": runtime,
            "labels": labels,
            "medoids": best_medoids.tolist(),
            "sampling_config": {
                "method": "CLARA (Clustering Large Applications - Kaufman & Rousseeuw 1990)",
                "num_samples": num_samples,
                "sample_size": effective_sample_size,
                "total_dataset_size": n_samples,
                "random_state": random_state,
                "metric_notes": "Silhouette uses native L1 cityblock distance. Davies-Bouldin is computed as supplementary Euclidean diagnostic alongside native Manhattan Dispersion Index."
            }
        }

