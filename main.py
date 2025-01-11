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
from camera import FlyingCamera
from node import NodeEditor
from shader_editor import ShaderEditor
from file_explorer import FileExplorer
import terrainEditor
import importlib
import os
import entity_editor
import node_system
from PyQt5.QtCore import pyqtSignal
import scirpt_inspector
import qdarktheme


class PandaTest(Panda3DWorld):
    def __init__(self, width=1024, height=768):
        Panda3DWorld.__init__(self, width=width, height=height)
        self.camera_controls = FlyingCamera(self)
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
        
        self.selected_node = None

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

    def make_terrain(self):
        global hierarchy_tree
        
        self.terrain_generate = terrainEditor.TerrainPainterApp(world, pandaWidget)

        hierarchy_tree.clear()
        
        populate_hierarchy(hierarchy_tree, render)

        selected_node = self.terrain_generate.terrain_node
    def reset_render(self):
        """
        Resets the render node to a new NodePath.
        """
        global render  # Make the new NodePath the global render
        old_render = render

        # Create a new root node
        render = NodePath("render")
        base.render = render  # Update ShowBase's render reference

        # Reparent global elements like the camera
        base.camera.reparent_to(render)

        # Detach the old render node (optional)
        old_render.detach_node()



def populate_hierarchy(hierarchy_widget, node, parent_item=None):
    
    # Create a new item for the current node
    item = QTreeWidgetItem(parent_item or hierarchy_widget, [node.getName()])
    item.setData(0, Qt.UserRole, node)  # Store the NodePath in the item data
    # Recursively add child nodes
    for child in node.getChildren():
        populate_hierarchy(hierarchy_widget, child, item)



class properties:
    def __init__():
        pass
    def update_node_property(self, coord):
        print(f"update_node_property called with coord: {coord}")
        if coord not in input_boxes:
            print(f"Error: {coord} not found in input_boxes. Current keys: {list(input_boxes.keys())}")
            return
        value = float(input_boxes[coord].text())
        if not world.selected_node:
            return
        try:
            value = float(input_boxes[coord].text())
        except ValueError:
            return  # Ignore invalid inputs

        if coord[0] == 0:  # Translation
            pos = list(world.selected_node.getPos())
            pos[coord[1]] = value
            world.selected_node.setPos(*pos)
        elif coord[0] == 1:  # Rotation
            hpr = list(world.selected_node.getHpr())
            hpr[coord[1]] = value
            world.selected_node.setHpr(*hpr)
        elif coord[0] == 2:  # Scale
            scale = list(world.selected_node.getScale())
            scale[coord[1]] = value
            world.selected_node.setScale(*scale)

def on_item_clicked(item, column):
    #global selected_node
    node = item.data(0, Qt.UserRole)  # Retrieve the NodePath stored in the item

    if node:
        world.selected_node = node
        # Update input boxes with node's properties
        input_boxes[(0, 0)].setText(str(node.getX()))
        input_boxes[(0, 1)].setText(str(node.getY()))
        input_boxes[(0, 2)].setText(str(node.getZ()))
        input_boxes[(1, 0)].setText(str(node.getH()))
        input_boxes[(1, 1)].setText(str(node.getP()))
        input_boxes[(1, 2)].setText(str(node.getR()))
        input_boxes[(2, 0)].setText(str(node.getScale().x))
        input_boxes[(2, 1)].setText(str(node.getScale().y))
        input_boxes[(2, 2)].setText(str(node.getScale().z))

        # Clear existing widgets in the ScriptInspector
        for i in reversed(range(inspector.scroll_layout.count())):
            widget = inspector.scroll_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Load scripts associated with the node
        if node in inspector.scripts:
            for path, script_instance in inspector.scripts[node].items():
                inspector.set_script(path, node)
        else:
            inspector.scripts[node] = {}  # Initialize script storage for the node
    else:
        print("No node selected.")

        

def new_tab(index):
    if index == 2:
        shader_editor.hide_nodes()
    else:
        shader_editor.show_nodes()

class Node:
    def __init__(self, ref, path):
        self.ref = ref
        self.paths = [path]

    def update(self, path):
        if path not in self.paths:
            self.paths.append(path)


#Toolbar functions
def new_project():
    print("Open file triggered")


def save_file():
    world.messenger.send("save")
    print("Save file triggered")


def load_project():
    file = QFileDialog.getOpenFileName(None, "Select Project Directory", "", ".toml")

    
    
def close(): #TODO when saving is introduced make a window pop up with save option(save don't save and don't exist(canel))
    """closing the editor"""
    exit()


#-------------------
#Terrain Generation
terrain_generate = None


def gen_terrain():
    global world
    global terrain_generate
    world.make_terrain()


#-------------------

