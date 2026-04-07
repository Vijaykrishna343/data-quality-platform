"""
File Manager — Optimised
========================
Key improvements over the original:
• read_csv_optimised  – low_memory=False, fast encoding fallback, optional nrows
• fast_row_count      – counts rows by streaming newlines (no pandas load)
• read_csv_chunked    – memory-efficient chunked reader for huge files
• read_csv_preview    – reads only first N rows for cheap previews
"""
from __future__ import annotations

import os
from typing import Optional

import pandas as pd

CLEANED_FOLDER = "backend/storage/cleaned"
os.makedirs(CLEANED_FOLDER, exist_ok=True)

# ─── Write ────────────────────────────────────────────────────────────────────

def save_cleaned_file(dataset_id: int, df: pd.DataFrame) -> str:
    path = os.path.join(CLEANED_FOLDER, f"{dataset_id}_cleaned.csv")
    df.to_csv(path, index=False)
    return path


# ─── Read helpers ─────────────────────────────────────────────────────────────

def read_csv_optimised(file_path: str, nrows: Optional[int] = None, **kwargs) -> pd.DataFrame:
    """
    Fast CSV reader.
    • Tries UTF-8 first, falls back to latin1.
    • Sets low_memory=False unless the caller explicitly passes engine='python'
      (python engine doesn't support low_memory).
    • nrows – optional row limit for cheap previews / validation.
    """
    if "engine" not in kwargs:
        kwargs.setdefault("low_memory", False)
    if nrows is not None:
        kwargs["nrows"] = nrows

    try:
        df = pd.read_csv(file_path, encoding="utf-8", **kwargs)
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="latin1", **kwargs)
    except Exception as exc:
        raise ValueError(f"Corrupted or unsupported dataset format: {exc}")

    if df.empty and nrows is None:
        raise ValueError("Uploaded dataset is empty")

    return df


# Legacy alias so existing callers don't break
def read_csv(file_path: str, **kwargs) -> pd.DataFrame:
    return read_csv_optimised(file_path, **kwargs)


def read_csv_preview(file_path: str, n: int = 100) -> pd.DataFrame:
    """Instantly load only the first n rows for preview rendering."""
    return read_csv_optimised(file_path, nrows=n)


def fast_row_count(file_path: str) -> int:
    """
    Count rows by streaming raw bytes — ~10× faster than pd.read_csv for large files.
    Counts newline characters and subtracts 1 for the header.
    """
    count = 0
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                count += chunk.count(b"\n")
        return max(0, count - 1)   # subtract header row
    except Exception:
        return -1                  # caller should fall back to len(df)


def read_csv_chunked(
    file_path: str,
    chunksize: int = 50_000,
    max_rows: Optional[int] = None,
    **kwargs,
) -> pd.DataFrame:
    """
    Memory-efficient reader for very large files.
    Reads in chunks of `chunksize` rows and concatenates.
    Pass max_rows to cap total rows (useful for sampling).
    """
    if "engine" not in kwargs:
        kwargs.setdefault("low_memory", False)

    chunks = []
    rows_read = 0
    try:
        for chunk in pd.read_csv(file_path, chunksize=chunksize, **kwargs):
            chunks.append(chunk)
            rows_read += len(chunk)
            if max_rows and rows_read >= max_rows:
                break
        if not chunks:
            raise ValueError("File produced no data chunks")
        return pd.concat(chunks, ignore_index=True)
    except Exception as exc:
        raise ValueError(f"Error reading large file: {exc}")


# ─── Legacy alias ─────────────────────────────────────────────────────────────
def read_large_csv(file_path: str, chunksize: int = 10_000, **kwargs) -> pd.DataFrame:
    return read_csv_chunked(file_path, chunksize=chunksize, **kwargs)