import os
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np

from app.core.config import settings
from app.core.constants import STATION_COORDINATES
from app.core.json_util import sanitize_for_json

class DataLoader:
    _cached_df: Optional[pd.DataFrame] = None
    _dataset_stats: Optional[Dict[str, Any]] = None

    @classmethod
    def load_raw_dataset(cls, file_path: Optional[Path] = None, force_reload: bool = False) -> pd.DataFrame:
        if cls._cached_df is not None and not force_reload:
            return cls._cached_df

        target_path = file_path or settings.DATA_PATH
        if not target_path.exists():
            # Fallback check
            alt_path = Path("weatherAUS.csv")
            if alt_path.exists():
                target_path = alt_path
            else:
                raise FileNotFoundError(f"Dataset not found at {target_path}")

        try:
            df = pd.read_csv(target_path)
        except Exception as e:
            raise ValueError(f"Failed to read CSV at {target_path}: {str(e)}")

        expected_cols = {'Date', 'Location', 'Rainfall'}
        if not expected_cols.issubset(set(df.columns)):
            raise ValueError(f"Dataset missing required primary columns: {expected_cols - set(df.columns)}")

        # Convert Date to datetime for chronological sorting
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

        # Stable Observation Identifier preserving observation identity across pipeline
        if 'observation_id' not in df.columns:
            df['observation_id'] = np.arange(len(df), dtype=np.int64)

        cls._cached_df = df
        return df

    @classmethod
    def get_dataset_summary(cls, df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        if cls._dataset_stats is not None and df is None:
            return cls._dataset_stats

        if df is None:
            df = cls.load_raw_dataset()

        total_rows = int(len(df))
        total_cols = int(df.shape[1])
        unique_locations = int(df['Location'].nunique())
        
        # Missing values summary
        missing_counts = df.isnull().sum().to_dict()
        missing_pcts = {k: round(float(v / total_rows * 100), 2) for k, v in missing_counts.items()}
        
        # Complete rows (zero missing in core columns)
        core_cols = ['MinTemp', 'MaxTemp', 'Rainfall', 'WindSpeed9am', 'WindSpeed3pm', 
                     'Humidity9am', 'Humidity3pm', 'Pressure9am', 'Pressure3pm', 'Temp9am', 'Temp3pm']
        present_core = [c for c in core_cols if c in df.columns]
        complete_rows = int(df[present_core].dropna().shape[0])
        
        # Date range
        min_date = str(df['Date'].min().strftime('%Y-%m-%d')) if pd.notnull(df['Date'].min()) else "N/A"
        max_date = str(df['Date'].max().strftime('%Y-%m-%d')) if pd.notnull(df['Date'].max()) else "N/A"
        
        # Rainfall distribution metrics
        rain_series = df['Rainfall'].dropna()
        rain_stats = {
            "mean": round(float(rain_series.mean()), 2),
            "median": round(float(rain_series.median()), 2),
            "max": round(float(rain_series.max()), 1),
            "std": round(float(rain_series.std()), 2),
            "skewness": round(float(rain_series.skew()), 2),
            "rain_days_pct": round(float((rain_series > 1.0).sum() / len(rain_series) * 100), 2),
            "zero_rain_pct": round(float((rain_series == 0.0).sum() / len(rain_series) * 100), 2)
        }

        # Station count and coverage
        location_counts = df['Location'].value_counts().to_dict()
        station_coverage = {
            loc: {
                "count": int(count),
                "has_coordinates": loc in STATION_COORDINATES,
                "coordinates": STATION_COORDINATES.get(loc, None)
            }
            for loc, count in location_counts.items()
        }

        # Duplicate records
        duplicate_count = int(df.duplicated(subset=['Date', 'Location']).sum())

        summary = sanitize_for_json({
            "total_observations": total_rows,
            "total_features": total_cols,
            "columns": list(df.columns),
            "unique_locations": unique_locations,
            "date_range": {"min": min_date, "max": max_date},
            "complete_core_rows": complete_rows,
            "duplicate_records": duplicate_count,
            "missing_counts": missing_counts,
            "missing_percentages": missing_pcts,
            "rainfall_distribution": rain_stats,
            "station_coverage": station_coverage
        })

        cls._dataset_stats = summary
        return summary

