import sys
import os
import shutil
import tempfile
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QTreeWidget,
    QTreeWidgetItem,
)

# class FileTree(QTreeWidget):
#     def __init__(self):
#         super().__init__()
#         self.setDragDropMode(self.DragDropMode.InternalMove)
#         self.setSelectionMode(self.SelectionMode.ExtendedSelection)
#         self.setHeaderLabel("USB Contents")
#
#     def dropEvent(self, event):
#         target_item = self.itemAt(event.position().toPoint())
#         dragged_items = self.selectedItems()
#
#         # If no target (e.g. dropping on empty area), allow it
#         if not target_item:
#             super().dropEvent(event)
#             return
#
#         # Helper: determine if an item represents a folder or a file
#         def is_folder(item):
#             return item.data(0, 0) == "folder"
#
#         def is_file(item):
#             return item.data(0, 0) == "file"
#
#         # Case 1: Dropping an MP3 onto another MP3 → BLOCK
#         if is_file(target_item):
#             QMessageBox.warning(self, "Invalid Drop", "You cannot drop an MP3 onto another MP3.")
#             event.ignore()
#             return
#
#         # Case 2: Dropping an MP3 into a different folder → BLOCK
#         for src in dragged_items:
#             parent = src.parent()
#             if is_file(src):
#                 # Find folder that will contain it
#                 dest_folder = target_item if is_folder(target_item) else target_item.parent()
#                 if parent != dest_folder:
#                     QMessageBox.warning(self, "Invalid Move", "MP3 files can only be reordered within their own folder.")
#                     event.ignore()
#                     return
#
#         # Otherwise, allow normal internal move
#         super().dropEvent(event)


class MP3Sorter(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("USB MP3 Sorter")
        self.resize(400, 500)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # self.list_widget = QListWidget()
        # self.list_widget.setSelectionMode(self.list_widget.SelectionMode.ExtendedSelection)
        # self.list_widget.setDragDropMode(self.list_widget.DragDropMode.InternalMove)
        # layout.addWidget(self.list_widget)

        self.tree_widget = QTreeWidget()
        self.tree_widget.setSelectionMode(
            self.tree_widget.SelectionMode.ExtendedSelection
        )
        self.tree_widget.setDragDropMode(self.tree_widget.DragDropMode.InternalMove)
        self.tree_widget.setHeaderLabels(["No folder selected"])
        layout.addWidget(self.tree_widget)

        self.load_button = QPushButton("Load USB Folder")
        self.save_button = QPushButton("Apply Order")
        layout.addWidget(self.load_button)
        layout.addWidget(self.save_button)

        self.load_button.clicked.connect(self.load_folder)
        self.save_button.clicked.connect(self.apply_order)
        self.save_button.setEnabled(False)
        self.folder_path = None

    def append_folder(self, parent_item: QTreeWidgetItem, folder_path: str):
        for f in sorted(os.listdir(folder_path)):
            path = os.path.join(folder_path, f)
            if os.path.isdir(path):
                dir_item = QTreeWidgetItem(parent_item, [f])
                dir_item.setFlags(Qt.ItemFlag.NoItemFlags)
                pass
                self.append_folder(parent_item=dir_item, folder_path=path)
            elif f.lower().endswith(".mp3"):
                mp3_item = QTreeWidgetItem(parent_item, [f])
                mp3_item.setFlags(Qt.ItemFlag.NoItemFlags)
                pass

    def load_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select USB Folder")
        if folder:
            self.folder_path = folder
            self.tree_widget.setHeaderLabel("Lexicographic order and file structure")
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
            "Re-copy files in set order? Note that this needs the same diskspace on the computer as the current files.",
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        with tempfile.TemporaryDirectory() as temp_dir:
            os.makedirs(temp_dir, exist_ok=True)

            # Copy all files to tmp dir
            top_item: QTreeWidgetItem = self.tree_widget.topLevelItem(0)
            root_path = Path(top_item.text(0))
            shutil.copytree(root_path, temp_dir, dirs_exist_ok=True)

            # Delete all files on drive
            shutil.rmtree(root_path)

            # Go through tree in order and copy files back to drive
            self.copy_folder(item=top_item, base_path=root_path, tmp_dir=temp_dir)

        QMessageBox.information(self, "Done", "Files reordered successfully!")

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MP3Sorter()
    window.show()
    sys.exit(app.exec())
