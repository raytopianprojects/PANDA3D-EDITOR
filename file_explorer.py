from PyQt5.Qt import *
import sys


class FileExplorer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_folder = QDir.currentPath()  # Set initial folder to current working directory
        self.fileModel = QFileSystemModel()
        self.fileModel.setRootPath(self.current_folder)  # Set the root path for the model

        # Set up layout and widgets
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.up_button = QPushButton("UP")
        self.up_button.clicked.connect(self.go_up)

        self.listview = QListView()
        self.listview.setModel(self.fileModel)
        self.listview.setRootIndex(self.fileModel.index(self.current_folder))
        self.listview.setDragEnabled(True)  # Enable dragging

        # Add widgets to layout
        self.layout.addWidget(self.up_button)
        self.layout.addWidget(self.listview)

        # Connect signals
        self.listview.clicked.connect(self.on_item_clicked)

    def startDrag(self, supportedActions):
        """
        Initiates a drag action with the selected file's path.
        """
        index = self.listview.currentIndex()
        if index.isValid():
            file_path = self.fileModel.filePath(index)  # Get the file path
            mime_data = QMimeData()
            mime_data.setUrls([QUrl.fromLocalFile(file_path)])  # Add file path to MIME data
            drag = QDrag(self)
            drag.setMimeData(mime_data)
            drag.exec_(supportedActions)

    def on_item_clicked(self, index):
        """
        Handles item clicks in the list view.
        """
        file_path = self.fileModel.filePath(index)  # Get the full file path
        print(f"Clicked: {file_path}")
        if self.fileModel.isDir(index):  # Check if the item is a directory
            self.current_folder = file_path
            self.listview.setRootIndex(self.fileModel.index(self.current_folder))
        else:
            print(f"Selected file: {file_path}")

    def go_up(self):
        """
        Navigates to the parent directory.
        """
        path = QDir(self.current_folder)
        if path.cdUp():
            self.current_folder = path.path()
            print(f"Navigated up to: {self.current_folder}")
            self.listview.setRootIndex(self.fileModel.index(self.current_folder))
