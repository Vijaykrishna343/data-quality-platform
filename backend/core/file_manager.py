import os

CLEANED_FOLDER = "backend/storage/cleaned"
os.makedirs(CLEANED_FOLDER, exist_ok=True)


def save_cleaned_file(dataset_id, df):
    path = os.path.join(CLEANED_FOLDER, f"{dataset_id}_cleaned.csv")
    df.to_csv(path, index=False)
    return path