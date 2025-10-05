from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt5.QtCore import Qt

class GlobalLogWidget(QWidget):
    _instance = None

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Global Chat/Error Log")
        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)
        GlobalLogWidget._instance = self

    @staticmethod
    def instance():
        if GlobalLogWidget._instance is None:
            GlobalLogWidget._instance = GlobalLogWidget()
        return GlobalLogWidget._instance

    def log(self, message, error=False):
        if error:
            self.text_edit.append(f'<span style="color:red;">{message}</span>')
        else:
            self.text_edit.append(message)
        self.text_edit.moveCursor(self.text_edit.textCursor().End)