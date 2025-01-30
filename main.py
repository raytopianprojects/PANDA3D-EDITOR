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
import ui_editor
from camera import FlyingCamera
import node
from shader_editor import ShaderEditor
from file_explorer import FileExplorer
import terrainEditor
import importlib
import os
import entity_editor
import node_system
from PyQt5.QtCore import pyqtSignal
from scirpt_inspector import ScriptInspector
import scirpt_inspector
import qdarktheme
from direct.gui.DirectGui import DirectButton, DirectLabel, DirectFrame
from direct.gui import DirectGuiGlobals as DGG
import input_manager


class PandaTest(Panda3DWorld):
    def __init__(self, width=1024, height=768, script_inspector=None):
        Panda3DWorld.__init__(self, width=width, height=height)
        
        self.setupRender2d()
        
        
        

        
        self.canvas = NodePath("UI-Canvas")
        self.canvas.reparent_to(self.render2d)
        
        self.canvas.set_python_tag("isCanvas", True)
        self.canvas.set_python_tag("isLabel", False)
        
        self.canvas.setPos(0, 0, 255)
        # Set up the orthographic camera
        self.ortho_cam = self.makeCamera(self.win)
        lens = OrthographicLens()
        lens.setFilmSize(20, 15)  # Adjust the size as needed
        self.ortho_cam.node().setLens(lens)
        self.ortho_cam.reparentTo(self.render)
        self.ortho_cam.setPos(0, 0, 0)
        
        self.script_inspector = script_inspector
        self.loader = self.loader
        self.camera_controls = FlyingCamera(self)
        self.cam.setPos(0, -58, 30)
        self.cam.setHpr(0, -30, 0)
        self.win.setClearColorActive(True)
        self.win.setClearColor(VBase4(0, 0, 0, 1))
        self.cam.node().getDisplayRegion(0).setSort(20)
        # Create a panda        
        self.panda = loader.loadModel("panda")
        self.panda.set_python_tag("model_path", "panda")
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
    
    def recreate_widget(self, text, frameColor, text_fg, scale, pos, parent):
        return uiEditor_inst.label(text, scale, pos, parent, frameColor, text_fg)
    def recreate_button(self, text, frameColor, text_fg, scale, pos, parent):
        return uiEditor_inst.button(text, scale, pos, parent, frameColor, text_fg)
    def make_hierarchy(self):
        self.hierarchy_tree = QTreeWidget()
        self.hierarchy_tree1 = QTreeWidget()

    def jump(self):
        self.jump_seq.start()

    def roll(self):
        self.roll_seq.start()

    def add_model(self, model):


        self.hierarchy_tree.clear()
        self.populate_hierarchy(self.hierarchy_tree, render)
        self.hierarchy_tree1.clear()
        self.populate_hierarchy(self.hierarchy_tree1, self.render2d)
        world.selected_node = model

    def make_terrain(self):


        self.hierarchy_tree.clear()
        self.hierarchy_tree1.clear()

        self.terrain_generate = terrainEditor.TerrainPainterApp(world, pandaWidget)

        world.selected_node = self.terrain_generate.terrain_node
        
        self.populate_hierarchy(self.hierarchy_tree, render)
        self.populate_hierarchy(self.hierarchy_tree1, self.render2d)

        selected_node = self.terrain_generate.terrain_node
    #def ui_editor_script_to_canvas(self):
    #    inspector.set_script(os.path.relpath("D:/000PANDA3d-EDITOR/PANDA3D-EDITOR/ui_editor_properties.py"), self.canvas, inspector.prop)
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

        self.camera_controls = FlyingCamera(self)
        self.cam.setPos(0, -58, 30)
        self.cam.setHpr(0, -30, 0)
        self.win.setClearColorActive(True)
        self.win.setClearColor(VBase4(0, 0, 0, 1))
        self.cam.node().getDisplayRegion(0).setSort(20)

        self.hierarchy_tree.clear()
        self.hierarchy_tree1.clear()
        
        self.populate_hierarchy(self.hierarchy_tree, render)
        self.populate_hierarchy(self.hierarchy_tree1, self.render2d)
    #TODO make each object from toml load up with a function that runs on load


    def populate_hierarchy(self, hierarchy_widget, node, parent_item=None):

        # Create a new item for the current node
        item = QTreeWidgetItem(parent_item or hierarchy_widget, [node.getName()])
        item.setData(0, Qt.UserRole, node)  # Store the NodePath in the item data
        # Recursively add child nodes
        for child in node.getChildren():
            self.populate_hierarchy(hierarchy_widget, child, item)



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
class properties_ui_editor:
    def __init__():
        pass
    def update_node_property(self, coord):
        print(f"update_node_property called with coord: {coord}")
        if coord not in uiEditor_inst.input_boxes:
            print(f"Error: {coord} not found in input_boxes. Current keys: {list(uiEditor_inst.input_boxes.keys())}")
            return
        value = float(uiEditor_inst.input_boxes[coord].text())
        if not world.selected_node:
            return
        try:
            value = float(uiEditor_inst.input_boxes[coord].text())
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

        
        inspector.recreate_property_box_for_node(node)
        
        ## Load scripts associated with the node
        #if node in inspector.scripts:
        #    for path, script_instance in inspector.scripts[node].items():
        #        if inspector.prop:
        #            
        #            inspector.set_script(path, node, inspector.prop)
        #else:
        #    inspector.scripts = {}  # Initialize script storage for the node
    else:
        print("No node selected.")
