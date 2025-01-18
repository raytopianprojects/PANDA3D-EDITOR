import os
import toml
import importlib.util
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Vec3, Filename

def load_script(script_path):
    """Dynamically load a Python module from a given file path."""
    module_name = os.path.splitext(os.path.basename(script_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    else:
        raise ImportError(f"Could not load script: {script_path}")

class Entity:
    def __init__(self, data):
        self.name = data.get("name", "Unnamed")
        self.entity_model = data.get("entity_model")
        self.entity_id = data.get("id")
        self.properties = data.get("properties", {})
        self.transform = data.get("transform", {})
        self.node = None
        self.behavior_instance = None

    def load(self, render):
        # Load model
        if not self.entity_model:
            print(f"No model specified for entity {self.name}")
            return
        
        self.node = loader.loadModel(os.path.relpath(self.entity_model))
        self.node.setName(self.name)
        self.node.set_python_tag("id", self.entity_id)

        # Set transform
        pos_data = self.transform.get("position", {})
        rot_data = self.transform.get("rotation", {})
        scale_data = self.transform.get("scale", {})

        pos = Vec3(pos_data.get("x", 0.0), pos_data.get("y", 0.0), pos_data.get("z", 0.0))
        hpr = Vec3(rot_data.get("h", 0.0), rot_data.get("p", 0.0), rot_data.get("r", 0.0))
        scl = Vec3(scale_data.get("x", 1.0), scale_data.get("y", 1.0), scale_data.get("z", 1.0))

        self.node.setPos(pos)
        self.node.setHpr(hpr)
        self.node.setScale(scl)
        self.node.reparentTo(render)

        # Load behavior scripts if available
        script_paths = self.properties.get("script_paths", {})
        script_properties = self.properties.get("script_properties", {})
        scripts = {}
        for script_path in script_paths.keys():
            try:
                module = load_script(script_path)
                class_name = os.path.splitext(os.path.basename(script_path))[0]
                if hasattr(module, class_name):
                    behavior_class = getattr(module, class_name)
                    self.behavior_instance = behavior_class(self.node)
                    # Apply script properties
                    props = script_properties.get(script_path, {})
                    for key, value in props.items():
                        setattr(self.behavior_instance, key, value)
                    scripts[script_path] = self.behavior_instance
                else:
                    print(f"Class {class_name} not found in {script_path}")
            except Exception as e:
                print(f"Error loading script {script_path}: {e}")

        self.node.set_python_tag("scripts", scripts)

def load_entity_from_toml(file_path, render):
    """Load a single entity from a TOML file."""
    data = toml.load(file_path)
    entity = Entity(data)
    entity.load(render)
    return entity

def load_all_entities_from_folder(folder_path, render):
    """Load all entities defined in TOML files within a folder."""
    entities = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".toml"):
            file_path = os.path.join(folder_path, filename)
            entity = load_entity_from_toml(file_path, render)
            if entity.node:
                entities.append(entity)
    return entities

class GamePreviewApp(ShowBase):
    def __init__(self):
        super().__init__()
        self.disableMouse()  # Optional: Disable default camera controls
        self.entities = []

        # Load all entities from the game_data folder
        data_folder = "saves"  # Folder containing TOML files
        self.entities = load_all_entities_from_folder(data_folder, self.render)

        # Set up additional preview settings (camera, lighting, etc.) if desired
        self.setup_camera()

    def setup_camera(self):
        # Example: Position camera to see the scene
        self.camera.setPos(0, -50, 20)
        self.camera.lookAt(0, 0, 0)

if __name__ == "__main__":
    app = GamePreviewApp()
    app.run()
