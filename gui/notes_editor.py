from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QSplitter
)
from PyQt5.QtCore import Qt
try:
    import markdown
except ImportError:
    markdown = None

class NotesEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()

        self.splitter = QSplitter(Qt.Horizontal)
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Write campaign notes in Markdown...")
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setPlaceholderText("Markdown preview will appear here.")

        self.splitter.addWidget(self.editor)
        self.splitter.addWidget(self.preview)
        layout.addWidget(self.splitter)

        self.render_btn = QPushButton("Render Markdown")
        self.render_btn.clicked.connect(self.render_markdown)
        layout.addWidget(self.render_btn)

        self.setLayout(layout)

    def render_markdown(self):
        text = self.editor.toPlainText()
        if markdown:
            html = markdown.markdown(text)
            self.preview.setHtml(html)
        else:
            self.preview.setPlainText("Markdown module not installed.\n\n" + text)