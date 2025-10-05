from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QSplitter, QMessageBox, QSizePolicy, QFrame, QSpacerItem
)
from PyQt5.QtCore import Qt
import os

try:
    import markdown
except ImportError:
    markdown = None


class NotesEditor(QWidget):
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.main_window = main_window


        # === Main Vertical Layout ===
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 15, 20, 20)
        main_layout.setSpacing(12)

        # === Splitter (Editor + Preview) ===
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # --- Left: Markdown Editor ---
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Write campaign notes in Markdown...")
        self.editor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.editor.setMinimumHeight(350)   # reduced visible area
        self.editor.setMaximumHeight(450)   # cap height so buttons come up

        # --- Right: Preview Pane ---
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setPlaceholderText("Markdown preview will appear here.")
        self.preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.preview.setMinimumHeight(350)
        self.preview.setMaximumHeight(450)

        self.splitter.addWidget(self.editor)
        self.splitter.addWidget(self.preview)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)

        # === Add splitter to layout ===
        main_layout.addWidget(self.splitter, stretch=1)

        # === Spacer above footer (breathing room) ===
        main_layout.addItem(QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # === Footer (buttons row) ===
        footer = QFrame()
        footer.setFrameShape(QFrame.NoFrame)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(10, 5, 10, 5)
        footer_layout.setSpacing(10)

        # --- Buttons ---
        self.save_btn = QPushButton("💾 Save Notes")
        self.save_btn.setMinimumWidth(120)
        self.save_btn.clicked.connect(self.save_notes)

        self.render_btn = QPushButton("🪄 Render Markdown")
        self.render_btn.setMinimumWidth(150)
        self.render_btn.clicked.connect(self.render_markdown)

        footer_layout.addWidget(self.save_btn)
        footer_layout.addWidget(self.render_btn)
        footer_layout.addStretch(1)

        main_layout.addWidget(footer, stretch=0)

        # --- Apply final layout ---
        self.setLayout(main_layout)
        self.setMinimumHeight(600)

        # Now that UI is set up, load notes if campaign is loaded
        if self.main_window and getattr(self.main_window, "campaign_folder", None):
            self.load_notes()

    def load_notes(self):
        """Load notes from notes.md in the current campaign folder, if available."""
        campaign_folder = None
        if hasattr(self, "main_window") and self.main_window is not None:
            campaign_folder = self.main_window.campaign_folder
        if not campaign_folder:
            self.editor.setPlainText("")
            return
        notes_path = os.path.join(campaign_folder, "notes.md")
        if os.path.exists(notes_path):
            try:
                with open(notes_path, "r", encoding="utf-8") as f:
                    self.editor.setPlainText(f.read())
            except Exception:
                self.editor.setPlainText("")
        else:
            self.editor.setPlainText("")

    # --- Markdown Rendering ---
    def render_markdown(self):
        text = self.editor.toPlainText()
        if markdown:
            html = markdown.markdown(text)
            self.preview.setHtml(html)
        else:
            self.preview.setPlainText("Markdown module not installed.\n\n" + text)

    # --- Save Notes ---
    def save_notes(self):
        campaign_folder = None
        if hasattr(self, "main_window") and self.main_window is not None:
            campaign_folder = self.main_window.campaign_folder

        notes_text = self.editor.toPlainText()

        if not campaign_folder:
            QMessageBox.warning(self, "No Campaign", "Please create or load a campaign first.")
            return

        notes_path = os.path.join(campaign_folder, "notes.md")
        try:
            with open(notes_path, "w", encoding="utf-8") as f:
                f.write(notes_text)
            QMessageBox.information(self, "Notes Saved", f"Notes saved to {notes_path}")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save notes:\n{e}")
