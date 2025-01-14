import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from direct.interval.IntervalGlobal import *


app = QApplication(sys.argv)

class QProperity(QWidget):
    def __init__(self, name, widget):
        super().__init__()
        self.l = QHBoxLayout()
        self.setLayout(self.l)
        self.name = QLabel(f"{name}:")
        self.widget = widget
        self.l.addWidget(self.name)
        self.l.addWidget(self.widget)


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

class QLerp(QInterval):
    i = LerpPosInterval(nodePath,
                        duration,
                        pos,
                        startPos=None,
                        other=None,
                        blendType='noBlend',
                        bakeInStart=1,
                        fluid=0,
                        name=None)
    LerpPosInterval(nodePath, duration, pos, startPos)
    LerpHprInterval(nodePath, duration, hpr, startHpr)
    LerpQuatInterval(nodePath, duration, quat, startHpr, startQuat)
    LerpScaleInterval(nodePath, duration, scale, startScale)
    LerpShearInterval(nodePath, duration, shear, startShear)
    LerpColorInterval(nodePath, duration, color, startColor)
    LerpColorScaleInterval(nodePath, duration, colorScale, startColorScale)
    LerpPosHprInterval(nodePath, duration, pos, hpr, startPos, startHpr)
    LerpPosQuatInterval(nodePath, duration, pos, quat, startPos, startQuat)
    LerpHprScaleInterval(nodePath, duration, hpr, scale, startHpr, startScale)
    LerpQuatScaleInterval(nodePath, duration, quat, scale, startQuat, startScale)
    LerpPosHprScaleInterval(nodePath, duration, pos, hpr, scale, startPos, startHpr, startScale)
    LerpPosQuatScaleInterval(nodePath, duration, pos, quat, scale, startPos, startQuat, startScale)
    LerpPosHprScaleShearInterval(nodePath, duration, pos, hpr, scale, shear, startPos, startHpr, startScale, startShear)
    LerpPosQuatScaleShearInterval(nodePath, duration, pos, quat, scale, shear, startPos, startQuat, startScale,
                                  startShear)
    i = LerpFunc(myFunction,
                 fromData=0,
                 toData=1,
                 duration=0.0,
                 blendType='noBlend',
                 extraArgs=[],
                 name=None)
    Func(myFunction, arg1, arg2)
    actorInterval(
        "Animation Name",
        loop= < 0 or 1 >,
    constrainedLoop = < 0 or 1 >,
    duration = D,
    startTime = T1,
    endTime = T2,
    startFrame = N1,
    endFrame = N2,
    playRate = R,
    partName = PN,
    lodName = LN,
    )

class QSound(QInterval):
    def __init__(self, mySound, loop, myDuration, volume, myStartTime):
        super().__init__()
        self.mySound, self.loop, self.myDuration, self.volume, self.myStartTime = mySound, loop, myDuration, volume, myStartTime
        self.i = SoundInterval(
        mySound,
        loop = loop,
        duration = myDuration,
        volume = self.volume,
        startTime = myStartTime
    )
        self.l = QVBoxLayout()
        self.w = QWidget()
        self.w.setLayout(self.l)

        self.l.addWidget(QProperity("Sound", QLabel("sound")))
        self.l.addWidget(QProperity("Loop", QCheckBox()))
        self.l.addWidget(QProperity("Duration", QDoubleSpinBox()))
        self.l.addWidget(QProperity("Volume", QDoubleSpinBox()))
        self.l.addWidget(QProperity("Start Time", QDoubleSpinBox()))

    def play(self):
        self.stop()
        self.i = SoundInterval(
            self.mySound,
            loop=self.loop,
            duration=self.myDuration,
            volume=self.volume,
            startTime=self.myStartTime
        )
        self.i.start()

    def stop(self):
        self.i.pause()
        self.i = None



class QSequence(QGraphicsItem):
    def __init__(self):
        super().__init__()
        self.intervals = []
        self.type = None


class QParallel(QGraphicsItem):
    def __init__(self):
        super().__init__()
        self.sequences = []

class Marker():
    ...

class Buttons(QWidget):
    def __init__(self):
        self.hbox = QHorizontalBox()
        self.layout.set(self.hbox)

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
