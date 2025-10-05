from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QInputDialog,
    QMessageBox,
    QDialog,
    QDialogButtonBox,
    QTextEdit,
    QComboBox,
)
from PyQt5.QtCore import Qt
import random
import re
import json
from utils.file_io import load_entities


# ---------- Helper functions ----------
def roll_dice(formula):
    """Basic dice roller for non-damage rolls like 1d20+5"""
    match = re.match(r"(\d+)d(\d+)([+-]\d+)?", formula.replace(" ", ""))
    if not match:
        return 0, "Invalid dice formula"
    num, die, mod = int(match.group(1)), int(match.group(2)), match.group(3)
    rolls = [random.randint(1, die) for _ in range(num)]
    total = sum(rolls)
    mod_val = int(mod) if mod else 0
    result = total + mod_val
    roll_str = f"({' + '.join(str(r) for r in rolls)})"
    if mod:
        roll_str += f" {mod}"
    return result, f"{formula}: {roll_str} = {result}"


def parse_tags(val):
    """Normalize resistance/immunity/vulnerability strings."""
    if not val:
        return set()
    if isinstance(val, (list, tuple, set)):
        items = val
    else:
        items = re.split(r"(?:,|/|;|\band\b|\bor\b)", str(val), flags=re.I)
    return {s.strip().lower() for s in items if s and s.strip()}


def roll_damage(formula, crit=False):
    """Roll damage with crit (doubles dice only)."""
    m = re.match(r"\s*(\d+)d(\d+)\s*([+-]\s*\d+)?\s*$", str(formula))
    if not m:
        return 0, f"Invalid damage formula '{formula}'"
    num, die = int(m.group(1)), int(m.group(2))
    mod = int(m.group(3).replace(" ", "")) if m.group(3) else 0
    num_eff = num * 2 if crit else num
    rolls = [random.randint(1, die) for _ in range(num_eff)]
    total = sum(rolls) + mod
    parts = " + ".join(str(r) for r in rolls)
    if mod:
        parts += f" {'+' if mod >= 0 else ''}{mod}"
    return max(
        0, total
    ), f"{num_eff}d{die}{('+' + str(mod)) if mod else ''}: ({parts}) = {total}"


def apply_resist_vuln_immune(base_damage, damage_type, target):
    """Adjust damage for resistances, vulnerabilities, immunities."""
    dtype = (damage_type or "").strip().lower()
    res = parse_tags(target.get("Resistances", ""))
    vul = parse_tags(target.get("Vulnerabilities", ""))
    imm = parse_tags(target.get("Immunities", ""))
    if dtype and dtype in imm:
        return 0, "immune"
    adjusted = base_damage
    note = None
    if dtype and dtype in res:
        adjusted = base_damage // 2
        note = "resistance"
    if dtype and dtype in vul:
        adjusted = adjusted * 2
        note = "vulnerability" if note is None else note + "+vulnerability"
    return adjusted, note


