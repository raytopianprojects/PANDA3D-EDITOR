from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
import os
import importlib
import uuid


class ScriptInspector(QWidget):
    def __init__(self, world, entity_editor, node, parent=None, ):
        super().__init__(parent)
        self.setWindowTitle("Script Inspector")
        self.resize(500, 700)

        self.parent = parent

        # Global vars
        self.world = world
        self.entity_editor = entity_editor
        self.node = node

        # Save
        self.do = DirectObject()
        self.do.accept("save", self.apply_changes)

        # Main layout
        self.layout = QVBoxLayout(self)
        self.header = QLabel("Property Editor")
        self.layout.addWidget(self.header)
        #self.apply_button = QPushButton("Apply Changes")
        #self.layout.addWidget(self.apply_button)

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

        self.add_script = QPushButton("add script")
        self.layout.addWidget(self.add_script)

        self.setAcceptDrops(True)

        # Signal connections
        #self.apply_button.clicked.connect(self.apply_changes)
        self.add_script.clicked.connect(self.show_list)

    def show_list(self):
        """
        Display a dialog with a list of .py files in a folder and allow removal of selected files.
        """
        folder_path = "./"  # Replace with the desired folder path
        py_files = [f for f in os.listdir(folder_path) if f in [""]]

        # Create a dialog to display the files
        dialog = QDialog(self)
        dialog.setWindowTitle("Python Files")
        dialog.resize(400, 300)

        # Dialog layout
        dialog_layout = QVBoxLayout(dialog)

        # List widget to display files
        file_list = QListWidget(dialog)
        file_list.addItems(py_files)
        dialog_layout.addWidget(file_list)

        # Remove button
        add_button = QPushButton("add Selected", dialog)
        dialog_layout.addWidget(add_button)

        # Close button
        close_button = QPushButton("Close", dialog)
        dialog_layout.addWidget(close_button)

        # Define remove action
        def add_selected():
            selected_items = file_list.selectedItems()
            for item in selected_items:
                file_name = item.text()
                file_path = os.path.join(folder_path, file_name)
                print(f"Selected file path: {file_path}")  # Debug print
                if self.world.selected_node:
                    self.set_script(file_path, self.node)

        # Connect buttons to actions
        add_button.clicked.connect(add_selected)
        close_button.clicked.connect(dialog.accept)

        # Show the dialog
        dialog.exec_()

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
                data = node.get_python_tag("script_properties") or {os.path.splitext(os.path.basename(path))[0]}
                node.set_python_tag("script_properties", data)
                node.set_python_tag("id", str(uuid.uuid4())[:8])

                # Create a new group box for the script
                script_box = self.create_script_box(path, script_instance, node)
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

    def create_script_box(self, path, script_instance, nodepath):

        """
        Create a QGroupBox for the script with its properties, including drag-and-drop support for object references.
        """
        script_box = QGroupBox()
        #script_box.setStyleSheet("QGroupBox { background-color: gray; border: 1px solid black; border-radius: 20px; }")

        script_layout = QVBoxLayout()

        # Horizontal layout for script label and image
        title_layout = QHBoxLayout()

        # Add small 10x10 image near the script label
        image_label = QLabel()
        image_label.setMaximumWidth(20)
        image_label.setMaximumHeight(20)
        pixmap = QPixmap("python_img.png")  # Replace with the path to your image file
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
                label = Label(f"{attr}:", value.getName())
                label.setMaximumHeight(max_height)
                script_layout.addWidget(label)
                # Connect textChanged signal to update NodePath tag
                label.textChanged.connect(lambda text, attr=attr: self.update(attr, text, nodepath, path))

            elif isinstance(value, Texture):  # Handle Texture type
                # Create a horizontal layout for texture details
                horizontal_layout = QHBoxLayout()

                # Convert Panda3D's Filename to a string path and load into QPixmap
                texture_path = Filename(value.get_name()).to_os_specific()
                pixmap = QPixmap(texture_path)
                texture_label = Label(f"Texture: {value.get_name()}", str(value.get_name()))
                texture_label.setMaximumHeight(100)
                if not pixmap.isNull():
                    texture_label.value.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio))
                else:
                    texture_label.value.setText("Image not found")

                # Connect textChanged signal to update NodePath tag
                texture_label.textChanged.connect(lambda text, attr=attr: self.update(attr, text, nodepath, path))

                horizontal_layout.addWidget(texture_label)

                # Add a label for the texture name
                # name_label = Label(f"Texture:", str(value.get_name()))
                # name_label.setMaximumHeight(max_height)
                # horizontal_layout.addWidget(name_label)

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

                # Connect textChanged signal to update NodePath tag
                input_field.textChanged.connect(lambda text, attr=attr: self.update(attr, text, nodepath, path))

        # Set layout properties for spacing
        script_layout.setSpacing(spacing)

        # Calculate the height based on the number of items
        num_items = len(attributes)
        total_height = (num_items * item_height) + ((num_items - 1) * spacing)
        script_box.setLayout(script_layout)

        return script_box

    def update(self, attr, value, node1, script_name):
        """
        Update the script properties of the NodePath.
        """
        # Retrieve or initialize the script_properties dictionary
        script_properties = node1.get_python_tag("script_properties")

        # Ensure script_properties is a dictionary
        if not isinstance(script_properties, dict):
            print(f"script_properties is not a dict: {type(script_properties)}. Reinitializing.")
            script_properties = {}

        # Ensure script_name exists as a key with a dictionary as its value
        if script_name not in script_properties:
            script_properties[script_name] = {}

        # Update the attribute value in the script properties
        script_properties[script_name][attr] = value

        # Save the updated dictionary back to the node
        node1.set_python_tag("script_properties", script_properties)

        print(f"Updated script_properties for {node1.get_name()} - {script_name}: {script_properties}")

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
                    if self.world.selected_node:
                        self.set_script(file_path, self.world.selected_node)
                        print(f"Script {file_path} dropped onto {self.world.selected_node.getName()}")
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
        for node in self.world.render.find_all_matches("**"):  # Search in the scene graph
            if node.get_name() == name:
                return node
        return None

    def apply_changes(self):
        """
        Apply changes made in the inspector to the script instances.
        """
        ee = self.entity_editor.Save()
        ee.save_scene_to_toml(self.world.render, "./saves/")


