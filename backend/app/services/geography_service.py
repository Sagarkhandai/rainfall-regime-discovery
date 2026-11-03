from typing import Dict, Any, List
import pandas as pd
import numpy as np
from app.core.constants import STATION_COORDINATES, REGIME_PALETTE
from app.core.json_util import sanitize_for_json

class GeographyService:
    @staticmethod
    def analyze_geography(df: pd.DataFrame, labels: np.ndarray, profiles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Computes station-level cluster distributions, dominant regimes, and geographic coordinates.
        """
        df_geo = df.copy()
        df_geo['Cluster'] = labels
        total_obs = len(df_geo)

        # Map cluster IDs to titles and colors
        cluster_meta = {
            p['cluster_id']: {
                "title": p['title'],
                "color": p['color'],
                "icon": p['icon']
            }
            for p in profiles
        }

        # Overall continental regime breakdown
        cluster_counts = df_geo['Cluster'].value_counts()
        continental_distribution = []
        for c_id, count in cluster_counts.items():
            pct = round(float(count / total_obs * 100), 2)
            meta = cluster_meta.get(int(c_id), {"title": f"Regime {c_id}", "color": REGIME_PALETTE[c_id % len(REGIME_PALETTE)]})
            continental_distribution.append({
                "cluster_id": int(c_id),
                "title": meta["title"],
                "color": meta["color"],
                "count": int(count),
                "percentage": pct
            })

        # Station-level breakdown
        stations_data = []
        for location, group in df_geo.groupby('Location'):
            loc_str = str(location)
            loc_count = len(group)
            coords = STATION_COORDINATES.get(loc_str, {
                "lat": -25.2744, "lon": 133.7751, "state": "AUS", "elev": 100, "name": loc_str
            })

            # Cluster counts for this station
            c_dist = group['Cluster'].value_counts().to_dict()
            proportions = {}
            for c_id in cluster_meta.keys():
                count = c_dist.get(c_id, 0)
                proportions[str(c_id)] = {
                    "count": int(count),
                    "percentage": round(float(count / loc_count * 100), 1)
                }

            # Dominant cluster
            dominant_c_id = int(group['Cluster'].mode()[0])
            dom_meta = cluster_meta.get(dominant_c_id, {"title": f"Regime {dominant_c_id}", "color": "#54D6E8"})

            # Station rainfall metrics
            stn_rain = group['Rainfall'].dropna()
            mean_rain = round(float(stn_rain.mean()), 2) if len(stn_rain) > 0 else 0.0
            max_rain = round(float(stn_rain.max()), 1) if len(stn_rain) > 0 else 0.0
            rainy_days_pct = round(float((stn_rain > 1.0).sum() / len(stn_rain) * 100), 1) if len(stn_rain) > 0 else 0.0

            stations_data.append({
                "location": loc_str,
                "name": coords.get("name", loc_str),
                "state": coords.get("state", "AUS"),
                "lat": coords.get("lat"),
                "lon": coords.get("lon"),
                "elevation": coords.get("elev"),
                "observation_count": loc_count,
                "mean_rainfall": mean_rain,
                "max_rainfall": max_rain,
                "rainy_days_pct": rainy_days_pct,
                "dominant_cluster": dominant_c_id,
                "dominant_title": dom_meta["title"],
                "dominant_color": dom_meta["color"],
                "proportions": proportions
            })

        # Sort stations by latitude (north to south)
        stations_data.sort(key=lambda x: x["lat"], reverse=True)

        return sanitize_for_json({
            "stations": stations_data,
            "total_stations": len(stations_data),
            "continental_distribution": continental_distribution,
            "bounds": {
                "min_lat": -44.0,
                "max_lat": -10.0,
                "min_lon": 112.0,
                "max_lon": 154.0
            }
        })

