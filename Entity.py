# entity.py

import os
import toml
from panda3d.core import Vec3
from script_loader import load_script

class Entity:
    def __init__(self, data):
        self.name = data.get("name", "Unnamed")
        self.entity_model = data.get("entity_model")
        self.entity_id = data.get("id")
        self.properties = data.get("properties", {})
        self.transform = data.get("transform", {})
        self.node = None
        self.behavior_instances = []  # Store multiple behavior instances

    def load(self, render):
        # Load model
        if not self.entity_model:
            print(f"No model specified for entity '{self.name}'")
            return

        self.node = loader.loadModel(os.path.relpath(self.entity_model))
        self.node.setName(self.name)
        self.node.set_python_tag("id", self.entity_id)

        # Apply transformations
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
                    try:
                        # Instantiate behavior with node reference
                        instance = behavior_class(self.node)
                    except TypeError:
                        # If constructor doesn't accept arguments, instantiate without
                        instance = behavior_class()
                        if hasattr(instance, 'node'):
                            instance.node = self.node

                    # Apply script properties (public variables)
                    props = script_properties.get(script_path, {})
                    for key, value in props.items():
                        setattr(instance, key, value)

                    self.behavior_instances.append(instance)
                    scripts[script_path] = instance
                else:
                    print(f"Class '{class_name}' not found in '{script_path}'")
            except Exception as e:
                print(f"Error loading script '{script_path}': {e}")

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
