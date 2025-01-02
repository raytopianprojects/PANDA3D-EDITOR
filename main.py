# -*- coding: utf-8 -*-
"""
Module : buttons_example
Author : Saifeddine ALOUI
Description :
    This is an example of how we can put together a simple Panda3D Word 
    wrapped inside a QMainWindow and add QT pushbuttons that interact with the world.
    This uses the Env_Grid_Maker helper to make a 3D grid in the scene 
"""

from QPanda3D.Panda3DWorld import Panda3DWorld
from QPanda3D.QPanda3DWidget import QPanda3DWidget
from QPanda3D.Helpers.Env_Grid_Maker import *
# import PyQt5 stuff
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
from panda3d.core import *
from direct.interval.LerpInterval import LerpHprInterval
from direct.interval.IntervalGlobal import *
from direct.gui.OnscreenImage import OnscreenImage
from direct.showbase.DirectObject import DirectObject


class CameraControls(DirectObject):
    def __init__(self, world: Panda3DWorld):
        # Todo: Page up and down, mouse wheel for speed, smooth camera rotation
        super().__init__()
        self.world = world
        self.cam = world.cam
        self.mx, self.my, self.x, self.y = 0, 0, 0, 0
        self.move_speed = 1

        # Enable controls
        self.keys = ("w", "s", "q", "e", "a", "d", "mouse2",  "arrow_left", "arrow_up", "arrow_down", "arrow_right",
                     "page_up", "page_down")
        self.input = {}
        for i in self.keys:
            self.input[i] = False
            self.accept(i, self.update, extraArgs=[i, True])
            self.accept(i + "-up", self.update, extraArgs=[i, False])

        # Mouse position
        self.accept("mouse-move", self.mouse_move)

        # Camera speed
        #self.accept("wheel_up", self.mouse_up)
        #self.accept("wheel_down", self.mouse_up)

        # Enable movement
        self.move_task = self.add_task(self.move)

    def mouse_up(self, *args):
        print("uo", args)

    def mouse_move(self, evt: dict):
        self.x, self.y = evt['x'], evt['y']

    def update(self, key, value, *args):
        self.input[key] = value
        
        # Reseat mouse position
        if args and value:
            args = args[0]
            self.x, self.y = args['x'], args['y']
            self.mx, self.my = self.x, self.y

    def move(self, task):
        # Mouse Rotation
        if self.world.mouseWatcherNode.hasMouse():
            if self.input["mouse2"]:
                dx, dy = self.mx - self.x, self.my - self.y

                self.cam.set_p(self.cam, dy * 0.25 * self.move_speed)
                self.cam.set_h(self.cam, dx * 0.25 * self.move_speed)

                self.mx, self.my = self.x, self.y

        # Keyboad Movement
        if self.input["q"] or self.input["page_up"]:
            self.cam.set_z(self.cam, 1 * self.move_speed)

        if self.input["e"] or self.input["page_down"]:
            self.cam.set_z(self.cam, -1 * self.move_speed)

        if self.input["w"] or self.input["arrow_up"]:
            self.cam.set_y(self.cam, 1 * self.move_speed)

        if self.input["s"] or self.input["arrow_down"]:
            self.cam.set_y(self.cam, -1 * self.move_speed)

        if self.input["d"] or self.input["arrow_right"]:
            self.cam.set_x(self.cam, 1 * self.move_speed)

        if self.input["a"] or self.input["arrow_left"]:
            self.cam.set_x(self.cam, -1 * self.move_speed)

        return task.cont


