import os
import json
from typing import Dict, List, Any

def load_compression_history(output_dir: str) -> List[Dict]:
    history_file = os.path.join(output_dir, 'compression_history.json')
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            return json.load(f)
    return []

def calculate_stats(history: List[Dict]) -> Dict[str, Any]:
    stats = {
        'total_files': 0,
        'total_original_size': 0,
        'total_compressed_size': 0,
        'total_savings': 0
    }
    # Implémentation des calculs
    return stats