def on_item_clicked1(item, column):
    #global selected_node
    node = item.data(0, Qt.UserRole)  # Retrieve the NodePath stored in the item

    if node:
        world.selected_node = node
        # Update input boxes with node's properties
        uiEditor_inst.input_boxes[(0, 0)].setText(str(node.getX()))
        uiEditor_inst.input_boxes[(0, 1)].setText(str(node.getY()))
        uiEditor_inst.input_boxes[(0, 2)].setText(str(node.getZ()))
        uiEditor_inst.input_boxes[(1, 0)].setText(str(node.getH()))
        uiEditor_inst.input_boxes[(1, 1)].setText(str(node.getP()))
        uiEditor_inst.input_boxes[(1, 2)].setText(str(node.getR()))
        uiEditor_inst.input_boxes[(2, 0)].setText(str(node.getScale().x))
        uiEditor_inst.input_boxes[(2, 1)].setText(str(node.getScale().y))
        uiEditor_inst.input_boxes[(2, 2)].setText(str(node.getScale().z))

        # Clear existing widgets in the ScriptInspector
        for i in reversed(range(uiEditor_inst.inspector_ui_tab.scroll_layout.count())):
            widget = uiEditor_inst.inspector_ui_tab.scroll_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                
        
        uiEditor_inst.inspector_ui_tab.recreate_property_box_for_node(node)

        # Load scripts associated with the node
        #if node in inspector.scripts:
        #    for path, script_instance in inspector.scripts[node].items():
        #        if inspector.prop:
        #            
        #            inspector.set_script(path, node, inspector.prop)
        #else:
        #    inspector.scripts = {}  # Initialize script storage for the node
        uiEditor_inst.inspector_ui_tab.set_ui_editor(node, node.get_python_tag("isCanvas"), node.get_python_tag("isLabel"), instance=uiEditor_inst, w=world)
    else:
        print("No node selected.")


def new_tab(index):
    if index == 1:
        shader_editor.show_nodes()
        pandaWidget.resizeEvent(pandaWidget)
        pandaWidget1.resizeEvent(pandaWidget1)
        world.cam.setPos(0, -55, 30)
        world.cam.lookAt(0, 0, 0)
    elif index == 2:
        shader_editor.hide_nodes()
        panda_widget_2.resizeEvent(panda_widget_2)
        world.cam.setPos(0, -55, 30)
        world.cam.lookAt(0, 0, 0)

    elif index == 3:
        print("!")
        shader_editor.show_nodes()
        pandaWidget.resizeEvent(pandaWidget)
        pandaWidget1.resizeEvent(pandaWidget1)
        panda_widget_2.resizeEvent(panda_widget_2)
        world.cam.setPos(0,-3, 255)
        world.cam.lookAt(world.canvas)
