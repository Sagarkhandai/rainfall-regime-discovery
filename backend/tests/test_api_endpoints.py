import sys
from pathlib import Path
from fastapi.testclient import TestClient

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.main import app

def test_api():
    with TestClient(app) as client:
        print("Testing GET / ...")
        r = client.get("/")
        assert r.status_code == 200, r.text
        print("[PASS] Root OK")

        print("Testing GET /api/health ...")
        r = client.get("/api/health")
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["status"] == "healthy"
        print("[PASS] Health OK")

        print("Testing GET /api/dataset/summary ...")
        r = client.get("/api/dataset/summary")
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["total_observations"] == 145460
        assert data["unique_locations"] == 49
        print("[PASS] Dataset Summary OK")

        print("Testing GET /api/results/metrics ...")
        r = client.get("/api/results/metrics")
        assert r.status_code == 200, r.text
        data = r.json()
        assert "silhouette_score" in data
        assert "davies_bouldin_index" in data
        print("[PASS] Results Metrics OK")

        print("Testing GET /api/results/profiles ...")
        r = client.get("/api/results/profiles")
        assert r.status_code == 200, r.text
        data = r.json()
        assert len(data) == 4
        for p in data:
            assert "title" in p
            assert "metrics" in p
        print("[PASS] Profiles OK")

        print("Testing GET /api/results/pca ...")
        r = client.get("/api/results/pca")
        assert r.status_code == 200, r.text
        data = r.json()
        assert len(data["points"]) > 0
        assert "explained_variance_ratio" in data
        print("[PASS] PCA OK")

        print("Testing GET /api/results/dendrogram ...")
        r = client.get("/api/results/dendrogram")
        assert r.status_code == 200, r.text
        data = r.json()
        assert "icoord" in data
        assert "dcoord" in data
        print("[PASS] Dendrogram OK")

        print("Testing GET /api/results/geography ...")
        r = client.get("/api/results/geography")
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["total_stations"] == 49
        assert len(data["continental_distribution"]) == 4
        print("[PASS] Geography OK")

        print("Testing GET /api/results/temporal ...")
        r = client.get("/api/results/temporal")
        assert r.status_code == 200, r.text
        data = r.json()
        assert len(data["monthly_distribution"]) == 12
        assert len(data["seasonal_distribution"]) == 4
        print("[PASS] Temporal OK")

        print("Testing GET /api/clustering/compare ...")
        r = client.get("/api/clustering/compare")
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["models_count"] >= 3
        assert "pairwise_ari" in data
        print("[PASS] Model Comparison OK")

        print("\nALL 10 API ENDPOINTS VALIDATED SUCCESSFULLY!")

if __name__ == "__main__":
    test_api()

