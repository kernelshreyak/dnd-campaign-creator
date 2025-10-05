from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QFormLayout, QPushButton, QMessageBox, QComboBox
)

class ItemEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()

        self.form = QFormLayout()
        self.name_edit = QLineEdit()
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Weapon", "Armor", "Gear", "Magic Item", "Other"])
        self.properties_edit = QLineEdit()
        self.desc_edit = QTextEdit()
        self.form.addRow("Name:", self.name_edit)
        self.form.addRow("Type:", self.type_combo)
        self.form.addRow("Properties:", self.properties_edit)
        self.form.addRow("Description:", self.desc_edit)
        layout.addLayout(self.form)

        self.save_btn = QPushButton("Save Item (placeholder)")
        self.save_btn.clicked.connect(self.save_item)
        layout.addWidget(self.save_btn)

        self.setLayout(layout)

    def save_item(self):
        # Placeholder: In real implementation, save to campaign data
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Missing Name", "Please enter an item name.")
            return
        QMessageBox.information(self, "Saved", "Item saved (placeholder).")