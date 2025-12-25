import sys
import shutil
import tempfile
import time
from pathlib import Path

import gettext
from typing import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QTreeWidget,
    QTreeWidgetItem, QProgressBar,
)

import os

lang = os.getenv("LANG")
locale_dir = Path(os.path.dirname(os.path.realpath(__file__))).joinpath(
    Path("./locale")
)


class MP3Sorter(QWidget):
    def __init__(self):
        super().__init__()

        self.translate = self.install_language()

        self.setWindowTitle(self.translate("USB MP3 Sorter"))
        self.resize(400, 500)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.tree_widget = QTreeWidget()
        self.tree_widget.setSelectionMode(
            self.tree_widget.SelectionMode.ExtendedSelection
        )
        self.tree_widget.setDragDropMode(self.tree_widget.DragDropMode.InternalMove)
        self.tree_widget.setHeaderLabel(self.translate("No folder selected"))
        self.layout.addWidget(self.tree_widget)

        self.load_button = QPushButton(self.translate("Load USB Folder"))
        self.save_button = QPushButton(self.translate("Apply order"))
        self.layout.addWidget(self.load_button)
        self.layout.addWidget(self.save_button)

        self.load_button.clicked.connect(self.load_folder)
        self.save_button.clicked.connect(self.apply_order)
        self.save_button.setEnabled(False)
        self.folder_path = None

    @staticmethod
    def install_language() -> Callable[[str], str] | None:
        if lang and lang.startswith("de"):
            gettext.bindtextdomain(domain="gui", localedir=locale_dir)
            gettext.textdomain(domain="gui")

            german = gettext.translation(
                domain="gui", localedir=locale_dir, languages=["de"]
            )
            german.install()
            return german.gettext
        return lambda s: s

    def append_folder(self, parent_item: QTreeWidgetItem, folder_path: str):
        for f in sorted(os.listdir(folder_path)):
            path = os.path.join(folder_path, f)
            if os.path.isdir(path):
                dir_item = QTreeWidgetItem(parent_item, [f])
                dir_item.setFlags(Qt.ItemFlag.NoItemFlags)
                self.append_folder(parent_item=dir_item, folder_path=path)
            elif f.lower().endswith(".mp3"):
                mp3_item = QTreeWidgetItem(parent_item, [f])
                mp3_item.setFlags(Qt.ItemFlag.NoItemFlags)

    def load_folder(self):
        folder = QFileDialog.getExistingDirectory(
            parent=self,
            caption=self.translate("Select USB Folder"),
            directory="/media/",
        )
        if folder:
            self.folder_path = folder
            self.tree_widget.setHeaderLabel(
                self.translate("Lexicographic order and file structure")
            )
            self.tree_widget.clear()
            root_item = QTreeWidgetItem([folder])
            self.append_folder(parent_item=root_item, folder_path=folder)
            self.tree_widget.addTopLevelItem(root_item)
            self.tree_widget.expandAll()
            self.save_button.setEnabled(True)

    def apply_order(self):
        self.save_button.setEnabled(False)
        confirm = QMessageBox.question(
            self,
            "Confirm",
            self.translate("Re-copy files in set order? Note that this needs the same diskspace on the computer as the current files."),
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        with tempfile.TemporaryDirectory() as temp_dir:
            progress_bar = QProgressBar(self)
            progress_bar.setMaximum(100)
            progress_bar.setValue(0)

            self.layout.addWidget(progress_bar)
            QApplication.processEvents()  # allow Qt to repaint and handle events

            # # Simulate progress while allowing the UI to update
            # for current_value in range(0, progress_bar.maximum() + 1, 2):
            #     progress_bar.setValue(current_value)
            #     QApplication.processEvents()  # allow Qt to repaint and handle events
            #     time.sleep(0.05)  # brief pause for visible progress (keeps simulation)

            os.makedirs(temp_dir, exist_ok=True)

            progress_bar.setValue(10)
            QApplication.processEvents()  # allow Qt to repaint and handle events

            # Copy all files to tmp dir
            top_item: QTreeWidgetItem = self.tree_widget.topLevelItem(0)
            root_path = Path(top_item.text(0))
            shutil.copytree(root_path, temp_dir, dirs_exist_ok=True)
            QApplication.processEvents()  # allow Qt to repaint and handle events
            progress_bar.setValue(60)

            # Delete all files on drive
            self.delete_folder_contents(path=root_path)
            QApplication.processEvents()  # allow Qt to repaint and handle events
            progress_bar.setValue(70)

            # Go through tree in order and copy files back to drive
            self.copy_folder(item=top_item, base_path=root_path, tmp_dir=temp_dir)
            QApplication.processEvents()  # allow Qt to repaint and handle events
            progress_bar.setValue(100)

        QMessageBox.information(
            self, "Done", self.translate("Files reordered successfully")
        )

        self.layout.removeWidget(progress_bar)

    def copy_folder(self, item: QTreeWidgetItem, base_path: Path, tmp_dir: str):
        base_path = base_path / item.text(0)
        os.makedirs(base_path, exist_ok=True)
        for i in range(item.childCount()):
            child = item.child(i)
            if child.text(0).endswith(".mp3"):
                # File
                dst_file = base_path / child.text(0)
                src_file = os.path.join(tmp_dir, child.text(0))
                shutil.copy2(src_file, dst_file)
            else:
                # Folder
                self.copy_folder(
                    item=child,
                    base_path=base_path,
                    tmp_dir=os.path.join(tmp_dir, child.text(0)),
                )

    @staticmethod
    def delete_folder_contents(path: Path):
        for f in os.listdir(path):
            full_path = os.path.join(path, f)
            if os.path.isdir(full_path):
                shutil.rmtree(full_path)
            else:
                os.remove(full_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MP3Sorter()
    window.show()
    sys.exit(app.exec())