class Node:
    def __init__(self, ref, path):
        self.ref = ref
        self.paths = [path]

    def update(self, path):
        if path not in self.paths:
            self.paths.append(path)

class Save_ui(QInputDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Second Window")
        self.setGeometry(150, 150, 300, 200)
        
        # Layout for the second window
        layout = QVBoxLayout()
        
        # Input field
        self.input_field = QLineEdit(self)
        self.input_field.setText("untitled.ui")
        self.input_field.setPlaceholderText("untitled.ui")
        layout.addWidget(self.input_field)
        
        # Button to process the input
        self.submit_button = QPushButton("Save", self)
        self.submit_button.clicked.connect(self.process_input)
        layout.addWidget(self.submit_button)
        
        self.setLayout(layout)
    
    def process_input(self):
        # Get the input text and display it in the label
        user_input = self.input_field.text()
        ent_editor = entity_editor.Save()
        ent_editor.save_scene_ui_to_toml(world.render2d, "./saves/ui/", user_input)
        
        

class Load_ui(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Second Window")
        self.setGeometry(150, 150, 300, 200)

        self.mesh_select = QComboBox(self)
        self.mesh_select.currentIndexChanged.connect(self.set_selected)
        
        matching_files = []
        for root, _, files in os.walk("./"):#FIXME this will be the project folder
            for file in files:
                if file.endswith(".ui"):  # Check file extension
                    matching_files.append(os.path.join(root, file))
                    self.mesh_select.addItem(file)
        
        
        
        # Layout for the second window
        layout = QVBoxLayout()

        
        # Button to process the input
        self.submit_button = QPushButton("Save", self)
        self.submit_button.clicked.connect(self.process_input)
        layout.addWidget(self.submit_button)
        
        self.setLayout(layout)
        
    def set_selected(self):
        self.selected_text = self.mesh_select.currentText()

    
    def process_input(self):
        global world
        # Get the input text and display it in the label
        #user_input = self.input_field.text()
        entity_editor.Load(world).load_ui_from_folder_toml(self.selected_text, world.render2d)
        
#Toolbar functions
def new_project():
    print("Open file triggered")


def save_file():
    world.messenger.send("save")
    print("Save file triggered")


save_ui_instance = None
load_ui_instance = None

def save_ui_func():
    global save_ui_instance
    save_ui_instance = Save_ui()
    save_ui_instance.show()
    
def load_ui_func():
    global load_ui_instance
    load_ui_instance = Load_ui()
    load_ui_instance.show()


import toml

def load_project(world):
    """
    Load a project and reset the scene.
    """
    # Prompt the user to select a TOML file
    file_path = QFileDialog.getExistingDirectory(None, "Select Project File", "")
    
    if not file_path:
        print("No file selected.")
        return

    # Reset the current scene
    world.reset_render()  # Ensure `world` is valid and has this method
    

    # Parse the TOML file and reconstruct the scene
    try:
        en = entity_editor
        data = en.Load(world).load_project_from_folder_toml(file_path, world.render)
        
        # Example: Debug print project data
        print(f"Loaded Project Data: {data}")

        # Construct the scene using project_data...
        # Add logic here to build the scene
    except Exception as e:
        print(f"Error loading project: {e}")

    # Iterate through entities


    
    
def close(): #TODO when saving is introduced make a window pop up with save option(save don't save and don't exist(canel))
    """closing the editor"""
    exit()

network_manager = input_manager.NetworkManager()
input_manager_c = input_manager.InputManager(network_manager)
input_settings = None
def show_input_manager():
    global input_settings
    input_settings = input_manager.InputSettingsWindow(input_manager_c)
    input_settings.show()

def play_mode():
    import Preview_build
    app = Preview_build.GamePreviewApp()
    app.run()

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

    action3 = QAction("play game", appw)
    action3.triggered.connect(play_mode)
    action3.setShortcut(QKeySequence("F5"))
    edit_tool_type_menu.addAction(action3)
    
    actionI = QAction("input manager", appw)
    actionI.triggered.connect(show_input_manager)
    edit_tool_type_menu.addAction(actionI)
    
    action2 = QAction("Load Project", appw)
    action2.triggered.connect(lambda: load_project(world))
    edit_tool_type_menu.addAction(action2)

    save_ui = QAction("save ui", appw)
    save_ui.triggered.connect(lambda: save_ui_func())
    edit_tool_type_menu.addAction(save_ui)
    
    load_ui = QAction("load ui", appw)
    load_ui.triggered.connect(lambda: load_ui_func())
    edit_tool_type_menu.addAction(load_ui)
    
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
    node_editor = node.MainWindow()
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

    inspector = scirpt_inspector.ScriptInspector(world, entity_editor, node, left_panel)
    world.script_inspector = inspector

    node = DummyNode("Cube")

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
    
    world.make_hierarchy()
    
    world.hierarchy_tree.setHeaderLabel("Scene Hierarchy")
    world.hierarchy_tree.setDragEnabled(True)
    world.hierarchy_tree.setAcceptDrops(True)
    right_panel.layout().addWidget(world.hierarchy_tree)
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

    # Add UI Editor
    viewport_tab1 = QWidget()
    viewport_layout1 = QVBoxLayout(viewport_tab1)
    
    # Splitter for left panel, viewport, and right panel
    viewport_splitter = QSplitter(Qt.Horizontal)
    viewport_layout.addWidget(viewport_splitter)

    viewport_splitter1 = QSplitter(Qt.Horizontal)
    viewport_layout1.addWidget(viewport_splitter1)
    
    panda_widget_2 = QPanda3DWidget(world)
    viewport_splitter.addWidget(panda_widget_2)

    shader_editor = ShaderEditor()
    viewport_splitter.addWidget(shader_editor)

    # 2D Viewport
    pandaWidget1 = QPanda3DWidget(world)
    uiEditor_inst = ui_editor.Drag_and_drop_ui_editor(world, world.render2d)
    viewport_splitter1.addWidget(uiEditor_inst.tab_content(viewport_tab1, world))
    
    
    tab_widget.addTab(viewport_tab, "Shader Editor")
    tab_widget.currentChanged.connect(new_tab)
    
    tab_widget.addTab(viewport_tab1, "UI Editor")
    tab_widget.currentChanged.connect(new_tab)

    # Set the main widget as the central widget
    appw.setCentralWidget(main_widget)

    # Populate the hierarchy tree with actual scene data
    world.populate_hierarchy(world.hierarchy_tree, render)  # This will populate the hierarchy panel
    world.populate_hierarchy(world.hierarchy_tree1, world.render2d)  # This will populate the hierarchy panel

    world.hierarchy_tree.itemClicked.connect(lambda item, column: on_item_clicked(item, column))
    world.hierarchy_tree1.itemClicked.connect(lambda item, column: on_item_clicked1(item, column))
    
    #world.ui_editor_script_to_canvas()
    
    

    prop = properties
    prop_ui_e = properties_ui_editor
    for coord, box in input_boxes.items():
        # Use a default argument to capture the value of `coord` correctly
        box.textChanged.connect(lambda box=box, coord=coord: prop.update_node_property(box, coord))
    for coord, box in uiEditor_inst.input_boxes.items():
        # Use a default argument to capture the value of `coord` correctly
        box.textChanged.connect(lambda box=box, coord=coord: prop_ui_e.update_node_property(box, coord))

    # Set the background color of the widget to gray
    qdarktheme.setup_theme()
    #apply_stylesheet(appw, theme="light_blue.xml")

    # Show the application window
    appw.show()
    sys.exit(app.exec_())