from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QFormLayout, QPushButton, QMessageBox
)

class SpellEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()

        self.form = QFormLayout()
        self.name_edit = QLineEdit()
        self.level_edit = QLineEdit()
        self.school_edit = QLineEdit()
        self.casting_time_edit = QLineEdit()
        self.range_edit = QLineEdit()
        self.components_edit = QLineEdit()
        self.duration_edit = QLineEdit()
        self.desc_edit = QTextEdit()
        self.form.addRow("Name:", self.name_edit)
        self.form.addRow("Level:", self.level_edit)
        self.form.addRow("School:", self.school_edit)
        self.form.addRow("Casting Time:", self.casting_time_edit)
        self.form.addRow("Range:", self.range_edit)
        self.form.addRow("Components:", self.components_edit)
        self.form.addRow("Duration:", self.duration_edit)
        self.form.addRow("Description:", self.desc_edit)
        layout.addLayout(self.form)

        self.save_btn = QPushButton("Save Spell (placeholder)")
        self.save_btn.clicked.connect(self.save_spell)
        layout.addWidget(self.save_btn)

        self.setLayout(layout)

    def save_spell(self):
        # Placeholder: In real implementation, save to campaign data
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Missing Name", "Please enter a spell name.")
            return
        QMessageBox.information(self, "Saved", "Spell saved (placeholder).")