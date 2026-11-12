from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

from app.core.constants import CORE_NUMERICAL_FEATURES, LEAKAGE_FEATURES
from app.preprocessing.data_loader import DataLoader

class PreprocessingPipeline:
    def __init__(
        self,
        features: Optional[List[str]] = None,
        use_log_rainfall: bool = True,
        observation_unit: str = "daily",  # 'daily' or 'location_monthly'
        imputation_strategy: str = "median"
    ):
        self.features = features or CORE_NUMERICAL_FEATURES.copy()
        # Ensure leakage variables are strictly removed
        self.features = [f for f in self.features if f not in LEAKAGE_FEATURES and f != 'RainToday']
        self.use_log_rainfall = use_log_rainfall
        self.observation_unit = observation_unit
        self.imputation_strategy = imputation_strategy
        
        self.imputer: Optional[SimpleImputer] = None
        self.scaler: Optional[StandardScaler] = None
        self.fitted_feature_names: List[str] = []
        self.feature_stats_: Dict[str, Dict[str, float]] = {}
        self.correlation_matrix_: Optional[Dict[str, Dict[str, float]]] = None

    def fit_transform(self, df: Optional[pd.DataFrame] = None) -> Tuple[np.ndarray, pd.DataFrame]:
        """
        Fits imputer & scaler, transforms features, and returns (scaled_array, processed_dataframe).
        """
        if df is None:
            df = DataLoader.load_raw_dataset()

        # Work on a copy
        df_work = df.copy()

        # Handle Observation Unit
        if self.observation_unit == "location_monthly":
            # Group by Location and Year-Month to capture persistent climatic regimes
            df_work['YearMonth'] = df_work['Date'].dt.to_period('M')
            numeric_cols = [c for c in self.features if c in df_work.columns]
            agg_dict = {c: 'mean' for c in numeric_cols}
            
            grouped = df_work.groupby(['Location', 'YearMonth']).agg(agg_dict).reset_index()
            # Explicit aggregation identifier and alignment metadata
            grouped['agg_id'] = [f"{loc}_{ym}" for loc, ym in zip(grouped['Location'], grouped['YearMonth'])]
            grouped['observation_id'] = np.arange(len(grouped), dtype=np.int64)
            grouped['Date'] = pd.to_datetime(grouped['YearMonth'].astype(str) + "-01")
            df_work = grouped

        # Ensure selected features exist in dataframe
        available_features = [f for f in self.features if f in df_work.columns]
        self.fitted_feature_names = available_features

        # Feature engineering: Rainfall log1p transformation to mitigate severe positive skew
        X_df = df_work[available_features].copy()
        if 'Rainfall' in X_df.columns and self.use_log_rainfall:
            # log1p(x) = log(1 + x), maps [0, inf) safely without negative infinity
            X_df['Rainfall'] = np.log1p(np.maximum(0, X_df['Rainfall'].values))

        # Imputation
        self.imputer = SimpleImputer(strategy=self.imputation_strategy)
        X_imputed = self.imputer.fit_transform(X_df)

        # Record feature statistics before standard scaling
        for idx, feat in enumerate(available_features):
            vals = X_imputed[:, idx]
            self.feature_stats_[feat] = {
                "mean": round(float(np.mean(vals)), 4),
                "std": round(float(np.std(vals)), 4),
                "median": round(float(np.median(vals)), 4),
                "min": round(float(np.min(vals)), 4),
                "max": round(float(np.max(vals)), 4)
            }

        # Correlation Analysis
        imputed_df = pd.DataFrame(X_imputed, columns=available_features)
        corr = imputed_df.corr().round(4).to_dict()
        self.correlation_matrix_ = corr

        # Standard Scaling (zero mean, unit variance)
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X_imputed)

        # Build clean processed dataframe
        processed_df = df_work.copy()
        for idx, feat in enumerate(available_features):
            processed_df[f"norm_{feat}"] = X_scaled[:, idx]

        return X_scaled, processed_df

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        if self.imputer is None or self.scaler is None:
            raise RuntimeError("Pipeline must be fitted before calling transform()")
        
        X_df = df[self.fitted_feature_names].copy()
        if 'Rainfall' in X_df.columns and self.use_log_rainfall:
            X_df['Rainfall'] = np.log1p(np.maximum(0, X_df['Rainfall'].values))
            
        X_imputed = self.imputer.transform(X_df)
        return self.scaler.transform(X_imputed)

    def get_pipeline_summary(self) -> Dict[str, Any]:
        return {
            "observation_unit": self.observation_unit,
            "fitted_features": self.fitted_feature_names,
            "feature_count": len(self.fitted_feature_names),
            "use_log_rainfall": self.use_log_rainfall,
            "imputation_strategy": self.imputation_strategy,
            "scaling_method": "StandardScaler (Z-score: mean=0, std=1)",
            "leakage_features_excluded": LEAKAGE_FEATURES + ['RainToday'],
            "feature_statistics": self.feature_stats_,
            "correlation_matrix": self.correlation_matrix_
        }
