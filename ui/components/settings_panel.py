from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSpinBox, QComboBox, QCheckBox, QHBoxLayout, QSlider, QGroupBox, QPushButton
from PySide6.QtCore import Qt
from core.settings import SettingsManager, APP_NAME, VERSION

class SettingsPanel(QWidget):
    def update_quality_value(self, value):
        self.quality_value.setText(f"{value}%")

    def update_settings(self):
        """Mise à jour des paramètres de base"""
        self.current_settings['quality'] = self.quality_slider.value()
        self.settings_manager.save_settings(self.current_settings)

    def update_output_formats(self):
        """Mise à jour des formats de sortie"""
        formats = []
        if self.jpg_check.isChecked():
            formats.append('jpg')
        if self.png_check.isChecked():
            formats.append('png')
        if self.webp_check.isChecked():
            formats.append('webp')
        self.current_settings['output_formats'] = formats
        self.settings_manager.save_settings(self.current_settings)

    def update_advanced_options(self):
        """Mise à jour des options avancées"""
        self.current_settings['optimize_web'] = self.optimize_check.isChecked()
        self.current_settings['remove_metadata'] = self.metadata_check.isChecked()
        self.current_settings['resize_enabled'] = self.resize_check.isChecked()
        self.current_settings['resize_percent'] = self.resize_spin.value()
        self.settings_manager.save_settings(self.current_settings)

    def apply_preset(self, preset_name):
        """Applique un preset prédéfini"""
        if preset_name == 'web':
            self.quality_slider.setValue(80)
            self.jpg_check.setChecked(True)
            self.png_check.setChecked(True)
            self.webp_check.setChecked(True)
            self.optimize_check.setChecked(True)
            self.metadata_check.setChecked(True)
            self.resize_check.setChecked(True)
            self.resize_spin.setValue(100)
        elif preset_name == 'print':
            self.quality_slider.setValue(100)
            self.jpg_check.setChecked(True)
            self.png_check.setChecked(False)
            self.webp_check.setChecked(False)
            self.optimize_check.setChecked(False)
            self.metadata_check.setChecked(False)
            self.resize_check.setChecked(False)
        elif preset_name == 'archive':
            self.quality_slider.setValue(95)
            self.jpg_check.setChecked(True)
            self.png_check.setChecked(True)
            self.webp_check.setChecked(False)
            self.optimize_check.setChecked(False)
            self.metadata_check.setChecked(False)
            self.resize_check.setChecked(False)
        # Sauvegarder les changements
        self.update_settings()
        self.update_output_formats()
        self.update_advanced_options()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings_manager = SettingsManager()
        self.current_settings = self.settings_manager.load_settings()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Quality setting
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("Qualité :"))
        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setRange(50, 100)
        self.quality_slider.setValue(self.current_settings['quality'])
        self.quality_slider.valueChanged.connect(self.update_quality_value)
        self.quality_value = QLabel(f"{self.current_settings['quality']}%")
        self.quality_value.setMinimumWidth(40)
        
        quality_layout.addWidget(self.quality_slider)
        quality_layout.addWidget(self.quality_value)
        layout.addLayout(quality_layout)
        
        # Output formats
        formats_group = QGroupBox("Formats de sortie")
        formats_layout = QVBoxLayout()
        
        self.jpg_check = QCheckBox("JPEG")
        self.jpg_check.setChecked('jpg' in self.current_settings['output_formats'])
        self.png_check = QCheckBox("PNG")
        self.png_check.setChecked('png' in self.current_settings['output_formats'])
        self.webp_check = QCheckBox("WebP")
        self.webp_check.setChecked('webp' in self.current_settings['output_formats'])
        
        formats_layout.addWidget(self.jpg_check)
        formats_layout.addWidget(self.png_check)
        formats_layout.addWidget(self.webp_check)
        formats_group.setLayout(formats_layout)
        layout.addWidget(formats_group)
        
        # Advanced options
        advanced_group = QGroupBox("Options avancées")
        advanced_layout = QVBoxLayout()
        
        self.optimize_check = QCheckBox("Utiliser des optimiseurs externes (jpegoptim/optipng)")
        self.optimize_check.setChecked(self.current_settings['optimize_web'])
        
        self.metadata_check = QCheckBox("Supprimer les métadonnées (EXIF, IPTC, etc.)")
        self.metadata_check.setChecked(self.current_settings['remove_metadata'])
        
        # Resize options
        resize_layout = QHBoxLayout()
        self.resize_check = QCheckBox("Redimensionner :")
        self.resize_check.setChecked(self.current_settings['resize_enabled'])
        self.resize_spin = QSpinBox()
        self.resize_spin.setRange(1, 100)
        self.resize_spin.setValue(self.current_settings['resize_percent'])
        self.resize_spin.setSuffix("%")
        self.resize_check.toggled.connect(self.resize_spin.setEnabled)
        self.resize_spin.setEnabled(self.resize_check.isChecked())
        
        resize_layout.addWidget(self.resize_check)
        resize_layout.addWidget(self.resize_spin)
        resize_layout.addStretch()
        
        advanced_layout.addWidget(self.optimize_check)
        advanced_layout.addWidget(self.metadata_check)
        advanced_layout.addLayout(resize_layout)
        advanced_group.setLayout(advanced_layout)
        layout.addWidget(advanced_group)
        
        # Presets
        presets_group = QGroupBox("Préréglages")
        presets_layout = QVBoxLayout()
        
        web_btn = QPushButton("Optimisation Web")
        web_btn.clicked.connect(lambda: self.apply_preset('web'))
        
        print_btn = QPushButton("Qualité Impression")
        print_btn.clicked.connect(lambda: self.apply_preset('print'))
        
        archive_btn = QPushButton("Archive")
        archive_btn.clicked.connect(lambda: self.apply_preset('archive'))
        
        presets_layout.addWidget(web_btn)
        presets_layout.addWidget(print_btn)
        presets_layout.addWidget(archive_btn)
        presets_group.setLayout(presets_layout)
        layout.addWidget(presets_group)
        
        self.setLayout(layout)
        
        # Connexions des widgets aux paramètres
        print("Connexion des widgets aux paramètres...")
        self.jpg_check.stateChanged.connect(self.update_output_formats)
        self.png_check.stateChanged.connect(self.update_output_formats)
        self.webp_check.stateChanged.connect(self.update_output_formats)
        
        self.optimize_check.stateChanged.connect(self.update_advanced_options)
        self.metadata_check.stateChanged.connect(self.update_advanced_options)
        self.resize_check.stateChanged.connect(self.update_advanced_options)
        self.resize_spin.valueChanged.connect(self.update_advanced_options)
        
        self.quality_slider.valueChanged.connect(self.update_settings)
        
    # Les méthodes dupliquées ont été supprimées pour éviter les conflits de redéclaration.
        
    def toggle_advanced(self, state):
        """Affichage/masquage des options avancées"""
        if state == Qt.CheckState.Checked:
            # TODO: Implémenter les options avancées
            pass
