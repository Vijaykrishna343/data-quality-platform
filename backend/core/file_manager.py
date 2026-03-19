import os
import pandas as pd

CLEANED_FOLDER = "backend/storage/cleaned"
os.makedirs(CLEANED_FOLDER, exist_ok=True)


def save_cleaned_file(dataset_id, df):
    path = os.path.join(CLEANED_FOLDER, f"{dataset_id}_cleaned.csv")
    df.to_csv(path, index=False)
    return path


def read_csv(file_path, **kwargs):
    """
    Reads a CSV file into a pandas DataFrame, trying multiple encodings.
    """
    encodings = ["utf-8", "latin1", "cp1252"]
    for encoding in encodings:
        try:
            return pd.read_csv(file_path, encoding=encoding, **kwargs)
        except (UnicodeDecodeError, LookupError):
            continue
        except Exception as e:
            # Re-raise other exceptions that aren't related to encoding
            raise e
    
    # If all encodings fail, try one last time with utf-8 to raise the original UnicodeDecodeError
    return pd.read_csv(file_path, encoding="utf-8", **kwargs)