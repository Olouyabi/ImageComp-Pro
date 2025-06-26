from PySide6.QtWidgets import QTextEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor

class LogView(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        self.setReadOnly(True)
        self.setFont(QFont("Consolas", 10))
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #FFFFFF;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
            }
            QTextEdit:focus {
                border: 1px solid #4CAF50;
            }
        """)
        
    def add_message(self, message, level="info"):
        color = {
            "info": "#FFFFFF",
            "warning": "#FFA500",
            "error": "#FF0000",
            "success": "#00FF00"
        }.get(level, "#FFFFFF")
        
        self.setTextColor(QColor(color))
        self.append(message)
        self.setTextColor(QColor("#FFFFFF"))  # Reset color
        
        # Scroll to bottom
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def clear(self):
        super().clear()
