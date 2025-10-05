from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QPushButton, QMessageBox, QLabel, QListWidgetItem
)
from gui.spell_editor import SpellEditor
from utils.file_io import load_entities, save_entity

class SpellTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.add_btn = QPushButton("+")
        self.add_btn.setToolTip("Add New Spell")
        self.add_btn.clicked.connect(self.new_spell)
        left_layout.addWidget(QLabel("Spells"))
        left_layout.addWidget(self.add_btn)
        left_layout.addWidget(self.list_widget)
        layout.addLayout(left_layout)

        self.editor = SpellEditor()
        self.editor.save_btn.clicked.disconnect()
        self.editor.save_btn.clicked.connect(self.save_spell)
        layout.addWidget(self.editor)

        self.setLayout(layout)
        self.list_widget.itemClicked.connect(self.load_spell)

        self.spells = []
        self.selected_index = None
        self.refresh_list()

    def refresh_list(self):
        folder = self.main_window.campaign_folder
        self.spells = load_entities("spells", folder) if folder else []
        self.list_widget.clear()
        for spell in self.spells:
            item = QListWidgetItem(spell.get("Name", "Unnamed"))
            self.list_widget.addItem(item)

    def new_spell(self):
        self.selected_index = None
        self.editor.name_edit.clear()
        self.editor.level_edit.clear()
        self.editor.school_edit.clear()
        self.editor.casting_time_edit.clear()
        self.editor.range_edit.clear()
        self.editor.components_edit.clear()
        self.editor.duration_edit.clear()
        self.editor.desc_edit.clear()

    def load_spell(self, item):
        idx = self.list_widget.row(item)
        spell = self.spells[idx]
        self.selected_index = idx
        self.editor.name_edit.setText(spell.get("Name", ""))
        self.editor.level_edit.setText(str(spell.get("Level", "")))
        self.editor.school_edit.setText(spell.get("School", ""))
        self.editor.casting_time_edit.setText(spell.get("Casting Time", ""))
        self.editor.range_edit.setText(spell.get("Range", ""))
        self.editor.components_edit.setText(spell.get("Components", ""))
        self.editor.duration_edit.setText(spell.get("Duration", ""))
        self.editor.desc_edit.setPlainText(spell.get("Description", ""))

    def save_spell(self):
        # Validate and collect data from editor
        mandatory = [
            (self.editor.name_edit, "Name"),
            (self.editor.level_edit, "Level"),
            (self.editor.school_edit, "School"),
            (self.editor.casting_time_edit, "Casting Time"),
            (self.editor.range_edit, "Range"),
            (self.editor.components_edit, "Components"),
            (self.editor.duration_edit, "Duration"),
        ]
        missing = [label for edit, label in mandatory if not edit.text().strip()]
        if missing:
            QMessageBox.warning(self, "Missing Fields", f"Please fill in all mandatory fields: {', '.join(missing)}")
            return
        spell_data = {
            "Name": self.editor.name_edit.text().strip(),
            "Level": self.editor.level_edit.text().strip(),
            "School": self.editor.school_edit.text().strip(),
            "Casting Time": self.editor.casting_time_edit.text().strip(),
            "Range": self.editor.range_edit.text().strip(),
            "Components": self.editor.components_edit.text().strip(),
            "Duration": self.editor.duration_edit.text().strip(),
            "Description": self.editor.desc_edit.toPlainText().strip(),
        }
        folder = self.main_window.campaign_folder
        if not folder:
            QMessageBox.warning(self, "No Campaign", "Please create or load a campaign first.")
            return
        save_entity("spells", spell_data, folder)
        QMessageBox.information(self, "Saved", "Spell saved.")
        self.refresh_list()