from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QListWidget,
    QPushButton,
    QMessageBox,
    QLabel,
    QListWidgetItem,
    QApplication,
    QInputDialog,
    QTableWidgetItem,
    QLineEdit,
    QSplitter,
)
from PyQt5.QtCore import Qt
from gui.npc_editor import NPCEditor
from utils.file_io import load_entities
import json

class NPCTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # --- Main horizontal layout with resizable panels ---
        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(8, 8, 8, 8)
        root_layout.setSpacing(12)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        root_layout.addWidget(splitter)

        # --- NPC list sidebar ---
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(6)

        sidebar_layout.addWidget(QLabel("NPCs"))

        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 0, 0, 0)

        self.list_widget = QListWidget()
        self.add_btn = QPushButton("+")
        self.add_btn.setToolTip("Add New NPC")
        self.add_btn.clicked.connect(self.new_npc)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setToolTip("Delete Selected NPC")
        self.delete_btn.clicked.connect(self.delete_npc)

        controls_layout.addWidget(self.add_btn)
        controls_layout.addWidget(self.delete_btn)
        sidebar_layout.addLayout(controls_layout)
        sidebar_layout.addWidget(self.list_widget, stretch=1)

        splitter.addWidget(sidebar)

        # --- Editor pane ---
        editor_panel = QWidget()
        editor_layout = QVBoxLayout(editor_panel)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(8)

        self.editor = NPCEditor()
        self.editor.save_btn.clicked.connect(self.save_npc)
        editor_layout.addWidget(self.editor, stretch=1)

        # Add "Copy Action as String" button below the actions table

        self.copy_action_btn = QPushButton("Copy Action as String")
        def copy_selected_action():
            row = self.editor.actions_table.currentRow()
            if row < 0:
                QMessageBox.warning(self, "No Action Selected", "Please select an action row to copy.")
                return
            action = {
                "name": self.editor.actions_table.item(row, 0).text() if self.editor.actions_table.item(row, 0) else "",
                "type": self.editor.actions_table.item(row, 1).text() if self.editor.actions_table.item(row, 1) else "",
                "attack_bonus": self.editor.actions_table.item(row, 2).text() if self.editor.actions_table.item(row, 2) else "",
                "damage": self.editor.actions_table.item(row, 3).text() if self.editor.actions_table.item(row, 3) else "",
                "damage_type": self.editor.actions_table.item(row, 4).text() if self.editor.actions_table.item(row, 4) else "",
                "description": self.editor.actions_table.item(row, 5).text() if self.editor.actions_table.item(row, 5) else "",
            }
            clipboard = QApplication.clipboard()
            clipboard.setText(json.dumps(action, indent=2))
            QMessageBox.information(self, "Copied", "Selected action copied to clipboard as JSON.")
        self.copy_action_btn.clicked.connect(copy_selected_action)
        editor_layout.addWidget(self.copy_action_btn, alignment=Qt.AlignLeft)

        # Add AI Action Generation input and button
        ai_action_layout = QHBoxLayout()
        self.ai_action_edit = QLineEdit()
        self.ai_action_edit.setPlaceholderText("Describe the action to generate (e.g. 'fireball attack')")
        self.ai_action_btn = QPushButton("Generate Action with AI")
        def generate_action_with_ai():
            import openai
            desc = self.ai_action_edit.text().strip()
            if not desc:
                QMessageBox.warning(self, "No Description", "Please enter a description for the action.")
                return
            prompt = (
                "You are an expert D&D 5e action generator. "
                "Generate a single action as a JSON object with fields: "
                "name, type, attack_bonus, damage, damage_type, description. "
                f"Description: {desc}\n"
                "Output only the JSON object."
            )
            try:
                response = openai.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300,
                    temperature=0.7,
                    response_format={"type": "json_object"}
                )
                import json as pyjson
                content = response.choices[0].message.content
                action = pyjson.loads(content)
                row = self.editor.actions_table.rowCount()
                self.editor.actions_table.insertRow(row)
                for col, key in enumerate(["name", "type", "attack_bonus", "damage", "damage_type", "description"]):
                    self.editor.actions_table.setItem(row, col, QTableWidgetItem(str(action.get(key, ""))))
                QMessageBox.information(self, "AI Generated", "Action generated and added to table.")
            except Exception as e:
                QMessageBox.critical(self, "AI Error", f"Failed to generate action with AI:\n{e}")
        self.ai_action_btn.clicked.connect(generate_action_with_ai)
        ai_action_layout.addWidget(self.ai_action_edit)
        ai_action_layout.addWidget(self.ai_action_btn)
        editor_layout.addLayout(ai_action_layout)
        editor_layout.addStretch()

        splitter.addWidget(editor_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        self.setLayout(root_layout)
        self.list_widget.itemClicked.connect(self.load_npc)

        self.npcs = []
        self.selected_index = None
        self.refresh_list()

    def delete_npc(self):
        selected = self.list_widget.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Delete NPC", "No NPC selected.")
            return
        npc = self.npcs[selected]
        name = npc.get("Name", "Unnamed")
        reply = QMessageBox.question(
            self, "Delete NPC",
            f"Are you sure you want to delete '{name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            # Remove from npcs.json
            folder = self.main_window.campaign_folder
            if folder:
                import os, json
                json_path = os.path.join(folder, "npcs.json")
                if os.path.exists(json_path):
                    with open(json_path, "r") as f:
                        npcs = json.load(f)
                    # Remove first entry with matching name
                    for i, c in enumerate(npcs):
                        if c.get("Name", "") == name:
                            del npcs[i]
                            break
                    with open(json_path, "w") as f:
                        json.dump(npcs, f, indent=2)
            # Remove from UI
            self.refresh_list()
            self.editor.name_edit.clear()
            self.editor.token_edit.clear()
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
            self.editor.resist_edit.clear()
            self.editor.vuln_edit.clear()
            self.editor.immune_edit.clear()
            self.editor.clear_actions()
            self.editor.stat_block_edit.clear()

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
        self.editor.token_edit.clear()
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
        self.editor.resist_edit.clear()
        self.editor.vuln_edit.clear()
        self.editor.immune_edit.clear()
        self.editor.clear_actions()
        self.editor.stat_block_edit.clear()

    def load_npc(self, item):
        idx = self.list_widget.row(item)
        npc = self.npcs[idx]
        self.selected_index = idx
        self.editor.name_edit.setText(npc.get("Name", ""))
        self.editor.token_edit.setText(npc.get("TokenImage", ""))
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
        self.editor.resist_edit.setText(npc.get("Resistances", ""))
        self.editor.vuln_edit.setText(npc.get("Vulnerabilities", ""))
        self.editor.immune_edit.setText(npc.get("Immunities", ""))
        actions = npc.get("Actions", [])
        self.editor.set_actions(actions)
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
        # Collect actions from the actions_table
        actions = []
        for row in range(self.editor.actions_table.rowCount()):
            action = {
                "name": self.editor.actions_table.item(row, 0).text() if self.editor.actions_table.item(row, 0) else "",
                "type": self.editor.actions_table.item(row, 1).text() if self.editor.actions_table.item(row, 1) else "",
                "attack_bonus": self.editor.actions_table.item(row, 2).text() if self.editor.actions_table.item(row, 2) else "",
                "damage": self.editor.actions_table.item(row, 3).text() if self.editor.actions_table.item(row, 3) else "",
                "damage_type": self.editor.actions_table.item(row, 4).text() if self.editor.actions_table.item(row, 4) else "",
                "description": self.editor.actions_table.item(row, 5).text() if self.editor.actions_table.item(row, 5) else "",
            }
            actions.append(action)
        npc_data = {
            "Name": self.editor.name_edit.text().strip(),
            "Type": self.editor.type_combo.currentText(),
            "TokenImage": self.editor.token_edit.text().strip(),
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
            "Resistances": self.editor.resist_edit.text().strip(),
            "Vulnerabilities": self.editor.vuln_edit.text().strip(),
            "Immunities": self.editor.immune_edit.text().strip(),
            "Actions": actions,
        }
        folder = self.main_window.campaign_folder
        if not folder:
            QMessageBox.warning(self, "No Campaign", "Please create or load a campaign first.")
            return
        # Override NPC with same name if exists
        import os, json
        json_path = os.path.join(folder, "npcs.json")
        npcs = []
        if os.path.exists(json_path):
            with open(json_path, "r") as f:
                try:
                    npcs = json.load(f)
                except Exception:
                    npcs = []
        # Remove any NPC with the same name
        npcs = [c for c in npcs if c.get("Name", "") != npc_data["Name"]]
        npcs.append(npc_data)
        with open(json_path, "w") as f:
            json.dump(npcs, f, indent=2)
        QMessageBox.information(self, "Saved", "NPC saved (overwritten if name existed).")
        self.refresh_list()
    def copy_action_string(self):
        import json
        actions = []
        for row in range(self.editor.actions_table.rowCount()):
            action = {
                "name": self.editor.actions_table.item(row, 0).text() if self.editor.actions_table.item(row, 0) else "",
                "type": self.editor.actions_table.item(row, 1).text() if self.editor.actions_table.item(row, 1) else "",
                "attack_bonus": self.editor.actions_table.item(row, 2).text() if self.editor.actions_table.item(row, 2) else "",
                "damage": self.editor.actions_table.item(row, 3).text() if self.editor.actions_table.item(row, 3) else "",
                "damage_type": self.editor.actions_table.item(row, 4).text() if self.editor.actions_table.item(row, 4) else "",
                "description": self.editor.actions_table.item(row, 5).text() if self.editor.actions_table.item(row, 5) else "",
            }
            actions.append(action)
        action_string = json.dumps(actions, indent=2)
        clipboard = QApplication.clipboard()
        clipboard.setText(action_string)
        QMessageBox.information(self, "Copied", "Action copied to clipboard as JSON string.")

    def import_action_string(self):
        import json
        action_string, ok = QInputDialog.getText(self, "Import Action", "Paste action JSON string:")
        if ok and action_string:
            try:
                actions = json.loads(action_string)
                self.editor.actions_table.setRowCount(0)
                for action in actions:
                    row = self.editor.actions_table.rowCount()
                    self.editor.actions_table.insertRow(row)
                    for col, key in enumerate(["name", "type", "attack_bonus", "damage", "damage_type", "description"]):
                        self.editor.actions_table.setItem(row, col, QTableWidgetItem(str(action.get(key, ""))))
                QMessageBox.information(self, "Imported", "Actions imported from JSON string.")
            except json.JSONDecodeError:
                QMessageBox.critical(self, "Error", "Invalid JSON string.")
