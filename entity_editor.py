from panda3d.core import NodePath, Loader
import toml
import os
import importlib.util

class Load:
    def load_scene_from_toml(self, input_folder: str, root_node: NodePath):
        """
        Load entities from TOML files, reconstruct them in the scene graph, attach models, scripts, and build a list of entities.

        Args:
            input_folder (str): Folder where TOML files are stored.
            root_node (NodePath): The root node to attach loaded entities to.

        Returns:
            list: A list of dictionaries containing all entity data.
        """
        # Check if the input folder exists
        if not os.path.exists(input_folder):
            print(f"Input folder {input_folder} does not exist.")
            return []

        entities = []  # List to store all entities

        # Iterate over all TOML files in the input folder
        for file_name in os.listdir(input_folder):
            if file_name.endswith(".toml"):  # Process only TOML files
                file_path = os.path.join(input_folder, file_name)

                # Load the TOML file
                with open(file_path, "r") as file:
                    entity_data = toml.load(file)

                # Iterate over all entities in the file
                for node_name, entity in entity_data.items():
                    # Extract data from the entity
                    entity_id = entity.get("id")
                    name = entity.get("name", "Unnamed")
                    transform = entity.get("transform", {})
                    properties = entity.get("properties", {})
                    script_path = entity.get("script")  # Path to the script file
                    model_path = entity.get("entity_model")  # Path to the model file

                    # Load the model and attach it to the scene
                    if model_path and os.path.exists(model_path):
                        entity_node = Loader.get_global_ptr().load_model(model_path)
                        if not entity_node:
                            print(f"Failed to load model for entity '{name}' from {model_path}")
                            continue
                        entity_node.set_name(name)  # Set the name of the NodePath
                        entity_node.reparent_to(root_node)
                    else:
                        print(f"No valid model found for entity '{name}' or model path invalid: {model_path}")
                        continue

                    # Set the ID tag
                    entity_node.set_python_tag("id", entity_id)

                    # Set the transform properties
                    position = transform.get("position", {"x": 0, "y": 0, "z": 0})
                    rotation = transform.get("rotation", {"h": 0, "p": 0, "r": 0})
                    scale = transform.get("scale", {"x": 1, "y": 1, "z": 1})
                    entity_node.set_pos(position["x"], position["y"], position["z"])
                    entity_node.set_hpr(rotation["h"], rotation["p"], rotation["r"])
                    entity_node.set_scale(scale["x"], scale["y"], scale["z"])

                    # Set custom properties
                    for key, value in properties.items():
                        entity_node.set_python_tag(key, value)

                    # Attach script to the entity
                    if script_path and os.path.exists(script_path):
                        try:
                            script_instance = self.load_script(script_path, entity_node)
                            entity_node.set_python_tag("script_instance", script_instance)
                            print(f"Script attached to entity '{name}' from {script_path}")
                        except Exception as e:
                            print(f"Error loading script {script_path} for entity '{name}': {e}")
                    else:
                        print(f"No script found for entity '{name}' or script path invalid: {script_path}")

                    # Append the entity to the list with all its data
                    entities.append({
                        "name": name,
                        "id": entity_id,
                        "transform": transform,
                        "properties": properties,
                        "script": script_path,
                        "model": model_path
                    })

                    print(f"Loaded entity '{name}' with ID '{entity_id}' and model '{model_path}'")

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
                    node.get_name() : {
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
                }

                # Convert dictionary to TOML string
                toml_string = toml.dumps(entity_data)

                # Save to a file with the node's name and ID
                file_name = f"{node.get_name()}_{entity_id}.toml"
                file_path = os.path.join(output_folder, file_name)
                with open(file_path, "w") as file:
                    file.write(toml_string)

                print(f"Saved {file_name} to {output_folder}")