import pandas as pd, os, json, sys, tempfile
sys.path.append('c:/data-quality-platform')
from backend.services.cleaning_service import clean_file

# Create temporary CSV with issues
fd, path = tempfile.mkstemp(suffix='.csv')
os.close(fd)

df = pd.DataFrame({
    'A': [1, 2, None, 4, 5, 5, 1000],
    'B': [10, 20, 30, 40, 50, 50, 60]
})
# Save CSV
df.to_csv(path, index=False)

# Mock Dataset model
class MockDataset:
    def __init__(self, id, file_path):
        self.id = id
        self.file_path = file_path

# Monkey-patch _get_dataset
from backend.services import cleaning_service
original_get = cleaning_service._get_dataset

def mock_get(dataset_id, db):
    return MockDataset(dataset_id, path)
cleaning_service._get_dataset = mock_get

options = {
    'missing_method': 'smart',
    'duplicate_method': 'smart',
    'outlier_method': 'iqr',
    'outlier_action': 'fix',
    'noisy_method': 'none'
}

result = clean_file(1, options, db=None)
print(json.dumps(result, indent=2))

# Restore original function
cleaning_service._get_dataset = original_get
