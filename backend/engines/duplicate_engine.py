import pandas as pd
from rapidfuzz import process, fuzz
import re
from collections import defaultdict

class DuplicateEngine:
    @staticmethod
    def detect_fuzzy_duplicates(df: pd.DataFrame, columns: list, threshold: float = 90.0) -> list:
        if df.empty or not columns:
            return []

        # 1. Normalize strings: lowercase, collapse spaces, trim
        combined = df[columns].fillna('').apply(lambda row: ' '.join(map(str, row)), axis=1)
        normalized = combined.str.lower().str.replace(r'\s+', ' ', regex=True).str.strip().tolist()
        
        duplicates_indices = set()
        
        # 2. Exact match grouping to instantly catch identical normalized strings
        exact_groups = defaultdict(list)
        for idx, s in enumerate(normalized):
            exact_groups[s].append(idx)
            
        for s, indices in exact_groups.items():
            if len(indices) > 1:
                # keep first, rest are duplicates
                duplicates_indices.update(indices[1:])
                
        unique_strings = list(exact_groups.keys())
        
        # 3. Create candidate groups (blocking) to avoid O(N^2)
        # Using a tuple of (first_letter, length_bucket)
        blocks = defaultdict(list)
        for s in unique_strings:
            if not s:
                continue
            # length bucket: strings must be within 10-20% length to match at >90% threshold
            # binning by length // 5 is safe enough for a candidate group
            # We also block by the first character to reduce the space significantly.
            bucket = len(s) // 4
            block_key = (s[0], bucket)
            blocks[block_key].append(s)

        # 4. Run fuzzy matching only inside groups
        processed_strings = set()
        
        for key, block_strings in blocks.items():
            if len(block_strings) < 2:
                continue
                
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
                        duplicates_indices.update(exact_groups[matched_string])

        return list(duplicates_indices)

    @staticmethod
    def remove_fuzzy_duplicates(df: pd.DataFrame, columns: list, threshold: float = 90.0) -> pd.DataFrame:
        dup_indices = DuplicateEngine.detect_fuzzy_duplicates(df, columns, threshold)
        return df.drop(index=df.index[dup_indices])
