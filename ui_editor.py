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

        viewport_splitter.addWidget(right_panel)
        return viewport_splitter
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
        entity_editor.Load.load_ui_from_folder_toml
    def save_ui(self, name):
        entity_editor.Save.save_scene_ui_to_toml(self.world.render2d, "/saves/uis/" + name)
    def label(self, text, scale=0.1, pos=(0, 0, 0.5), parent=None, frameColor=(0.5, 0.5, 0.5, 1), text_fg=(1, 1, 1, 1)):

        # Create a draggable label
        label1 = DirectLabel(
            text=text,
            scale=scale,
            pos=pos,
            parent=parent,
            frameColor=frameColor,
            text_fg=text_fg,
        )
        
        label1.set_python_tag("widget_type", "l")
        
        
        self.attach_collision_to_widget(label1)

        # Bind events for dragging (for both elements)
        #self.draggable_button.bind(DGG.B1PRESS, self.start_drag, extraArgs=[self.draggable_button, self.label1])
        #self.label1.bind(DGG.B1PRESS, self.start_drag, extraArgs=[self.draggable_button, self.label1])
        #self.draggable_button.bind(DGG.B1RELEASE, self.stop_drag)
        #self.label1.bind(DGG.B1RELEASE, self.stop_drag)
    def button(self, text, scale=0.1, pos=(0, 0, 0.5), parent=None, frameColor=(0.5, 0.5, 0.5, 1), text_fg=(1, 1, 1, 1)):

        # Create a draggable label
        label1 = DirectButton(
            text=text,
            scale=scale,
            pos=pos,
            parent=parent,
            frameColor=frameColor,
            text_fg=text_fg,
        )
        
        self.widgets.append(label1)
        
        
        label1.set_python_tag("widget_type", "b")
        
        
        self.attach_collision_to_widget(label1)

        # Bind events for dragging (for both elements)
        #self.draggable_button.bind(DGG.B1PRESS, self.start_drag, extraArgs=[self.draggable_button, self.label1])
        #self.label1.bind(DGG.B1PRESS, self.start_drag, extraArgs=[self.draggable_button, self.label1])
        #self.draggable_button.bind(DGG.B1RELEASE, self.stop_drag)
        #self.label1.bind(DGG.B1RELEASE, self.stop_drag)

    def Frame(self, path):
        image_frame = DirectFrame(
            frameSize=(-0.5, 0.5, -0.5, 0.5),
            frameColor=(0, 0, 0, 0),   # Transparent frame
            image=path,  # Path to the image
            parent=self.world.canvas,
            image_scale=(1, 1, 1),     # Scale the image
            pos=(0, 0, 0)
        )
        
        self.widgets.append(image_frame)
        
        image_frame.set_python_tag("widget_type", "f")

        # Bind events for dragging
        self.draggable_button.bind(DGG.B1PRESS, self.start_drag, extraArgs=[self.draggable_button, self.image_frame])
        self.image_frame.bind(DGG.B1PRESS, self.start_drag, extraArgs=[self.draggable_button, self.image_frame])
        self.draggable_button.bind(DGG.B1RELEASE, self.stop_drag)
        self.image_frame.bind(DGG.B1RELEASE, self.stop_drag)

    def get_all_2d_nodes(self):
        """
        Get all 2D NodePaths under render2d.
        """
        nodepaths = []
        for node in self.world.render2d.find_all_matches("**"):
            nodepaths.append(node)
        return nodepaths

    def create_widget(self, widget_type, text, id):
        if widget_type == "label":
            self.label(text)
        elif widget_type == "image":
            self.Frame(text)
        return self.get_all_2d_nodes()

    
    
    
    def is_mouse_over_widget(self, world, widget):
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
        pos = widget.getPos(world.render2d)  # Returns an LVecBase3f
        wx = pos.x
        wz = pos.z  # For 2D, x and z coordinates are used (assuming y is depth which is constant)

        # Get widget's scale (assuming uniform scaling for width and height)
        scale = widget.getScale(world.render2d)
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
            return True
        else:
            return False
    def drag_task(self, task):
        if self.is_mouse_over_widget(self.world, self.label1):
            print("test!!!!!")
            self.draggable = True
            if self.draggable and self.is_moving:
                self.world.add_task(self.move_widget, "move_widget", appendTask=True, extraArgs = [self.label1])
                self.draggable = False
                self.is_moving = False
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
        hit_node_path.setPos(Vec3(pMouse[0], 0, pMouse[1]))
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
            