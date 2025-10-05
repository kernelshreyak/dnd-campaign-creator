from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QPushButton, QMessageBox, QLabel, QListWidgetItem
)
from gui.item_editor import ItemEditor
from utils.file_io import load_entities, save_entity

class ItemTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.add_btn = QPushButton("+")
        self.add_btn.setToolTip("Add New Item")
        self.add_btn.clicked.connect(self.new_item)
        left_layout.addWidget(QLabel("Items"))
        left_layout.addWidget(self.add_btn)
        left_layout.addWidget(self.list_widget)
        layout.addLayout(left_layout)

        self.editor = ItemEditor()
        self.editor.save_btn.clicked.disconnect()
        self.editor.save_btn.clicked.connect(self.save_item)
        layout.addWidget(self.editor)

        self.setLayout(layout)
        self.list_widget.itemClicked.connect(self.load_item)

        self.items = []
        self.selected_index = None
        self.refresh_list()

    def refresh_list(self):
        folder = self.main_window.campaign_folder
        self.items = load_entities("items", folder) if folder else []
        self.list_widget.clear()
        for item in self.items:
            item_widget = QListWidgetItem(item.get("Name", "Unnamed"))
            self.list_widget.addItem(item_widget)

    def new_item(self):
        self.selected_index = None
        self.editor.name_edit.clear()
        self.editor.type_combo.setCurrentIndex(0)
        self.editor.properties_edit.clear()
        self.editor.desc_edit.clear()

    def load_item(self, item):
        idx = self.list_widget.row(item)
        item_data = self.items[idx]
        self.selected_index = idx
        self.editor.name_edit.setText(item_data.get("Name", ""))
        self.editor.type_combo.setCurrentText(item_data.get("Type", "Weapon"))
        self.editor.properties_edit.setText(item_data.get("Properties", ""))
        self.editor.desc_edit.setPlainText(item_data.get("Description", ""))

    def save_item(self):
        # Validate and collect data from editor
        mandatory = [
            (self.editor.name_edit, "Name"),
            (self.editor.type_combo, "Type"),
        ]
        missing = [label for edit, label in mandatory if not (edit.text().strip() if hasattr(edit, "text") else edit.currentText().strip())]
        if missing:
            QMessageBox.warning(self, "Missing Fields", f"Please fill in all mandatory fields: {', '.join(missing)}")
            return
        item_data = {
            "Name": self.editor.name_edit.text().strip(),
            "Type": self.editor.type_combo.currentText(),
            "Properties": self.editor.properties_edit.text().strip(),
            "Description": self.editor.desc_edit.toPlainText().strip(),
        }
        folder = self.main_window.campaign_folder
        if not folder:
            QMessageBox.warning(self, "No Campaign", "Please create or load a campaign first.")
            return
        save_entity("items", item_data, folder)
        QMessageBox.information(self, "Saved", "Item saved.")
        self.refresh_list()