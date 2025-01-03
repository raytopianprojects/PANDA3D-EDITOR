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
from direct.task.Task import Task
import traceback
from camera import FlyingCamera
from node import NodeEditor
from shader_editor import ShaderEditor


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


class properties:
    def update_node_property(self, coord):
        print(f"update_node_property called with coord: {coord}")
        if coord not in input_boxes:
            print(f"Error: {coord} not found in input_boxes. Current keys: {list(input_boxes.keys())}")
            return
        value = float(input_boxes[coord].text())
        if not selected_node:
            return
        try:
            value = float(input_boxes[coord].text())
        except ValueError:
            return  # Ignore invalid inputs

        if coord[0] == 0:  # Translation
            pos = list(selected_node.getPos())
            pos[coord[1]] = value
            selected_node.setPos(*pos)
        elif coord[0] == 1:  # Rotation
            hpr = list(selected_node.getHpr())
            hpr[coord[1]] = value
            selected_node.setHpr(*hpr)
        elif coord[0] == 2:  # Scale
            scale = list(selected_node.getScale())
            scale[coord[1]] = value
            selected_node.setScale(*scale)


async def update_properties_tick(task):
    await Task.pause(0.1)
    try:
        if selected_node:
            for index in range(3):
                if index == 0:
                    x, y, z = selected_node.get_pos()
                    input_boxes[index, 0].setText(str(x)[:8])
                    input_boxes[index, 1].setText(str(y)[:8])
                    input_boxes[index, 2].setText(str(z)[:8])
                elif index == 1:
                    h, p, r = selected_node.get_hpr()
                    input_boxes[index, 0].setText(str(h)[:8])
                    input_boxes[index, 1].setText(str(p)[:8])
                    input_boxes[index, 2].setText(str(r)[:8])
                else:
                    sx, sy, sz = selected_node.get_scale()
                    input_boxes[index, 0].setText(str(sx)[:8])
                    input_boxes[index, 1].setText(str(sy)[:8])
                    input_boxes[index, 2].setText(str(sz)[:8])
    except Exception as e:
        print(e, "ERROR", traceback.format_exc())
    return task.cont


def on_item_clicked(item, column):
    global selected_node
    node = item.data(0, Qt.UserRole)  # Retrieve the NodePath stored in the item

    if node:
        selected_node = node
        # Update the input boxes with the node's properties
        input_boxes[(0, 0)].setText(str(node.getX()))
        input_boxes[(0, 1)].setText(str(node.getY()))
        input_boxes[(0, 2)].setText(str(node.getZ()))

        input_boxes[(1, 0)].setText(str(node.getH()))
        input_boxes[(1, 1)].setText(str(node.getP()))
        input_boxes[(1, 2)].setText(str(node.getR()))

        input_boxes[(2, 0)].setText(str(node.getScale().x))
        input_boxes[(2, 1)].setText(str(node.getScale().y))
        input_boxes[(2, 2)].setText(str(node.getScale().z))


def new_tab(index):
    if index == 2:
        pandawidget_2.resizeEvent(pandawidget_2)
        shader_editor.hide_nodes()
    else:
        pandaWidget.resizeEvent(pandaWidget)
        shader_editor.show_nodes()

#Toolbar functions
def new_project():
    print("Open file triggered")

def save_file():
    print("Save file triggered")
def load_project():
    print("Custom action triggered")
def close(): #TODO when saving is introduced make a window pop up with save option(save don't save and don't exist(canel))
    """closing the editor"""
    exit()

if __name__ == "__main__":
    world = PandaTest()
    world.add_task(update_properties_tick)
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
    edit_tool_type_menu = QMenu("Edit Tool Type", appw)
    
    # Create an action for the menu
    action = QAction("new project", appw)
    action.triggered.connect(new_project)  # Replace with your function
    edit_tool_type_menu.addAction(action)
    
    action1 = QAction("save project", appw)
    action1.triggered.connect(save_file)  # Replace with your function
    edit_tool_type_menu.addAction(action1)
    
    action2 = QAction("load project", appw)
    action2.triggered.connect(load_project)  # Replace with your function
    edit_tool_type_menu.addAction(action2)

    action3 = QAction("exit", appw)
    action3.triggered.connect(exit)  # Replace with your function
    edit_tool_type_menu.addAction(action3)
    

    # Create a tool button for the menu
    tool_button = QToolButton()
    tool_button.setText("Edit Tool Type")
    tool_button.setMenu(edit_tool_type_menu)
    tool_button.setPopupMode(QToolButton.InstantPopup)
    toolbar.addWidget(tool_button)


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
    input_box = QLineEdit()
    left_panel.layout().addWidget(input_box)
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

    pandawidget_2 = QPanda3DWidget(world)
    viewport_splitter.addWidget(pandawidget_2)

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

    # Show the application window
    appw.show()
    sys.exit(app.exec_())
