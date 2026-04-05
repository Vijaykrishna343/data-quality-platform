import pandas as pd
import numpy as np
from backend.engines.imputation_engine import ImputationEngine
from backend.engines.duplicate_engine import DuplicateEngine

def test_imputation_engine():
    df = pd.DataFrame({
        "a": [1, 2, np.nan, 4, 5],
        "b": [np.nan, 2, 3, 4, 5],
        "c": ["cat", "dog", "dog", None, "cat"]
    })
    
    df_imputed = ImputationEngine.impute_missing(df, n_neighbors=2)
    assert not df_imputed["a"].isnull().any()
    assert not df_imputed["b"].isnull().any()
    assert not df_imputed["c"].isnull().any()
    assert df_imputed["c"].iloc[3] in ["cat", "dog"]

def test_duplicate_engine():
    df = pd.DataFrame({
        "name": ["john doe", "jon doe", "jane smith", "john doe  "]
    })
    
    indices = DuplicateEngine.detect_fuzzy_duplicates(df, ["name"], threshold=90.0)
    assert len(indices) > 0
    
    df_clean = DuplicateEngine.remove_fuzzy_duplicates(df, ["name"], threshold=90.0)
    assert len(df_clean) < len(df)
