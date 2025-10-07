import random
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QMessageBox, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QDialogButtonBox, QGridLayout, QTextEdit
)

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

class CharacterEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()

        # Character fields (main fields as per Fantasy Grounds)
        self.form = QFormLayout()
        self.name_edit = QLineEdit()
        self.race_edit = QLineEdit()
        self.class_edit = QLineEdit()
        self.level_edit = QLineEdit()
        self.alignment_edit = QLineEdit()
        self.hp_edit = QLineEdit()
        self.ac_edit = QLineEdit()
        # Individual stat fields
        self.str_edit = QLineEdit()
        self.dex_edit = QLineEdit()
        self.con_edit = QLineEdit()
        self.int_edit = QLineEdit()
        self.wis_edit = QLineEdit()
        self.cha_edit = QLineEdit()
        self.form.addRow("Name:", self.name_edit)
        self.form.addRow("Race:", self.race_edit)
        self.form.addRow("Class:", self.class_edit)
        self.form.addRow("Level:", self.level_edit)
        self.form.addRow("Alignment:", self.alignment_edit)
        self.form.addRow("HP:", self.hp_edit)
        self.form.addRow("AC:", self.ac_edit)
        self.form.addRow("STR:", self.str_edit)
        self.form.addRow("DEX:", self.dex_edit)
        self.form.addRow("CON:", self.con_edit)
        self.form.addRow("INT:", self.int_edit)
        self.form.addRow("WIS:", self.wis_edit)
        self.form.addRow("CHA:", self.cha_edit)
        # Add Resistances, Vulnerabilities, Immunities
        self.resist_edit = QLineEdit()
        self.vuln_edit = QLineEdit()
        self.immune_edit = QLineEdit()
        self.form.addRow("Resistances:", self.resist_edit)
        self.form.addRow("Vulnerabilities:", self.vuln_edit)
        self.form.addRow("Immunities:", self.immune_edit)
        layout.addLayout(self.form)

        # Roll stats button
        roll_layout = QHBoxLayout()
        self.roll_btn = QPushButton("Roll Stats (4d6 drop lowest)")
        self.roll_btn.clicked.connect(self.roll_stats)
        roll_layout.addWidget(self.roll_btn)
        layout.addLayout(roll_layout)

        # Actions section as table
        layout.addWidget(QLabel("Actions:"))
        self.actions_table = QTableWidget(0, 6)
        self.actions_table.setHorizontalHeaderLabels(["Name", "Type", "Attack Bonus", "Damage", "Damage Type", "Description"])
        self.actions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.actions_table)

        actions_btn_layout = QHBoxLayout()
        self.add_action_btn = QPushButton("Add Action")
        self.edit_action_btn = QPushButton("Edit Action")
        self.remove_action_btn = QPushButton("Remove Action")
        actions_btn_layout.addWidget(self.add_action_btn)
        actions_btn_layout.addWidget(self.edit_action_btn)
        actions_btn_layout.addWidget(self.remove_action_btn)
        layout.addLayout(actions_btn_layout)

        self.add_action_btn.clicked.connect(self.add_action)
        self.edit_action_btn.clicked.connect(self.edit_action)
        self.remove_action_btn.clicked.connect(self.remove_action)

        # Save button
        self.save_btn = QPushButton("Save Character")
        self.save_btn.clicked.connect(self.save_character)
        layout.addWidget(self.save_btn)

        self.setLayout(layout)

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

    def roll_stats(self):
        stats = [self.roll_4d6_drop_lowest() for _ in range(6)]
        self.str_edit.setText(str(stats[0]))
        self.dex_edit.setText(str(stats[1]))
        self.con_edit.setText(str(stats[2]))
        self.int_edit.setText(str(stats[3]))
        self.wis_edit.setText(str(stats[4]))
        self.cha_edit.setText(str(stats[5]))

    def roll_4d6_drop_lowest(self):
        rolls = sorted([random.randint(1, 6) for _ in range(4)])
        return sum(rolls[1:])

    def save_character(self):
        # Validate mandatory fields
        mandatory = [
            (self.name_edit, "Name"),
            (self.race_edit, "Race"),
            (self.class_edit, "Class"),
            (self.level_edit, "Level"),
            (self.alignment_edit, "Alignment"),
            (self.hp_edit, "HP"),
            (self.ac_edit, "AC"),
            (self.str_edit, "STR"),
            (self.dex_edit, "DEX"),
            (self.con_edit, "CON"),
            (self.int_edit, "INT"),
            (self.wis_edit, "WIS"),
            (self.cha_edit, "CHA"),
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
        # Example: character_data = {..., "Resistances": resistances, "Vulnerabilities": vulnerabilities, "Immunities": immunities, ...}
        QMessageBox.information(self, "Saved", "Character saved (placeholder).")