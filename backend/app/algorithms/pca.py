from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

from app.core.json_util import sanitize_for_json

class PCAReduction:
    @staticmethod
    def compute(
        X: np.ndarray,
        feature_names: List[str],
        labels: Optional[np.ndarray] = None,
        metadata_df: Optional[pd.DataFrame] = None,
        max_scatter_points: int = 2500,
        random_state: int = 42
    ) -> Dict[str, Any]:
        """
        Fit PCA on standardized features, compute explained variance and loadings,
        and generate 3D/2D coordinates for visualization.
        """
        pca = PCA(n_components=min(len(feature_names), 3), random_state=random_state)
        coords = pca.fit_transform(X)

        explained_variance_ratio = [round(float(v), 4) for v in pca.explained_variance_ratio_]
        cumulative_variance = [round(float(v), 4) for v in np.cumsum(pca.explained_variance_ratio_)]

        # Feature Loadings: components_ has shape (n_components, n_features)
        # PC loadings indicate the contribution and direction of each physical variable
        loadings = {}
        for i, pc_name in enumerate(["PC1", "PC2", "PC3"][:pca.n_components_]):
            loadings[pc_name] = {
                feat: round(float(pca.components_[i, j]), 4)
                for j, feat in enumerate(feature_names)
            }

        # Interpret physical meaning of components based on top absolute loadings
        pc_interpretations = {}
        for i, pc_name in enumerate(["PC1", "PC2", "PC3"][:pca.n_components_]):
            sorted_feats = sorted(loadings[pc_name].items(), key=lambda x: abs(x[1]), reverse=True)
            top_feats = [f"{f} ({w:+0.2f})" for f, w in sorted_feats[:3]]
            pc_interpretations[pc_name] = ", ".join(top_feats)

        # Subsample for interactive 3D WebGL rendering
        n_samples = len(X)
        if n_samples > max_scatter_points:
            rng = np.random.RandomState(random_state)
            # Stratified sampling across clusters if labels provided
            if labels is not None:
                sample_indices = []
                unique_clusters = np.unique(labels)
                per_cluster = max_scatter_points // len(unique_clusters)
                for c in unique_clusters:
                    c_indices = np.where(labels == c)[0]
                    chosen = rng.choice(c_indices, size=min(per_cluster, len(c_indices)), replace=False)
                    sample_indices.extend(chosen)
                sample_indices = np.array(sample_indices)
            else:
                sample_indices = rng.choice(n_samples, size=max_scatter_points, replace=False)
        else:
            sample_indices = np.arange(n_samples)

        # Build point records
        points = []
        for idx in sample_indices:
            pt = {
                "id": int(idx),
                "pc1": round(float(coords[idx, 0]), 3),
                "pc2": round(float(coords[idx, 1]), 3),
                "pc3": round(float(coords[idx, 2]), 3) if coords.shape[1] > 2 else 0.0,
                "cluster": int(labels[idx]) if labels is not None else 0
            }
            if metadata_df is not None:
                if 'Location' in metadata_df.columns:
                    pt["location"] = str(metadata_df.iloc[idx]['Location'])
                if 'Date' in metadata_df.columns:
                    d_val = metadata_df.iloc[idx]['Date']
                    pt["date"] = str(d_val.strftime('%Y-%m-%d')) if pd.notnull(d_val) and hasattr(d_val, 'strftime') else str(d_val)
                if 'Rainfall' in metadata_df.columns:
                    r_val = metadata_df.iloc[idx]['Rainfall']
                    pt["rainfall"] = round(float(r_val), 1) if pd.notnull(r_val) and not np.isnan(r_val) else None
            points.append(pt)

        # Eigenvector 3D vectors for visual compass/axes
        eigenvectors = []
        for i, pc_name in enumerate(["PC1", "PC2", "PC3"][:pca.n_components_]):
            # 3D direction vector
            vec = [0.0, 0.0, 0.0]
            vec[i] = 1.0
            eigenvectors.append({
                "component": pc_name,
                "variance_ratio": explained_variance_ratio[i],
                "vector": vec,
                "top_influencers": pc_interpretations[pc_name]
            })

        return sanitize_for_json({
            "explained_variance_ratio": explained_variance_ratio,
            "cumulative_variance": cumulative_variance,
            "feature_loadings": loadings,
            "interpretations": pc_interpretations,
            "eigenvectors": eigenvectors,
            "total_variance_captured": round(float(cumulative_variance[-1] * 100), 2),
            "points": points,
            "points_count": len(points),
            "total_observations": n_samples
        })

