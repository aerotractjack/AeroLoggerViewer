import sys
from PyQt6.QtWidgets import (QApplication, QWizard, QHBoxLayout, QVBoxLayout, 
                             QLabel, QPushButton, QWizardPage,
                            QListWidget, QTextEdit, QComboBox)
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtCore import Qt
import requests
import json 

from syntax_highlight import LogHighlighter

from requires_nas import requires_nas_loop
from aerologger import AeroLogger
logger = AeroLogger(
    'AeroLoggerDash',
    'AeroLoggerDash/AeroLoggerDash.log'
)

class LogSelectionPage(QWizardPage):
    def __init__(self):
        super().__init__()
        requires_nas_loop(info_logger=logger.info, error_logger=logger.error)
        with open("/home/aerotract/NAS/main/software/host_map.json", "r") as fp:
            self.api_url_map = json.loads(fp.read())
        self.api_host = "My Machine"
        self.api_url = self.api_url_map["My Machine"] 
        self.logList = QListWidget()
        self.logList.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.log_descs = self.describe_logs()
        self.init_ui()

    def on_api_selection_changed(self, text):
        self.api_host = text
        self.api_url = self.api_url_map[text]
        self.log_descs = self.describe_logs() 
        self.update_log_list()

    def update_log_list(self):
        self.logList.clear()  # Clear existing items in the list
        for key in self.log_descs.keys():
            self.logList.addItem(key)  # Add new items based on updated log descriptions

    def describe_logs(self):
        req = requests.get(self.api_url + "/describe_logs")
        if not req.status_code == 200:
            raise ValueError("Error reaching API: " + req.text)
        return req.json()
        
    def init_ui(self):
        layout = QVBoxLayout(self)

        self.apiSelectionCombo = QComboBox()
        for key in self.api_url_map.keys():
            self.apiSelectionCombo.addItem(key)
        self.apiSelectionCombo.setCurrentText("My Machine")  
        self.apiSelectionCombo.currentTextChanged.connect(self.on_api_selection_changed)
        layout.addWidget(self.apiSelectionCombo)
        
        titleLabel = QLabel("Select one or more logs to view")
        titleLabel.setFont(QFont("Liberation Mono", 16, QFont.Weight.Bold)) 
        layout.addWidget(titleLabel)

        self.update_log_list()
        layout.addWidget(self.logList)

    def initializePage(self):
        self.wizard().setMaximumSize(400, 400)

    def nextId(self):
        selected_logs = [item.text() for item in self.logList.selectedItems()]
        self.wizard().logContentPage.setLogContents(self.api_host, self.api_url, selected_logs, self.log_descs)
        return super().nextId()

class LogContentPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighters = []
        self.current_log_keys = []
        self.current_log_descs = {}
        self.host_label = None
        self.initUI()

    def initUI(self):
        self.mainLayout = QVBoxLayout(self)  # Main layout to hold everything

        self.host_label = QLabel("API URL: Not Set")
        self.host_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.mainLayout.addWidget(self.host_label)

        # Create and add the refresh button at the top
        self.refreshButton = QPushButton("Refresh")
        self.refreshButton.clicked.connect(self.refreshLogs)
        self.mainLayout.addWidget(self.refreshButton)

        # Horizontal layout for log content
        self.logLayout = QHBoxLayout()
        self.mainLayout.addLayout(self.logLayout)

    def setLogContents(self, api_host, api_url, log_keys, log_descs):
        self.current_api_host = api_host
        self.current_api_url = api_url
        self.current_log_keys = log_keys        
        self.current_log_descs = log_descs
        self.host_label.setText(f"Reading logs from: {self.current_api_host}")
        self.refreshLogs()

    def refreshLogs(self):
        # Clear existing widgets in the log layout
        self.clearLayout(self.logLayout)

        # Repopulate the logs
        for key in self.current_log_keys:
            self.addLogContent(key, self.current_log_descs[key])

    def addLogContent(self, key, log_desc):
        # Create a QVBoxLayout for each log entry (title + textEdit)
        logLayout = QVBoxLayout()

        # Create and add a title label
        titleLabel = QLabel(key)
        titleLabel.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logLayout.addWidget(titleLabel)

        # Create the QTextEdit for log content
        logContent = self.readLogAPI(log_desc)
        textEdit = QTextEdit()
        textEdit.setPlainText(logContent)
        textEdit.setReadOnly(True)
        textEdit.setMinimumSize(600, 600)
        logLayout.addWidget(textEdit)

        # Apply syntax highlighter
        highlighter = LogHighlighter(textEdit.document())
        self.highlighters.append(highlighter)

        # Scroll to bottom
        cursor = QTextCursor(textEdit.document())
        cursor.movePosition(QTextCursor.MoveOperation.End)
        textEdit.setTextCursor(cursor)

        # Add this log's layout to the main log layout
        self.logLayout.addLayout(logLayout)
        
    def readLogAPI(self, log_desc):
        req = requests.post(self.current_api_url + "/read_log", 
                            json=log_desc,
                            headers={"Content-Type": "application/json"})
        return req.json()

    def clearLayout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                innerLayout = item.layout()
                if innerLayout is not None:
                    self.clearLayout(innerLayout)
                    innerLayout.deleteLater()


class App(QWizard):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AeroLogger Dashboard")
        self.selp = LogSelectionPage()  # Log Selection Page
        self.logContentPage = LogContentPage()  # Log Content Page
        self.addPage(self.selp)
        self.addPage(self.logContentPage)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())
