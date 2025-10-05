from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QFormLayout, QPushButton, QMessageBox, QComboBox, QHBoxLayout
)
import re

class NPCEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()

        # Stat block input
        layout.addWidget(QLabel("Paste NPC/Monster Stat Block:"))
        self.stat_block_edit = QTextEdit()
        layout.addWidget(self.stat_block_edit)

        self.parse_btn = QPushButton("Parse Stat Block")
        self.parse_btn.clicked.connect(self.parse_stat_block)
        layout.addWidget(self.parse_btn)

        # NPC fields
        self.form = QFormLayout()
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
        layout.addLayout(self.form)

        # Actions section
        layout.addWidget(QLabel("Actions (one per line, or use ; to separate name and description):"))
        self.actions_edit = QTextEdit()
        layout.addWidget(self.actions_edit)

        # Save button
        self.save_btn = QPushButton("Save NPC")
        self.save_btn.clicked.connect(self.save_npc)
        layout.addWidget(self.save_btn)

        self.setLayout(layout)

    def parse_stat_block(self):
        text = self.stat_block_edit.toPlainText()
        # Placeholder AI parsing logic (regexes for demo, not robust)
        self.name_edit.setText("Parsed NPC")
        self.role_edit.setText("")
        self.ac_edit.setText(self._find_regex(r"AC (\d+)", text))
        self.hp_edit.setText(self._find_regex(r"HP (\d+)", text))
        self.initiative_edit.setText(self._find_regex(r"Initiative ([+\-\d]+)", text))
        self.speed_edit.setText(self._find_regex(r"Speed ([\d ]+ft\.)", text))
        self.str_edit.setText(self._find_stat("Str", text))
        self.dex_edit.setText(self._find_stat("Dex", text))
        self.con_edit.setText(self._find_stat("Con", text))
        self.int_edit.setText(self._find_stat("Int", text))
        self.wis_edit.setText(self._find_stat("Wis", text))
        self.cha_edit.setText(self._find_stat("Cha", text))
        self.skills_edit.setText(self._find_regex(r"Skills ([^\n]+)", text))
        self.gear_edit.setText(self._find_regex(r"Gear ([^\n]+)", text))
        self.senses_edit.setText(self._find_regex(r"Senses ([^\n]+)", text))
        self.languages_edit.setText(self._find_regex(r"Languages ([^\n]+)", text))
        self.cr_edit.setText(self._find_regex(r"CR ([^\n]+)", text))
        self.habitat_edit.setText(self._find_regex(r"Habitat: ([^\n]+)", text))
        self.desc_edit.setPlainText("")
        # Actions
        actions = self._extract_actions(text)
        self.actions_edit.setPlainText("\n".join([f"{a['name']}; {a['desc']}" for a in actions]))
        # Set type based on stat block (very basic)
        if "hostile" in text.lower():
            self.type_combo.setCurrentText("Hostile")
        elif "friendly" in text.lower():
            self.type_combo.setCurrentText("Friendly")
        else:
            self.type_combo.setCurrentText("Neutral")
        QMessageBox.information(self, "Parsed", "Stat block parsed (basic demo). Please review and complete all fields.")

    def _find_regex(self, pattern, text):
        m = re.search(pattern, text, re.IGNORECASE)
        return m.group(1).strip() if m else ""

    def _find_stat(self, stat, text):
        # Looks for stat name followed by value, e.g. "Str\n16"
        m = re.search(rf"{stat}\s*\n\s*(\d+)", text, re.IGNORECASE)
        return m.group(1).strip() if m else ""

    def _extract_actions(self, text):
        # Extracts actions section (very basic, demo only)
        actions = []
        if "Actions" in text:
            actions_text = text.split("Actions", 1)[1]
            for line in actions_text.splitlines():
                if "." in line:
                    name, desc = line.split(".", 1)
                    actions.append({"name": name.strip(), "desc": desc.strip()})
        return actions

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
        # Actions can be empty, but we collect them
        actions = []
        for line in self.actions_edit.toPlainText().splitlines():
            if ";" in line:
                name, desc = line.split(";", 1)
                actions.append({"name": name.strip(), "desc": desc.strip()})
            elif line.strip():
                actions.append({"name": line.strip(), "desc": ""})
        # Placeholder: Save logic would go here
        QMessageBox.information(self, "Saved", "NPC saved (placeholder).")