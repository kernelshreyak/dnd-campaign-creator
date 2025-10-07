import os

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSplitter,
    QVBoxLayout,
    QWidget,
    QPlainTextEdit,
    QTextBrowser,
)

try:
    import markdown
except ImportError:
    markdown = None


class NotesEditor(QWidget):
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.main_window = main_window

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 15, 20, 20)
        main_layout.setSpacing(12)

        self.splitter = QSplitter(Qt.Horizontal)

        # Editor pane (plain text Markdown).
        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("Write campaign notes in Markdown…")
        self.editor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.editor.setMinimumHeight(360)
        self.editor.textChanged.connect(self._on_editor_changed)
        self.splitter.addWidget(self.editor)

        # Live preview pane.
        self.preview = QTextBrowser()
        self.preview.setPlaceholderText("Markdown preview appears here.")
        self.preview.setOpenExternalLinks(True)
        self.preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.splitter.addWidget(self.preview)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)

        main_layout.addWidget(self.splitter, stretch=1)

        main_layout.addItem(QSpacerItem(0, 6, QSizePolicy.Minimum, QSizePolicy.Fixed))

        footer = QFrame()
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(10, 5, 10, 5)
        footer_layout.setSpacing(10)

        self.save_btn = QPushButton("💾 Save Notes")
        self.save_btn.setMinimumWidth(120)
        self.save_btn.clicked.connect(self.save_notes)
        footer_layout.addWidget(self.save_btn)
        footer_layout.addStretch(1)

        main_layout.addWidget(footer, stretch=0)

        self.setLayout(main_layout)
        self.setMinimumHeight(600)

        # Debounced render timer triggers preview update 2s after last edit.
        self.render_timer = QTimer(self)
        self.render_timer.setSingleShot(True)
        self.render_timer.setInterval(2000)
        self.render_timer.timeout.connect(self.render_markdown)

        if self.main_window and getattr(self.main_window, "campaign_folder", None):
            self.load_notes()
        else:
            self.render_markdown()

    # --- Editor / preview helpers -----------------------------------
    def _on_editor_changed(self):
        # Restart the timer so rendering only happens after user pauses typing.
        self.render_timer.start()

    def render_markdown(self):
        text = self.editor.toPlainText()
        if markdown:
            try:
                html_content = markdown.markdown(text)
                self.preview.setHtml(html_content)
            except Exception as exc:
                self.preview.setPlainText(f"Failed to render markdown:\n{exc}")
        else:
            self.preview.setPlainText("Markdown module not installed.\n\n" + text)

    # --- Notes IO ---------------------------------------------------
    def load_notes(self):
        campaign_folder = getattr(self.main_window, "campaign_folder", None) if self.main_window else None
        if not campaign_folder:
            self.editor.setPlainText("")
            self.render_markdown()
            return

        notes_path = os.path.join(campaign_folder, "notes.md")
        if os.path.exists(notes_path):
            try:
                with open(notes_path, "r", encoding="utf-8") as f:
                    self.editor.blockSignals(True)
                    self.editor.setPlainText(f.read())
                    self.editor.blockSignals(False)
            except Exception:
                self.editor.blockSignals(True)
                self.editor.setPlainText("")
                self.editor.blockSignals(False)
        else:
            self.editor.blockSignals(True)
            self.editor.setPlainText("")
            self.editor.blockSignals(False)
        self.render_markdown()

    def save_notes(self):
        campaign_folder = getattr(self.main_window, "campaign_folder", None) if self.main_window else None
        if not campaign_folder:
            QMessageBox.warning(self, "No Campaign", "Please create or load a campaign first.")
            return

        notes_path = os.path.join(campaign_folder, "notes.md")
        notes_text = self.editor.toPlainText()
        try:
            with open(notes_path, "w", encoding="utf-8") as f:
                f.write(notes_text)
            QMessageBox.information(self, "Notes Saved", f"Notes saved to {notes_path}")
        except Exception as exc:
            QMessageBox.critical(self, "Save Error", f"Failed to save notes:\n{exc}")
