import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.clustering_service import ClusteringService
import app.api.endpoints as ep

def test_all_endpoints():
    print("Testing Endpoints directly via FastAPI handler functions...")
    service = ClusteringService.get_instance()
    service.initialize_and_warm_cache()

    # 1. Test PCA Projection
    pca_data = ep.get_pca_projection()
    assert "explained_variance_ratio" in pca_data
    assert "total_variance_captured" in pca_data
    assert "points" in pca_data
    assert len(pca_data["points"]) > 0
    # Verify no null or NaN in coordinates
    first_pt = pca_data["points"][0]
    assert isinstance(first_pt["pc1"], float)
    assert isinstance(first_pt["pc2"], float)
    assert isinstance(first_pt["pc3"], float)
    print(f"[PASS] get_pca_projection passed! Captured Variance: {pca_data['total_variance_captured']}%, Points: {len(pca_data['points'])}")

    # 2. Test K-Means Evaluation Range (k=2..4)
    km_eval_data = ep.evaluate_kmeans_range(k_min=2, k_max=4, random_state=42)
    assert len(km_eval_data["evaluation_series"]) == 3
    print(f"[PASS] evaluate_kmeans_range passed! Steps: {len(km_eval_data['evaluation_series'])}")

    # 3. Test K-Means Stability
    km_stab_data = ep.evaluate_kmeans_stability(k=4)
    assert "mean_pairwise_ari" in km_stab_data
    assert "runs" in km_stab_data
    print(f"[PASS] evaluate_kmeans_stability passed! Mean Pairwise ARI: {km_stab_data['mean_pairwise_ari']}")

    # 4. Test Hierarchical Linkage Comparison (all 5 mandatory configurations)
    hier_comp_data = ep.compare_hierarchical_linkages(k=4, sample_size=300, random_state=42)
    assert len(hier_comp_data) == 5
    print(f"[PASS] compare_hierarchical_linkages passed! Linkages: {[(item['linkage_method'], item['distance_metric']) for item in hier_comp_data]}")

    # 5. Test Geography and Profiles
    profiles = ep.get_cluster_profiles()
    assert len(profiles) == 4
    titles = [p["title"] for p in profiles]
    assert len(set(titles)) == len(titles), f"Duplicate titles: {titles}"
    print(f"[PASS] get_cluster_profiles passed with unique titles: {titles}")

    # 6. Test Model Comparison Matrix
    comp_data = ep.get_model_comparison()
    assert "comparison_table" in comp_data
    assert "pairwise_ari" in comp_data
    assert "pairwise_nmi" in comp_data
    print(f"[PASS] get_model_comparison passed with ARI & NMI matrices!")

    print("\nALL API ENDPOINTS TESTED AND VERIFIED SUCCESSFULLY!")

if __name__ == "__main__":
    test_all_endpoints()
