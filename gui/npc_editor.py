from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QFormLayout,
    QPushButton,
    QMessageBox,
    QComboBox,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QSplitter,
    QScrollArea,
    QSizePolicy,
)
from PyQt5.QtCore import Qt
import os
import openai
import json

class ActionDialog(QDialog):
    def __init__(self, action=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Action" if action else "Add Action")
        layout = QGridLayout()
        self.name_edit = QLineEdit()
        self.type_edit = QLineEdit()
        self.attack_bonus_edit = QLineEdit()
        self.damage_edit = QLineEdit()
        self.damage_type_edit = QLineEdit()
        self.desc_edit = QTextEdit()
        layout.addWidget(QLabel("Name:"), 0, 0)
        layout.addWidget(self.name_edit, 0, 1)
        layout.addWidget(QLabel("Type:"), 1, 0)
        layout.addWidget(self.type_edit, 1, 1)
        layout.addWidget(QLabel("Attack Bonus:"), 2, 0)
        layout.addWidget(self.attack_bonus_edit, 2, 1)
        layout.addWidget(QLabel("Damage:"), 3, 0)
        layout.addWidget(self.damage_edit, 3, 1)
        layout.addWidget(QLabel("Damage Type:"), 4, 0)
        layout.addWidget(self.damage_type_edit, 4, 1)
        layout.addWidget(QLabel("Description:"), 5, 0)
        layout.addWidget(self.desc_edit, 5, 1)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons, 6, 0, 1, 2)
        self.setLayout(layout)
        if action:
            self.name_edit.setText(action.get("name", ""))
            self.type_edit.setText(action.get("type", ""))
            self.attack_bonus_edit.setText(str(action.get("attack_bonus", "")))
            self.damage_edit.setText(str(action.get("damage", "")))
            self.damage_type_edit.setText(action.get("damage_type", ""))
            self.desc_edit.setPlainText(action.get("description", ""))

    def get_action(self):
        return {
            "name": self.name_edit.text().strip(),
            "type": self.type_edit.text().strip(),
            "attack_bonus": self.attack_bonus_edit.text().strip(),
            "damage": self.damage_edit.text().strip(),
            "damage_type": self.damage_type_edit.text().strip(),
            "description": self.desc_edit.toPlainText().strip(),
        }

class NPCEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # OpenAI API key input (optional, fallback to env var)
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("OpenAI API Key (or set OPENAI_API_KEY env var)")
        layout.addWidget(self.api_key_edit)
        
        # Stat block input (with max height)
        layout.addWidget(QLabel("Paste NPC/Monster Stat Block:"))
        self.stat_block_edit = QTextEdit()
        self.stat_block_edit.setMaximumHeight(120)
        layout.addWidget(self.stat_block_edit)
        
        # --- Main vertical splitter for form and actions ---
        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.setChildrenCollapsible(False)

        # --- Form area in a scroll area ---
        form_scroll = QScrollArea()
        form_scroll.setWidgetResizable(True)

        form_container = QWidget()
        form_container_layout = QVBoxLayout(form_container)
        form_container_layout.setContentsMargins(12, 12, 12, 12)
        form_container_layout.setSpacing(10)

        self.form = QFormLayout()
        self.form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        self.form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.form.setFormAlignment(Qt.AlignTop | Qt.AlignLeft)

        # NPC fields
        self.name_edit = QLineEdit()
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Hostile", "Friendly", "Neutral"])
        self.role_edit = QLineEdit()
        self.ac_edit = QLineEdit()
        self.hp_edit = QLineEdit()
        self.initiative_edit = QLineEdit()
        self.speed_edit = QLineEdit()
        self.str_edit = QLineEdit()
        self.dex_edit = QLineEdit()
        self.con_edit = QLineEdit()
        self.int_edit = QLineEdit()
        self.wis_edit = QLineEdit()
        self.cha_edit = QLineEdit()
        self.skills_edit = QLineEdit()
        self.gear_edit = QLineEdit()
        self.senses_edit = QLineEdit()
        self.languages_edit = QLineEdit()
        self.cr_edit = QLineEdit()
        self.habitat_edit = QLineEdit()
        self.desc_edit = QTextEdit()
        self.resist_edit = QLineEdit()
        self.vuln_edit = QLineEdit()
        self.immune_edit = QLineEdit()

        self.form.addRow("Name:", self.name_edit)
        self.form.addRow("Type:", self.type_combo)
        self.form.addRow("Role/Title:", self.role_edit)
        self.form.addRow("AC:", self.ac_edit)
        self.form.addRow("HP:", self.hp_edit)
        self.form.addRow("Initiative:", self.initiative_edit)
        self.form.addRow("Speed:", self.speed_edit)
        self.form.addRow("STR:", self.str_edit)
        self.form.addRow("DEX:", self.dex_edit)
        self.form.addRow("CON:", self.con_edit)
        self.form.addRow("INT:", self.int_edit)
        self.form.addRow("WIS:", self.wis_edit)
        self.form.addRow("CHA:", self.cha_edit)
        self.form.addRow("Skills:", self.skills_edit)
        self.form.addRow("Gear:", self.gear_edit)
        self.form.addRow("Senses:", self.senses_edit)
        self.form.addRow("Languages:", self.languages_edit)
        self.form.addRow("CR:", self.cr_edit)
        self.form.addRow("Habitat:", self.habitat_edit)
        self.form.addRow("Description:", self.desc_edit)
        self.form.addRow("Resistances:", self.resist_edit)
        self.form.addRow("Vulnerabilities:", self.vuln_edit)
        self.form.addRow("Immunities:", self.immune_edit)

        form_container_layout.addLayout(self.form)
        form_container_layout.addStretch()

        form_scroll.setWidget(form_container)
        self.splitter.addWidget(form_scroll)

        # --- Actions area (table + buttons) ---
        self.actions_table = QTableWidget(0, 6)
        self.actions_table.setHorizontalHeaderLabels(["Name", "Type", "Attack Bonus", "Damage", "Damage Type", "Description"])
        self.actions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        self.add_action_btn = QPushButton("Add Action")
        self.edit_action_btn = QPushButton("Edit Action")
        self.remove_action_btn = QPushButton("Remove Action")
        self.save_btn = QPushButton("Save NPC")
        self.save_btn.clicked.connect(self.save_npc)
        
        actions_widget = QWidget()
        actions_layout = QVBoxLayout(actions_widget)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.addWidget(QLabel("Actions:"))
        actions_layout.addWidget(self.actions_table)
        actions_btn_layout = QHBoxLayout()
        actions_btn_layout.addWidget(self.add_action_btn)
        actions_btn_layout.addWidget(self.edit_action_btn)
        actions_btn_layout.addWidget(self.remove_action_btn)
        actions_layout.addLayout(actions_btn_layout)
        actions_layout.addWidget(self.save_btn)
        actions_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.splitter.addWidget(actions_widget)
        
        self.splitter.setStretchFactor(0, 2)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes([400, 200])  # Initial split
        
        layout.addWidget(self.splitter)

        self.parse_btn = QPushButton("Parse Stat Block (AI)")
        self.parse_btn.clicked.connect(self.parse_stat_block)
        layout.addWidget(self.parse_btn)

        self.add_action_btn.clicked.connect(self.add_action)
        self.edit_action_btn.clicked.connect(self.edit_action)
        self.remove_action_btn.clicked.connect(self.remove_action)

    def set_actions(self, actions):
        """Set the actions table from a list of action dicts."""
        self.actions_table.setRowCount(0)
        for action in actions:
            row = self.actions_table.rowCount()
            self.actions_table.insertRow(row)
            for col, key in enumerate(["name", "type", "attack_bonus", "damage", "damage_type", "description"]):
                self.actions_table.setItem(row, col, QTableWidgetItem(str(action.get(key, ""))))

    def clear_actions(self):
        self.actions_table.setRowCount(0)

    def add_action(self):
        dialog = ActionDialog(parent=self)
        if dialog.exec_():
            action = dialog.get_action()
            row = self.actions_table.rowCount()
            self.actions_table.insertRow(row)
            for col, key in enumerate(["name", "type", "attack_bonus", "damage", "damage_type", "description"]):
                self.actions_table.setItem(row, col, QTableWidgetItem(action[key]))

    def edit_action(self):
        row = self.actions_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Select an action to edit.")
            return
        action = {key: self.actions_table.item(row, col).text() if self.actions_table.item(row, col) else "" for col, key in enumerate(["name", "type", "attack_bonus", "damage", "damage_type", "description"])}
        dialog = ActionDialog(action, parent=self)
        if dialog.exec_():
            action = dialog.get_action()
            for col, key in enumerate(["name", "type", "attack_bonus", "damage", "damage_type", "description"]):
                self.actions_table.setItem(row, col, QTableWidgetItem(action[key]))

    def remove_action(self):
        row = self.actions_table.currentRow()
        if row >= 0:
            self.actions_table.removeRow(row)

    def parse_stat_block(self):
        text = self.stat_block_edit.toPlainText()
        api_key = self.api_key_edit.text().strip() or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            QMessageBox.warning(self, "API Key Required", "Please enter your OpenAI API key or set the OPENAI_API_KEY environment variable.")
            return

        prompt = (
            "You are an expert D&D 5e NPC stat block parser. "
            "Read the provided stat block and populate every field in the response schema. "
            "Fill missing information with reasonable defaults based on the stat block context. "
            "List ALL actions, including specials such as reactions, bonus actions, and legendary actions. "
            "For legendary actions, set the action type to \"legendary\" and include recharge notes in the description. "
            "Parse resistances, vulnerabilities, and immunities exactly as written when they appear; leave them empty strings if truly absent. "
            "Preserve quantities (e.g., HP numbers, save DCs, damage dice) as strings. "
            "Use concise text without markdown. "
            "Stat block follows:\n"
            f"{text}"
        )

        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "npc_stat_block",
                "schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "Name": {"type": "string"},
                        "Type": {"type": "string"},
                        "Role/Title": {"type": "string"},
                        "AC": {"type": "string"},
                        "HP": {"type": "string"},
                        "Initiative": {"type": "string"},
                        "Speed": {"type": "string"},
                        "STR": {"type": "string"},
                        "DEX": {"type": "string"},
                        "CON": {"type": "string"},
                        "INT": {"type": "string"},
                        "WIS": {"type": "string"},
                        "CHA": {"type": "string"},
                        "Skills": {"type": "string"},
                        "Gear": {"type": "string"},
                        "Senses": {"type": "string"},
                        "Languages": {"type": "string"},
                        "CR": {"type": "string"},
                        "Habitat": {"type": "string"},
                        "Description": {"type": "string"},
                        "Resistances": {"type": "string"},
                        "Vulnerabilities": {"type": "string"},
                        "Immunities": {"type": "string"},
                        "Actions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "additionalProperties": False,
                                "properties": {
                                    "name": {"type": "string"},
                                    "type": {"type": "string"},
                                    "attack_bonus": {"type": ["string", "null"]},
                                    "damage": {"type": ["string", "null"]},
                                    "damage_type": {"type": ["string", "null"]},
                                    "description": {"type": "string"},
                                },
                                "required": ["name", "type", "attack_bonus", "damage", "damage_type", "description"],
                            },
                        },
                    },
                    "required": [
                        "Name",
                        "Type",
                        "Role/Title",
                        "AC",
                        "HP",
                        "Initiative",
                        "Speed",
                        "STR",
                        "DEX",
                        "CON",
                        "INT",
                        "WIS",
                        "CHA",
                        "Skills",
                        "Gear",
                        "Senses",
                        "Languages",
                        "CR",
                        "Habitat",
                        "Description",
                        "Resistances",
                        "Vulnerabilities",
                        "Immunities",
                        "Actions",
                    ],
                },
            },
        }

        try:
            openai.api_key = api_key
            response = openai.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1200,
                temperature=0.2,
                response_format=response_format,
            )
            content = response.choices[0].message.content
            npc_data = json.loads(content)
        except Exception as e:
            QMessageBox.critical(self, "OpenAI Error", f"Failed to parse stat block with OpenAI:\n{e}")
            return

        # Fill fields from AI response
        self.name_edit.setText(str(npc_data.get("Name", "")))
        self.role_edit.setText(str(npc_data.get("Role/Title", "")))
        self.ac_edit.setText(str(npc_data.get("AC", "")))
        self.hp_edit.setText(str(npc_data.get("HP", "")))
        self.initiative_edit.setText(str(npc_data.get("Initiative", "")))
        self.speed_edit.setText(str(npc_data.get("Speed", "")))
        self.str_edit.setText(str(npc_data.get("STR", "")))
        self.dex_edit.setText(str(npc_data.get("DEX", "")))
        self.con_edit.setText(str(npc_data.get("CON", "")))
        self.int_edit.setText(str(npc_data.get("INT", "")))
        self.wis_edit.setText(str(npc_data.get("WIS", "")))
        self.cha_edit.setText(str(npc_data.get("CHA", "")))
        self.skills_edit.setText(str(npc_data.get("Skills", "")))
        self.gear_edit.setText(str(npc_data.get("Gear", "")))
        self.senses_edit.setText(str(npc_data.get("Senses", "")))
        self.languages_edit.setText(str(npc_data.get("Languages", "")))
        self.cr_edit.setText(str(npc_data.get("CR", "")))
        self.habitat_edit.setText(str(npc_data.get("Habitat", "")))
        self.desc_edit.setPlainText(str(npc_data.get("Description", "")))
        self.resist_edit.setText(str(npc_data.get("Resistances", "")))
        self.vuln_edit.setText(str(npc_data.get("Vulnerabilities", "")))
        self.immune_edit.setText(str(npc_data.get("Immunities", "")))
        # Set type
        t = str(npc_data.get("Type", "Neutral"))
        if t in ["Hostile", "Friendly", "Neutral"]:
            self.type_combo.setCurrentText(t)
        else:
            self.type_combo.setCurrentText("Neutral")
        # Actions
        self.actions_table.setRowCount(0)
        actions = npc_data.get("Actions", [])
        for action in actions:
            row = self.actions_table.rowCount()
            self.actions_table.insertRow(row)
            for col, key in enumerate(["name", "type", "attack_bonus", "damage", "damage_type", "description"]):
                self.actions_table.setItem(row, col, QTableWidgetItem(str(action.get(key, ""))))
        QMessageBox.information(self, "Parsed", "Stat block parsed using OpenAI. Please review and complete all fields.")

    def save_npc(self):
        # Validate all fields
        mandatory = [
            (self.name_edit, "Name"),
            (self.role_edit, "Role/Title"),
            (self.ac_edit, "AC"),
            (self.hp_edit, "HP"),
            (self.initiative_edit, "Initiative"),
            (self.speed_edit, "Speed"),
            (self.str_edit, "STR"),
            (self.dex_edit, "DEX"),
            (self.con_edit, "CON"),
            (self.int_edit, "INT"),
            (self.wis_edit, "WIS"),
            (self.cha_edit, "CHA"),
            (self.skills_edit, "Skills"),
            (self.gear_edit, "Gear"),
            (self.senses_edit, "Senses"),
            (self.languages_edit, "Languages"),
            (self.cr_edit, "CR"),
            (self.habitat_edit, "Habitat"),
        ]
        missing = [label for edit, label in mandatory if not edit.text().strip()]
        if missing:
            QMessageBox.warning(self, "Missing Fields", f"Please fill in all mandatory fields: {', '.join(missing)}")
            return
        # Collect actions from table
        actions = []
        for row in range(self.actions_table.rowCount()):
            action = {
                "name": self.actions_table.item(row, 0).text() if self.actions_table.item(row, 0) else "",
                "type": self.actions_table.item(row, 1).text() if self.actions_table.item(row, 1) else "",
                "attack_bonus": self.actions_table.item(row, 2).text() if self.actions_table.item(row, 2) else "",
                "damage": self.actions_table.item(row, 3).text() if self.actions_table.item(row, 3) else "",
                "damage_type": self.actions_table.item(row, 4).text() if self.actions_table.item(row, 4) else "",
                "description": self.actions_table.item(row, 5).text() if self.actions_table.item(row, 5) else "",
            }
            actions.append(action)
        # Collect resistances, vulnerabilities, immunities
        resistances = self.resist_edit.text().strip()
        vulnerabilities = self.vuln_edit.text().strip()
        immunities = self.immune_edit.text().strip()
        # Placeholder: Save logic would go here, now includes new fields
        # Example: npc_data = {..., "Resistances": resistances, "Vulnerabilities": vulnerabilities, "Immunities": immunities, ...}
        QMessageBox.information(self, "Saved", "NPC saved (placeholder).")
