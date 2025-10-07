from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QWidget,
)
import os

class CampaignDialog(QDialog):
    def __init__(self, parent=None, mode="both"):
        super().__init__(parent)
        self.mode = mode
        if mode == "create":
            self.setWindowTitle("Create Campaign")
        elif mode == "load":
            self.setWindowTitle("Load Campaign")
        else:
            self.setWindowTitle("Create or Load Campaign")
        self.setMinimumWidth(400)

        self.campaign_name = ""
        self.campaign_folder = ""

        layout = QVBoxLayout()

        # Campaign name input
        name_container = QWidget()
        name_layout = QHBoxLayout(name_container)
        name_layout.setContentsMargins(0, 0, 0, 0)
        name_label = QLabel("Campaign Name:")
        self.name_edit = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        layout.addWidget(name_container)

        # Folder selection
        folder_container = QWidget()
        folder_layout = QHBoxLayout(folder_container)
        folder_layout.setContentsMargins(0, 0, 0, 0)
        folder_label = QLabel("Campaign Folder:")
        self.folder_edit = QLineEdit()
        self.folder_edit.setReadOnly(True)
        folder_btn = QPushButton("Choose Folder")
        folder_btn.clicked.connect(self.choose_folder)
        folder_layout.addWidget(folder_label)
        folder_layout.addWidget(self.folder_edit)
        folder_layout.addWidget(folder_btn)
        layout.addWidget(folder_container)

        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_campaign)
        load_btn = QPushButton("Load")
        load_btn.clicked.connect(self.load_campaign)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(load_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        if self.mode == "create":
            load_btn.hide()
        elif self.mode == "load":
            create_btn.hide()
            name_container.hide()

        self.setLayout(layout)

    def choose_folder(self):
        default_dir = os.path.expanduser('~/DnD_Campaigns/')
        folder = QFileDialog.getExistingDirectory(self, "Select Campaign Folder", default_dir)
        if folder:
            self.folder_edit.setText(folder)

    def create_campaign(self):
        name = self.name_edit.text().strip()
        folder = self.folder_edit.text().strip()
        if not name or not folder:
            QMessageBox.warning(self, "Missing Info", "Please enter a campaign name and choose a folder.")
            return
        campaign_path = os.path.join(folder, name)
        try:
            os.makedirs(campaign_path, exist_ok=True)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not create campaign folder:\n{e}")
            return
        self.campaign_name = name
        self.campaign_folder = campaign_path
        self.accept()

    def load_campaign(self):
        default_dir = os.path.expanduser('~/DnD_Campaigns/')
        folder = QFileDialog.getExistingDirectory(self, "Select Existing Campaign Folder", default_dir)
        if folder:
            self.campaign_name = os.path.basename(folder)
            self.campaign_folder = folder
            self.accept()