if __name__ == "__main__":
    world = PandaTest()
    app = QApplication(sys.argv)
    appw = QMainWindow()
    appw.setGeometry(50, 50, 1024, 768)

    # Main Widget
    main_widget = QWidget()
    main_layout = QVBoxLayout(main_widget)  # Use vertical layout for tabs

    # Create the toolbar
    toolbar = QToolBar("Main Toolbar")
    appw.addToolBar(toolbar)

    # Create the menu
    edit_tool_type_menu = QMenu("File", appw)
    terrain_3d = QMenu("Terrain 3D", appw)

    # Create an action for the Edit menu
    action = QAction("New Project", appw)
    action.triggered.connect(new_project)
    edit_tool_type_menu.addAction(action)

    action1 = QAction("Save Project", appw)
    action1.triggered.connect(save_file)
    action1.setShortcut(QKeySequence("Ctrl+S"))
    edit_tool_type_menu.addAction(action1)

    action2 = QAction("Load Project", appw)
    action2.triggered.connect(load_project)
    edit_tool_type_menu.addAction(action2)

    action3 = QAction("Exit", appw)
    action3.triggered.connect(exit)
    edit_tool_type_menu.addAction(action3)

    #--------------------------
    #actions for Terrain3D menu
    action = QAction("Generate Terrain", appw)
    action.triggered.connect(gen_terrain)
    terrain_3d.addAction(action)
    #--------------------------

    # Create a tool button for the menu
    tool_button = QToolButton()
    tool_button.setText("File")
    tool_button.setMenu(edit_tool_type_menu)
    tool_button.setPopupMode(QToolButton.InstantPopup)
    toolbar.addWidget(tool_button)

    # Create a tool button for the menu
    tool_button1 = QToolButton()
    tool_button1.setText("Terrain 3D")
    tool_button1.setMenu(terrain_3d)
    tool_button1.setPopupMode(QToolButton.InstantPopup)
    toolbar.addWidget(tool_button1)

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
    left_panel_layout = QVBoxLayout()
    left_panel.setLayout(left_panel_layout)

    # Example node and script
    class DummyNode:
        def __init__(self, name):
            self.name = name
            self.tags = {}

        def get_name(self):
            return self.name

        def set_python_tag(self, key, value):
            self.tags[key] = value

        def get_python_tag(self, key):
            return self.tags.get(key)


    node = DummyNode("Cube")

    inspector = scirpt_inspector.ScriptInspector(world, entity_editor, node, left_panel)
    #inspector.show()
    left_panel_layout.addWidget(inspector)
    viewport_splitter.addWidget(left_panel)

    # Splitter for 3D Viewport and File System
    viewport_inner_splitter = QSplitter(Qt.Vertical)
    viewport_splitter.addWidget(viewport_inner_splitter)

    # 3D Viewport
    pandaWidget = QPanda3DWidget(world)
    viewport_inner_splitter.addWidget(pandaWidget)

    # Drag-and-Drop File System
    file_system_panel = FileExplorer()
    #file_system_panel.setHeaderLabel("File System")
    viewport_inner_splitter.addWidget(file_system_panel)

    # Hierarchy Viewer (Right Panel)
    right_panel = QWidget()
    right_panel.setLayout(QVBoxLayout())
    hierarchy_tree = QTreeWidget()
    hierarchy_tree.setHeaderLabel("Scene Hierarchy")
    hierarchy_tree.setDragEnabled(True)
    hierarchy_tree.setAcceptDrops(True)
    right_panel.layout().addWidget(hierarchy_tree)
    # Create a QWidget to hold the grid layout
    grid_widget = QWidget()
    # Create a grid layout for the input boxes (3x3)
    grid_layout = QGridLayout(grid_widget)

    # Create 3x3 QLineEdit input boxes
    input_boxes = {}
    for i in range(3):
        for j in range(3):
            if i == 0 and j == 0:
                label = QLabel("transforms x y z: ")
            if i == 1 and j == 0:
                label = QLabel("rotation x y z: ")
            if i == 2 and j == 0:
                label = QLabel("scale x y z: ")
            input_box = QLineEdit(grid_widget)
            input_boxes[(i, j)] = input_box
            grid_layout.addWidget(label, i * 2, j)  # Add label in a separate row
            grid_layout.addWidget(input_box, i * 2 + 1, j)  # Add input box below the label

    # Add the grid widget to the main layout
    right_panel.layout().addWidget(grid_widget)

    viewport_splitter.addWidget(right_panel)

    # Add the 3D Viewport Tab to Tabs
    tab_widget.addTab(viewport_tab, "3D Viewport")

    # Add Shader Editor
    viewport_tab = QWidget()
    viewport_layout = QVBoxLayout(viewport_tab)

    # Splitter for left panel, viewport, and right panel
    viewport_splitter = QSplitter(Qt.Horizontal)
    viewport_layout.addWidget(viewport_splitter)

    panda_widget_2 = QPanda3DWidget(world)
    viewport_splitter.addWidget(panda_widget_2)

    shader_editor = ShaderEditor()
    viewport_splitter.addWidget(shader_editor)

    tab_widget.addTab(viewport_tab, "Shader Editor")
    tab_widget.currentChanged.connect(new_tab)

    # Set the main widget as the central widget
    appw.setCentralWidget(main_widget)

    # Populate the hierarchy tree with actual scene data
    populate_hierarchy(hierarchy_tree, render)  # This will populate the hierarchy panel

    hierarchy_tree.itemClicked.connect(lambda item, column: on_item_clicked(item, column))

    prop = properties
    for coord, box in input_boxes.items():
        # Use a default argument to capture the value of `coord` correctly
        box.textChanged.connect(lambda box=box, coord=coord: prop.update_node_property(box, coord))

    # Set the background color of the widget to gray
    qdarktheme.setup_theme()
    #apply_stylesheet(appw, theme="light_blue.xml")

    # Show the application window
    appw.show()
    sys.exit(app.exec_())