class PandaTest(Panda3DWorld):
    def __init__(self, width=1024, height=768):
        Panda3DWorld.__init__(self, width=width, height=height)
        self.camera_controls = CameraControls(self)
        self.cam.setPos(0, -58, 30)
        self.cam.setHpr(0, -30, 0)
        self.win.setClearColorActive(True)
        self.win.setClearColor(VBase4(0, 0, 0, 1))
        self.cam.node().getDisplayRegion(0).setSort(20)
        # Create a panda        
        self.panda = loader.loadModel("panda")
        self.panda.reparentTo(render)
        self.panda.setPos(0, 0, 0)

        self.grid_maker = Env_Grid_Maker()
        self.grid = self.grid_maker.create()
        self.grid.reparentTo(render)
        self.grid.setLightOff()  # THE GRID SHOULD NOT BE LIT

        # Now create some lights to apply to everything in the scene.

        # Create Ambient Light
        ambientLight = AmbientLight('ambientLight')
        ambientLight.setColor(Vec4(0.1, 0.1, 0.1, 1))
        ambientLightNP = render.attachNewNode(ambientLight)
        render.setLight(ambientLightNP)

        # Directional light 01
        directionalLight = DirectionalLight("directionalLight")
        directionalLight.setColor(Vec4(0.8, 0.1, 0.1, 1))
        directionalLightNP = render.attachNewNode(directionalLight)
        # This light is facing backwards, towards the camera.
        directionalLightNP.setHpr(180, -20, 0)
        directionalLightNP.setPos(10, -100, 10)
        render.setLight(directionalLightNP)

        # If we did not call setLightOff() first, the green light would add to
        # the total set of lights on this object.  Since we do call
        # setLightOff(), we are turning off all the other lights on this
        # object first, and then turning on only the green light.
        self.panda.setLightOff()
        self.jump_up = self.panda.posInterval(1.0, Point3(0, 0, 5), blendType="easeOut")
        self.jump_down = self.panda.posInterval(1.0, Point3(0, 0, 0), blendType="easeIn")
        self.jump_seq = Sequence(self.jump_up, self.jump_down)

        self.jump_up2 = self.panda.posInterval(1.0, Point3(10, 0, 15))
        self.jump_down2 = self.panda.posInterval(1.0, Point3(0, 0, 0))
        self.roll_left = self.panda.hprInterval(1.0, Point3(0, 0, 180))
        self.roll_right = self.panda.hprInterval(1.0, Point3(0, 0, 0))
        self.roll_seq = Sequence(Parallel(self.jump_up2, self.roll_left), Parallel(self.jump_down2, self.roll_right))

    def jump(self):
        self.jump_seq.start()

    def roll(self):
        self.roll_seq.start()


def populate_hierarchy(hierarchy_widget, node, parent_item=None):
    # Create a new item for the current node
    item = QTreeWidgetItem(parent_item or hierarchy_widget, [node.getName()])
    item.setData(0, Qt.UserRole, node)  # Store the NodePath in the item data
    # Recursively add child nodes
    for child in node.getChildren():
        populate_hierarchy(hierarchy_widget, child, item)


selected_node = None


def on_item_clicked(item, column):
    global selected_node
    node = item.data(0, Qt.UserRole)  # Retrieve the NodePath stored in the item
    if node:
        selected_node = node


