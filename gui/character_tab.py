from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QListWidget,
    QPushButton,
    QMessageBox,
    QLabel,
    QListWidgetItem,
    QTableWidgetItem,
    QLineEdit,
    QApplication,
    QSplitter,
)
from PyQt5.QtCore import Qt
from gui.character_editor import CharacterEditor
from utils.file_io import load_entities
from gui.global_log import GlobalLogWidget
import os
import json
import openai

class CharacterTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(8, 8, 8, 8)
        root_layout.setSpacing(12)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        root_layout.addWidget(splitter)

        sidebar = QWidget()
        left_layout = QVBoxLayout(sidebar)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)
        self.list_widget = QListWidget()
        self.add_btn = QPushButton("+")
        self.add_btn.setToolTip("Add New Character")
        self.add_btn.clicked.connect(self.new_character)
        left_layout.addWidget(QLabel("Characters"))
        left_layout.addWidget(self.add_btn)
        # Add Delete button
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setToolTip("Delete Selected Character")
        self.delete_btn.clicked.connect(self.delete_character)
        left_layout.addWidget(self.delete_btn)
        left_layout.addWidget(self.list_widget)
        splitter.addWidget(sidebar)

        # --- AI Generation UI ---
        ai_layout = QHBoxLayout()
        ai_layout.setContentsMargins(0, 0, 0, 0)
        ai_layout.setSpacing(6)
        self.ai_desc_edit = QLineEdit()
        self.ai_desc_edit.setPlaceholderText("Describe the character to generate (e.g. 'elven wizard, level 5')")
        self.ai_generate_btn = QPushButton("Generate with AI")
        self.ai_generate_btn.clicked.connect(self.generate_with_ai)
        ai_layout.addWidget(self.ai_desc_edit)
        ai_layout.addWidget(self.ai_generate_btn)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)
        right_layout.addLayout(ai_layout)

        self.editor = CharacterEditor()
        self.editor.save_btn.clicked.disconnect()
        self.editor.save_btn.clicked.connect(self.save_character)
        right_layout.addWidget(self.editor, stretch=1)

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
        self.editor.add_footer_widget(self.copy_action_btn)

        # Add AI Action Generation input and button
        ai_action_layout = QHBoxLayout()
        ai_action_layout.setContentsMargins(0, 0, 0, 0)
        ai_action_layout.setSpacing(6)
        self.ai_action_edit = QLineEdit()
        self.ai_action_edit.setPlaceholderText("Describe the action to generate (e.g. 'fireball attack')")
        self.ai_action_btn = QPushButton("Generate Action with AI")
        def generate_action_with_ai():
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
                content = response.choices[0].message.content
                action = json.loads(content)
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
        self.editor.add_footer_layout(ai_action_layout)

        right_layout.addStretch()
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

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
        self.editor.token_edit.clear()
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
        self.editor.resist_edit.clear()
        self.editor.vuln_edit.clear()
        self.editor.immune_edit.clear()
        # Clear actions table
        self.editor.actions_table.setRowCount(0)

    def load_character(self, item):
        idx = self.list_widget.row(item)
        char = self.characters[idx]
        self.selected_index = idx
        self.editor.name_edit.setText(char.get("Name", ""))
        self.editor.token_edit.setText(char.get("TokenImage", ""))
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
        self.editor.resist_edit.setText(char.get("Resistances", ""))
        self.editor.vuln_edit.setText(char.get("Vulnerabilities", ""))
        self.editor.immune_edit.setText(char.get("Immunities", ""))
        actions = char.get("Actions", [])
        self.editor.actions_table.setRowCount(0)
        for action in actions:
            row = self.editor.actions_table.rowCount()
            self.editor.actions_table.insertRow(row)
            for col, key in enumerate(["name", "type", "attack_bonus", "damage", "damage_type", "description"]):
                self.editor.actions_table.setItem(row, col, QTableWidgetItem(str(action.get(key, ""))))

    def save_character(self):
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
            msg = f"Please fill in all mandatory fields: {', '.join(missing)}"
            GlobalLogWidget.instance().log(msg, error=True)
            QMessageBox.warning(self, "Missing Fields", msg)
            return
        # Collect actions from table
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
        char_data = {
            "Name": self.editor.name_edit.text().strip(),
            "TokenImage": self.editor.token_edit.text().strip(),
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
            "Resistances": self.editor.resist_edit.text().strip(),
            "Vulnerabilities": self.editor.vuln_edit.text().strip(),
            "Immunities": self.editor.immune_edit.text().strip(),
            "Actions": actions,
        }
        folder = self.main_window.campaign_folder
        if not folder:
            msg = "Please create or load a campaign first."
            GlobalLogWidget.instance().log(msg, error=True)
            QMessageBox.warning(self, "No Campaign", msg)
            return
        # Override character with same name if exists
        json_path = os.path.join(folder, "characters.json")
        chars = []
        if os.path.exists(json_path):
            with open(json_path, "r") as f:
                chars = json.load(f)
            # Remove any character with the same name
            chars = [c for c in chars if c.get("Name", "") != char_data["Name"]]
        chars.append(char_data)
        with open(json_path, "w") as f:
            json.dump(chars, f, indent=2)
        QMessageBox.information(self, "Saved", "Character saved.")
        self.refresh_list()

    def generate_with_ai(self):
        desc = self.ai_desc_edit.text().strip()
        prompt = (
            "You are an expert D&D 5e character generator. "
            "Generate a character as a JSON object with fields: "
            "Name, Race, Class, Level, Alignment, HP, AC, STR, DEX, CON, INT, WIS, CHA, Actions (list of dicts with name, type, attack_bonus, damage, damage_type, description). "
            f"Description: {desc}\n"
            "Output only the JSON object."
        )
        try:
            response = openai.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            char = json.loads(content)
            # Fill editor fields
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
            self.editor.actions_table.setRowCount(0)
            for action in actions:
                row = self.editor.actions_table.rowCount()
                self.editor.actions_table.insertRow(row)
                for col, key in enumerate(["name", "type", "attack_bonus", "damage", "damage_type", "description"]):
                    self.editor.actions_table.setItem(row, col, QTableWidgetItem(str(action.get(key, ""))))
            QMessageBox.information(self, "AI Generated", "Character generated and fields populated.")
        except Exception as e:
            QMessageBox.critical(self, "AI Error", f"Failed to generate character with AI:\n{e}")

    def delete_character(self):
        selected = self.list_widget.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Delete Character", "No character selected.")
            return
        char = self.characters[selected]
        name = char.get("Name", "Unnamed")
        reply = QMessageBox.question(
            self, "Delete Character",
            f"Are you sure you want to delete '{name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            # Remove from characters.json
            folder = self.main_window.campaign_folder
            if folder:
                json_path = os.path.join(folder, "characters.json")
                if os.path.exists(json_path):
                    with open(json_path, "r") as f:
                        chars = json.load(f)
                    # Remove first entry with matching name
                    for i, c in enumerate(chars):
                        if c.get("Name", "") == name:
                            del chars[i]
                            break
                    with open(json_path, "w") as f:
                        json.dump(chars, f, indent=2)
            # Remove from UI
            self.refresh_list()
            self.editor.name_edit.clear()
            self.editor.token_edit.clear()
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
            self.editor.resist_edit.clear()
            self.editor.vuln_edit.clear()
            self.editor.immune_edit.clear()
            self.editor.actions_table.setRowCount(0)
