import pandas as pd
from rapidfuzz import process, fuzz
import re
from collections import defaultdict

class DuplicateEngine:
    @staticmethod
    def detect_fuzzy_duplicates(df: pd.DataFrame, columns: list, threshold: float = 90.0) -> list:
        if df.empty or not columns:
            return []

        # Optimization: Sample large datasets to prevent O(N^2) bottleneck
        if len(df) > 50000:
            df_sample = df.sample(n=50000, random_state=42)
            # Find duplicates in sample and map back? 
            # Or just warn user and only detect among sample for score.
            # User requested "sample-based duplicate detection for datasets > 50k rows".
            df_for_analysis = df_sample
        else:
            df_for_analysis = df

        # 1. Normalize strings: lowercase, collapse spaces, trim
        combined = df_for_analysis[columns].fillna('').apply(lambda row: ' '.join(map(str, row)), axis=1)
        normalized = combined.str.lower().str.replace(r'\s+', ' ', regex=True).str.strip().tolist()
        
        duplicates_indices_set = set()
        
        # 2. Exact match grouping to instantly catch identical normalized strings
        exact_groups = defaultdict(list)
        for idx_pos, s in enumerate(normalized):
            # map back to original index
            orig_idx = df_for_analysis.index[idx_pos]
            exact_groups[s].append(orig_idx)
            
        for s, indices in exact_groups.items():
            if len(indices) > 1:
                # keep first, rest are duplicates
                duplicates_indices_set.update(indices[1:])
                
        unique_strings = list(exact_groups.keys())
        
        # 3. Create candidate groups (blocking) to avoid O(N^2)
        # Using a tuple of (first_letter, length_bucket)
        blocks = defaultdict(list)
        for s in unique_strings:
            if not s:
                continue
            # Binning by length buckets to reduce comparisons
            bucket = len(s) // 5
            block_key = (s[0], bucket)
            blocks[block_key].append(s)

        # 4. Run fuzzy matching only inside groups
        processed_strings = set()
        
        for key, block_strings in blocks.items():
            if len(block_strings) < 2:
                continue
            
            # Additional safety: limit block size to prevent local O(M^2)
            if len(block_strings) > 1000:
                block_strings = block_strings[:1000]
                
            for i, s1 in enumerate(block_strings):
                if s1 in processed_strings:
                    continue
                
                # compare s1 with the remaining items in the SAME block
                candidates = block_strings[i+1:]
                if not candidates:
                    continue
                    
                matches = process.extract(s1, candidates, scorer=fuzz.ratio, score_cutoff=threshold)
                
                for match in matches:
                    matched_string = match[0]
                    if matched_string not in processed_strings:
                        processed_strings.add(matched_string)
                        # Add original indices of this newly found duplicate string
                        # These are already absolute indices from the original df/sampled df
                        duplicates_indices_set.update(exact_groups[matched_string])

        return list(duplicates_indices_set)

    @staticmethod
    def remove_fuzzy_duplicates(df: pd.DataFrame, columns: list, threshold: float = 90.0) -> pd.DataFrame:
        dup_indices = DuplicateEngine.detect_fuzzy_duplicates(df, columns, threshold)
        # dup_indices are already label-based index values (from df.index[pos])
        return df.drop(index=dup_indices, errors="ignore")

