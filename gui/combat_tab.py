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
    QPlainTextEdit,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap, QTextCharFormat, QColor
import random
import re
import os
import json
from utils.file_io import load_entities
import openai

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
    dmg_types = parse_tags(damage_type)
    res = parse_tags(target.get("Resistances", ""))
    vul = parse_tags(target.get("Vulnerabilities", ""))
    imm = parse_tags(target.get("Immunities", ""))
    
    # if immune to all damage types
    if dmg_types and len(dmg_types & imm) == len(dmg_types):
        return 0, "immune"

    adjusted = base_damage
    notes = []
    if dmg_types and dmg_types & res:
        adjusted = base_damage // 2
        notes.append("resistance")
    if dmg_types and dmg_types & vul:
        adjusted = adjusted * 2
        notes.append("vulnerability")

    note = "+".join(notes) if notes else None
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
        msg += f" Damage: {adj_dmg} ({dmg_type}). HP: {hp_before} → {hp_after}."
        if crit:
            msg += " (Critical Hit!)"
        self.log_callback(msg)

        if hp_before > 0 and hp_after == 0:
            self.log_callback(f"{target['Name']} has fallen!")

        # 🎭 Enhanced AI narration with damage, effects, and death context
        try:
            dmg_text = f"{adj_dmg} {dmg_type} damage" if adj_dmg > 0 else "no damage"
            effect_text = action.get("description", "").strip()
            fallen = hp_after == 0

            prompt = (
                "You are a dramatic and concise Dungeon Master narrator in D&D 5e combat. "
                "Write a vivid cinematic describing the outcome of the action, "
                "from a third-person perspective."
                "Take into account the calculation results provided,the action description as well as target's vulnerabilities, resistances and immunities to more accurately describe the oucome"
                "Include tone, motion, and consequence, not numbers. "
                "If the target is slain or falls to 0 HP, make it climactic and final. "
                "Keep it short but engaging enough.\n\n"
                f"Attacker: {self.combatant['Name']} (class: {self.combatant['Class']}, race: {self.combatant['Race']})\n"
                f"Action: {action.get('name', 'Unknown Action')}\n"
                f"Description: {effect_text}\n"
                f"Calculation by combat engine: {msg}\n"
                f"Target: {target['Name']} (class: {self.combatant['Class']}, race: {self.combatant['Race']}, Immunities: {target['Immunities']}, Resistances: {target['Resistances']},Vulnerabilities {target['Vulnerabilities']})\n"
                f"Hit: {hit}\n"
                f"Critical: {crit}\n"
                f"Damage: {dmg_text}\n"
                f"Target HP before: {hp_before}, after: {hp_after}\n"
                f"Target Fallen: {fallen}\n"
            )

            resp = openai.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=120,
                temperature=1.0,
            )
            narration = resp.choices[0].message.content.strip()
            if narration:
                self.log_callback(f"DM: {narration}")
        except Exception as e:
            self.log_callback(f"[Narration skipped: {e}]")

        # ✅ ensure table refreshes to show updated HP
        parent_tab = self.parent()
        if parent_tab and hasattr(parent_tab, "refresh_table"):
            parent_tab.refresh_table()
        if parent_tab and hasattr(parent_tab, "save_state"):
            parent_tab.save_state(silent=True)


class CombatTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.combatants = []
        self._token_cache = {}
        self._format_cache = {
            "hit": self._make_format(QColor("#c62828")),
            "fallen": self._make_format(QColor("#8e0000")),
            "roll": self._make_format(QColor("#1e88e5")),
            "default": self._make_format(QColor("#000000")),
        }
        self.active_speaker = None
        self.dm_speaker = {"Name": "Dungeon Master", "Type": "Narrator"}

        main_layout = QHBoxLayout()

        left_layout = QVBoxLayout()
        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        self.log_widget.setLineWrapMode(QTextEdit.WidgetWidth)
        left_layout.addWidget(self.log_widget, stretch=1)

        self.speaker_label = QLabel("Speaking as: None")
        left_layout.addWidget(self.speaker_label)

        self.chat_input = QPlainTextEdit()
        self.chat_input.setPlaceholderText("Type in-character dialogue...")
        self.chat_input.setFixedHeight(80)
        left_layout.addWidget(self.chat_input)

        chat_btn_row = QHBoxLayout()
        self.chat_send_btn = QPushButton("Send")
        self.chat_send_btn.clicked.connect(self.send_chat)
        chat_btn_row.addWidget(self.chat_send_btn, alignment=Qt.AlignLeft)
        self.chat_dm_btn = QPushButton("Chat as DM")
        self.chat_dm_btn.clicked.connect(self.chat_as_dm)
        chat_btn_row.addWidget(self.chat_dm_btn, alignment=Qt.AlignLeft)
        chat_btn_row.addStretch(1)
        left_layout.addLayout(chat_btn_row)

        main_layout.addLayout(left_layout, stretch=1)

        right_layout = QVBoxLayout()
        add_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add Combatant")
        self.add_btn.clicked.connect(self.add_combatant)
        add_layout.addWidget(self.add_btn)

        self.roll_initiative_btn = QPushButton("Roll Initiative")
        self.roll_initiative_btn.clicked.connect(self.roll_initiative)
        add_layout.addWidget(self.roll_initiative_btn)

        self.save_state_btn = QPushButton("Save Combat State")
        self.save_state_btn.clicked.connect(self.save_state)
        add_layout.addWidget(self.save_state_btn)

        add_layout.addStretch(1)
        right_layout.addLayout(add_layout)

        self.table = QTableWidget(0, 9)
        self.table.setHorizontalHeaderLabels(
            [
                "Name",
                "Type",
                "HP",
                "AC",
                "Initiative",
                "Chat As",
                "Actions",
                "Show Stats",
                "Remove",
            ]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        right_layout.addWidget(self.table)
        self.table.currentCellChanged.connect(
            lambda row, _col, _old_row, _old_col: self.update_token_preview(row)
        )

        self.token_preview = QLabel("Select a combatant to preview token.")
        self.token_preview.setAlignment(Qt.AlignCenter)
        self.token_preview.setFixedHeight(160)
        self.token_preview.setStyleSheet("border: 1px solid #ccc; background-color: #f8f8f8;")
        right_layout.addWidget(self.token_preview)

        main_layout.addLayout(right_layout, stretch=2)
        self.setLayout(main_layout)
        self._update_speaker_label()

    def _make_format(self, color):
        fmt = QTextCharFormat()
        fmt.setForeground(color)
        return fmt

    def log_message(self, msg):
        if msg.startswith("Attack Roll") or msg.startswith("Damage") or "=" in msg:
            fmt = self._format_cache["roll"]
        elif "has fallen" in msg:
            fmt = self._format_cache["fallen"]
        elif "hits" in msg or "Attack Roll" in msg:
            fmt = self._format_cache["hit"]
        else:
            fmt = self._format_cache["default"]

        cursor = self.log_widget.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(msg + "\n", fmt)
        self.log_widget.setTextCursor(cursor)

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
                "Class": ent.get("Class", ""),
                "Race": ent.get("Race", ""),
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
                "TokenImage": ent.get("TokenImage", ""),
            }
            self.combatants.append(combatant)
            self.refresh_table()
            self.save_state(silent=True)

    def refresh_table(self):
        self.table.setRowCount(len(self.combatants))
        for row, c in enumerate(self.combatants):
            name_item = QTableWidgetItem(str(c.get("Name", "")))
            pixmap = self._get_token_pixmap(c.get("TokenImage", ""))
            if pixmap:
                name_item.setIcon(QIcon(pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)))
            name_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.table.setItem(row, 0, name_item)

            for offset, key in enumerate(["Type", "HP", "AC", "Initiative"], start=1):
                item = QTableWidgetItem(str(c.get(key, "")))
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.table.setItem(row, offset, item)

            chat_btn = QPushButton("Chat As")
            chat_btn.clicked.connect(lambda _, r=row: self.chat_as(r))
            self.table.setCellWidget(row, 5, chat_btn)

            actions_btn = QPushButton("Actions")
            actions_btn.clicked.connect(lambda _, r=row: self.open_actions_dialog(r))
            self.table.setCellWidget(row, 6, actions_btn)

            stats_btn = QPushButton("Show Stats")
            stats_btn.clicked.connect(lambda _, r=row: self.show_stats_dialog(r))
            self.table.setCellWidget(row, 7, stats_btn)

            rm_btn = QPushButton("Remove")
            rm_btn.setEnabled(int(c.get("HP", 0)) == 0)
            rm_btn.clicked.connect(lambda _, r=row: self.remove_combatant(r))
            self.table.setCellWidget(row, 8, rm_btn)

        current_row = self.table.currentRow()
        if current_row >= 0:
            self.update_token_preview(current_row)
        elif self.combatants:
            self.table.selectRow(0)
        else:
            self.update_token_preview(-1)
        self._update_speaker_label()

    def chat_as(self, row):
        if row < 0 or row >= len(self.combatants):
            return
        self.active_speaker = self.combatants[row]
        self.table.selectRow(row)
        self._update_speaker_label()

    def _update_speaker_label(self):
        if (
            self.active_speaker not in self.combatants
            and self.active_speaker is not self.dm_speaker
        ):
            self.active_speaker = None
        if self.active_speaker is self.dm_speaker:
            self.speaker_label.setText("Speaking as: Dungeon Master")
        elif self.active_speaker:
            name = self.active_speaker.get("Name", "Unknown")
            self.speaker_label.setText(f"Speaking as: {name}")
        else:
            self.speaker_label.setText("Speaking as: None")

    def chat_as_dm(self):
        self.active_speaker = self.dm_speaker
        self._update_speaker_label()

    def send_chat(self):
        message = self.chat_input.toPlainText().strip()
        if not message:
            return
        if not self.active_speaker:
            QMessageBox.warning(
                self,
                "No Speaker Selected",
                "Choose a combatant to speak as using the 'Chat As' button.",
            )
            return
        name = self.active_speaker.get("Name", "Unknown")
        self.log_message(f"{name} said: {message}")
        self.chat_input.clear()
        self.save_state(silent=True)

    def _state_file_path(self):
        folder = getattr(self.main_window, "campaign_folder", None)
        if not folder:
            return None
        return os.path.join(folder, "combat_state.json")

    def save_state(self, silent=False):
        path = self._state_file_path()
        if not path:
            if not silent:
                QMessageBox.warning(self, "No Campaign", "Load a campaign before saving combat state.")
            return
        state = {
            "combatants": self.combatants,
            "log_lines": self.log_widget.toPlainText().splitlines(),
            "active_speaker": (
                "__DM__" if self.active_speaker is self.dm_speaker else self.active_speaker.get("Name")
            )
        }
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
            if not silent:
                QMessageBox.information(self, "Combat Saved", f"Combat state saved to {path}")
        except Exception as exc:
            QMessageBox.critical(self, "Save Error", f"Failed to save combat state:\n{exc}")

    def load_saved_state(self):
        path = self._state_file_path()
        self.log_widget.clear()
        self.chat_input.clear()
        self._token_cache.clear()
        if not path or not os.path.exists(path):
            self.combatants = []
            self.active_speaker = None
            self.refresh_table()
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as exc:
            QMessageBox.warning(self, "Load Warning", f"Could not load combat state:\n{exc}")
            self.combatants = []
            self.active_speaker = None
            self.refresh_table()
            return

        self.combatants = data.get("combatants", [])
        speaker_name = data.get("active_speaker")
        if speaker_name == "__DM__":
            self.active_speaker = self.dm_speaker
        else:
            self.active_speaker = next(
                (c for c in self.combatants if c.get("Name") == speaker_name), None
            )
        for line in data.get("log_lines", []):
            if isinstance(line, str):
                self.log_message(line)
        self.refresh_table()

    def _get_token_pixmap(self, source):
        if not source:
            return None
        if source in self._token_cache:
            return self._token_cache[source]

        pixmap = QPixmap()
        try:
            if source.lower().startswith(("http://", "https://")):
                from urllib.request import urlopen

                with urlopen(source) as resp:
                    data = resp.read()
                pixmap.loadFromData(data)
            else:
                if os.path.exists(source):
                    pixmap.load(source)
                else:
                    pixmap.load(source)
        except Exception:
            pixmap = QPixmap()

        if not pixmap.isNull():
            self._token_cache[source] = pixmap
            return pixmap

        self._token_cache[source] = None
        return None

    def update_token_preview(self, row):
        if row is None or row < 0 or row >= len(self.combatants):
            self.token_preview.setText("Select a combatant to preview token.")
            self.token_preview.setPixmap(QPixmap())
            return
        pixmap = self._get_token_pixmap(self.combatants[row].get("TokenImage", ""))
        if pixmap and not pixmap.isNull():
            scaled = pixmap.scaled(140, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.token_preview.setPixmap(scaled)
            self.token_preview.setText("")
        else:
            self.token_preview.setPixmap(QPixmap())
            self.token_preview.setText("No token available.")

    def show_stats_dialog(self, row):
        if row < 0 or row >= len(self.combatants):
            return
        combatant = self.combatants[row]
        dlg = QDialog(self)
        dlg.setWindowTitle(f"{combatant.get('Name', 'Combatant')} Stats")
        layout = QVBoxLayout()
        for label, key in [
            ("STR", "STR"),
            ("DEX", "DEX"),
            ("CON", "CON"),
            ("INT", "INT"),
            ("WIS", "WIS"),
            ("CHA", "CHA"),
            ("Resistances", "Resistances"),
            ("Vulnerabilities", "Vulnerabilities"),
            ("Immunities", "Immunities"),
        ]:
            layout.addWidget(QLabel(f"{label}: {combatant.get(key, '')}"))
        btns = QDialogButtonBox(QDialogButtonBox.Ok)
        btns.accepted.connect(dlg.accept)
        layout.addWidget(btns)
        dlg.setLayout(layout)
        dlg.exec_()

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
        if self.active_speaker is combatant:
            self.active_speaker = None
        self.log_message(f"{name} has been removed from combat.")
        self.refresh_table()
        self.save_state(silent=True)

    def roll_initiative(self):
        for c in self.combatants:
            c["Initiative"] = random.randint(1, 20)
        self.combatants.sort(key=lambda x: int(x.get("Initiative", 0)), reverse=True)
        self.refresh_table()
        self.save_state(silent=True)
