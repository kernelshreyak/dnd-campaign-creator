from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QPushButton, QMessageBox, QLabel, QListWidgetItem
)
from gui.npc_editor import NPCEditor
from utils.file_io import load_entities, save_entity

class NPCTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.add_btn = QPushButton("+")
        self.add_btn.setToolTip("Add New NPC")
        self.add_btn.clicked.connect(self.new_npc)
        left_layout.addWidget(QLabel("NPCs"))
        left_layout.addWidget(self.add_btn)
        left_layout.addWidget(self.list_widget)
        layout.addLayout(left_layout)

        self.editor = NPCEditor()
        self.editor.save_btn.clicked.disconnect()
        self.editor.save_btn.clicked.connect(self.save_npc)
        layout.addWidget(self.editor)

        self.setLayout(layout)
        self.list_widget.itemClicked.connect(self.load_npc)

        self.npcs = []
        self.selected_index = None
        self.refresh_list()

    def refresh_list(self):
        folder = self.main_window.campaign_folder
        self.npcs = load_entities("npcs", folder) if folder else []
        self.list_widget.clear()
        for npc in self.npcs:
            item = QListWidgetItem(npc.get("Name", "Unnamed"))
            self.list_widget.addItem(item)

    def new_npc(self):
        self.selected_index = None
        self.editor.name_edit.clear()
        self.editor.type_combo.setCurrentIndex(0)
        self.editor.role_edit.clear()
        self.editor.ac_edit.clear()
        self.editor.hp_edit.clear()
        self.editor.initiative_edit.clear()
        self.editor.speed_edit.clear()
        self.editor.str_edit.clear()
        self.editor.dex_edit.clear()
        self.editor.con_edit.clear()
        self.editor.int_edit.clear()
        self.editor.wis_edit.clear()
        self.editor.cha_edit.clear()
        self.editor.skills_edit.clear()
        self.editor.gear_edit.clear()
        self.editor.senses_edit.clear()
        self.editor.languages_edit.clear()
        self.editor.cr_edit.clear()
        self.editor.habitat_edit.clear()
        self.editor.desc_edit.clear()
        self.editor.actions_edit.clear()
        self.editor.stat_block_edit.clear()

    def load_npc(self, item):
        idx = self.list_widget.row(item)
        npc = self.npcs[idx]
        self.selected_index = idx
        self.editor.name_edit.setText(npc.get("Name", ""))
        self.editor.type_combo.setCurrentText(npc.get("Type", "Neutral"))
        self.editor.role_edit.setText(npc.get("Role/Title", ""))
        self.editor.ac_edit.setText(str(npc.get("AC", "")))
        self.editor.hp_edit.setText(str(npc.get("HP", "")))
        self.editor.initiative_edit.setText(str(npc.get("Initiative", "")))
        self.editor.speed_edit.setText(str(npc.get("Speed", "")))
        self.editor.str_edit.setText(str(npc.get("STR", "")))
        self.editor.dex_edit.setText(str(npc.get("DEX", "")))
        self.editor.con_edit.setText(str(npc.get("CON", "")))
        self.editor.int_edit.setText(str(npc.get("INT", "")))
        self.editor.wis_edit.setText(str(npc.get("WIS", "")))
        self.editor.cha_edit.setText(str(npc.get("CHA", "")))
        self.editor.skills_edit.setText(npc.get("Skills", ""))
        self.editor.gear_edit.setText(npc.get("Gear", ""))
        self.editor.senses_edit.setText(npc.get("Senses", ""))
        self.editor.languages_edit.setText(npc.get("Languages", ""))
        self.editor.cr_edit.setText(npc.get("CR", ""))
        self.editor.habitat_edit.setText(npc.get("Habitat", ""))
        self.editor.desc_edit.setPlainText(npc.get("Description", ""))
        actions = npc.get("Actions", [])
        self.editor.actions_edit.setPlainText("\n".join([f"{a['name']}; {a['desc']}" for a in actions]))
        self.editor.stat_block_edit.clear()

    def save_npc(self):
        # Validate and collect data from editor
        mandatory = [
            (self.editor.name_edit, "Name"),
            (self.editor.role_edit, "Role/Title"),
            (self.editor.ac_edit, "AC"),
            (self.editor.hp_edit, "HP"),
            (self.editor.initiative_edit, "Initiative"),
            (self.editor.speed_edit, "Speed"),
            (self.editor.str_edit, "STR"),
            (self.editor.dex_edit, "DEX"),
            (self.editor.con_edit, "CON"),
            (self.editor.int_edit, "INT"),
            (self.editor.wis_edit, "WIS"),
            (self.editor.cha_edit, "CHA"),
            (self.editor.skills_edit, "Skills"),
            (self.editor.gear_edit, "Gear"),
            (self.editor.senses_edit, "Senses"),
            (self.editor.languages_edit, "Languages"),
            (self.editor.cr_edit, "CR"),
            (self.editor.habitat_edit, "Habitat"),
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
        npc_data = {
            "Name": self.editor.name_edit.text().strip(),
            "Type": self.editor.type_combo.currentText(),
            "Role/Title": self.editor.role_edit.text().strip(),
            "AC": self.editor.ac_edit.text().strip(),
            "HP": self.editor.hp_edit.text().strip(),
            "Initiative": self.editor.initiative_edit.text().strip(),
            "Speed": self.editor.speed_edit.text().strip(),
            "STR": self.editor.str_edit.text().strip(),
            "DEX": self.editor.dex_edit.text().strip(),
            "CON": self.editor.con_edit.text().strip(),
            "INT": self.editor.int_edit.text().strip(),
            "WIS": self.editor.wis_edit.text().strip(),
            "CHA": self.editor.cha_edit.text().strip(),
            "Skills": self.editor.skills_edit.text().strip(),
            "Gear": self.editor.gear_edit.text().strip(),
            "Senses": self.editor.senses_edit.text().strip(),
            "Languages": self.editor.languages_edit.text().strip(),
            "CR": self.editor.cr_edit.text().strip(),
            "Habitat": self.editor.habitat_edit.text().strip(),
            "Description": self.editor.desc_edit.toPlainText().strip(),
            "Actions": actions,
        }
        folder = self.main_window.campaign_folder
        if not folder:
            QMessageBox.warning(self, "No Campaign", "Please create or load a campaign first.")
            return
        save_entity("npcs", npc_data, folder)
        QMessageBox.information(self, "Saved", "NPC saved.")
        self.refresh_list()