from typing import Dict, Any, List
import numpy as np
import pandas as pd
from app.core.constants import REGIME_PALETTE

from typing import Dict, Any, List
import numpy as np
import pandas as pd
from app.core.constants import REGIME_PALETTE
from app.core.json_util import sanitize_for_json

class ProfilingService:
    @staticmethod
    def profile_clusters(df: pd.DataFrame, labels: np.ndarray) -> List[Dict[str, Any]]:
        """
        Calculates descriptive meteorological profiles for each cluster based on real dataset values.
        Ensures strictly unique, climatologically grounded names without duplicates.
        """
        df_copy = df.copy()
        df_copy['Cluster'] = labels
        total_obs = len(df_copy)
        unique_clusters = sorted(df_copy['Cluster'].unique())

        raw_cluster_stats = []
        for cluster_id in unique_clusters:
            c_df = df_copy[df_copy['Cluster'] == cluster_id]
            count = len(c_df)
            pct = round(count / total_obs * 100, 2)

            rain = c_df['Rainfall'].dropna()
            mean_rain = round(float(rain.mean()), 2) if len(rain) > 0 else 0.0
            median_rain = round(float(rain.median()), 2) if len(rain) > 0 else 0.0
            rain_freq = round(float((rain > 1.0).sum() / len(rain) * 100), 2) if len(rain) > 0 else 0.0

            t_min = c_df['MinTemp'].dropna()
            t_max = c_df['MaxTemp'].dropna()
            t_3pm = c_df['Temp3pm'].dropna()
            mean_min_temp = round(float(t_min.mean()), 1) if len(t_min) > 0 else 0.0
            mean_max_temp = round(float(t_max.mean()), 1) if len(t_max) > 0 else 0.0
            mean_temp_3pm = round(float(t_3pm.mean()), 1) if len(t_3pm) > 0 else 0.0
            diurnal_delta = round(mean_max_temp - mean_min_temp, 1)

            h_9am = c_df['Humidity9am'].dropna()
            h_3pm = c_df['Humidity3pm'].dropna()
            mean_h_9am = round(float(h_9am.mean()), 1) if len(h_9am) > 0 else 0.0
            mean_h_3pm = round(float(h_3pm.mean()), 1) if len(h_3pm) > 0 else 0.0

            p_9am = c_df['Pressure9am'].dropna()
            p_3pm = c_df['Pressure3pm'].dropna()
            mean_p_9am = round(float(p_9am.mean()), 1) if len(p_9am) > 0 else 1015.0
            mean_p_3pm = round(float(p_3pm.mean()), 1) if len(p_3pm) > 0 else 1013.0
            baro_delta = round(mean_p_3pm - mean_p_9am, 2)

            w_3pm = c_df['WindSpeed3pm'].dropna()
            mean_w_3pm = round(float(w_3pm.mean()), 1) if len(w_3pm) > 0 else 0.0

            top_locations = c_df['Location'].value_counts().head(3).index.tolist() if 'Location' in c_df.columns else []

            raw_cluster_stats.append({
                "cluster_id": int(cluster_id),
                "count": count,
                "pct": pct,
                "mean_rain": mean_rain,
                "median_rain": median_rain,
                "rain_freq": rain_freq,
                "mean_min_temp": mean_min_temp,
                "mean_max_temp": mean_max_temp,
                "mean_temp_3pm": mean_temp_3pm,
                "diurnal_delta": diurnal_delta,
                "mean_h_9am": mean_h_9am,
                "mean_h_3pm": mean_h_3pm,
                "mean_p_3pm": mean_p_3pm,
                "baro_delta": baro_delta,
                "mean_w_3pm": mean_w_3pm,
                "top_locations": top_locations
            })

        # Rank clusters by physical characteristics to ensure unique, accurate naming
        used_titles = set()
        profiles = []

        # Sort by rainfall descending
        rain_ranks = {item["cluster_id"]: r for r, item in enumerate(sorted(raw_cluster_stats, key=lambda x: x["mean_rain"], reverse=True))}
        temp_ranks = {item["cluster_id"]: r for r, item in enumerate(sorted(raw_cluster_stats, key=lambda x: x["mean_temp_3pm"], reverse=True))}

        for s in raw_cluster_stats:
            c_id = s["cluster_id"]
            r_val = s["mean_rain"]
            rf_val = s["rain_freq"]
            t_val = s["mean_temp_3pm"]
            h_val = s["mean_h_3pm"]
            d_val = s["diurnal_delta"]

            # Dynamic climatological regime descriptor synthesis
            if r_val >= 3.0 or rf_val >= 30.0:
                if t_val >= 26.0:
                    base_title = "Monsoonal Tropical Convective"
                    icon = "cyclone"
                else:
                    base_title = "Maritime Orographic Wet"
                    icon = "thunderstorm"
            elif r_val < 1.0 and d_val >= 12.0:
                base_title = "Arid Continental High-Fluctuation"
                icon = "sunny"
            elif t_val <= 19.0 and h_val >= 50.0:
                base_title = "Cool Polar Maritime Frontal"
                icon = "waves"
            elif t_val >= 24.0:
                base_title = "Warm Subtropical Intermediate"
                icon = "wb_sunny"
            else:
                base_title = "Temperate Coastal Maritime"
                icon = "air"

            # Ensure strict title uniqueness across all clusters
            title = base_title
            counter = 2
            while title in used_titles:
                title = f"{base_title} (Type {counter})"
                counter += 1
            used_titles.add(title)

            # Ground geographic tag in actual top empirical station locations
            loc_summary = ", ".join(s["top_locations"][:3]) if s["top_locations"] else "Continental Stations"
            tag = f"High Frequency: {loc_summary}"

            # Ground narrative strictly in measured empirical statistics
            desc = (
                f"Empirical regime discovered across {s['count']:,} observations ({s['pct']}%). "
                f"Mean precipitation: {s['mean_rain']} mm/day with {s['rain_freq']}% rain days. "
                f"Afternoon temperature averages {s['mean_temp_3pm']}°C with {s['mean_h_3pm']}% humidity "
                f"and {s['mean_p_3pm']} hPa surface pressure."
            )

            color = REGIME_PALETTE[c_id % len(REGIME_PALETTE)]

            profile = {
                "cluster_id": c_id,
                "regime_number": f"REGIME 0{c_id + 1}",
                "title": title,
                "icon": icon,
                "color": color,
                "geographic_tag": tag,
                "description": desc,
                "observation_count": s["count"],
                "observation_percentage": s["pct"],
                "top_locations": s["top_locations"],
                "metrics": {
                    "mean_rainfall": f"{s['mean_rain']} mm/day",
                    "median_rainfall": f"{s['median_rain']} mm/day",
                    "rain_frequency": f"{s['rain_freq']}%",
                    "mean_min_temp": f"{s['mean_min_temp']} °C",
                    "mean_max_temp": f"{s['mean_max_temp']} °C",
                    "diurnal_delta": f"+{s['diurnal_delta']} °C",
                    "temp_3pm": f"{s['mean_temp_3pm']} °C",
                    "humidity_9am": f"{s['mean_h_9am']}%",
                    "humidity_3pm": f"{s['mean_h_3pm']}%",
                    "pressure_3pm": f"{s['mean_p_3pm']} hPa",
                    "barometric_delta": f"{s['baro_delta']:+} hPa",
                    "wind_speed_3pm": f"{s['mean_w_3pm']} km/h"
                },
                "raw_values": {
                    "mean_rainfall": s["mean_rain"],
                    "median_rainfall": s["median_rain"],
                    "rain_frequency": s["rain_freq"],
                    "temp_3pm": s["mean_temp_3pm"],
                    "humidity_9am": s["mean_h_9am"],
                    "humidity_3pm": s["mean_h_3pm"],
                    "pressure_3pm": s["mean_p_3pm"],
                    "diurnal_delta": s["diurnal_delta"],
                    "barometric_delta": s["baro_delta"]
                }
            }
            profiles.append(profile)

        return sanitize_for_json(profiles)

