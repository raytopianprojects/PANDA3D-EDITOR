from direct.gui.DirectGui import DirectButton, DirectLabel, DirectFrame
from panda3d.core import Point3, CollisionTraverser, CollisionHandlerQueue, CollisionRay, CollisionNode
from QPanda3D.Panda3DWorld import Panda3DWorld
from direct.gui import DirectGuiGlobals as DGG
from panda3d.core import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import scirpt_inspector
import entity_editor
from QPanda3D.QPanda3DWidget import QPanda3DWidget
from file_explorer import FileExplorer
import entity_editor

class Drag_and_drop_ui_editor:
    def __init__(self, world: Panda3DWorld, panda_widget):
        self.world = world
        self.widget = panda_widget
        self.widgets = []
        self.task_drag = None  # Initialize task_drag once
        
        self.draggable = False
        self.is_moving = False
        
        self.collision_traverser = CollisionTraverser()
        self.collision_handler = CollisionHandlerQueue()
        
        self.mouse_ray = CollisionRay()
        self.mouse_node = CollisionNode('mouse_ray')
        self.mouse_node.add_solid(self.mouse_ray)
        self.mouse_node.set_from_collide_mask(BitMask32.bit(1))
        self.mouse_node.set_into_collide_mask(BitMask32.bit(1))
        self.mouse_node_path = self.world.camera.attach_new_node(self.mouse_node)

        self.collision_traverser.add_collider(self.mouse_node_path, self.collision_handler)
        
        self.world.accept("mouse1", self.start_holding)
        self.world.accept('mouse1-up', self.stop_drag)
        self.world.accept("mouse-move", self.mouse_move)
        
        # Create UI elements
        #self.label("hello world!", 0.1, parent=world.canvas)
        print("hello world")
        
        self.grid = False
    
    def tab_content(self, viewport_tab, world):
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
        self.inspector_ui_tab = scirpt_inspector.ScriptInspector(world, entity_editor, node, left_panel)
        world.script_inspector = self.inspector_ui_tab


        #inspector.show()
        left_panel_layout.addWidget(self.inspector_ui_tab)
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

        world.hierarchy_tree1.setHeaderLabel("Scene Hierarchy")
        world.hierarchy_tree1.setDragEnabled(True)
        world.hierarchy_tree1.setAcceptDrops(True)
        right_panel.layout().addWidget(world.hierarchy_tree1)
        # Create a QWidget to hold the grid layout
        grid_widget = QWidget()
        # Create a grid layout for the input boxes (3x3)
        self.grid_layout = QGridLayout(grid_widget)

        # Create 3x3 QLineEdit input boxes
        self.input_boxes = {}
        for i in range(3):
            for j in range(3):
                if i == 0 and j == 0:
                    label1 = QLabel("transforms x y z: ")
                if i == 1 and j == 0:
                    label1 = QLabel("rotation x y z: ")
                if i == 2 and j == 0:
                    label1 = QLabel("scale x y z: ")
                self.input_box = QLineEdit(grid_widget)
                self.input_boxes[(i, j)] = self.input_box
                self.grid_layout.addWidget(label1, i * 2, j)  # Add label in a separate row
                self.grid_layout.addWidget(self.input_box, i * 2 + 1, j)  # Add input box below the label
                
        

        # Add the grid widget to the main layout
        right_panel.layout().addWidget(grid_widget)
        grid_check = QCheckBox(grid_widget)
        grid_check.setText("Enable Grid")
        grid_check.stateChanged.connect(self.toggle_grid)

        viewport_splitter.addWidget(right_panel)
        return viewport_splitter
    def toggle_grid(self):
        self.grid = not self.grid
    def attach_collision_to_widget(self, widget):
        # Define corners of a rectangle in the widget's coordinate space.
        # Adjust coordinates as necessary to match widget size/position.
        corners = [
            Point3(-0.5, 0, -0.5),
            Point3(0.5, 0, -0.5),
            Point3(0.5, 0, 0.5),
            Point3(-0.5, 0, 0.5)
        ]
        polygon = CollisionPolygon(*corners)
        collisionNode = CollisionNode('uiCollision')
        collisionNode.addSolid(polygon)
        
        # Set collision masks to match the ray's settings.
        collisionNode.set_into_collide_mask(BitMask32.bit(1))
        
        # Attach collision node to the widget
        collisionNP = widget.attachNewNode(collisionNode)
        # Optional: visualize collision geometry for debugging
        # collisionNP.show()
        collisionNP.show()
        return collisionNP

    def set_script_to_widget(self, widget, script):
        widget.set_python_tag("action", script)
    
    
    def load_ui(self):
        entity_editor.Load.load_ui_from_folder_toml()
    def save_ui(self, name):
        entity_editor.Save.save_scene_ui_to_toml(self.world.render2d, "/saves/uis/" + name)
    def label(self, text1, scale1=0.1, pos1=(0, 0, 0.5), parent1=None, frameColor1=(0.5, 0.5, 0.5, 1), text_fg1=(1, 1, 1, 1)):
        
        # Ensure 'frameColor' is in the correct format
        if isinstance(frameColor1, dict):  # Uniform scale
            frameColor1 = (frameColor1.get('r', 0), frameColor1.get('g', 0), frameColor1.get('b', 0), 1.0)
        # Ensure 'text_fg' is in the correct format
        if isinstance(text_fg1, dict):  # Uniform scale
            text_fg1 = (text_fg1.get('r', 0), text_fg1.get('g', 0), text_fg1.get('b', 0), 1.0)
        # Ensure 'scale' is in the correct format
        if isinstance(scale1, (int, dict)):  # Uniform scale
            scale1 = LVecBase3f(scale1.get('x', 0), scale1.get('y', 0), scale1.get('z', 0))
        elif isinstance(scale1, (list, dict)) and len(scale1) == 3:  # Non-uniform scale
            scale1 = LVecBase3f(scale1.get('x', 0), scale1.get('y', 0), scale1.get('z', 0))
        elif not isinstance(scale1, LVecBase3f):  # If invalid, default to uniform scale
            scale1 = LVecBase3f(0.1, 0.1, 0.1)

        # 'text' is a valid Panda3D text (convert if necessary)
        if isinstance(text1, dict):  # If `pos` is a dictionary, handle it
            text1 = LPoint3(text1.get('text1', "tea time"))
        # Ensure 'pos' is a valid Panda3D position (convert if necessary)
        if isinstance(pos1, dict):  # If `pos` is a dictionary, handle it
            pos1 = LPoint3(pos1.get('x', 0), pos1.get('y', 0), pos1.get('z', 0))
        elif isinstance(pos1, tuple):  # If it's a tuple, convert to LPoint3
            pos1 = LPoint3(*pos1)
        
        print(text1)
        
        # Create a draggable label
        ui_reference1 = DirectLabel(
            text=text1,
            scale=scale1,
            pos=pos1,
            parent=self.world.render2d,
            frameColor=frameColor1,
            text_fg=text_fg1,
        )
        
        ui_reference1.setPythonTag("widget_type", "l")
        ui_reference1.setPythonTag("ui_reference", ui_reference1)
        ui_reference1.setPythonTag("frameColor1", {"r" : frameColor1[0], "g" : frameColor1[1], "b" : frameColor1[2]})
        ui_reference1.setPythonTag("text_fg1", {"r" : text_fg1[0], "g" : text_fg1[1], "b" : text_fg1[2]})
        ui_reference1.setPythonTag("isCanvas", False)
        ui_reference1.setPythonTag("isLabel", True)
        ui_reference1.setPythonTag("isButton", False)
        self.widgets.append(ui_reference1)
        return ui_reference1
        #label1.set_python_tag("widget_type", "l")
        
        
        #self.attach_collision_to_widget(label1)

        # Bind events for dragging (for both elements)
        #self.draggable_button.bind(DGG.B1PRESS, self.start_drag, extraArgs=[self.draggable_button, self.label1])
        #self.label1.bind(DGG.B1PRESS, self.start_drag, extraArgs=[self.draggable_button, self.label1])
        #self.draggable_button.bind(DGG.B1RELEASE, self.stop_drag)
        #self.label1.bind(DGG.B1RELEASE, self.stop_drag)
    def button(self, text, scale=0.1, pos=(0, 0, 0.5), parent=None, frameColor=(0.5, 0.5, 0.5, 1), text_fg=(1.0, 1.0, 1.0, 1.0)):
        
        # Ensure 'scale' is in the correct format
        if isinstance(scale, (int, dict)):  # Uniform scale
            scale = LVecBase3f(scale.get('x', 0), scale.get('y', 0), scale.get('z', 0))
        elif isinstance(scale, (list, dict)) and len(scale) == 3:  # Non-uniform scale
            scale = LVecBase3f(scale.get('x', 0), scale.get('y', 0), scale.get('z', 0))
        elif not isinstance(scale, LVecBase3f):  # If invalid, default to uniform scale
            scale = LVecBase3f(0.1, 0.1, 0.1)

        # 'text' is a valid Panda3D text (convert if necessary)
        if isinstance(text, dict):  # If `pos` is a dictionary, handle it
            text = LPoint3(text.get('text', "tea time"))
        # Ensure 'pos' is a valid Panda3D position (convert if necessary)
        if isinstance(pos, dict):  # If `pos` is a dictionary, handle it
            pos = LPoint3(pos.get('x', 0), pos.get('y', 0), pos.get('z', 0))
        if isinstance(frameColor, dict):  # Uniform scale
            frameColor = (frameColor.get('r', 0), frameColor.get('g', 0), frameColor.get('b', 0), 1.0)
        if isinstance(text_fg, dict):  # If `pos` is a dictionary, handle it
            text_fg = (text_fg.get('r', 0), text_fg.get('g', 0), text_fg.get('b', 0), 1.0)
        elif isinstance(pos, tuple):  # If it's a tuple, convert to LPoint3
            pos = LPoint3(*pos)
        
        # Create a draggable label
        ui_reference1 = DirectButton(
            text=text,
            scale=scale,
            pos=pos,
            parent=parent,
            frameColor=frameColor,
            text_fg=text_fg,
        )
         
        ui_reference1.setPythonTag("widget_type", "b")
        ui_reference1.setPythonTag("ui_reference", ui_reference1)
        ui_reference1.setPythonTag("frameColor1", {"r" : frameColor[0], "g" : frameColor[1], "b" : frameColor[2]})
        ui_reference1.setPythonTag("text_fg1", {"r" : text_fg[0], "g" : text_fg[1], "b" : text_fg[2]})
        ui_reference1.setPythonTag("isCanvas", False)
        ui_reference1.setPythonTag("isLabel", False)
        ui_reference1.setPythonTag("isButton", True)
        self.widgets.append(ui_reference1)
        return ui_reference1
        # Bind events for dragging (for both elements)
        #self.draggable_button.bind(DGG.B1PRESS, self.start_drag, extraArgs=[self.draggable_button, self.label1])
        #self.label1.bind(DGG.B1PRESS, self.start_drag, extraArgs=[self.draggable_button, self.label1])
        #self.draggable_button.bind(DGG.B1RELEASE, self.stop_drag)
        #self.label1.bind(DGG.B1RELEASE, self.stop_drag)

    def Frame(self, path, parent,frameSize=(-0.5, 0.5, -0.5, 0.5), scale=(0.1,0.1,0.1), pos=(0.0,0.0,0.5), frameColor=(0, 0, 0, 0)):
        ui_reference1 = DirectFrame(
            frameSize=frameSize,
            frameColor=(1, 1, 1, 1),   # Transparent frame
            image=path,  # Path to the image
            parent=parent,
            image_scale=scale,     # Scale the image
            pos=pos
        )
        
        self.widgets.append(ui_reference1)
        
        ui_reference1.setPythonTag("widget_type", "i")
        ui_reference1.setPythonTag("ui_reference", ui_reference1)

        ui_reference1.setPythonTag("isCanvas", False)
        ui_reference1.setPythonTag("isLabel", False)
        ui_reference1.setPythonTag("isButton", False)
        ui_reference1.setPythonTag("isFrame", True)
        self.widgets.append(ui_reference1)
        return ui_reference1

    def get_all_2d_nodes(self):
        """
        Get all 2D NodePaths under render2d.
        """
        nodepaths = []
        for node in self.world.render2d.find_all_matches("**"):
            nodepaths.append(node)
        return nodepaths

    def create_widget(self, widget_type, text):
        if widget_type == "l":
            self.label(text)
        if widget_type == "b":
            self.button(text)
        elif widget_type == "i":
            self.Frame(text)
        return self.get_all_2d_nodes()

    
    
    
    def is_mouse_over_widget(self, world):
        for widget in self.widgets:
            if widget is None:
                continue  # Skip invalid entries
            else:
                print(self.widgets)
                
                
                # Check if mouse is available
                if not world.mouseWatcherNode.hasMouse():
                    return False

                # Retrieve normalized mouse position from the mouse watcher node
                mouse_norm = world.mouseWatcherNode.getMouse()  # Vec2

                # Convert normalized mouse coordinates to render2d coordinates
                # In a default render2d setup, normalized mouse coordinates correspond directly to render2d space
                mouse_x = mouse_norm.getX()
                mouse_z = mouse_norm.getY()  # Using z-axis for vertical in render2d

                # Get widget's position relative to render2d
                pos = widget.getPos()  # Returns an LVecBase3f
                wx = pos.x
                wz = pos.z  # For 2D, x and z coordinates are used (assuming y is depth which is constant)

                # Get widget's scale (assuming uniform scaling for width and height)
                scale = widget.getScale()
                # Estimate width and height based on known base dimensions and widget scale.
                # You may need to adjust these factors to match the actual visual size of your widget.
                base_width = 0.5   # Base width for a scale of 1; adjust as needed
                base_height = 0.5  # Base height for a scale of 1; adjust as needed
                width = base_width * scale.x
                height = base_height * scale.z  # assuming z-scale affects height in render2d

                # Define boundaries of the widget
                left = wx - width
                right = wx + width
                bottom = wz - height
                top = wz + height

                print(left, mouse_x, right, pos.z)

                # Check if mouse position lies within these boundaries
                if (left <= mouse_x <= right) and (bottom <= mouse_z <= top):
                    self.draggable = True
                    if self.draggable and self.is_moving:
                        self.world.add_task(self.move_widget, "move_widget", appendTask=True, extraArgs = [widget])
                        self.draggable = False
                        self.is_moving = False
                    return True
        return False
    def drag_task(self, task):
        
        if self.is_mouse_over_widget(self.world):
            print("test!!!!!")
            
        return task.cont if self.holding else task.done
        #if self.collision_handler.get_num_entries() > 0:
        #    print("works")
        #    self.collision_handler.sort_entries()
        #    entry = self.collision_handler.get_entry(0)
        #    point = entry.getSurfacePoint(self.world.render)
        #    hit_node_path = entry.getIntoNodePath()  # Retrieve the NodePath that was hit

        #    if not hit_node_path.isEmpty():
        #        print(Vec3(point[0], point[1], 255))
        #        self.draggable = True
        #        
        #        
        #        # Optionally, if you want to drag the child, you can set the task to keep updating
        #        # self.task_drag = self.world.taskMgr.add(self.drag_task, "drag-task", extraArgs=[element, hit_node_path], appendTask=True)
        #    else:
        #        print("No valid node found in collision entry")
        #else:
        #    print("No entries found in collision queue")
    
    def move_widget(self, hit_node_path, task):
        pMouse = self.world.mouseWatcherNode.getMouse()
        if self.grid:
            grid_size = 0.1  # Adjust this to your desired grid size
        else:
            grid_size = 0.01
        snap_x = round(pMouse[0] / grid_size) * grid_size
        snap_y = round(pMouse[1] / grid_size) * grid_size
        hit_node_path.setPos(Vec3(snap_x, 0, snap_y))
        hit_node_path.getParent().setPos(Vec3(pMouse[0], 0, pMouse[1]))
        return task.cont if self.holding else task.done
    
    def start_holding(self, position):
        self.mx, self.my = position['x'], position['y']
        self.is_moving = True
        self.world.add_task(self.drag_task, "on_mouse_click", appendTask=True)
        self.height = 0.0
        self.holding = True
    
    def mouse_move(self, evt: dict):
        self.mx, self.my = evt['x'], evt['y']

    def stop_drag(self, event):
        """
        Stop dragging the element.
        """
        print("Drag stopped.")
        self.holding = False
        if self.task_drag:
            self.world.taskMgr.remove(self.task_drag)
            self.task_drag = None
            