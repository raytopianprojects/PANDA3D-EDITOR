from PyQt5.QtCore import Qt, QMimeData, QDataStream
from PyQt5.QtGui import QDrag, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTreeView, QPushButton, QLabel

class DragDropExample(QWidget):
    def __init__(self):
        super().__init__()

        # Layout setup
        self.layout = QVBoxLayout()

        # Create the tree view and model
        self.tree_view = QTreeView()
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Objects'])

        # Populate the tree with example objects
        root_item = QStandardItem('Root')
        item1 = QStandardItem('Object 1')
        item2 = QStandardItem('Object 2')
        root_item.appendRow(item1)
        root_item.appendRow(item2)
        self.model.appendRow(root_item)

        self.tree_view.setModel(self.model)
        self.tree_view.setDragEnabled(True)
        self.tree_view.setAcceptDrops(True)

        # Create the button to drop items onto
        self.drop_button = QPushButton("Drop Object Here")
        self.drop_button.setAcceptDrops(True)

        # Create the label to display dropped content
        self.label = Label(self)

        # Set up the layout
        self.layout.addWidget(self.tree_view)
        self.layout.addWidget(self.drop_button)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        self.setWindowTitle('Drag-and-Drop Example')
        self.setGeometry(300, 300, 400, 300)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def startDrag(self, event):
        selected_item = self.tree_view.selectedIndexes()[0]
        item = self.model.itemFromIndex(selected_item)
        mime_data = QMimeData()
        mime_data.setText(item.text())

        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.exec_(Qt.CopyAction)

class Label(QLabel):
    def __init__(self, parent):
        super(Label, self).__init__(parent)
        self.setAcceptDrops(True)
        self.setText("None")

    def dragEnterEvent(self, event):
        mime = event.mimeData()
        if mime.hasText() or mime.hasFormat('application/x-qabstractitemmodeldatalist'):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        mime = event.mimeData()
        if mime.hasText():
            self.setText(mime.text())
        elif mime.hasFormat('application/x-qabstractitemmodeldatalist'):
            textList = []
            stream = QDataStream(mime.data('application/x-qabstractitemmodeldatalist'))
            while not stream.atEnd():
                row = stream.readInt()
                col = stream.readInt()
                for dataSize in range(stream.readInt()):
                    role, value = stream.readInt(), stream.readQVariant()
                    if role == Qt.DisplayRole:
                        textList.append(value)
            self.setText(', '.join(textList))

if __name__ == '__main__':
    app = QApplication([])
    window = DragDropExample()
    window.show()
    app.exec_()
