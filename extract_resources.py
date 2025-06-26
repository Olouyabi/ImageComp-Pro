import zipfile
import os
from pathlib import Path

def extract_resources():
    """Extrait les ressources de l'archive ZIP"""
    # Chemin vers l'archive ZIP
    zip_path = Path("resources.zip")
    
    # Vérifier si l'archive existe
    if not zip_path.exists():
        print("L'archive de ressources n'existe pas")
        return
    
    # Créer le dossier resources s'il n'existe pas
    resources_dir = Path("resources")
    resources_dir.mkdir(exist_ok=True)
    
    # Extraire les fichiers
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zipf.extractall(resources_dir)

if __name__ == "__main__":
    extract_resources()
