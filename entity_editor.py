from panda3d.core import NodePath, Loader
import toml
import os
import importlib.util

import os
import toml
from panda3d.core import NodePath  # Assuming NodePath is from panda3d.core

class Load:
    def __init__(self, world):
        self.world = world

    def load_project_from_folder_toml(self, input_folder: str, root_node: NodePath):
        """
        Load entities from TOML files, reconstruct them in the scene graph, attach models, scripts, and build a list of entities.
        Args:
            input_folder (str): Folder where TOML files are stored.
            root_node (NodePath): The root node to attach loaded entities to.
        Returns:
            list: A list of dictionaries containing all entity data.
        """
        if not os.path.exists(input_folder):
            print(f"Input folder {input_folder} does not exist.")
            return []

        entities = []

        # Iterate over all TOML files in the input folder
        for file_name in os.listdir(input_folder):
            if file_name.endswith(".toml"):
                file_path = os.path.join(os.path.relpath(input_folder), file_name)
                with open(file_path, "r") as file:
                    entity_data = toml.load(file)

                # Extract data from the entity
                name = entity_data.get("name", "Unnamed")
                entity_id = entity_data.get("id", None)
                model_path = entity_data.get("entity_model", "")
                entity_type = entity_data.get("type", "")

                transform = entity_data.get("transform", {})
                properties = entity_data.get("properties", {})

                if model_path and os.path.exists(model_path):
                    entity_node = self.world.loader.load_model(os.path.relpath(model_path))
                    if entity_node:
                        entity_node.set_name(name)
                        entity_node.reparent_to(root_node)
                        print(f"Model loaded and attached for {name}: {model_path}")
                    else:
                        print(f"Failed to load model for {name} from {model_path}")
                        continue
                else:
                    print(f"Model path invalid or not found for {name}: {model_path}")
                    continue

                # Set transformation properties
                position = transform.get("position", {"x": 0, "y": 0, "z": 0})
                rotation = transform.get("rotation", {"h": 0, "p": 0, "r": 0})
                scale = transform.get("scale", {"x": 1, "y": 1, "z": 1})
                parent = properties.get("parent", None)
                entity_node.set_pos(position["x"], position["y"], position["z"])
                entity_node.set_hpr(rotation["h"], rotation["p"], rotation["r"])
                entity_node.set_scale(scale["x"], scale["y"], scale["z"])
                script_paths = properties.get("script_paths", "")
                s_property = properties.get("script_properties", "")

                # Set properties
                for key, value in properties.items():
                    entity_node.set_python_tag(key, value)
                    self.world.populate_hierarchy(self.world.hierarchy_tree, entity_node, parent)
                for s in script_paths:
                    prop = {}

                    for attr, value in s_property.items():
                        prop[attr] = (value)
                        print("iiii:", value)
                        self.world.script_inspector.set_script(os.path.relpath(s), entity_node, prop)
                    prop.clear()
                # Append entity data to the list
                entities.append({
                    "name": name,
                    "id": entity_id,
                    "transform": transform,
                    "properties": properties,
                    "model": model_path
                })

                print(f"Entity '{name}' with ID '{entity_id}' loaded.")

        return entities

    def load_script(self, script_path: str, node: NodePath):
        """
        Dynamically load a script and attach it to a NodePath.

        Args:
            script_path (str): Path to the Python script.
            node (NodePath): The NodePath to attach the script to.

        Returns:
            object: An instance of the script's class.
        """
        spec = importlib.util.spec_from_file_location("script", script_path)
        script_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(script_module)

        if hasattr(script_module, "Script"):
            return script_module.Script(node)
        else:
            raise AttributeError(f"The script at {script_path} does not define a 'Script' class.")



class Save():
    def save_scene_to_toml(self, root_node: NodePath, output_folder: str):
        """
        Traverse the scene graph, extract entity data, and save each entity to a TOML file.

        Args:
            root_node (NodePath): The root of the scene graph to traverse.
            output_folder (str): Folder where TOML files will be saved.
        """
        # Ensure the output folder exists
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        for node in root_node.find_all_matches("**"):  # Traverse all nodes in the scene graph
            tags = node.get_python_tag_keys()

            # Check if the node has an 'id' tag
            if "id" in tags:
                entity_id = node.get_python_tag("id")
                
                model_path = node.get_python_tag("model_path")

                # Get transform properties
                position = node.get_pos()
                rotation = node.get_hpr()
                scale = node.get_scale()

                # Get custom properties
                properties = {}
                for key in tags:
                    if key not in ("id", "pos", "hpr", "scale", "scripts"):  # Exclude transform tags
                        properties[key] = node.get_python_tag(key)

                # Create a dictionary to store entity data
                entity_data = {
                    "name": node.get_name(),
                    "id": entity_id,
                    "entity_model": model_path,
                    "type": "script",
                    "transform": {
                        "position": {"x": position.x, "y": position.y, "z": position.z},
                        "rotation": {"h": rotation.x, "p": rotation.y, "r": rotation.z},
                        "scale": {"x": scale.x, "y": scale.y, "z": scale.z},
                    },
                    "properties": properties
                }

                # Convert dictionary to TOML string
                toml_string = toml.dumps(entity_data)
                # Save to a file with the node's name and ID
                file_name = f"{node.get_name()}_{entity_id}.toml"
                file_path = os.path.join(output_folder, file_name)
                with open(file_path, "w") as file:
                    file.write(toml_string)
                print(f"Saved {file_name} to {output_folder}")
    def save_whole_scene_to_toml(self, root_node: NodePath, output_folder: str):
        """
        Traverse the scene graph, extract entity data, and save each entity to a TOML file.

        Args:
            root_node (NodePath): The root of the scene graph to traverse.
            output_folder (str): Folder where TOML files will be saved.
        """
        # Ensure the output folder exists
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        entity_data = {}
        for node in root_node.find_all_matches("**"):  # Traverse all nodes in the scene graph
            tags = node.get_python_tag_keys()

            # Check if the node has an 'id' tag
            if "id" in tags:
                entity_id = node.get_python_tag("id")
                
                model_path = node.get_python_tag("model_path")

                # Get transform properties
                position = node.get_pos()
                rotation = node.get_hpr()
                scale = node.get_scale()

                # Get custom properties
                properties = {}
                for key in tags:
                    if key not in ("id", "pos", "hpr", "scale", "scripts"):  # Exclude transform tags
                        properties[key] = node.get_python_tag(key)

                # Create a dictionary to store entity data
                entity_data[node.get_name()] = {
                    "name": node.get_name(),
                    "id": entity_id,
                    "entity_model": model_path,
                    "type": "script",
                    "transform": {
                        "position": {"x": position.x, "y": position.y, "z": position.z},
                        "rotation": {"h": rotation.x, "p": rotation.y, "r": rotation.z},
                        "scale": {"x": scale.x, "y": scale.y, "z": scale.z},
                    },
                    "properties": properties,
                }

        # Convert dictionary to TOML string
        toml_string = toml.dumps(entity_data)
        # Save to a file with the node's name and ID
        file_name = f"{node.get_name()}_{entity_id}.toml"
        file_path = os.path.join(output_folder, file_name)
        with open(file_path, "w") as file:
            file.write(toml_string)
        print(f"Saved {file_name} to {output_folder}")