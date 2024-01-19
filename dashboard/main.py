import sys
from PyQt6.QtWidgets import (QApplication, QWizard, QHBoxLayout, QVBoxLayout, 
                    QComboBox, QLabel, QPushButton, QFileDialog, QWizardPage,
                    QListWidget)
from PyQt6.QtCore import QFileInfo
from PyQt6.QtGui import QFont
import json
import os
from pathlib import Path

from aerologger import AeroLogger
dup_logger = AeroLogger(
    'AeroLoggerDash',
    'AeroLoggerDash/AeroLoggerDash.log'
)

class ProjectDataSelectionPage(QWizardPage):
    def __init__(self):
        super().__init__()
        
    def init_ui(self):
        pass

class App(QWizard):
    def __init__(self):
        super().__init__()
        self.selp = ProjectDataSelectionPage() # 0
        self.addPage(self.selp)
        self.setWindowTitle("AeroLogger Dashboard")
        self.finished.connect(self.on_submit)

    def on_submit(self):
        return

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())
