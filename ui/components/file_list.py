from PySide6.QtWidgets import QListWidget, QListWidgetItem, QAbstractItemView
from PySide6.QtCore import Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent
import os
from core.file_utils import SUPPORTED_FORMATS

class DragDropListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DropOnly)
        self.setStyleSheet("""
            QListWidget {
                border: 2px dashed #aaa;
                border-radius: 5px;
                padding: 10px;
            }
            QListWidget::item {
                padding: 5px;
            }
        """)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        event.acceptProposedAction()
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isdir(path):
                self.add_folder_contents(path)
            elif path.lower().endswith(SUPPORTED_FORMATS):
                self.add_image_file(path)

    def add_folder_contents(self, folder_path):
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(SUPPORTED_FORMATS):
                    self.add_image_file(os.path.join(root, file))

    def add_image_file(self, file_path):
        if not any(self.item(i).text() == file_path for i in range(self.count())):
            item = QListWidgetItem(file_path)
            item.setToolTip(file_path)
            self.addItem(item)


