import sys
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsItem, QGraphicsRectItem, QGraphicsEllipseItem, \
    QApplication
from PyQt5.QtGui import QBrush, QPen, QPainter, QColor
from PyQt5.QtCore import Qt, QPointF

app = QApplication(sys.argv)


class SequenceView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHint(QPainter.Antialiasing)

    def wheelEvent(self, event):
        """
        Zoom in or out of the view.
        """
        zoomInFactor = 1.25
        zoomOutFactor = 1 / zoomInFactor

        # Save the scene pos
        oldPos = view.mapToScene(event.pos())

        # Zoom
        if event.angleDelta().y() > 0:
            zoomFactor = zoomInFactor
        else:
            zoomFactor = zoomOutFactor
        self.scale(zoomFactor, zoomFactor)

        # Get the new position
        newPos = self.mapToScene(event.pos())

        # Move scene to old position
        delta = newPos - oldPos
        print(delta)
        self.translate(delta.x(), delta.y())

    def mouseMoveEvent(self, event):
        point = view.mapToScene(event.pos()).toPoint()
        # print(point)
        self.translate(point.x(), point.y())
        return super().mouseMoveEvent(event)


class QInterval(QGraphicsItem):
    def __init__(self):
        super().__init__()
        self.keys = []
        self.type = None
        self.other = {}


class QSequence(QGraphicsItem):
    def __init__(self):
        super().__init__()
        self.intervals = []
        self.type = None


class QParallel(QGraphicsItem):
    def __init__(self):
        super().__init__()
        self.sequences = []


def itemChange(change, value):
    if change == QGraphicsItem.ItemPositionChange:
        print(QPointF(int(value.x() * 20) // 20, value.x()))
        return QPointF(int(value.x() * 20) // 20, rect.rect().y())
    return QGraphicsItem.itemChange(rect, change, value)  # Call super


# Defining a scene rect of 400x200, with it's origin at 0,0.
# If we don't set this on creation, we can set it later with .setSceneRect
scene = QGraphicsScene()
brush = QBrush()
brush.setColor(QColor('#999'))
brush.setStyle(Qt.CrossPattern)  # Grid pattern.
scene.setBackgroundBrush(brush)

# Draw a rectangle item, setting the dimensions.
rect = QGraphicsRectItem(0, 0, 200, 50)
rect.itemChange = itemChange

# Set the origin (position) of the rectangle in the scene.
rect.setPos(50, 20)

# Define the brush (fill).
brush = QBrush(Qt.red)
rect.setBrush(brush)

# Define the pen (line)
pen = QPen(Qt.cyan)
pen.setWidth(10)
rect.setPen(pen)

ellipse = QGraphicsEllipseItem(0, 0, 100, 100)
ellipse.setPos(75, 30)

brush = QBrush(Qt.blue)
ellipse.setBrush(brush)

pen = QPen(Qt.green)
pen.setWidth(5)
ellipse.setPen(pen)

# Add the items to the scene. Items are stacked in the order they are added.
scene.addItem(ellipse)
scene.addItem(rect)
rect.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemSendsGeometryChanges)

ellipse.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
view = SequenceView(scene)
#view.mouseMoveEvent = mouseMoveEvent
view.show()
app.exec_()
