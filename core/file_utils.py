import os
from typing import List

SUPPORTED_FORMATS = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff')

def get_supported_files(folder_path: str) -> List[str]:
    files = []
    for root, _, filenames in os.walk(folder_path):
        for filename in filenames:
            if filename.lower().endswith(SUPPORTED_FORMATS):
                files.append(os.path.join(root, filename))
    return files