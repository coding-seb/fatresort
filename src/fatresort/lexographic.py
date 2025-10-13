import sys

from PyQt6.QtWidgets import QVBoxLayout, QWidget, QListWidget, QPushButton, QApplication


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
        from PyQt6.QtWidgets import QFileDialog
        import os

        folder = QFileDialog.getExistingDirectory(self, "Select USB Folder")
        if folder:
            self.folder_path = folder
            self.list_widget.clear()
            for f in sorted(os.listdir(folder)):
                if f.lower().endswith(".mp3"):
                    self.list_widget.addItem(f)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MP3Sorter()
    window.show()
    sys.exit(app.exec())