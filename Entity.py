import os
import toml
from panda3d.core import Vec3
from script_loader import load_script
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor


from panda3d.core import PointLight, Spotlight, DirectionalLight, Vec4, NodePath

class LightEntity:
    def __init__(self, light_type="point", color=(1, 1, 1, 1), position=(0, 0, 10)):
        self.node = NodePath("Light")
        
        if light_type == "directional":
            self.light = DirectionalLight("directionalLight")
            self.node.setPos(position)
        elif light_type == "spot":
            self.light = Spotlight("spotlight")
            self.node.setPos(position)
        else:  # Default to Point Light
            self.light = PointLight("pointLight")
            self.node.setPos(position)
        
        self.light.setColor(Vec4(*color))
        self.node.setLight(self.node.attachNewNode(self.light))



class Entity:
    def __init__(self, data, input_manager, network_manager=None):
        self.input_manager = input_manager
        self.name = data.get("name", "Unnamed")
        self.entity_model = data.get("entity_model")
        self.entity_id = data.get("id")
        self.properties = data.get("properties", {})
        self.transform = data.get("transform", {})
        self.node = None
        self.behavior_instances = []  # Store multiple behavior instances
        self.network_manager = network_manager

    def load(self, render):
        if not self.entity_model:
            print(f"No model specified for entity '{self.name}'")
            return

        self.node = loader.loadModel(os.path.relpath(self.entity_model))
        self.node.setName(self.name)
        self.node.set_python_tag("id", self.entity_id)

        pos = Vec3(*self.transform.get("position", {"x": 0.0, "y": 0.0, "z": 0.0}).values())
        hpr = Vec3(*self.transform.get("rotation", {"h": 0.0, "p": 0.0, "r": 0.0}).values())
        scl = Vec3(*self.transform.get("scale", {"x": 1.0, "y": 1.0, "z": 1.0}).values())

        self.node.setPos(pos)
        self.node.setHpr(hpr)
        self.node.setScale(scl)
        self.node.reparentTo(render)

        self.load_behaviors()

    def load_behaviors(self):
        script_paths = self.properties.get("script_paths", {})
        script_properties = self.properties.get("script_properties", {})
        scripts = {}

        for script_path in script_paths.keys():
            try:
                module = load_script(script_path)
                class_name = os.path.splitext(os.path.basename(script_path))[0]
                if hasattr(module, class_name):
                    behavior_class = getattr(module, class_name)
                    instance = behavior_class(self.node, self.network_manager, self.input_manager) if self.network_manager else behavior_class(self.node, self.input_manager)
                    instance.node = self.node
                    
                    # Auto-register public variables with defined sync categories
                    for attr in dir(instance):
                        if not attr.startswith("_") and not callable(getattr(instance, attr)):
                            sync_category = getattr(instance, f"_{attr}_sync", "private")
                            if self.network_manager and sync_category == "shared":
                                self.network_manager.register_behavior(instance)
                    
                    for key, value in script_properties.get(script_path, {}).items():
                        setattr(instance, key, value)
                    
                    self.behavior_instances.append(instance)
                    scripts[script_path] = instance
                else:
                    print(f"Class '{class_name}' not found in '{script_path}'")
            except Exception as e:
                print(f"Error loading script '{script_path}': {e}")

        self.node.set_python_tag("scripts", scripts)


def load_entity_from_toml(file_path, render, network_manager=None, input_manager=None):
    data = toml.load(file_path)
    entity = Entity(data, network_manager, input_manager)
    entity.load(render)
    return entity


def load_all_entities_from_folder(folder_path, render, network_manager=None, input_manager=None):
    entities = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".toml"):
            file_path = os.path.join(folder_path, filename)
            entity = load_entity_from_toml(file_path, render, network_manager, input_manager)
            if entity.node:
                entities.append(entity)
    return entities
