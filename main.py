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
#import qdarktheme
from qt_material import apply_stylesheet


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

    def make_terrain(self):
        self.terrain_generate = terrainEditor.TerrainPainterApp(world, pandaWidget)
        selected_node = self.terrain_generate.terrain_node


def populate_hierarchy(hierarchy_widget, node, parent_item=None):
    # Create a new item for the current node
    item = QTreeWidgetItem(parent_item or hierarchy_widget, [node.getName()])
    item.setData(0, Qt.UserRole, node)  # Store the NodePath in the item data
    # Recursively add child nodes
    for child in node.getChildren():
        populate_hierarchy(hierarchy_widget, child, item)


selected_node = None


class properties:
    def __init__():
        pass

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


def on_item_clicked(item, column):
    global selected_node
    node = item.data(0, Qt.UserRole)  # Retrieve the NodePath stored in the item

    if node:
        selected_node = node
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
        panda_widget_2.resizeEvent(panda_widget_2)
    else:
        shader_editor.show_nodes()
        pandaWidget.resizeEvent(pandaWidget)


class Node:
    def __init__(self, ref, path):
        self.ref = ref
        self.paths = [path]

    def update(self, path):
        if path not in self.paths:
            self.paths.append(path)


class ScriptInspector(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Script Inspector")
        self.resize(500, 700)

        self.parent = parent

        # Main layout
        self.layout = QVBoxLayout(self)
        self.apply_button = QPushButton("Apply Changes")
        self.layout.addWidget(self.apply_button)

        # Data storage
        self.scripts = {}  # Stores scripts with their group boxes
        self.current_script_instance = None

        # Scrollable area setup
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)  # Allow the scroll area to resize its content
        self.scroll_widget = QWidget()  # Create a widget to hold all the script boxes
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_area.setWidget(self.scroll_widget)
        self.layout.addWidget(self.scroll_area)  # Add the scroll area to the main layout

        self.fpath = {}

        self.setAcceptDrops(True)

        # Signal connections
        self.apply_button.clicked.connect(self.apply_changes)

    def set_script(self, path, node):
        """
        Load a script, create an instance, and display its properties in a new box.
        """
        try:
            # Load and execute the script
            spec = importlib.util.spec_from_file_location("script", path)
            script_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(script_module)

            if hasattr(script_module, "Script"):
                # Check if the script is already associated with the node

                script_instance = script_module.Script()
                self.scripts.setdefault(node, {})[path] = script_instance
                node.set_python_tag("scripts", self.scripts[node])

                # Create a new group box for the script
                script_box = self.create_script_box(path, script_instance)
                self.scroll_layout.addWidget(script_box)  # Add to the scrollable layout
                self.current_script_instance = script_instance
                print(f"Script loaded successfully: {path}")
        except Exception as e:
            print(f"Error loading script from {path}: {e}")

    def clear_inspector(self):
        """
        Clears all widgets from the scroll layout.
        """
        while self.scroll_layout.count():
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def create_script_box(self, path, script_instance):
        """
        Create a QGroupBox for the script with its properties, including drag-and-drop support for object references.
        """
        script_box = QGroupBox()
        script_box.setStyleSheet("QGroupBox { background-color: gray; border: 1px solid black; border-radius: 20px; }")

        script_layout = QVBoxLayout()

        # Horizontal layout for script label and image
        title_layout = QHBoxLayout()

        # Add small 10x10 image near the script label
        image_label = QLabel()
        image_label.setMaximumWidth(20)
        image_label.setMaximumHeight(20)
        pixmap = QPixmap("Grass.png")  # Replace with the path to your image file
        if not pixmap.isNull():
            pixmap = pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label.setPixmap(pixmap)
        else:
            image_label.setText("No Image")  # Fallback if image can't be loaded

        script_layout.addLayout(title_layout)
        title_layout.addWidget(image_label)

        # Label for script name
        script_name = QLabel(f"Script: {os.path.splitext(os.path.basename(path))[0]}")
        script_name.setMaximumHeight(30)
        title_layout.addWidget(script_name)

        # Add properties as editable fields
        attributes = vars(script_instance)
        item_height = 30  # Desired height for input fields
        max_height = 30  # Maximum height for input fields
        spacing = 30  # Space between items

        for attr, value in attributes.items():
            if isinstance(value, NodePath):  # Handle NodePath (object reference)
                label = Label(f"{attr}: {value.getName()}")
                label.setMaximumHeight(max_height)
                script_layout.addWidget(label)
            elif isinstance(value, Texture):  # Handle Texture type
                # Create a horizontal layout for texture details
                horizontal_layout = QHBoxLayout()

                # Convert Panda3D's Filename to a string path and load into QPixmap
                texture_path = Filename(value.get_name()).to_os_specific()
                pixmap = QPixmap(texture_path)
                texture_label = Label(None)
                texture_label.setMaximumHeight(100)
                if not pixmap.isNull():
                    texture_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio))
                else:
                    texture_label.setText("Image not found")

                horizontal_layout.addWidget(texture_label)

                # Add a label for the texture name
                name_label = Label(f"Texture: {value.get_name()}")
                name_label.setMaximumHeight(max_height)
                horizontal_layout.addWidget(name_label)

                # Container for horizontal layout
                container_widget = QWidget()
                container_widget.setMaximumHeight(110)
                container_widget.setLayout(horizontal_layout)

                # Add container to the script layout
                script_layout.addWidget(container_widget)
            else:
                # Regular input fields
                input_field = QLineEdit(str(value))
                input_field.setObjectName(attr)
                input_field.setMaximumHeight(max_height)  # Set maximum height
                script_layout.addWidget(input_field)

        # Set layout properties for spacing
        script_layout.setSpacing(spacing)

        # Calculate the height based on the number of items
        num_items = len(attributes)
        total_height = (num_items * item_height) + ((num_items - 1) * spacing)
        script_box.setLayout(script_layout)

        return script_box

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():  # Check for valid URLs
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.endswith('.py'):  # Ensure it's a Python script
                    if selected_node:
                        self.set_script(file_path, selected_node)
                        print(f"Script {file_path} dropped onto {selected_node.getName()}")
                    else:
                        print("No selected node to attach the script.")
                else:
                    print(f"Ignored non-Python file: {file_path}")
            event.accept()
        else:
            event.ignore()

    def get_node_by_name(self, name):
        """
        Retrieve a NodePath by name from the scene graph.
        """
        for node in render.find_all_matches("**"):  # Search in the scene graph
            if node.get_name() == name:
                return node
        return None

    def apply_changes(self):
        """
        Apply changes made in the inspector to the script instances.
        """
        for path, script_box in self.scripts.items():
            for i in range(script_box.layout().count()):
                widget = script_box.layout().itemAt(i).widget()
                if isinstance(widget, QLineEdit):
                    attr_name = widget.objectName()
                    new_value = widget.text()

                    try:
                        script_instance = self.scripts[path].script_instance
                        old_value = getattr(script_instance, attr_name)
                        if isinstance(old_value, int):
                            new_value = int(new_value)
                        elif isinstance(old_value, float):
                            new_value = float(new_value)
                        setattr(script_instance, attr_name, new_value)
                    except ValueError:
                        print(f"Invalid value for {attr_name} in script {path}.")
                    except Exception as e:
                        print(f"Error applying changes to {attr_name}: {e}")


