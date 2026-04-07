import sys, os, json, pandas as pd, tempfile
sys.path.append('c:/data-quality-platform')
from backend.services.cleaning_service import clean_dataframe

# Create dataframe with issues
fd, path = tempfile.mkstemp(suffix='.csv')
os.close(fd)

df = pd.DataFrame({
    'A': [1, 2, None, 4, 5, 5, 1000],
    'B': [10, 20, 30, 40, 50, 50, 60]
})

options = {
    'missing_method': 'smart',
    'duplicate_method': 'smart',
    'outlier_method': 'iqr',
    'outlier_action': 'fix',
    'noisy_method': 'none'
}

cleaned = clean_dataframe(df, options)
print('Rows before:', len(df), 'after:', len(cleaned))
print('Missing after:', cleaned.isnull().sum().sum())
print('Duplicates after:', cleaned.duplicated().sum())
