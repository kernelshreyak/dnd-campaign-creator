from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QInputDialog, QMessageBox, QDialog, QDialogButtonBox, QTextEdit, QComboBox
)
from PyQt5.QtCore import Qt
import random
import re
import json
from utils.file_io import load_entities

def roll_dice(formula):
    # Supports e.g. "2d6+3", "1d8", "3d4-1"
    match = re.match(r"(\d+)d(\d+)([+-]\d+)?", formula.replace(" ", ""))
    if not match:
        return 0, "Invalid damage formula"
    num, die, mod = int(match.group(1)), int(match.group(2)), match.group(3)
    rolls = [random.randint(1, die) for _ in range(num)]
    total = sum(rolls)
    mod_val = int(mod) if mod else 0
    result = total + mod_val
    roll_str = f"({' + '.join(str(r) for r in rolls)})"
    if mod:
        roll_str += f" {mod}"
    return result, f"{formula}: {roll_str} = {result}"

class ActionDialog(QDialog):
    def __init__(self, combatant, all_combatants, log_callback, main_window, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Actions for {combatant['Name']}")
        self.combatant = combatant
        self.all_combatants = all_combatants
        self.log_callback = log_callback
        self.main_window = main_window
        self.layout = QVBoxLayout()
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "Name", "Type", "Attack Bonus", "Damage", "Damage Type", "Description", "Execute"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table)
        self.refresh_table()

        # Add Refresh Actions button
        refresh_btn = QPushButton("Refresh Actions")
        refresh_btn.clicked.connect(self.refresh_actions_from_campaign)
        self.layout.addWidget(refresh_btn)

        self.setLayout(self.layout)
        self.resize(700, 300)

    def refresh_table(self):
        self.table.setRowCount(len(self.combatant.get("Actions", [])))
        for row, action in enumerate(self.combatant.get("Actions", [])):
            for col, key in enumerate(["name", "type", "attack_bonus", "damage", "damage_type", "description"]):
                item = QTableWidgetItem(str(action.get(key, "")))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, col, item)
            exec_btn = QPushButton("Execute")
            exec_btn.clicked.connect(lambda _, r=row: self.execute_action(r))
            self.table.setCellWidget(row, 6, exec_btn)

    def refresh_actions_from_campaign(self):
        folder = self.main_window.campaign_folder
        if not folder:
            QMessageBox.warning(self, "No Campaign", "No campaign loaded.")
            return
        name = self.combatant.get("Name", "")
        typ = self.combatant.get("Type", "")
        if typ == "Character":
            entities = load_entities("characters", folder)
        elif typ == "NPC":
            entities = load_entities("npcs", folder)
        else:
            entities = []
        found = None
        for ent in entities:
            if ent.get("Name", "") == name:
                found = ent
                break
        if found:
            self.combatant["Actions"] = [dict(a) for a in found.get("Actions", [])]
            self.refresh_table()
            if self.log_callback:
                self.log_callback(f"Actions for {name} refreshed from campaign data.")
        else:
            QMessageBox.warning(self, "Not Found", f"{typ} '{name}' not found in campaign data.")

    def add_action(self):
        # No longer used
        pass

    def execute_action(self, row):
        action = self.combatant.get("Actions", [])[row]
        # Log the action being executed
        if self.log_callback:
            self.log_callback(f"{self.combatant['Name']} prepares to use {action['name']}.")
        # Select target
        target, ok = self.select_target_dialog()
        if not ok:
            return

        # 1. Roll attack
        try:
            attack_bonus = int(action.get("attack_bonus", 0))
        except Exception:
            attack_bonus = 0
        d20 = random.randint(1, 20)
        attack_total = d20 + attack_bonus
        ac = int(target.get("AC", 10))
        attack_str = (
            f"Attack Roll: d20({d20}) + Attack Bonus({attack_bonus}) = {attack_total} vs AC {ac}"
        )
        if self.log_callback:
            self.log_callback(attack_str)

        # 2. Ask AI to determine hit/miss, effect, reaction, etc.
        try:
            import openai
            prompt = (
                "You are a D&D 5e combat AI and narrator. Given the action (as JSON), the source (as JSON), the target (as JSON), "
                "if the action is a utility action or spell, just show its effect on the target (bit dramatically depending on type of spell or action) and return success true."
                "the attack roll (d20), the attack bonus, and the target's AC (armor class), "
                "determine if the attack hits (taking into account resistances, immunities, etc.), "
                "STANDARD RULE: if the d20 roll is a natural 20, the attack always hits and is a critical hit; "
                "STANDARD RULE: if the d20 roll is a natural 1, the attack always misses. "
                "STANDARD RULE: if attack role (plus modifiers) is greater than or equal to target AC, the attack hits. "
                "and return a JSON object with fields: "
                "hit (true/false), success (true/false), effect (string), log (string for log window), "
                "reaction (short, dramatic reaction from the target's perspective, 1 sentence, 5-12 words, vivid and in-character). "
                "If the attack misses, set hit to false and success to false."
              
                "If the attack hits, set hit to true and determine if the action is successful (e.g., saving throw, etc.). "
                "Do not include damage calculation; that will be done by the system. "
                "Action JSON:\n" + json.dumps(action, indent=2) +
                f"\nSource JSON:\n{json.dumps(self.combatant, indent=2)}" +
                f"\nTarget JSON:\n{json.dumps(target, indent=2)}" +
                f"\nAttack Roll: {d20}\nAttack Bonus: {attack_bonus}\nTarget AC: {ac}\n"
                "Output only the JSON object."
            )
            response = openai.chat.completions.create(
                model="gpt-4.1-nano",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=340,
                temperature=0.8,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            ai_result = json.loads(content)
            # 3. If hit and success, roll damage
            damage_log = ""
            if ai_result.get("hit", False) and ai_result.get("success", False):
                dmg_formula = action.get("damage", "")
                if dmg_formula:
                    dmg, dmg_str = roll_dice(dmg_formula)
                    damage_log = f"Damage Roll: {dmg_str}"
                    # Optionally, apply damage to target here if desired
            # 4. Log everything
            log_msg = (
                f"{self.combatant['Name']} uses {action['name']} on {target['Name']}: "
                f"{ai_result.get('log', ai_result.get('effect', ''))} "
                f"({target['Name']}: {ai_result.get('reaction', '').strip()})"
            )
            if self.log_callback:
                self.log_callback(log_msg)
                if damage_log:
                    self.log_callback(damage_log)
        except Exception as e:
            err_msg = f"AI error: {e}"
            if self.log_callback:
                self.log_callback(err_msg)

    def select_target_dialog(self):
        # Show a dialog to select a target from all combatants except self
        targets = [c for c in self.all_combatants if c is not self.combatant]
        if not targets:
            QMessageBox.warning(self, "No Target", "No other combatants to target.")
            return None, False
        dlg = QDialog(self)
        dlg.setWindowTitle("Select Target")
        layout = QVBoxLayout()
        combo = QComboBox()
        for t in targets:
            combo.addItem(t["Name"])
        layout.addWidget(QLabel("Select target:"))
        layout.addWidget(combo)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(btns)
        dlg.setLayout(layout)
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        if dlg.exec_() == QDialog.Accepted:
            idx = combo.currentIndex()
            return targets[idx], True
        return None, False

    def accept(self):
        # No editing of actions in combat, so nothing to save
        super().accept()

class CombatTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.combatants = []  # In-memory list of combatants

        main_layout = QHBoxLayout()

        # Log window (left half) - now QTextEdit with word wrap
        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        self.log_widget.setLineWrapMode(QTextEdit.WidgetWidth)
        main_layout.addWidget(self.log_widget, stretch=1)

        right_layout = QVBoxLayout()

        # Add buttons for adding combatants and rolling initiative
        add_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Combatant")
        self.add_btn.clicked.connect(self.add_combatant)
        add_layout.addWidget(self.add_btn)

        self.roll_initiative_btn = QPushButton("Roll Initiative")
        self.roll_initiative_btn.clicked.connect(self.roll_initiative)
        add_layout.addWidget(self.roll_initiative_btn)

        add_layout.addStretch(1)
        right_layout.addLayout(add_layout)

        # Table for combatants (now with Initiative, Actions, Deal Damage, Remove columns)
        self.table = QTableWidget(0, 15)
        self.table.setHorizontalHeaderLabels([
            "Name", "Type", "HP", "AC", "STR", "DEX", "CON", "INT", "WIS", "CHA", "Initiative", "Actions", "Deal Damage", "Remove", ""
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        right_layout.addWidget(self.table)

        main_layout.addLayout(right_layout, stretch=2)
        self.setLayout(main_layout)

    def add_combatant(self):
        folder = self.main_window.campaign_folder
        if not folder:
            QMessageBox.warning(self, "No Campaign", "Please create or load a campaign first.")
            return
        chars = load_entities("characters", folder)
        npcs = load_entities("npcs", folder)
        options = [("Character", c) for c in chars] + [("NPC", n) for n in npcs]
        if not options:
            QMessageBox.warning(self, "No Entities", "No characters or NPCs available in this campaign.")
            return
        dlg = QDialog(self)
        dlg.setWindowTitle("Select Combatant")
        layout = QVBoxLayout()
        combo = QComboBox()
        for typ, ent in options:
            combo.addItem(f"{typ}: {ent.get('Name', 'Unnamed')}")
        layout.addWidget(QLabel("Select a character or NPC to add to combat:"))
        layout.addWidget(combo)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(btns)
        dlg.setLayout(layout)
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        if dlg.exec_() == QDialog.Accepted:
            idx = combo.currentIndex()
            typ, ent = options[idx]
            # Copy entity data for combatant (deep copy, but only relevant fields)
            combatant = {
                "Name": ent.get("Name", ""),
                "Type": typ,
                "HP": int(ent.get("HP", 10)),
                "AC": int(ent.get("AC", 10)),
                "STR": int(ent.get("STR", 10)),
                "DEX": int(ent.get("DEX", 10)),
                "CON": int(ent.get("CON", 10)),
                "INT": int(ent.get("INT", 10)),
                "WIS": int(ent.get("WIS", 10)),
                "CHA": int(ent.get("CHA", 10)),
                "Initiative": 0,
                "Actions": [dict(a) for a in ent.get("Actions", [])]
            }
            self.combatants.append(combatant)
            self.refresh_table()

    def refresh_table(self):
        self.table.setRowCount(len(self.combatants))
        for row, c in enumerate(self.combatants):
            for col, key in enumerate(["Name", "Type", "HP", "AC", "STR", "DEX", "CON", "INT", "WIS", "CHA", "Initiative"]):
                item = QTableWidgetItem(str(c.get(key, "")))
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.table.setItem(row, col, item)
            # Actions button
            actions_btn = QPushButton("Actions")
            actions_btn.clicked.connect(lambda _, r=row: self.open_actions_dialog(r))
            self.table.setCellWidget(row, 11, actions_btn)
            # Deal Damage button
            dmg_btn = QPushButton("Deal Damage")
            dmg_btn.clicked.connect(lambda _, r=row: self.deal_damage_dialog(r))
            self.table.setCellWidget(row, 12, dmg_btn)
            # Remove button (enabled only if HP == 0)
            btn = QPushButton("Remove")
            btn.setEnabled(int(c.get("HP", 0)) == 0)
            btn.clicked.connect(lambda _, r=row: self.remove_combatant(r))
            self.table.setCellWidget(row, 13, btn)

    def open_actions_dialog(self, row):
        dlg = ActionDialog(self.combatants[row], self.combatants, self.log_message, self.main_window, self)
        if dlg.exec_():
            self.refresh_table()

    def deal_damage_dialog(self, row):
        c = self.combatants[row]
        dmg, ok = QInputDialog.getInt(self, "Deal Damage", f"How much damage to {c['Name']}?", 0, 0, 999)
        if ok and dmg > 0:
            c["HP"] = max(0, int(c.get("HP", 0)) - dmg)
            self.log_message(f"{c['Name']} takes {dmg} damage. HP is now {c['HP']}.")
            self.refresh_table()

    def log_message(self, msg):
        self.log_widget.append(msg)
        self.log_widget.moveCursor(self.log_widget.textCursor().End)

    def remove_combatant(self, row):
        if row < 0 or row >= len(self.combatants):
            return
        combatant = self.combatants[row]
        if int(combatant.get("HP", 0)) != 0:
            QMessageBox.warning(self, "Cannot Remove", "Combatant can only be removed if HP is 0.")
            return
        name = combatant.get("Name", "Unknown")
        del self.combatants[row]
        self.log_message(f"{name} has been removed from combat.")
        self.refresh_table()

    def roll_initiative(self):
        for c in self.combatants:
            c["Initiative"] = random.randint(1, 20)
        # Sort by initiative descending
        self.combatants.sort(key=lambda x: int(x.get("Initiative", 0)), reverse=True)
        self.refresh_table()