class Label(QWidget):
    textChanged = pyqtSignal(str)

    def __init__(self, attr, value, parent=None):
        super(Label, self).__init__(parent)
        self.setAcceptDrops(True)
        self.hbox = QHBoxLayout()
        self.setLayout(self.hbox)

        self.attr = QLabel(attr)
        self.attr.setMinimumHeight(20)
        self.value = QLabel(value)
        self.value.setMinimumHeight(20)

        self.hbox.addWidget(self.attr)
        self.hbox.addWidget(self.value)

    def settText(self, text):
        self.textChanged.emit(text)  # Emit custom signal

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
                        self.attr.setText(f"Texture: {urls[0].fileName()}" )
                        # Display the image
                        self.value.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio))
                        print(f"Image loaded successfully: {file_path}")
                        #self.value.settText(mime.text())
                    else:
                        print(f"Failed to load image: {file_path}")
                        self.value.setText("Invalid Image")
                else:
                    # If not an image, treat as a general file path
                    print(f"Non-image file dropped: {file_path}")
                    self.value.setText(file_path)
            event.accept()

        elif mime.hasText():  # Handle plain text drops
            self.value.setText(mime.text())
            self.value.settText(mime.text())
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

            self.value.setText(', '.join(textList))

            self.value.settText(', '.join(textList))

            print(f"Internal data dropped: {', '.join(textList)}")
            event.accept()

        else:
            print("Unsupported drop data type")
            event.ignore()
