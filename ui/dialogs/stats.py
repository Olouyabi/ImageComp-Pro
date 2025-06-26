from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QPushButton, QGroupBox, QTextEdit, QHBoxLayout,
    QFileDialog, QMessageBox)
from PySide6.QtCore import Qt
from typing import Dict, Any
import os
import json
import csv
from datetime import datetime

class StatsDialog(QDialog):
    def __init__(self, stats: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Statistiques de compression")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout()
        
        # Summary section
        summary_group = QGroupBox("Résumé")
        summary_layout = QVBoxLayout()
        
        stats_text = QTextEdit()
        stats_text.setReadOnly(True)
        
        summary = [
            f"<b>Fichiers totaux :</b> {stats['total_files']}",
            f"<b>Traités :</b> {stats['processed']}",
            f"<b>Échecs :</b> {stats['failed_files']}",
            f"<b>Durée :</b> {stats['time_elapsed']:.2f} secondes",
            f"<b>Taille originale :</b> {stats['total_original_size'] / (1024*1024):.2f} Mo",
            f"<b>Taille compressée :</b> {stats['total_compressed_size'] / (1024*1024):.2f} Mo",
            f"<b>Gain total :</b> {100 - (stats['total_compressed_size'] * 100 / stats['total_original_size']):.1f}%"
        ]
        
        stats_text.setHtml("<br>".join(summary))
        summary_layout.addWidget(stats_text)
        summary_group.setLayout(summary_layout)
        
        # Detailed results
        details_group = QGroupBox("Détails des résultats")
        details_layout = QVBoxLayout()
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Original", "Format", "Taille originale", "Taille compressée", "Gain"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        
        details_layout.addWidget(self.table)
        details_group.setLayout(details_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        export_btn = QPushButton("Exporter en CSV")
        export_btn.clicked.connect(self.export_to_csv)
        close_btn = QPushButton("Fermer")
        close_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(export_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        
        # Main layout
        layout.addWidget(summary_group)
        layout.addWidget(details_group)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
        # Load data
        self.load_stats(stats)
    
    def load_stats(self, stats: Dict[str, Any]):
        # Correction: ensure all values are cast to int before str, to avoid float assignment
        details = []
        history_file = os.path.join(stats.get('output_dir', ''), 'compression_history.json')
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r') as f:
                    history = json.load(f)
                    for entry in history:
                        original = entry.get('original', '')
                        for fmt, res in entry.get('results', {}).items():
                            orig_size = res.get("original_size", 0)
                            comp_size = res.get("compressed_size", 0)
                            savings = res.get("savings", 0)
                            # Defensive: cast float to int, then to str
                            orig_size_str = str(int(float(orig_size))) if isinstance(orig_size, float) else str(int(orig_size)) if not isinstance(orig_size, str) else orig_size
                            comp_size_str = str(int(float(comp_size))) if isinstance(comp_size, float) else str(int(comp_size)) if not isinstance(comp_size, str) else comp_size
                            savings_str = str(int(float(savings))) if isinstance(savings, float) else str(int(savings)) if not isinstance(savings, str) else savings
                            details.append([
                                str(original),
                                str(fmt),
                                orig_size_str,
                                comp_size_str,
                                savings_str
                            ])
            except Exception:
                pass
        self.table.setRowCount(len(details))
        for row, entry in enumerate(details):
            self.table.setItem(row, 0, QTableWidgetItem(entry[0]))
            self.table.setItem(row, 1, QTableWidgetItem(entry[1]))
            self.table.setItem(row, 2, QTableWidgetItem(entry[2]))
            self.table.setItem(row, 3, QTableWidgetItem(entry[3]))
            self.table.setItem(row, 4, QTableWidgetItem(entry[4]))
    
    def export_to_csv(self):
        # Get default filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"compression_stats_{timestamp}.csv"
        
        # Get save location
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Statistics",
            default_filename,
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_path:
            return
            
        try:
            # Write CSV file
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                # Write header
                writer.writerow(["Original", "Format", "Original Size", "Compressed Size", "Savings"])
                # Write data
                for row in range(self.table.rowCount()):
                    row_data = []
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        if item:
                            row_data.append(item.text())
                        else:
                            row_data.append("")
                    writer.writerow(row_data)
            QMessageBox.information(self, "Succès", "Statistiques exportées avec succès !")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Échec de l'export des statistiques : {str(e)}")

class CompressionStatsDialog(QDialog):
    def __init__(self, stats, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Statistiques de compression")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout()
        
        # Summary section
        summary_group = QGroupBox("Résumé")
        summary_layout = QVBoxLayout()
        
        stats_text = QTextEdit()
        stats_text.setReadOnly(True)
        
        summary = [
            f"<b>Fichiers totaux :</b> {stats['total_files']}",
            f"<b>Traités :</b> {stats['processed']}",
            f"<b>Échecs :</b> {stats['failed_files']}",
            f"<b>Durée :</b> {stats['time_elapsed']:.2f} secondes",
            f"<b>Taille originale :</b> {stats['total_original_size'] / (1024*1024):.2f} Mo",
            f"<b>Taille compressée :</b> {stats['total_compressed_size'] / (1024*1024):.2f} Mo",
            f"<b>Gain total :</b> {100 - (stats['total_compressed_size'] * 100 / stats['total_original_size']):.1f}%"
        ]
        
        stats_text.setHtml("<br>".join(summary))
        summary_layout.addWidget(stats_text)
        summary_group.setLayout(summary_layout)
        
        # Detailed results
        details_group = QGroupBox("Détails des résultats")
        details_layout = QVBoxLayout()
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Original", "Format", "Taille originale", "Taille compressée", "Gain"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        
        details_layout.addWidget(self.table)
        details_group.setLayout(details_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        export_btn = QPushButton("Exporter en CSV")
        export_btn.clicked.connect(self.export_to_csv)
        close_btn = QPushButton("Fermer")
        close_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(export_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        
        # Main layout
        layout.addWidget(summary_group)
        layout.addWidget(details_group)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
        # Load data
        self.load_stats(stats)
    
    def load_stats(self, stats):
        # Correction: ensure all values are cast to int before str, to avoid float assignment
        details = []
        history_file = os.path.join(stats.get('output_dir', ''), 'compression_history.json')
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r') as f:
                    history = json.load(f)
                    for entry in history:
                        original = entry.get('original', '')
                        for fmt, res in entry.get('results', {}).items():
                            orig_size = res.get("original_size", 0)
                            comp_size = res.get("compressed_size", 0)
                            savings = res.get("savings", 0)
                            # Defensive: cast float to int, then to str
                            orig_size_str = str(int(float(orig_size))) if isinstance(orig_size, float) else str(int(orig_size)) if not isinstance(orig_size, str) else orig_size
                            comp_size_str = str(int(float(comp_size))) if isinstance(comp_size, float) else str(int(comp_size)) if not isinstance(comp_size, str) else comp_size
                            savings_str = str(int(float(savings))) if isinstance(savings, float) else str(int(savings)) if not isinstance(savings, str) else savings
                            details.append([
                                str(original),
                                str(fmt),
                                orig_size_str,
                                comp_size_str,
                                savings_str
                            ])
            except Exception:
                pass
        self.table.setRowCount(len(details))
        for row, entry in enumerate(details):
            self.table.setItem(row, 0, QTableWidgetItem(entry[0]))
            self.table.setItem(row, 1, QTableWidgetItem(entry[1]))
            self.table.setItem(row, 2, QTableWidgetItem(entry[2]))
            self.table.setItem(row, 3, QTableWidgetItem(entry[3]))
            self.table.setItem(row, 4, QTableWidgetItem(entry[4]))
    
    def export_to_csv(self):
        # Get default filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"compression_stats_{timestamp}.csv"
        
        # Get save location
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Statistics",
            default_filename,
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_path:
            return
            
        try:
            # Write CSV file
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                # Write header
                writer.writerow(["Original", "Format", "Original Size", "Compressed Size", "Savings"])
                # Write data
                for row in range(self.table.rowCount()):
                    row_data = []
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        if item:
                            row_data.append(item.text())
                        else:
                            row_data.append("")
                    writer.writerow(row_data)
            QMessageBox.information(self, "Succès", "Statistiques exportées avec succès !")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Échec de l'export des statistiques : {str(e)}")
