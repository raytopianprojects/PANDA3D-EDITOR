from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
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

    def sizeHint(self):
        return QSize(.6 * self.width(), .3 * self.height())

    def on_clicked(self, index):
        print(index)
        item = self.fileModel.itemData(index)
        print(item, item[0].split("."))
        print(item[1].name())
        if item[1].name() != "folder":
            ...
        else:
            print(self.fileModel.filePath(index))
            self.fileModel.setRootPath(self.fileModel.filePath(index))
            self.listview.setRootIndex(self.fileModel.index(self.fileModel.filePath(index)))
            print(self.listview.rootIndex())

    @Slot()
    def go_up(self):
        path = QDir(self.fileModel.rootPath())
        path.cdUp()
        path.rootPath()
        print(path.path())
        self.fileModel.setRootPath(path.path())
        self.listview.setRootIndex(self.fileModel.index(path.path()))
