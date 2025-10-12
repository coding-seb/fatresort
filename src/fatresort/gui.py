import sys
import os
import shutil
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QListWidget, QPushButton, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt


class MP3Sorter(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("USB MP3 Sorter")
        self.resize(400, 500)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(self.list_widget.SelectionMode.ExtendedSelection)
        self.list_widget.setDragDropMode(self.list_widget.DragDropMode.InternalMove)
        layout.addWidget(self.list_widget)

        self.load_button = QPushButton("Load USB Folder")
        self.save_button = QPushButton("Apply Order")
        layout.addWidget(self.load_button)
        layout.addWidget(self.save_button)

        self.load_button.clicked.connect(self.load_folder)
        self.save_button.clicked.connect(self.apply_order)
        self.folder_path = None

    def load_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select USB Folder")
        if folder:
            self.folder_path = folder
            self.list_widget.clear()
            for f in sorted(os.listdir(folder)):
                if f.lower().endswith(".mp3"):
                    self.list_widget.addItem(f)

    def apply_order(self):
        if not self.folder_path:
            return
        items = [self.list_widget.item(i).text() for i in range(self.list_widget.count())]
        confirm = QMessageBox.question(self, "Confirm", "Re-copy files in this order?")
        if confirm != QMessageBox.StandardButton.Yes:
            return

        temp_dir = os.path.join(self.folder_path, "_temp")
        os.makedirs(temp_dir, exist_ok=True)

        for i, fname in enumerate(items, start=1):
            src = os.path.join(self.folder_path, fname)
            dst = os.path.join(temp_dir, f"{i:03d}_{fname}")
            shutil.copy2(src, dst)

        # Clear old files and replace
        for f in os.listdir(self.folder_path):
            if f.lower().endswith(".mp3"):
                os.remove(os.path.join(self.folder_path, f))
        for f in os.listdir(temp_dir):
            shutil.move(os.path.join(temp_dir, f), os.path.join(self.folder_path, f))
        os.rmdir(temp_dir)

        QMessageBox.information(self, "Done", "Files reordered successfully!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MP3Sorter()
    window.show()
    sys.exit(app.exec())
