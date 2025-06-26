import os
import json
from PIL import Image, ImageOps
import subprocess
from datetime import datetime
import time
from typing import List, Dict, Any
from PySide6.QtCore import QThread, Signal


class ImageCompressorThread(QThread):
    progress_updated = Signal(int, int)
    status_updated = Signal(str)
    compression_complete = Signal(dict)
    error_occurred = Signal(str)

    def __init__(self, files, output_dir, settings):
        super().__init__()
        self.files = files
        self.output_dir = output_dir
        self.settings = settings
        self._is_paused = False
        self._should_stop = False
        self.compression_stats = {
            'total_files': len(files),
            'processed': 0,
            'total_original_size': 0,
            'total_compressed_size': 0,
            'failed_files': 0,
            # Ajout de types corrects pour les champs temporels et erreurs
            'start_time': '',
            'end_time': '',
            'time_elapsed': 0.0,
            'error': ''
        }

    def run(self):
        try:
            self.compression_stats['start_time'] = datetime.now().isoformat()
            
            for idx, file_path in enumerate(self.files, 1):
                if self._should_stop:
                    break
                
                while self._is_paused:
                    time.sleep(0.5)
                
                try:
                    self.process_file(file_path)
                    self.compression_stats['processed'] = idx
                    self.progress_updated.emit(idx, len(self.files))
                except Exception as e:
                    self.error_occurred.emit(f"Erreur lors du traitement de {file_path} : {str(e)}")
                    self.compression_stats['failed_files'] += 1
                    continue
            
            self.compression_stats['end_time'] = datetime.now().isoformat()
            self.compression_stats['time_elapsed'] = float(
                (
                    datetime.fromisoformat(self.compression_stats['end_time']) -
                    datetime.fromisoformat(self.compression_stats['start_time'])
                ).total_seconds()
            )
            
            if not self._should_stop:
                self.compression_complete.emit(self.compression_stats)
                
        except Exception as e:
            self.error_occurred.emit(f"Erreur critique : {str(e)}")

    def process_file(self, file_path):
        original_size = os.path.getsize(file_path)
        self.compression_stats['total_original_size'] += original_size
        
        try:
            img = Image.open(file_path)
        except Exception as e:
            raise Exception(f"Fichier image invalide : {str(e)}")

        base_name = os.path.splitext(os.path.basename(file_path))[0]
        results = {}
        
        for fmt in self.settings['output_formats']:
            output_path = os.path.join(
                self.output_dir, 
                f"{base_name}_optimized.{fmt if fmt != 'jpg' else 'jpeg'}"
            )
            try:
                compressed_size = self.compress_image(img, file_path, output_path, fmt)
                orig_size_int = int(original_size)
                comp_size_int = int(compressed_size)
                # Use integer math for savings
                savings_int = 100 - (comp_size_int * 100 // orig_size_int) if orig_size_int > 0 else 0
                results[fmt] = {
                    'path': output_path,
                    'original_size': orig_size_int,
                    'compressed_size': comp_size_int,
                    'savings': savings_int
                }
                self.compression_stats['total_compressed_size'] += comp_size_int
                self.status_updated.emit(
                    f"Traitée : {base_name}.{fmt} | "
                    f"Gain : {savings_int}% | "
                    f"{orig_size_int//1024}Ko → {comp_size_int//1024}Ko"
                )
            except Exception as e:
                self.error_occurred.emit(f"Échec de la compression de {file_path} en {fmt} : {str(e)}")
                continue
        self.save_to_history(file_path, results)

    def compress_image(self, img, input_path, output_path, fmt):
        try:
            # Resize if needed
            if self.settings['resize_enabled'] and 1 <= self.settings['resize_percent'] < 100:
                w, h = img.size
                new_size = (
                    max(1, int(w * self.settings['resize_percent'] / 100)),
                    max(1, int(h * self.settings['resize_percent'] / 100))
                )
                img = img.resize(new_size, Image.Resampling.LANCZOS)

            # Remove metadata if requested
            if self.settings['remove_metadata']:
                img.info.pop("exif", None)
                if fmt.lower() in ('jpg', 'jpeg'):
                    img = ImageOps.exif_transpose(img)

            # Save in appropriate format
            save_args = {}
            if img is not None:
                if fmt.lower() in ('jpg', 'jpeg'):
                    img = img.convert('RGB')
                    save_args = {
                        'format': 'JPEG',
                        'quality': self.settings['quality'],
                        'optimize': True,
                        'progressive': True
                    }
                elif fmt.lower() == 'png':
                    save_args = {
                        'format': 'PNG',
                        'optimize': True
                    }
                elif fmt.lower() == 'webp':
                    save_args = {
                        'format': 'WEBP',
                        'quality': self.settings['quality'],
                        'method': 6
                    }
                else:
                    save_args = {'format': fmt.upper()}

                img.save(output_path, **save_args)
            else:
                raise Exception("L'image à compresser est invalide (NoneType)")
            
            # Additional optimization if requested
            if self.settings['optimize_web']:
                self.optimize_with_external_tools(output_path, fmt)
            
            return os.path.getsize(output_path)
        except Exception as e:
            raise Exception(f"Erreur de compression : {str(e)}")

    def optimize_with_external_tools(self, file_path, fmt):
        try:
            if fmt.lower() in ('jpg', 'jpeg'):
                subprocess.run([
                    'jpegoptim', 
                    '--strip-all', 
                    f'--max={self.settings["quality"]}', 
                    '--all-progressive', 
                    file_path
                ], check=True, capture_output=True)
            elif fmt.lower() == 'png':
                subprocess.run([
                    'optipng', 
                    '-o2', 
                    file_path
                ], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Erreur de l'outil d'optimisation : {e.stderr.decode().strip()}")
        except FileNotFoundError:
            raise Exception("Outil d'optimisation introuvable. Veuillez installer jpegoptim/optipng.")

    def save_to_history(self, original_path, results):
        """Enregistre les résultats de compression dans le fichier d'historique"""
        history_file = os.path.join(self.output_dir, 'compression_history.json')
        
        # Charger l'historique existant s'il existe
        history = []
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r') as f:
                    history = json.load(f)
            except Exception as e:
                self.error_occurred.emit(f"Failed to load history: {str(e)}")
                history = []
        
        # Ajouter une nouvelle entrée
        history.append({
            'original': original_path,
            'results': results,
            'timestamp': datetime.now().isoformat()
        })
        
        # Sauvegarder l'historique mis à jour
        try:
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            self.error_occurred.emit(f"Échec de la sauvegarde de l'historique : {str(e)}")
            self.compression_stats['error'] = str(e)

    def pause(self):
        self._is_paused = True

    def resume(self):
        self._is_paused = False

    def stop(self):
        self._should_stop = True

