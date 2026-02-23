import pandas as pd

def process_large_csv(file_path: str):
    """
    Reads large CSV file in chunks.
    Returns:
        dataset_info (dict)
        df_sample (DataFrame sample for profiling)
    """

    chunk_size = 100000
    total_rows = 0
    total_columns = 0
    sample_df = None

    for chunk in pd.read_csv(file_path, chunksize=chunk_size):
        chunk = chunk.replace(["", " ", "NA", "null"], pd.NA)

        if sample_df is None:
            sample_df = chunk.copy()

        total_rows += len(chunk)
        total_columns = len(chunk.columns)

    dataset_info = {
        "total_rows": total_rows,
        "total_columns": total_columns
    }

    return dataset_info, sample_df