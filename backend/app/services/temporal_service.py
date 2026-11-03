from typing import Dict, Any, List
import pandas as pd
import numpy as np
from app.core.json_util import sanitize_for_json

class TemporalService:
    @staticmethod
    def analyze_temporal(df: pd.DataFrame, labels: np.ndarray, profiles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyzes cluster regime distribution across months, seasons, years, and calculates regime persistence.
        """
        df_time = df.copy()
        df_time['Cluster'] = labels
        df_time['Date'] = pd.to_datetime(df_time['Date'], errors='coerce')
        df_time = df_time.dropna(subset=['Date'])

        df_time['Month'] = df_time['Date'].dt.month
        df_time['MonthName'] = df_time['Date'].dt.strftime('%b')
        df_time['Year'] = df_time['Date'].dt.year

        # Southern Hemisphere Seasons definition:
        # Summer: Dec (12), Jan (1), Feb (2)
        # Autumn: Mar (3), Apr (4), May (5)
        # Winter: Jun (6), Jul (7), Aug (8)
        # Spring: Sep (9), Oct (10), Nov (11)
        season_map = {
            12: 'Summer', 1: 'Summer', 2: 'Summer',
            3: 'Autumn', 4: 'Autumn', 5: 'Autumn',
            6: 'Winter', 7: 'Winter', 8: 'Winter',
            9: 'Spring', 10: 'Spring', 11: 'Spring'
        }
        df_time['Season'] = df_time['Month'].map(season_map)

        # Monthly Distribution
        month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        monthly_distribution = []
        for m_idx, m_name in enumerate(month_order, start=1):
            m_group = df_time[df_time['Month'] == m_idx]
            total_m = len(m_group)
            counts = m_group['Cluster'].value_counts().to_dict()
            monthly_distribution.append({
                "month": m_name,
                "month_num": m_idx,
                "total": total_m,
                "cluster_counts": {str(k): int(v) for k, v in counts.items()},
                "cluster_percentages": {str(k): round(float(v / total_m * 100), 1) if total_m > 0 else 0.0 for k, v in counts.items()}
            })

        # Seasonal Distribution
        seasons_order = ['Summer', 'Autumn', 'Winter', 'Spring']
        seasonal_distribution = []
        for s_name in seasons_order:
            s_group = df_time[df_time['Season'] == s_name]
            total_s = len(s_group)
            counts = s_group['Cluster'].value_counts().to_dict()
            seasonal_distribution.append({
                "season": s_name,
                "total": total_s,
                "cluster_counts": {str(k): int(v) for k, v in counts.items()},
                "cluster_percentages": {str(k): round(float(v / total_s * 100), 1) if total_s > 0 else 0.0 for k, v in counts.items()}
            })

        # Yearly Distribution (2007 to 2017)
        years = sorted(df_time['Year'].unique())
        yearly_distribution = []
        for y in years:
            y_group = df_time[df_time['Year'] == y]
            total_y = len(y_group)
            counts = y_group['Cluster'].value_counts().to_dict()
            yearly_distribution.append({
                "year": int(y),
                "total": total_y,
                "cluster_counts": {str(k): int(v) for k, v in counts.items()},
                "cluster_percentages": {str(k): round(float(v / total_y * 100), 1) if total_y > 0 else 0.0 for k, v in counts.items()}
            })

        # Daily Regime Persistence (Markov Transition Probability Matrix)
        # Sort by station and date to evaluate day-to-day regime continuity
        df_sorted = df_time.sort_values(by=['Location', 'Date'])
        df_sorted['Prev_Date'] = df_sorted.groupby('Location')['Date'].shift(1)
        df_sorted['Prev_Cluster'] = df_sorted.groupby('Location')['Cluster'].shift(1)
        
        # Strictly enforce consecutive-day rule: only transitions separated by exactly 1 calendar day
        is_consecutive = (df_sorted['Date'] - df_sorted['Prev_Date']) == pd.Timedelta(days=1)
        valid_transitions = df_sorted[is_consecutive].dropna(subset=['Prev_Cluster', 'Cluster'])
        
        unique_clusters = sorted(df_time['Cluster'].unique())
        transition_matrix = {}
        persistence_rates = {}
        for c1 in unique_clusters:
            from_c = valid_transitions[valid_transitions['Prev_Cluster'] == c1]
            total_trans = len(from_c)
            row = {}
            for c2 in unique_clusters:
                to_c_count = len(from_c[from_c['Cluster'] == c2])
                prob = round(float(to_c_count / total_trans), 3) if total_trans > 0 else 0.0
                row[str(c2)] = prob
            transition_matrix[str(c1)] = row
            # Persistence is the diagonal entry P(c1 -> c1)
            persistence_rates[str(c1)] = row.get(str(c1), 0.0)

        return sanitize_for_json({
            "monthly_distribution": monthly_distribution,
            "seasonal_distribution": seasonal_distribution,
            "yearly_distribution": yearly_distribution,
            "persistence_rates": persistence_rates,
            "transition_matrix": transition_matrix,
            "scientific_disclaimer": "Unsupervised pattern analysis characterizes historical regime persistence and seasonal frequency. It does not constitute a deterministic forecasting model."
        })

