from panda3d.core import NodePath
import toml
import os

class Load():
    def load_scene_from_toml(self, input_folder: str, root_node: NodePath):
        """
        Load entities from TOML files and reconstruct them in the scene graph.

        Args:
            input_folder (str): Folder where TOML files are stored.
            root_node (NodePath): The root node to attach loaded entities to.
        """
        # Check if the input folder exists
        if not os.path.exists(input_folder):
            print(f"Input folder {input_folder} does not exist.")
            return

        # Iterate over all TOML files in the input folder
        for file_name in os.listdir(input_folder):
            if file_name.endswith(".toml"):  # Process only TOML files
                file_path = os.path.join(input_folder, file_name)

                # Load the TOML file
                with open(file_path, "r") as file:
                    entity_data = toml.load(file)

                # Extract data from the TOML structure
                entity_id = entity_data.get("id")
                name = entity_data.get("name", "Unnamed")
                transform = entity_data.get("transform", {})
                properties = entity_data.get("properties", {})

                # Create a new NodePath for the entity
                entity_node = root_node.attach_new_node(name)

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

                print(f"Loaded entity '{name}' with ID '{entity_id}'")

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
                    "type": "script",
                    "name": node.get_name(),
                    "id": entity_id,
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