class Label(QLabel):
    def __init__(self, parent):
        super(Label, self).__init__(parent)
        self.setAcceptDrops(True)
        self.setText("None")
        self.setStyleSheet("QGroupBox { background-color: gray; border: 2px solid white; border-radius: 10px;}")

    def dragEnterEvent(self, event):
        mime = event.mimeData()
        if mime.hasText() or mime.hasFormat('application/x-qabstractitemmodeldatalist'):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        mime = event.mimeData()

        if mime.hasUrls():  # Handle file drops, including image files
            urls = mime.urls()
            if urls:
                file_path = urls[0].toLocalFile()  # Convert URL to a local file path
                if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):  # Check for image formats
                    pixmap = QPixmap(file_path)
                    if not pixmap.isNull():
                        # Display the image
                        self.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio))
                        print(f"Image loaded successfully: {file_path}")
                    else:
                        print(f"Failed to load image: {file_path}")
                        self.setText("Invalid Image")
                else:
                    # If not an image, treat as a general file path
                    print(f"Non-image file dropped: {file_path}")
                    self.setText(file_path)
            event.accept()

        elif mime.hasText():  # Handle plain text drops
            self.setText(mime.text())
            print(f"Text dropped: {mime.text()}")
            event.accept()

        elif mime.hasFormat('application/x-qabstractitemmodeldatalist'):  # Handle internal Qt data
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
            print(f"Internal data dropped: {', '.join(textList)}")
            event.accept()

        else:
            print("Unsupported drop data type")
            event.ignore()


#Toolbar functions
def new_project():
    print("Open file triggered")


def save_file():
    world.messenger.send("save")
    print("Save file triggered")


def load_project():
    print("Custom action triggered")


def close():  #TODO when saving is introduced make a window pop up with save option(save don't save and don't exist(canel))
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
    edit_tool_type_menu = QMenu("Edit", appw)
    terrain_3d = QMenu("Terrain 3D", appw)

    # Create an action for the Edit menu
    action = QAction("new project", appw)
    action.triggered.connect(new_project)
    edit_tool_type_menu.addAction(action)

    action1 = QAction("save project", appw)
    action1.triggered.connect(save_file)
    edit_tool_type_menu.addAction(action1)

    action2 = QAction("load project", appw)
    action2.triggered.connect(load_project)
    edit_tool_type_menu.addAction(action2)

    action3 = QAction("exit", appw)
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
    tool_button.setText("Edit")
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
    left_panel.setLayout(QVBoxLayout())
    input_box = QLineEdit()
    left_panel.layout().addWidget(input_box)
    left_label = QLabel("Left Panel (Empty)")
    left_panel.layout().addWidget(left_label)


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

    inspector = ScriptInspector(left_panel)
    inspector.show()
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
    #qdarktheme.setup_theme()
    apply_stylesheet(appw, theme="light_cyan.xml")

    # Show the application window
    appw.show()
    sys.exit(app.exec_())
