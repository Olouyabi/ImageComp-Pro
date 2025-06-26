import os
import sys
from PySide6.QtCore import QResource
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication

# Compile resources
def compile_resources():
    # Get the path to the .qrc file
    qrc_path = os.path.join(os.path.dirname(__file__), 'resources.qrc')
    
    # Use pyside6-rcc to compile the resources
    os.system('pyside6-rcc -o resources_rc.py resources.qrc')

if __name__ == '__main__':
    compile_resources()
