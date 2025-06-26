import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from core.settings import SettingsManager

def main():
    # Extraire les ressources au démarrage
    from extract_resources import extract_resources
    extract_resources()

    app = QApplication(sys.argv)
    app.setApplicationName("ImageComp Pro")
    app.setApplicationVersion("2.1.0")
    app.setStyle("Fusion")

    # Initialiser les paramètres
    settings_manager = SettingsManager()
    settings = settings_manager.load_settings()

    # Créer et afficher la fenêtre principale
    window = MainWindow()
    window.show()

    # Démarrer l'application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()