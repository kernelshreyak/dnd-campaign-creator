from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QTabWidget, QVBoxLayout, QLabel, QPushButton
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DnD 5e Campaign Creator")
        self.setGeometry(100, 100, 1000, 700)

        self.campaign_name = None
        self.campaign_folder = None

        self.tabs = QTabWidget()
        self.tabs.addTab(self._make_campaign_tab(), "Campaign")
        self.tabs.addTab(self._make_characters_tab(), "Characters")
        self.tabs.addTab(self._make_spells_tab(), "Spells")
        self.tabs.addTab(self._make_items_tab(), "Items")
        self.tabs.addTab(self._make_npcs_tab(), "NPCs")
        self.tabs.addTab(self._make_notes_tab(), "Notes")

        main_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

    def _make_campaign_tab(self):
        from gui.campaign_dialog import CampaignDialog
        widget = QWidget()
        layout = QVBoxLayout()
        self.campaign_label = QLabel("No campaign loaded.")
        btn = QPushButton("Create/Load Campaign")
        btn.clicked.connect(self.open_campaign_dialog)
        layout.addWidget(self.campaign_label)
        layout.addWidget(btn)
        widget.setLayout(layout)
        return widget

    def _make_characters_tab(self):
        from gui.character_tab import CharacterTab
        return CharacterTab(self)

    def _make_spells_tab(self):
        from gui.spell_tab import SpellTab
        return SpellTab(self)

    def _make_items_tab(self):
        from gui.item_tab import ItemTab
        return ItemTab(self)

    def _make_npcs_tab(self):
        from gui.npc_tab import NPCTab
        return NPCTab(self)

    def _make_notes_tab(self):
        from gui.notes_editor import NotesEditor
        return NotesEditor(self)

    def open_campaign_dialog(self):
        from gui.campaign_dialog import CampaignDialog
        dialog = CampaignDialog(self)
        if dialog.exec_():
            self.campaign_name = dialog.campaign_name
            self.campaign_folder = dialog.campaign_folder
            self.campaign_label.setText(
                f"Current Campaign: {self.campaign_name}\nFolder: {self.campaign_folder}"
            )

    def _make_tab(self, name):
        widget = QWidget()
        layout = QVBoxLayout()
        label = QLabel(f"{name} section coming soon...")
        layout.addWidget(label)
        widget.setLayout(layout)
        return widget