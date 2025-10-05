from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DnD 5e Campaign Creator")
        self.campaign_name = None
        self.campaign_folder = None


        self.tabs = QTabWidget()
        self.tabs.addTab(self._make_campaign_tab(), "Campaign")
        self.tabs.addTab(self._make_characters_tab(), "Characters")
        self.tabs.addTab(self._make_npcs_tab(), "NPCs")
        self.tabs.addTab(self._make_notes_tab(), "Notes")
        self.tabs.addTab(self._make_combat_tab(), "Combat")

        main_widget = QWidget()
        main_layout = QHBoxLayout()

        # Ensure the tab widget expands to fill available space
        self.tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(self.tabs, stretch=1)
        main_widget.setLayout(main_layout)
        main_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setCentralWidget(main_widget)

        self.showFullScreen()

    def _make_campaign_tab(self):
        from PyQt5.QtCore import Qt
        widget = QWidget()
        layout = QVBoxLayout()
        self.campaign_label = QLabel("No campaign loaded.")
        layout.addWidget(self.campaign_label, alignment=Qt.AlignHCenter)

        # Center the button horizontally and vertically
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        btn = QPushButton("Create/Load Campaign")
        btn.clicked.connect(self.open_campaign_dialog)
        button_layout.addWidget(btn)
        button_layout.addStretch(1)

        layout.addStretch(1)
        layout.addLayout(button_layout)
        layout.addStretch(1)

        widget.setLayout(layout)
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return widget

    def _make_characters_tab(self):
        from gui.character_tab import CharacterTab
        return CharacterTab(self)

    def _make_npcs_tab(self):
        from gui.npc_tab import NPCTab
        return NPCTab(self)

    def _make_notes_tab(self):
        from gui.notes_editor import NotesEditor
        return NotesEditor(main_window=self)

    def _make_combat_tab(self):
        from gui.combat_tab import CombatTab
        return CombatTab(self)

    def open_campaign_dialog(self):
        from gui.campaign_dialog import CampaignDialog
        dialog = CampaignDialog(self)
        if dialog.exec_():
            self.campaign_name = dialog.campaign_name
            self.campaign_folder = dialog.campaign_folder
            self.campaign_label.setText(
                f"Current Campaign: {self.campaign_name}\nFolder: {self.campaign_folder}"
            )
            # Refresh entity tabs after loading campaign
            # Tab order: 0=Campaign, 1=Characters, 2=NPCs, 3=Notes
            for idx in [1, 2, 3, 4]:
                tab = self.tabs.widget(idx)
                if hasattr(tab, "refresh_list"):
                    tab.refresh_list()
            # Load notes in Notes tab (assumed to be tab index 3)
            notes_tab_index = 3
            if self.tabs.count() > notes_tab_index:
                notes_tab = self.tabs.widget(notes_tab_index)
                if hasattr(notes_tab, "load_notes"):
                    notes_tab.load_notes()

    def _make_tab(self, name):
        widget = QWidget()
        layout = QVBoxLayout()
        label = QLabel(f"{name} section coming soon...")
        layout.addWidget(label)
        widget.setLayout(layout)
        return widget