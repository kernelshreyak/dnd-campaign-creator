from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QFileDialog
)
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DnD 5e Solo Campaign Creator")
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

        layout.addStretch(1)

        button_col = QVBoxLayout()
        button_col.setSpacing(16)

        create_btn = QPushButton("Create Campaign")
        create_btn.setMinimumWidth(220)
        create_btn.clicked.connect(lambda: self.open_campaign_dialog(mode="create"))
        button_col.addWidget(create_btn, alignment=Qt.AlignHCenter)

        load_btn = QPushButton("Load Campaign")
        load_btn.setMinimumWidth(220)
        load_btn.clicked.connect(self.load_campaign_direct)
        button_col.addWidget(load_btn, alignment=Qt.AlignHCenter)

        exit_btn = QPushButton("Exit")
        exit_btn.setMinimumWidth(220)
        exit_btn.clicked.connect(self.close)
        button_col.addWidget(exit_btn, alignment=Qt.AlignHCenter)

        layout.addLayout(button_col)
        layout.addStretch(2)

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

    def open_campaign_dialog(self, mode="both"):
        from gui.campaign_dialog import CampaignDialog
        dialog = CampaignDialog(self, mode=mode)
        if dialog.exec_():
            self._apply_campaign(dialog.campaign_name, dialog.campaign_folder)

    def load_campaign_direct(self):
        default_dir = os.path.expanduser('~/DnD_Campaigns/')
        folder = QFileDialog.getExistingDirectory(
            self, "Select Existing Campaign Folder", default_dir
        )
        if folder:
            name = os.path.basename(folder)
            self._apply_campaign(name, folder)

    def _apply_campaign(self, name, folder):
        self.campaign_name = name
        self.campaign_folder = folder
        self.campaign_label.setText(
            f"Current Campaign: {self.campaign_name}\nFolder: {self.campaign_folder}"
        )
        # Refresh entity tabs after loading campaign
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
