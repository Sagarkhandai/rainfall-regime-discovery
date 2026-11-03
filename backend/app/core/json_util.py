import math
from typing import Any
import numpy as np
import pandas as pd

def sanitize_for_json(obj: Any) -> Any:
    """
    Recursively sanitize Python/NumPy/Pandas data structures for strict JSON compliance.
    Converts non-finite floating point numbers (NaN, +Inf, -Inf) to None (JSON null).
    Preserves exact zeroes and valid finite numbers.
    """
    if obj is None:
        return None
    if isinstance(obj, (float, np.floating)):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return float(obj)
    if isinstance(obj, (int, np.integer)):
        return int(obj)
    if isinstance(obj, (bool, np.bool_)):
        return bool(obj)
    if isinstance(obj, (str, bytes)):
        return obj if isinstance(obj, str) else obj.decode('utf-8', errors='replace')
    if isinstance(obj, dict):
        return {str(k): sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, np.ndarray, pd.Series)):
        return [sanitize_for_json(v) for v in obj]
    if pd.isna(obj):
        return None
    return obj

