from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QPushButton, QMessageBox, QLabel, QListWidgetItem
)
from gui.character_editor import CharacterEditor
from utils.file_io import load_entities, save_entity

class CharacterTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.add_btn = QPushButton("+")
        self.add_btn.setToolTip("Add New Character")
        self.add_btn.clicked.connect(self.new_character)
        left_layout.addWidget(QLabel("Characters"))
        left_layout.addWidget(self.add_btn)
        left_layout.addWidget(self.list_widget)
        layout.addLayout(left_layout)

        self.editor = CharacterEditor()
        self.editor.save_btn.clicked.disconnect()
        self.editor.save_btn.clicked.connect(self.save_character)
        layout.addWidget(self.editor)

        self.setLayout(layout)
        self.list_widget.itemClicked.connect(self.load_character)

        self.characters = []
        self.selected_index = None
        self.refresh_list()

    def refresh_list(self):
        folder = self.main_window.campaign_folder
        self.characters = load_entities("characters", folder) if folder else []
        self.list_widget.clear()
        for char in self.characters:
            item = QListWidgetItem(char.get("Name", "Unnamed"))
            self.list_widget.addItem(item)

    def new_character(self):
        self.selected_index = None
        self.editor.name_edit.clear()
        self.editor.race_edit.clear()
        self.editor.class_edit.clear()
        self.editor.level_edit.clear()
        self.editor.alignment_edit.clear()
        self.editor.hp_edit.clear()
        self.editor.ac_edit.clear()
        self.editor.str_edit.clear()
        self.editor.dex_edit.clear()
        self.editor.con_edit.clear()
        self.editor.int_edit.clear()
        self.editor.wis_edit.clear()
        self.editor.cha_edit.clear()
        self.editor.actions_edit.clear()

    def load_character(self, item):
        idx = self.list_widget.row(item)
        char = self.characters[idx]
        self.selected_index = idx
        self.editor.name_edit.setText(char.get("Name", ""))
        self.editor.race_edit.setText(char.get("Race", ""))
        self.editor.class_edit.setText(char.get("Class", ""))
        self.editor.level_edit.setText(str(char.get("Level", "")))
        self.editor.alignment_edit.setText(char.get("Alignment", ""))
        self.editor.hp_edit.setText(str(char.get("HP", "")))
        self.editor.ac_edit.setText(str(char.get("AC", "")))
        self.editor.str_edit.setText(str(char.get("STR", "")))
        self.editor.dex_edit.setText(str(char.get("DEX", "")))
        self.editor.con_edit.setText(str(char.get("CON", "")))
        self.editor.int_edit.setText(str(char.get("INT", "")))
        self.editor.wis_edit.setText(str(char.get("WIS", "")))
        self.editor.cha_edit.setText(str(char.get("CHA", "")))
        actions = char.get("Actions", [])
        self.editor.actions_edit.setPlainText("\n".join([f"{a['name']}; {a['desc']}" for a in actions]))

    def save_character(self):
        # Validate and collect data from editor
        mandatory = [
            (self.editor.name_edit, "Name"),
            (self.editor.race_edit, "Race"),
            (self.editor.class_edit, "Class"),
            (self.editor.level_edit, "Level"),
            (self.editor.alignment_edit, "Alignment"),
            (self.editor.hp_edit, "HP"),
            (self.editor.ac_edit, "AC"),
            (self.editor.str_edit, "STR"),
            (self.editor.dex_edit, "DEX"),
            (self.editor.con_edit, "CON"),
            (self.editor.int_edit, "INT"),
            (self.editor.wis_edit, "WIS"),
            (self.editor.cha_edit, "CHA"),
        ]
        missing = [label for edit, label in mandatory if not edit.text().strip()]
        if missing:
            QMessageBox.warning(self, "Missing Fields", f"Please fill in all mandatory fields: {', '.join(missing)}")
            return
        actions = []
        for line in self.editor.actions_edit.toPlainText().splitlines():
            if ";" in line:
                name, desc = line.split(";", 1)
                actions.append({"name": name.strip(), "desc": desc.strip()})
            elif line.strip():
                actions.append({"name": line.strip(), "desc": ""})
        char_data = {
            "Name": self.editor.name_edit.text().strip(),
            "Race": self.editor.race_edit.text().strip(),
            "Class": self.editor.class_edit.text().strip(),
            "Level": self.editor.level_edit.text().strip(),
            "Alignment": self.editor.alignment_edit.text().strip(),
            "HP": self.editor.hp_edit.text().strip(),
            "AC": self.editor.ac_edit.text().strip(),
            "STR": self.editor.str_edit.text().strip(),
            "DEX": self.editor.dex_edit.text().strip(),
            "CON": self.editor.con_edit.text().strip(),
            "INT": self.editor.int_edit.text().strip(),
            "WIS": self.editor.wis_edit.text().strip(),
            "CHA": self.editor.cha_edit.text().strip(),
            "Actions": actions,
        }
        folder = self.main_window.campaign_folder
        if not folder:
            QMessageBox.warning(self, "No Campaign", "Please create or load a campaign first.")
            return
        save_entity("characters", char_data, folder)
        QMessageBox.information(self, "Saved", "Character saved.")
        self.refresh_list()