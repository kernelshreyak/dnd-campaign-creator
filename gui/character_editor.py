import random
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QMessageBox, QTextEdit, QHBoxLayout
)

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
        layout.addLayout(self.form)

        # Roll stats button
        roll_layout = QHBoxLayout()
        self.roll_btn = QPushButton("Roll Stats (4d6 drop lowest)")
        self.roll_btn.clicked.connect(self.roll_stats)
        roll_layout.addWidget(self.roll_btn)
        layout.addLayout(roll_layout)

        # Actions section
        layout.addWidget(QLabel("Actions (one per line, or use ; to separate name and description):"))
        self.actions_edit = QTextEdit()
        layout.addWidget(self.actions_edit)

        # Save button
        self.save_btn = QPushButton("Save Character")
        self.save_btn.clicked.connect(self.save_character)
        layout.addWidget(self.save_btn)

        self.setLayout(layout)

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
        # Actions can be empty, but we collect them
        actions = []
        for line in self.actions_edit.toPlainText().splitlines():
            if ";" in line:
                name, desc = line.split(";", 1)
                actions.append({"name": name.strip(), "desc": desc.strip()})
            elif line.strip():
                actions.append({"name": line.strip(), "desc": ""})
        # Placeholder: Save logic would go here
        QMessageBox.information(self, "Saved", "Character saved (placeholder).")