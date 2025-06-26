import os
import json
from typing import Dict, Any
import sys

# Constants
APP_NAME = "ImageComp Pro"
VERSION = "2.1.0"

DEFAULT_SETTINGS = {
    'quality': 90,
    'output_formats': ['jpg'],
    'optimize_web': False,
    'remove_metadata': False,
    'resize_percent': 100,
    'resize_enabled': False,
    'output_dir': os.path.expanduser('~'),
    'theme': 'light',
    'last_used_dir': os.path.expanduser('~')
}

class SettingsManager:
    # Chemins des icônes (compatibles avec les modes développement et exécutable)
    @staticmethod
    def get_icon_path(icon_name: str) -> str:
        # Obtenir le chemin de base (développement ou exécutable)
        if hasattr(sys, '_MEIPASS'):
            # Exécution en mode exécutable
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(__file__)))
        else:
            # Exécution en mode développement
            base_path = os.path.dirname(os.path.dirname(__file__))
        return os.path.join(base_path, "resources", "icons", icon_name)

    # Icon paths
    APP_ICON = get_icon_path("app_icon.png")
    FILE_ICON = get_icon_path("file_icon.png")
    FOLDER_ICON = get_icon_path("folder_icon.png")
    SETTINGS_ICON = get_icon_path("settings_icon.png")
    ABOUT_ICON = get_icon_path("about_icon.png")
    STATS_ICON = get_icon_path("stats_icon.png")

    def __init__(self):
        self.settings_file = os.path.join(os.path.expanduser('~'), '.imagecomp_pro_settings.json')
        self.settings = DEFAULT_SETTINGS.copy()

    def load_settings(self) -> Dict[str, Any]:
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded = json.load(f)
                    self.settings.update(loaded)
        except Exception:
            pass
        return self.settings

    def save_settings(self, settings: Dict[str, Any]) -> bool:
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            self.settings = settings
            return True
        except Exception:
            return False