# ---------- ActionDialog ----------
class ActionDialog(QDialog):
    def __init__(
        self, combatant, all_combatants, log_callback, main_window, parent=None
    ):
        super().__init__(parent)
        self.setWindowTitle(f"Actions for {combatant['Name']}")
        self.combatant = combatant
        self.all_combatants = all_combatants
        self.log_callback = log_callback
        self.main_window = main_window

        self.layout = QVBoxLayout()
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(
            [
                "Name",
                "Type",
                "Attack Bonus",
                "Damage",
                "Damage Type",
                "Description",
                "Execute",
            ]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table)
        self.refresh_table()

        refresh_btn = QPushButton("Refresh Actions")
        refresh_btn.clicked.connect(self.refresh_actions_from_campaign)
        self.layout.addWidget(refresh_btn)

        self.setLayout(self.layout)
        self.resize(700, 300)

    def refresh_table(self):
        self.table.setRowCount(len(self.combatant.get("Actions", [])))
        for row, action in enumerate(self.combatant.get("Actions", [])):
            for col, key in enumerate(
                ["name", "type", "attack_bonus", "damage", "damage_type", "description"]
            ):
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
        entities = []
        if typ == "Character":
            entities = load_entities("characters", folder)
        elif typ == "NPC":
            entities = load_entities("npcs", folder)
        found = next((e for e in entities if e.get("Name", "") == name), None)
        if found:
            self.combatant["Actions"] = [dict(a) for a in found.get("Actions", [])]
            self.refresh_table()
            if self.log_callback:
                self.log_callback(f"Actions for {name} refreshed from campaign data.")
        else:
            QMessageBox.warning(
                self, "Not Found", f"{typ} '{name}' not found in campaign data."
            )

    def select_target_dialog(self):
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

    def execute_action(self, row):
        action = self.combatant.get("Actions", [])[row]
        if self.log_callback:
            self.log_callback(
                f"{self.combatant['Name']} prepares to use {action.get('name', 'Unknown Action')}."
            )

        target, ok = self.select_target_dialog()
        if not ok:
            return

        # Roll attack
        try:
            attack_bonus = int(action.get("attack_bonus", 0))
        except Exception:
            attack_bonus = 0

        d20 = random.randint(1, 20)
        ac = int(target.get("AC", 10))
        total = d20 + attack_bonus
        crit = d20 == 20
        hit = d20 != 1 and (crit or total >= ac)

        self.log_callback(
            f"Attack Roll: d20({d20}) + Attack Bonus({attack_bonus}) = {total} vs AC {ac}"
        )

        if not hit:
            self.log_callback(
                f"{self.combatant['Name']}'s attack misses {target['Name']}."
            )
            return

        # Roll and apply damage
        dmg_formula = action.get("damage", "")
        dmg_type = action.get("damage_type", "")
        dmg, dmg_str = roll_damage(dmg_formula, crit=crit)
        adj_dmg, note = apply_resist_vuln_immune(dmg, dmg_type, target)
        hp_before = int(target.get("HP", 0))
        hp_after = max(0, hp_before - adj_dmg)
        target["HP"] = hp_after

        msg = f"{self.combatant['Name']} hits {target['Name']} with {action['name']}! {dmg_str}"
        if note:
            msg += f" ({note})"
        msg += f" Damage: {adj_dmg}. HP: {hp_before} → {hp_after}."
        if crit:
            msg += " (Critical Hit!)"
        self.log_callback(msg)

        if hp_before > 0 and hp_after == 0:
            self.log_callback(f"{target['Name']} has fallen!")

        # Optional AI narration
        try:
            import openai

            prompt = (
                f"You are a D&D 5e DM narrator. Describe in one vivid sentence how "
                f"{self.combatant['Name']}'s {action['name']} strikes {target['Name']}."
            )
            resp = openai.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.9,
            )
            narration = resp.choices[0].message.content.strip()
            if narration:
                self.log_callback(f"DM: {narration}")
        except Exception:
            pass

        # ✅ ensure table refreshes to show updated HP
        parent_tab = self.parent()
        if parent_tab and hasattr(parent_tab, "refresh_table"):
            parent_tab.refresh_table()


class CombatTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.combatants = []

        main_layout = QHBoxLayout()
        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        self.log_widget.setLineWrapMode(QTextEdit.WidgetWidth)
        main_layout.addWidget(self.log_widget, stretch=1)

        right_layout = QVBoxLayout()
        add_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add Combatant")
        self.add_btn.clicked.connect(self.add_combatant)
        add_layout.addWidget(self.add_btn)

        self.roll_initiative_btn = QPushButton("Roll Initiative")
        self.roll_initiative_btn.clicked.connect(self.roll_initiative)
        add_layout.addWidget(self.roll_initiative_btn)

        add_layout.addStretch(1)
        right_layout.addLayout(add_layout)

        # Table without “Deal Damage” column
        self.table = QTableWidget(0, 13)
        self.table.setHorizontalHeaderLabels(
            [
                "Name",
                "Type",
                "HP",
                "AC",
                "STR",
                "DEX",
                "CON",
                "INT",
                "WIS",
                "CHA",
                "Initiative",
                "Actions",
                "Remove",
            ]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        right_layout.addWidget(self.table)

        main_layout.addLayout(right_layout, stretch=2)
        self.setLayout(main_layout)

    def log_message(self, msg):
        self.log_widget.append(msg)
        self.log_widget.moveCursor(self.log_widget.textCursor().End)

    def add_combatant(self):
        folder = self.main_window.campaign_folder
        if not folder:
            QMessageBox.warning(self, "No Campaign", "Please load a campaign first.")
            return
        chars = load_entities("characters", folder)
        npcs = load_entities("npcs", folder)
        options = [("Character", c) for c in chars] + [("NPC", n) for n in npcs]
        if not options:
            QMessageBox.warning(self, "No Entities", "No characters or NPCs available.")
            return

        dlg = QDialog(self)
        dlg.setWindowTitle("Select Combatant")
        layout = QVBoxLayout()
        combo = QComboBox()
        for typ, ent in options:
            combo.addItem(f"{typ}: {ent.get('Name', 'Unnamed')}")
        layout.addWidget(QLabel("Select a character or NPC:"))
        layout.addWidget(combo)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(btns)
        dlg.setLayout(layout)
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        if dlg.exec_() == QDialog.Accepted:
            idx = combo.currentIndex()
            typ, ent = options[idx]
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
                "Actions": [dict(a) for a in ent.get("Actions", [])],
                "Resistances": ent.get("Resistances", ""),
                "Vulnerabilities": ent.get("Vulnerabilities", ""),
                "Immunities": ent.get("Immunities", ""),
            }
            self.combatants.append(combatant)
            self.refresh_table()

    def refresh_table(self):
        self.table.setRowCount(len(self.combatants))
        for row, c in enumerate(self.combatants):
            for col, key in enumerate(
                [
                    "Name",
                    "Type",
                    "HP",
                    "AC",
                    "STR",
                    "DEX",
                    "CON",
                    "INT",
                    "WIS",
                    "CHA",
                    "Initiative",
                ]
            ):
                item = QTableWidgetItem(str(c.get(key, "")))
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.table.setItem(row, col, item)

            # Actions button
            actions_btn = QPushButton("Actions")
            actions_btn.clicked.connect(lambda _, r=row: self.open_actions_dialog(r))
            self.table.setCellWidget(row, 11, actions_btn)

            # Remove button (only active if HP == 0)
            rm_btn = QPushButton("Remove")
            rm_btn.setEnabled(int(c.get("HP", 0)) == 0)
            rm_btn.clicked.connect(lambda _, r=row: self.remove_combatant(r))
            self.table.setCellWidget(row, 12, rm_btn)

    def open_actions_dialog(self, row):
        dlg = ActionDialog(
            self.combatants[row],
            self.combatants,
            self.log_message,
            self.main_window,
            self,
        )
        if dlg.exec_():
            self.refresh_table()

    def remove_combatant(self, row):
        if row < 0 or row >= len(self.combatants):
            return
        combatant = self.combatants[row]
        if int(combatant.get("HP", 0)) != 0:
            QMessageBox.warning(self, "Cannot Remove", "Can only remove if HP is 0.")
            return
        name = combatant.get("Name", "Unknown")
        del self.combatants[row]
        self.log_message(f"{name} has been removed from combat.")
        self.refresh_table()

    def roll_initiative(self):
        for c in self.combatants:
            c["Initiative"] = random.randint(1, 20)
        self.combatants.sort(key=lambda x: int(x.get("Initiative", 0)), reverse=True)
        self.refresh_table()
