from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, 
    QPushButton, QGroupBox, QTextEdit, QHBoxLayout, QFileDialog, QMessageBox)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import os
from core.settings import APP_NAME, VERSION


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        from core.settings import SettingsManager
        self.settings_manager = SettingsManager()
        self.setWindowTitle(f"À propos de {APP_NAME}")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()

        # Logo et titre
        logo_label = QLabel()

        # Chargement de l'icône
        try:
            logo_pixmap = QPixmap(self.settings_manager.APP_ICON).scaled(64, 64,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
        except Exception:
            # Si l'icône ne se charge pas, on laisse vide
            pass

        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel(f"<h1>{APP_NAME}</h1>")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        version_label = QLabel(f"Version : {VERSION}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Texte d'information
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setHtml("""
            <p>Un outil professionnel de compression d'images avec des fonctionnalités avancées.</p>
            <p><b>Fonctionnalités :</b></p>
            <ul>
                <li>Prise en charge de plusieurs formats (JPG, PNG, WebP)</li>
                <li>Traitement par lot</li>
                <li>Suppression des métadonnées</li>
                <li>Options de redimensionnement</li>
                <li>Outils d'optimisation externes</li>
                <li>Rapports détaillés de compression</li>
            </ul>
            <p>© 2025 ImageComp Pro. Tous droits réservés.</p>
        """)

        # Bouton de fermeture
        close_btn = QPushButton("Fermer")
        close_btn.clicked.connect(self.accept)

        # Organisation du layout
        layout.addWidget(logo_label)
        layout.addWidget(title_label)
        layout.addWidget(version_label)
        layout.addWidget(info_text)
        layout.addWidget(close_btn)
        self.setLayout(layout)



