from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QTextEdit, QFileDialog, QLabel, QSlider, 
    QSpinBox, QCheckBox, QComboBox, QDialog, QTableWidget, QTableWidgetItem,
    QProgressBar, QGroupBox, QMessageBox, QListWidgetItem,
    QMenuBar, QMenu
)
from PySide6.QtGui import QIcon, QPixmap, QFont, QColor
from PySide6.QtCore import Qt, QThread, Signal, QSize, QTimer
from PySide6.QtWidgets import QAbstractItemView
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QAction
from core.settings import SettingsManager, APP_NAME, VERSION
from core.compression import ImageCompressorThread
from core.file_utils import SUPPORTED_FORMATS
from .components.file_list import DragDropListWidget
from .components.settings_panel import SettingsPanel
from .components.log_view import LogView
from .dialogs.about import AboutDialog
from .dialogs.stats import StatsDialog, CompressionStatsDialog 
import os
import sys
import traceback


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings_manager = SettingsManager()
        self.current_settings = self.settings_manager.load_settings()
        self.compression_thread = None
        self.watcher_thread = None
        
        # Get the base path (either development or executable)
        if hasattr(sys, '_MEIPASS'):
            # Running as executable
            self.base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        else:
            # Running in development
            self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Set window icon
        app_icon = QIcon(self.get_icon_path("app_icon.ico"))
        self.setWindowIcon(app_icon)
        
        self.setup_ui()
        self.apply_theme(self.current_settings['theme'])
        
        # Initialize menu bar style
        self.update_menu_bar_style()
        
    # Suppression de la redéclaration inutile de get_icon_path (voir plus bas)
        
    def setup_ui(self):
        self.setWindowTitle(f"{APP_NAME} {VERSION}")
        self.setMinimumSize(900, 700)
        
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # Header
        self.setup_header(main_layout)
        
        # Main content area
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # Left panel - Settings
        left_panel = self.setup_left_panel()
        content_layout.addLayout(left_panel, 1)
        
        # Right panel - File list and log
        right_panel = self.setup_right_panel()
        content_layout.addLayout(right_panel, 2)
        
        main_layout.addLayout(content_layout)
        
        # Bottom panel - Progress and buttons
        self.setup_bottom_panel(main_layout)
        
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Prêt", 5000)
        
        # Menu bar
        self.setup_menu_bar()
        
    def setup_header(self, main_layout):
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Logo and title
        logo_label = QLabel()
        logo_path = self.get_icon_path("app_icon.png")
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            if not logo_pixmap.isNull():
                logo_pixmap = logo_pixmap.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                logo_label.setPixmap(logo_pixmap)
            else:
                print(f"[Logo] ERREUR: QPixmap est null pour {logo_path}")
        else:
            print(f"[Logo] ERREUR: Fichier logo introuvable: {logo_path}")

        title_label = QLabel(f"<h1 style='margin:0;'>{APP_NAME}</h1><p style='color:#666; margin:0;'>Outil professionnel de compression d'images</p>")
        
        # Theme toggle
        self.theme_btn = QPushButton()
        self.theme_btn.setFixedSize(32, 32)
        self.theme_btn.setFlat(True)
        self.theme_btn.clicked.connect(self.toggle_theme)
        self.update_theme_icon()
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.theme_btn)
        
        main_layout.addWidget(header)
    
    def setup_left_panel(self):
        left_layout = QVBoxLayout()
        left_layout.setSpacing(15)
        
        # Compression settings group
        settings_group = QGroupBox("Paramètres de compression")
        settings_layout = QVBoxLayout()
        
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
        settings_layout.addLayout(quality_layout)
        
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
        settings_layout.addWidget(formats_group)
        
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
        settings_layout.addWidget(advanced_group)
        
        settings_group.setLayout(settings_layout)
        left_layout.addWidget(settings_group)
        
        # Presets
        presets_group = QGroupBox("Préréglages")
        presets_layout = QVBoxLayout()
        
        web_btn = QPushButton("Optimisation Web")
        web_btn.clicked.connect(lambda: self.apply_preset('web'))
        
        print_btn = QPushButton("Qualité Impression")
        print_btn.clicked.connect(lambda: self.apply_preset('print'))
        
        archive_btn = QPushButton("Archivage")
        archive_btn.clicked.connect(lambda: self.apply_preset('archive'))
        
        presets_layout.addWidget(web_btn)
        presets_layout.addWidget(print_btn)
        presets_layout.addWidget(archive_btn)
        presets_group.setLayout(presets_layout)
        left_layout.addWidget(presets_group)
        
        left_layout.addStretch()
        
        return left_layout
    
    def setup_right_panel(self):
        right_layout = QVBoxLayout()
        right_layout.setSpacing(15)
        
        # File list
        file_group = QGroupBox("Fichiers à traiter")
        file_layout = QVBoxLayout()
        
        self.file_list = DragDropListWidget()
        self.file_list.setMinimumHeight(200)
        
        file_btn_layout = QHBoxLayout()
        add_files_btn = QPushButton("Ajouter des fichiers")
        add_files_btn.clicked.connect(self.add_files)
        add_folder_btn = QPushButton("Ajouter un dossier")
        add_folder_btn.clicked.connect(self.add_folder)
        clear_btn = QPushButton("Vider la liste")
        clear_btn.clicked.connect(self.file_list.clear)
        
        file_btn_layout.addWidget(add_files_btn)
        file_btn_layout.addWidget(add_folder_btn)
        file_btn_layout.addWidget(clear_btn)
        
        file_layout.addWidget(self.file_list)
        file_layout.addLayout(file_btn_layout)
        file_group.setLayout(file_layout)
        right_layout.addWidget(file_group)
        
        # Log output
        log_group = QGroupBox("Journal de traitement")
        log_layout = QVBoxLayout()
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMinimumHeight(150)
        
        log_btn_layout = QHBoxLayout()
        clear_log_btn = QPushButton("Vider le journal")
        clear_log_btn.clicked.connect(self.log_output.clear)
        save_log_btn = QPushButton("Enregistrer le journal")
        save_log_btn.clicked.connect(self.save_log)
        
        log_btn_layout.addWidget(clear_log_btn)
        log_btn_layout.addWidget(save_log_btn)
        
        log_layout.addWidget(self.log_output)
        log_layout.addLayout(log_btn_layout)
        log_group.setLayout(log_layout)
        right_layout.addWidget(log_group)
        
        return right_layout
    
    def setup_bottom_panel(self, main_layout):
        bottom_layout = QVBoxLayout()
        bottom_layout.setSpacing(10)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(True)
        bottom_layout.addWidget(self.progress_bar)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        
        output_btn = QPushButton("Définir le dossier de sortie")
        output_btn.clicked.connect(self.set_output_folder)
        self.output_label = QLabel(f"Sortie : {self.current_settings['output_dir']}")
        self.output_label.setWordWrap(True)
        
        process_btn = QPushButton("Démarrer le traitement")
        process_btn.clicked.connect(self.start_processing)
        process_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        stop_btn = QPushButton("Arrêter")
        stop_btn.clicked.connect(self.stop_processing)
        stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        
        btn_layout.addWidget(output_btn)
        btn_layout.addWidget(self.output_label)
        btn_layout.addStretch()
        btn_layout.addWidget(stop_btn)
        btn_layout.addWidget(process_btn)
        
        bottom_layout.addLayout(btn_layout)
        main_layout.addLayout(bottom_layout)
    
    def setup_menu_bar(self):
        # Get the menu bar
        menu_bar = self.menuBar()
        
        # Clear existing menus
        for action in menu_bar.actions():
            menu = action.menu()
            # Vérifie que c'est bien un QMenu avant d'appeler clear
            from PySide6.QtWidgets import QMenu
            if isinstance(menu, QMenu):
                menu.clear()
        menu_bar.clear()
        
        # Menu Fichier
        file_menu = menu_bar.addMenu("&Fichier")
        
        # Nouvelle session
        new_action = QAction("&Nouvelle session", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_session)
        file_menu.addAction(new_action)
        
        # Ouvrir des fichiers
        open_action = QAction("&Ouvrir des fichiers...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.add_files)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        # Quitter
        exit_action = QAction("&Quitter", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Paramètres
        settings_menu = menu_bar.addMenu("&Paramètres")
        settings_action = QAction("&Préférences...", self)
        settings_action.setIcon(QIcon(self.settings_manager.SETTINGS_ICON))
        settings_action.triggered.connect(self.show_settings)
        settings_menu.addAction(settings_action)
        
        # Menu Aide
        help_menu = menu_bar.addMenu("&Aide")
        about_action = QAction("&À propos", self)
        about_action.setIcon(QIcon(self.settings_manager.ABOUT_ICON))
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        docs_action = QAction("&Documentation", self)
        docs_action.triggered.connect(self.show_docs)
        help_menu.addAction(docs_action)
    
    def update_quality_value(self, value):
        self.quality_value.setText(f"{value}%")
    
    def apply_preset(self, preset_name):
        if preset_name == 'web':
            self.quality_slider.setValue(80)
            self.jpg_check.setChecked(True)
            self.png_check.setChecked(True)
            self.webp_check.setChecked(True)
            self.optimize_check.setChecked(True)
            self.metadata_check.setChecked(True)
            self.resize_check.setChecked(True)
            self.resize_spin.setValue(100)
            self.log_output.append("Préréglage 'Optimisation Web' appliqué")
        elif preset_name == 'print':
            self.quality_slider.setValue(100)
            self.jpg_check.setChecked(True)
            self.png_check.setChecked(False)
            self.webp_check.setChecked(False)
            self.optimize_check.setChecked(False)
            self.metadata_check.setChecked(False)
            self.resize_check.setChecked(False)
            self.log_output.append("Préréglage 'Qualité Impression' appliqué")
        elif preset_name == 'archive':
            self.quality_slider.setValue(95)
            self.jpg_check.setChecked(True)
            self.png_check.setChecked(True)
            self.webp_check.setChecked(False)
            self.optimize_check.setChecked(False)
            self.metadata_check.setChecked(False)
            self.resize_check.setChecked(False)
            self.log_output.append("Préréglage 'Archivage' appliqué")
    
    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Sélectionner des fichiers image",
            self.current_settings['last_used_dir'],
            "Images (*.jpg *.jpeg *.png *.webp *.bmp *.tiff)"
        )
        
        if files:
            self.current_settings['last_used_dir'] = os.path.dirname(files[0])
            for file in files:
                self.file_list.add_image_file(file)
            self.status_bar.showMessage(f"{len(files)} fichier(s) ajouté(s)", 3000)
    
    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Sélectionner un dossier",
            self.current_settings['last_used_dir']
        )
        
        if folder:
            self.current_settings['last_used_dir'] = folder
            self.file_list.add_folder_contents(folder)
            self.status_bar.showMessage(f"Contenu du dossier ajouté : {folder}", 3000)
    
    def set_output_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Sélectionner le dossier de sortie",
            self.current_settings['output_dir']
        )
        
        if folder:
            self.current_settings['output_dir'] = folder
            self.output_label.setText(f"Sortie : {folder}")
            self.status_bar.showMessage(f"Dossier de sortie défini : {folder}", 3000)
    
    def save_log(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Enregistrer le journal",
            os.path.join(self.current_settings['output_dir'], "compression_log.txt"),
            "Fichiers texte (*.txt);;Tous les fichiers (*)"
        )
        
        if file_path:
            try:
                # Récupérer le texte du journal
                log_text = self.log_output.toPlainText()
                
                # Écrire avec l'encodage UTF-8
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(log_text)
                
                # Afficher un message de succès
                self.status_bar.showMessage(f"Journal enregistré : {file_path}", 5000)
            except Exception as e:
                # Afficher un message d'erreur détaillé
                QMessageBox.warning(self, "Erreur", 
                    f"Échec de l'enregistrement du journal : {str(e)}\n\n"
                    f"Veuillez vérifier vos droits d'écriture et réessayer.")
    
    def start_processing(self):
        if self.compression_thread and self.compression_thread.isRunning():
            QMessageBox.warning(self, "Attention", "Le traitement est déjà en cours")
            return
        
        # Récupérer tous les fichiers de la liste
        files = []
        for i in range(self.file_list.count()):
            files.append(self.file_list.item(i).text())
        
        if not files:
            QMessageBox.warning(self, "Attention", "Aucun fichier à traiter")
            return
        
        # Créer le dossier de sortie s'il n'existe pas
        if not os.path.exists(self.current_settings['output_dir']):
            try:
                os.makedirs(self.current_settings['output_dir'])
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de créer le dossier de sortie : {str(e)}")
                return
        
        # Préparer les paramètres
        settings = {
            'quality': self.quality_slider.value(),
            'output_formats': [],
            'optimize_web': self.optimize_check.isChecked(),
            'remove_metadata': self.metadata_check.isChecked(),
            'resize_enabled': self.resize_check.isChecked(),
            'resize_percent': self.resize_spin.value()
        }
        
        if self.jpg_check.isChecked():
            settings['output_formats'].append('jpg')
        if self.png_check.isChecked():
            settings['output_formats'].append('png')
        if self.webp_check.isChecked():
            settings['output_formats'].append('webp')
        
        if not settings['output_formats']:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner au moins un format de sortie")
            return
        
        # Sauvegarder les paramètres courants
        self.current_settings.update(settings)
        self.settings_manager.save_settings(self.current_settings)
        
        # Démarrer le thread de compression
        self.compression_thread = ImageCompressorThread(
            files,
            self.current_settings['output_dir'],
            settings
        )
        
        # Connecter les signaux
        self.compression_thread.progress_updated.connect(self.update_progress)
        self.compression_thread.status_updated.connect(self.log_output.append)
        self.compression_thread.error_occurred.connect(self.log_output.append)
        self.compression_thread.compression_complete.connect(self.processing_complete)
        
        # Vider le journal et réinitialiser la progression
        self.log_output.clear()
        self.progress_bar.setValue(0)
        
        # Démarrer le traitement
        self.compression_thread.start()
        self.status_bar.showMessage("Traitement démarré...", 3000)
    
    def stop_processing(self):
        if self.compression_thread and self.compression_thread.isRunning():
            self.compression_thread.stop()
            self.status_bar.showMessage("Traitement arrêté", 3000)
            self.log_output.append("Traitement arrêté par l'utilisateur")
        else:
            QMessageBox.warning(self, "Attention", "Aucun traitement actif à arrêter")
    
    def update_progress(self, current, total):
        progress = int((current / total) * 100)
        self.progress_bar.setValue(progress)
        self.status_bar.showMessage(f"Traitement : {current} sur {total} ({progress}%)")
    
    def processing_complete(self, stats):
        self.progress_bar.setValue(100)
        self.status_bar.showMessage("Traitement terminé", 5000)
        self.log_output.append("\nTraitement terminé !")
        
        # Afficher la boîte de dialogue des statistiques
        stats_dialog = CompressionStatsDialog(stats, self)
        stats_dialog.exec()
    
    def toggle_theme(self):
        new_theme = 'dark' if self.current_settings['theme'] == 'light' else 'light'
        self.current_settings['theme'] = new_theme
        self.settings_manager.save_settings(self.current_settings)
        self.apply_theme(new_theme)
        self.update_theme_icon()
    
    def load_icon(self, icon_name):
        """Charge une icône depuis le fichier."""
        try:
            icon_path = self.get_icon_path(icon_name)
            if os.path.exists(icon_path):
                print(f"Loading icon from: {icon_path}")
                return QIcon(icon_path)
            else:
                print(f"Warning: Icon file not found at: {icon_path}")
                return None
        except Exception as e:
            print(f"Error loading icon: {str(e)}")
            return None

    def get_icon_path(self, icon_name: str) -> str:
        """Get the full path to an icon file"""
        icon_path = os.path.join(self.base_path, "resources", "icons", icon_name)
        return os.path.abspath(icon_path)

    def update_theme_icon(self):
        from PySide6.QtGui import QImageReader
        """Met à jour l'icône du bouton de changement de thème."""
        if self.current_settings['theme'] == 'dark':
            icon_name = "light_mode.png"
        else:
            icon_name = "dark_mode.png"
        icon_path = self.get_icon_path(icon_name)
        if not os.path.exists(icon_path):
            return
        try:
            from PIL import Image
            with Image.open(icon_path) as img:
                pass  # Vérification silencieuse
        except Exception:
            pass
        icon = QIcon(icon_path)
        self.theme_btn.setIcon(icon)

    def apply_theme(self, theme):
        check_path = self.get_icon_path("check.png").replace("\\", "/")
        uncheck_path = self.get_icon_path("uncheck.png").replace("\\", "/")
        if theme == 'dark':
            self.setStyleSheet(f"""
                QMainWindow {{
                    background-color: #1a1a1a;
                    color: #ffffff;
                }}
                QMenuBar {{
                    background-color: #2d2d2d;
                    color: #ffffff;
                }}
                QMenuBar::item {{
                    background-color: #2d2d2d;
                    color: #ffffff;
                }}
                QMenuBar::item:selected {{
                    background-color: #4a4a4a;
                }}
                QMenu {{
                    background-color: #2d2d2d;
                    color: #ffffff;
                }}
                QMenu::item {{
                    background-color: #2d2d2d;
                    color: #ffffff;
                }}
                QMenu::item:selected {{
                    background-color: #4a4a4a;
                }}
                QPushButton {{
                    background-color: #2d2d2d;
                    color: #ffffff;
                    border: 1px solid #4a4a4a;
                    padding: 5px 10px;
                    border-radius: 4px;
                }}
                QPushButton:hover {{
                    background-color: #4a4a4a;
                }}
                QPushButton:pressed {{
                    background-color: #3a3a3a;
                }}
                QProgressBar {{
                    border: 1px solid #4a4a4a;
                    background-color: #2d2d2d;
                    text-align: center;
                }}
                QProgressBar::chunk {{
                    background-color: #4a4a4a;
                }}
                QSlider::handle:horizontal {{
                    background-color: #ffffff;
                    width: 18px;
                    margin: -2px 0;
                    border-radius: 9px;
                }}
                QSlider::groove:horizontal {{
                    background-color: #4a4a4a;
                    height: 4px;
                }}
                QCheckBox {{
                    color: #ffffff;
                    spacing: 5px;
                }}
                QCheckBox::indicator {{
                    width: 16px;
                    height: 16px;
                    border: 1px solid #4a4a4a;
                    background-color: #2d2d2d;
                }}
                QCheckBox::indicator:checked {{
                    image: url({check_path});
                }}
                QCheckBox::indicator:unchecked {{
                    image: url({uncheck_path});
                }}
                QLabel {{
                    color: #ffffff;
                }}
                QListWidget {{
                    background-color: #2d2d2d;
                    color: #ffffff;
                    border: 1px solid #4a4a4a;
                }}
                QListWidget::item:selected {{
                    background-color: #4a4a4a;
                }}
                QTextEdit {{
                    background-color: #2d2d2d;
                    color: #ffffff;
                    border: 1px solid #4a4a4a;
                }}
                QGroupBox {{
                    border: 1px solid #4a4a4a;
                    border-radius: 4px;
                    margin-top: 1ex;
                }}
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 3px 0 3px;
                    color: #ffffff;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QMainWindow {{
                    background-color: #ffffff;
                    color: #000000;
                }}
                QMenuBar {{
                    background-color: #f0f0f0;
                    color: #000000;
                }}
                QMenuBar::item {{
                    background-color: #f0f0f0;
                    color: #000000;
                }}
                QMenuBar::item:selected {{
                    background-color: #d9d9d9;
                }}
                QMenu {{
                    background-color: #f0f0f0;
                    color: #000000;
                }}
                QMenu::item {{
                    background-color: #f0f0f0;
                    color: #000000;
                }}
                QMenu::item:selected {{
                    background-color: #d9d9d9;
                }}
                QPushButton {{
                    background-color: #f0f0f0;
                    color: #000000;
                    border: 1px solid #d9d9d9;
                    padding: 5px 10px;
                    border-radius: 4px;
                }}
                QPushButton:hover {{
                    background-color: #d9d9d9;
                }}
                QPushButton:pressed {{
                    background-color: #c0c0c0;
                }}
                QProgressBar {{
                    border: 1px solid #d9d9d9;
                    background-color: #f0f0f0;
                    text-align: center;
                }}
                QProgressBar::chunk {{
                    background-color: #d9d9d9;
                }}
                QSlider::handle:horizontal {{
                    background-color: #000000;
                    width: 18px;
                    margin: -2px 0;
                    border-radius: 9px;
                }}
                QSlider::groove:horizontal {{
                    background-color: #d9d9d9;
                    height: 4px;
                }}
                QCheckBox {{
                    color: #000000;
                }}
                QCheckBox::indicator {{
                    width: 16px;
                    height: 16px;
                }}
                QCheckBox::indicator:checked {{
                    image: url({check_path});
                }}
                QCheckBox::indicator:unchecked {{
                    image: url({uncheck_path});
                }}
                QLabel {{
                    color: #000000;
                }}
                QListWidget {{
                    background-color: #f0f0f0;
                    color: #000000;
                    border: 1px solid #d9d9d9;
                }}
                QListWidget::item:selected {{
                    background-color: #d9d9d9;
                }}
                QTextEdit {{
                    background-color: #f0f0f0;
                    color: #000000;
                    border: 1px solid #d9d9d9;
                }}
                QGroupBox {{
                    border: 1px solid #d9d9d9;
                    border-radius: 4px;
                    margin-top: 1ex;
                }}
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 3px 0 3px;
                    color: #000000;
                }}
            """)
        # Update menu bar style
        self.update_menu_bar_style()

    def update_menu_bar_style(self):
        """Update menu bar style based on current theme"""
        if self.current_settings['theme'] == 'dark':
            style = """
            QMenuBar {
                color: white;
            }
            QMenuBar::item {
                color: white;
            }
            QMenu {
                color: white;
            }
            QMenu::item {
                color: white;
            }
            """
        else:
            style = """
            QMenuBar {
                color: black;
            }
            QMenuBar::item {
                color: black;
            }
            QMenu {
                color: black;
            }
            QMenu::item {
                color: black;
            }
            """
        self.menuBar().setStyleSheet(style)

    # def setup_menu_bar(self):
    #     # ... (rest of the method remains the same)

    #     # Update menu bar style
    #     self.update_menu_bar_style()
    
    def new_session(self):
        self.file_list.clear()
        self.log_output.clear()
        self.progress_bar.setValue(0)
        self.status_bar.showMessage("Nouvelle session démarrée", 3000)
    
    def show_settings(self):
        # Implement settings dialog
        pass
    
    def show_about(self):
        about_dialog = AboutDialog(self)
        about_dialog.exec()
    
    def show_docs(self):
        QMessageBox.information(
            self,
            "Documentation",
            "Veuillez consulter notre site web pour la documentation complète.",
            QMessageBox.StandardButton.Ok
        )
    
    def closeEvent(self, event):
        if self.compression_thread and self.compression_thread.isRunning():
            reply = QMessageBox.question(
                self,
                "Traitement en cours",
                "La compression est toujours en cours. Voulez-vous vraiment quitter ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.compression_thread.stop()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
