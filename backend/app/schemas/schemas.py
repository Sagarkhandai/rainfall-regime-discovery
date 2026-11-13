from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# Dataset Schemas
class DateRange(BaseModel):
    min: str
    max: str

class RainfallStats(BaseModel):
    mean: float
    median: float
    max: float
    std: float
    rain_days_pct: float
    zero_rain_pct: float

class StationMeta(BaseModel):
    count: int
    has_coordinates: bool
    coordinates: Optional[Dict[str, Any]] = None

class DatasetSummaryResponse(BaseModel):
    total_observations: int
    total_features: int
    columns: List[str]
    unique_locations: int
    date_range: DateRange
    complete_core_rows: int
    duplicate_records: int
    missing_counts: Dict[str, int]
    missing_percentages: Dict[str, float]
    rainfall_distribution: RainfallStats
    station_coverage: Dict[str, StationMeta]

# Preprocessing Schemas
class PreprocessingConfigRequest(BaseModel):
    features: Optional[List[str]] = None
    use_log_rainfall: bool = True
    observation_unit: str = Field(default="daily", description="'daily' or 'location_monthly'")
    imputation_strategy: str = Field(default="median", description="'median', 'mean', or 'most_frequent'")

class PreprocessingSummaryResponse(BaseModel):
    observation_unit: str
    fitted_features: List[str]
    feature_count: int
    use_log_rainfall: bool
    imputation_strategy: str
    scaling_method: str
    leakage_features_excluded: List[str]
    feature_statistics: Dict[str, Dict[str, float]]
    correlation_matrix: Optional[Dict[str, Dict[str, float]]] = None

# Clustering Requests
class KMeansRequest(BaseModel):
    k: int = Field(default=4, ge=2, le=8)
    random_state: int = 42

class KMedoidsRequest(BaseModel):
    k: int = Field(default=4, ge=2, le=8)
    random_state: int = 42

class HierarchicalRequest(BaseModel):
    k: int = Field(default=4, ge=2, le=8)
    linkage: str = Field(default="ward", description="'ward', 'complete', or 'average'")
    metric: Optional[str] = Field(default="euclidean", description="'euclidean' or 'cityblock'")
    random_state: int = 42

class SelectModelRequest(BaseModel):
    model_key: str

# Clustering Result Schemas
class ModelMetricSummary(BaseModel):
    algorithm: str
    distance_metric: str
    linkage: Optional[str] = "N/A"
    k: int
    silhouette_score: float
    davies_bouldin_index: float
    wcss: Optional[float] = None
    manhattan_cost_sad: Optional[float] = None
    cophenetic_correlation: Optional[float] = None
    balance_ratio: float
    cluster_sizes: Dict[str, int]
    runtime_seconds: float

class ClusterProfileItem(BaseModel):
    cluster_id: int
    regime_number: str
    title: str
    icon: str
    color: str
    geographic_tag: str
    description: str
    observation_count: int
    observation_percentage: float
    top_locations: List[str]
    metrics: Dict[str, str]
    raw_values: Dict[str, float]

class PCAPoint(BaseModel):
    id: int
    pc1: float
    pc2: float
    pc3: float
    cluster: int
    location: Optional[str] = None
    date: Optional[str] = None
    rainfall: Optional[float] = None

class EigenvectorItem(BaseModel):
    component: str
    variance_ratio: float
    vector: List[float]
    top_influencers: str

class PCAResponse(BaseModel):
    explained_variance_ratio: List[float]
    cumulative_variance: List[float]
    feature_loadings: Dict[str, Dict[str, float]]
    interpretations: Dict[str, str]
    eigenvectors: List[EigenvectorItem]
    total_variance_captured: float
    points: List[PCAPoint]
    points_count: int
    total_observations: int

class DendrogramResponse(BaseModel):
    icoord: List[List[float]]
    dcoord: List[List[float]]
    color_list: List[str]
    leaves: List[int]
    max_distance: float
    cophenetic_correlation: float

class StationGeoItem(BaseModel):
    location: str
    name: str
    state: str
    lat: float
    lon: float
    elevation: int
    observation_count: int
    mean_rainfall: float
    max_rainfall: float
    rainy_days_pct: float
    dominant_cluster: int
    dominant_title: str
    dominant_color: str
    proportions: Dict[str, Any]

class GeographyResponse(BaseModel):
    stations: List[StationGeoItem]
    total_stations: int
    continental_distribution: List[Dict[str, Any]]
    bounds: Dict[str, float]

class TemporalResponse(BaseModel):
    monthly_distribution: List[Dict[str, Any]]
    seasonal_distribution: List[Dict[str, Any]]
    yearly_distribution: List[Dict[str, Any]]
    persistence_rates: Dict[str, float]
    transition_matrix: Dict[str, Dict[str, float]]
    scientific_disclaimer: str

class ModelComparisonResponse(BaseModel):
    comparison_table: List[Dict[str, Any]]
    models_count: int
    common_sample_size: Optional[int] = None
    pairwise_ari: Dict[str, Dict[str, float]]
    pairwise_nmi: Dict[str, Dict[str, float]]
    evaluation_notes: List[str]

class ExperimentItem(BaseModel):
    experiment_id: str
    timestamp: str
    dataset_version: str
    observation_unit: str
    algorithm: str
    distance_metric: str
    linkage: Optional[str] = "N/A"
    k: int
    feature_count: int
    objective_metric: str
    objective_value: Optional[float] = None
    silhouette_score: Optional[float] = None
    davies_bouldin_index: Optional[float] = None
    balance_ratio: Optional[float] = None
    runtime_seconds: float
    status: str

