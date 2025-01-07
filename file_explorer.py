from PyQt5.Qt import *
import sys


class FileExplorer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_folder = ''
        self.fileModel = QFileSystemModel()
        self.fileModel.setRootPath(sys.argv[0])

        self.v = QVBoxLayout(self)
        self.setLayout(self.v)

        self.up = QPushButton(text="UP")
        self.up.clicked.connect(self.go_up)

        self.listview = QListView()
        self.listview.setModel(self.fileModel)
        self.listview.setDragDropMode(QAbstractItemView.InternalMove)

        self.v.addWidget(self.up)
        self.v.addWidget(self.listview)

        path = QDir().path()
        self.listview.setRootIndex(self.fileModel.index(path))
        self.listview.clicked[QModelIndex].connect(self.on_clicked)

        self.menu = QMenu()

        self.menu.addAction("Item 1")
        self.menu.addAction("Item 2")
        self.menu.addAction("Item 3")
        self.menu.triggered[QAction].connect(self.handle_popup_menu)

    def handle_popup_menu(self, action):
        # Do something when the user clicks an item in the pop-up menu
        print(action.text())

    def on_clicked(self, index):
        item = self.fileModel.itemData(index)
        extension = item[0].split(".")
        if len(extension) > 1:
            ...
        else:
            self.fileModel.setRootPath(self.fileModel.filePath(index))
            self.listview.setRootIndex(self.fileModel.index(self.fileModel.filePath(index)))

    def go_up(self):
        path = QDir(self.fileModel.rootPath())
        path.cdUp()
        path.rootPath()
        self.fileModel.setRootPath(path.path())
        self.listview.setRootIndex(self.fileModel.index(path.path()))

    def contextMenuEvent(self, event):
        # Display the pop-up menu
        self.menu.exec_(event.globalPos())
        event.