import zipfile
import os
from pathlib import Path

def create_resources_zip():
    # Chemin vers les ressources
    resources_dir = Path("resources")
    
    # Créer l'archive ZIP
    with zipfile.ZipFile("resources.zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Ajouter les fichiers individuels
        for file in resources_dir.glob("**/*"):
            if file.is_file():
                zipf.write(file, arcname=str(file.relative_to(resources_dir)))

if __name__ == "__main__":
    create_resources_zip()