class NodeEditor(QGraphicsView):
    def __init__(self, parent=None):
        super(NodeEditor, self).__init__(parent)
        self.setScene(QGraphicsScene(self))
        self.setRenderHint(QPainter.Antialiasing)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        self.temp_line = None  # Temporary line for connections
        self.start_connector = None  # Starting connector of the connection
        self.connections = []  # Store the connections between nodes

    def show_context_menu(self, position):
        context_menu = QMenu()

        add_node_action = context_menu.addAction("Add Node")
        add_node_action.triggered.connect(lambda: self.add_node(position))

        add_add_node_action = context_menu.addAction("Add 'Add' Node")
        add_add_node_action.triggered.connect(lambda: self.add_specific_node(position, "Add"))

        add_action_node_action = context_menu.addAction("Add 'Action' Node")
        add_action_node_action.triggered.connect(lambda: self.add_specific_node(position, "Action"))

        context_menu.exec_(self.mapToGlobal(position))

    def add_node(self, position):
        self.add_specific_node(position, "Default")

    def add_specific_node(self, position, node_type):
        scene_position = self.mapToScene(position)
        node = QGraphicsRectItem(0, 0, 120, 60)
        node.setPos(scene_position)
        node.setBrush(QBrush(Qt.lightGray))
        node.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.scene().addItem(node)

        text = QGraphicsTextItem(node_type, node)
        text.setDefaultTextColor(Qt.black)
        text.setPos(10, 10)

        # Add input connector
        input_connector = QGraphicsEllipseItem(-10, 20, 10, 10, node)
        input_connector.setBrush(QBrush(Qt.darkGray))
        input_connector.setPen(QPen(Qt.NoPen))
        input_connector.setData(0, "input")
        input_connector.setFlag(QGraphicsItem.ItemIsSelectable)

        # Add output connector
        output_connector = QGraphicsEllipseItem(120, 20, 10, 10, node)
        output_connector.setBrush(QBrush(Qt.darkGray))
        output_connector.setPen(QPen(Qt.NoPen))
        output_connector.setData(0, "output")
        output_connector.setFlag(QGraphicsItem.ItemIsSelectable)

    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        if isinstance(item, QGraphicsEllipseItem):  # Connector clicked
            connector_type = item.data(0)
            if connector_type == "output":  # Start a connection
                self.start_connector = item
                scene_pos = item.sceneBoundingRect().center()
                self.temp_line = QGraphicsLineItem(QLineF(scene_pos, scene_pos))
                self.temp_line.setPen(QPen(Qt.red, 2))
                self.scene().addItem(self.temp_line)
        super(NodeEditor, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.temp_line:
            line = self.temp_line.line()
            line.setP2(self.mapToScene(event.pos()))
            self.temp_line.setLine(line)
        super(NodeEditor, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.temp_line:
            end_item = self.itemAt(event.pos())
            if isinstance(end_item, QGraphicsEllipseItem):
                end_type = end_item.data(0)
                if self.start_connector and end_type == "input" and self.start_connector.data(0) == "output":
                    # Complete the connection
                    start_pos = self.start_connector.sceneBoundingRect().center()
                    end_pos = end_item.sceneBoundingRect().center()

                    # Check if the connection already exists
                    if not self.is_connection_exists(self.start_connector, end_item):
                        connection_line = QGraphicsLineItem(QLineF(start_pos, end_pos))
                        connection_line.setPen(QPen(Qt.blue, 2))
                        self.scene().addItem(connection_line)
                        self.connections.append((self.start_connector, end_item, connection_line))
                    else:
                        print("Connection already exists.")
                else:
                    print("Invalid connection attempt.")
            else:
                print("Connection failed: Not a valid connector.")

            # Clean up temporary line
            self.scene().removeItem(self.temp_line)
            self.temp_line = None
            self.start_connector = None
        super(NodeEditor, self).mouseReleaseEvent(event)

    def is_connection_exists(self, start_connector, end_connector):
        """Check if the connection already exists between the start and end connectors."""
        for conn in self.connections:
            if conn[0] == start_connector and conn[1] == end_connector:
                return True
        return False

    def delete_connection(self, connection_line):
        """Remove a connection."""
        self.scene().removeItem(connection_line)
        self.connections = [conn for conn in self.connections if conn[2] != connection_line]


if __name__ == "__main__":
    world = PandaTest()
    app = QApplication(sys.argv)
    appw = QMainWindow()
    appw.setGeometry(50, 50, 1024, 768)

    # Main Widget
    main_widget = QWidget()
    main_layout = QVBoxLayout(main_widget)  # Use vertical layout for tabs

    # Tabs
    tab_widget = QTabWidget()
    main_layout.addWidget(tab_widget)

    # Node Editor Tab
    node_editor_tab = QWidget()
    node_editor_layout = QVBoxLayout(node_editor_tab)
    node_editor = NodeEditor()
    node_editor_layout.addWidget(node_editor)
    tab_widget.addTab(node_editor_tab, "Node Editor")

    # 3D Viewport Tab
    viewport_tab = QWidget()
    viewport_layout = QVBoxLayout(viewport_tab)

    # Splitter for left panel, viewport, and right panel
    viewport_splitter = QSplitter(Qt.Horizontal)
    viewport_layout.addWidget(viewport_splitter)

    # Empty Left Panel
    left_panel = QWidget()
    left_panel.setLayout(QVBoxLayout())
    left_label = QLabel("Left Panel (Empty)")
    left_panel.layout().addWidget(left_label)
    viewport_splitter.addWidget(left_panel)

    # Splitter for 3D Viewport and File System
    viewport_inner_splitter = QSplitter(Qt.Vertical)
    viewport_splitter.addWidget(viewport_inner_splitter)

    # 3D Viewport
    pandaWidget = QPanda3DWidget(world)
    viewport_inner_splitter.addWidget(pandaWidget)

    # Drag-and-Drop File System
    file_system_panel = QTreeWidget()
    file_system_panel.setHeaderLabel("File System")
    viewport_inner_splitter.addWidget(file_system_panel)

    # Hierarchy Viewer (Right Panel)
    right_panel = QWidget()
    right_panel.setLayout(QVBoxLayout())
    hierarchy_tree = QTreeWidget()
    hierarchy_tree.setHeaderLabel("Scene Hierarchy")
    right_panel.layout().addWidget(hierarchy_tree)

    # Add example hierarchy nodes
    root_item = QTreeWidgetItem(hierarchy_tree, ["Root Node"])
    panda_item = QTreeWidgetItem(root_item, ["Panda"])
    grid_item = QTreeWidgetItem(root_item, ["Grid"])
    root_item.setExpanded(True)  # Expand the root node

    viewport_splitter.addWidget(right_panel)

    # Add the 3D Viewport Tab to Tabs
    tab_widget.addTab(viewport_tab, "3D Viewport")

    # Set the main widget as the central widget
    appw.setCentralWidget(main_widget)

    # Populate the hierarchy tree with actual scene data
    populate_hierarchy(hierarchy_tree, render)  # This will populate the hierarchy panel

    hierarchy_tree.itemClicked.connect(lambda item, column: on_item_clicked(item, column))

    # Show the application window
    appw.show()
    sys.exit(app.exec_())
