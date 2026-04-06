import os
import pandas as pd

CLEANED_FOLDER = "backend/storage/cleaned"
os.makedirs(CLEANED_FOLDER, exist_ok=True)


def save_cleaned_file(dataset_id, df):
    path = os.path.join(CLEANED_FOLDER, f"{dataset_id}_cleaned.csv")
    df.to_csv(path, index=False)
    return path


    # If all encodings fail, let pandas throw the default exception, we catch it locally
    try:
        df = pd.read_csv(file_path, encoding="utf-8", **kwargs)
    except Exception as e:
        raise ValueError(f"Corrupted or unsupported dataset format: {str(e)}")
        
    if df.empty:
        raise ValueError("Uploaded dataset is empty")
        
    return df