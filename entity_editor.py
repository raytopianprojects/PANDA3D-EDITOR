from panda3d.core import NodePath, Loader
import toml
import os
import importlib.util

import os

import zipfile
import toml
from panda3d.core import NodePath  # Assuming NodePath is from panda3d.core

from panda3d.core import PointLight, Spotlight, DirectionalLight, AmbientLight, Vec4, Vec3

class MapLoader:
    def __init__(self, world):
        self.world = world

    def extract_map(self, map_file, extract_to):
        """Extracts the .map file (ZIP archive) to a target directory."""
        if not os.path.exists(map_file):
            print(f"❌ Map file not found: {map_file}")
            return False
        if os.path.isfile(map_file):
            print(f"❌ Map file not found: {map_file}")
            return False

        os.makedirs(extract_to, exist_ok=True)  # Ensure target directory exists

        try:
            with zipfile.ZipFile(map_file, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            print(f"📂 Extracted map to {extract_to}")
            return True
        except Exception as e:
            print(f"❌ Failed to extract .map file: {e}")
            return False

    def load_map(self, map_file):
        """Extracts and loads a .map file into the scene."""
        extract_dir = f"./maps_extracted/{os.path.basename(map_file).replace('.map', '')}"

        if self.extract_map(self, map_file, extract_dir):
            print("✅ Map extraction successful, loading scene...")
            entity_loader = Load.load_project_from_folder_toml(extract_dir, self.world.render)
            print("🎮 Scene loaded successfully!")
        else:
            print("❌ Failed to load map.")

class Load:
    def __init__(self, world):
        self.world = world
        
    def load_lights_from_toml(self, file_path: str, render):
        """
        Load lights from a TOML file and attach them to the render node.

        Args:
            file_path (str): Path to the TOML file.
            render (NodePath): The root node to attach lights to.
        """
        if not file_path or not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return

        with open(file_path, "r") as file:
            lights_data = toml.load(file)

        for light_name, light_data in lights_data.items():
            light_type = light_data.get("type", "point")
            position = light_data.get("position", {"x": 0, "y": 0, "z": 0})
            color = light_data.get("color", {"r": 1.0, "g": 1.0, "b": 1.0, "a": 1.0})

            if light_type == "point":
                light = PointLight(light_name)
            elif light_type == "directional":
                light = DirectionalLight(light_name)
            elif light_type == "spot":
                light = Spotlight(light_name)
                fov = light_data.get("fov", 45.0)
                light.getLens().setFov(fov)
            else:
                print(f"Unsupported light type: {light_type}")
                continue

            light.setColor(Vec4(color["r"], color["g"], color["b"], color["a"]))
            light_node = render.attachNewNode(light)
            light_node.setPos(Vec3(position["x"], position["y"], position["z"]))

            if light_type in ["directional", "spot"]:
                direction = light_data.get("direction", {"x": 0, "y": -1, "z": 0})
                light_node.lookAt(Vec3(direction["x"], direction["y"], direction["z"]))

            render.setLight(light_node)

        print(f"Lights loaded from {file_path}")

    def load_ui_from_folder_toml(self, input_folder: str, root_node: NodePath):
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
        
        with open(input_folder, "r") as file:
            input_folder = file.read().strip()

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
                widget_type = entity_data.get("widget_type", "")
                action = entity_data.get("action", "")
                properties = entity_data.get("properties", {})
                specials = properties.get("specials", "")
                __UIEditorLabel__ = specials.get("__UIEditorLabel__", "")
                __UIEditorButton__ = specials.get("__UIEditorButton__", "")
                
                if __UIEditorLabel__ != "":
                    text = __UIEditorLabel__.get("text", "")
                
                if __UIEditorButton__ != "":
                    text = __UIEditorButton__.get("text", "")
                    
                coloring = entity_data.get("coloring", {})
                frame_color = coloring.get("frameColor1", {"r": 0.5, "g": 0.5, "b": 0.5})
                color = coloring.get("text_fg1", {"r": 1.0, "g": 1.0, "b": 1.0})
                image = entity_data.get("image", "")
                parent = entity_data.get("parent", "")

                transform = entity_data.get("transform", {})
                isCanvas = entity_data.get("isCanvas", False)
                isLabel = entity_data.get("isLabel", False)
                isButton = entity_data.get("isButton", False)
                isImage = entity_data.get("isImage", False)
                #TODO load UI object to ui editor

                # Set transformation properties
                position = transform.get("position", {"x": 0, "y": 0, "z": 0})
                rotation = transform.get("rotation", {"h": 0, "p": 0, "r": 0})
                scale = transform.get("scale", {"x": 0.1, "y": 0.1, "z": 0.1})
                parent = properties.get("parent", self.world.render2d)
                script_paths = properties.get("script_paths", "")
                s_property = properties.get("script_properties", "")

                if widget_type == "l":
                    self.widget = self.world.recreate_widget(text, frame_color, color, scale, position, parent)
                    self.widget.set_python_tag("widget_type", "l")
                    
                if widget_type == "b":
                    self.widget = self.world.recreate_button(text, frame_color, color, scale, position, parent)
                    self.widget.set_python_tag("widget_type", "b")
                    
                if widget_type == None:
                    self.widget = NodePath("None")
                    
                # Set properties
                for key, value in properties.items():
                    self.widget.set_python_tag(key, value)
                for s in script_paths:
                    prop = {}

                    for attr, value in s_property.items():
                        prop[attr] = (value)
                        print("iiii:", value)
                    prop.clear()
                # Append entity data to the list
                entities.append({
                    "name": name,
                    "id": entity_id,
                    "transform": transform,
                    "properties": properties,
                    "model": model_path
                })

                self.world.hierarchy_tree1.clear()
                self.world.populate_hierarchy(self.world.hierarchy_tree1, self.world.render2d)
                
                print(f"Entity '{name}' with ID '{entity_id}' loaded.")

        return entities
    def load_project_from_folder_toml(self, input_folder: str, root_node: NodePath):
        """Load entities from TOML files, reconstruct models, attach scripts, lights, and particles."""
        if not os.path.exists(input_folder):
            print(f"❌ Input folder {input_folder} does not exist.")
            return []
        
        self.load_lights_from_toml(input_folder + "lights.toml", root_node)

        entities = []
        for file_name in os.listdir(input_folder):
            if file_name.endswith(".toml"):
                file_path = os.path.join(input_folder, file_name)
                with open(file_path, "r") as file:
                    entity_data = toml.load(file)

                # Extract entity details
                name = entity_data.get("name", "Unnamed")
                entity_id = entity_data.get("id", None)
                model_path = entity_data.get("entity_model", "")
                transform = entity_data.get("transform", {})

                # Load the model
                entity_node = root_node.attach_new_node(name)
                if model_path and os.path.exists(model_path):
                    model = loader.load_model(model_path)
                    model.reparent_to(entity_node)
                    print(f"✅ Loaded model for {name}: {model_path}")

                # Apply transformations
                pos = transform.get("position", {"x": 0, "y": 0, "z": 0})
                rot = transform.get("rotation", {"h": 0, "p": 0, "r": 0})
                scale = transform.get("scale", {"x": 1, "y": 1, "z": 1})
                entity_node.set_pos(pos["x"], pos["y"], pos["z"])
                entity_node.set_hpr(rot["h"], rot["p"], rot["r"])
                entity_node.set_scale(scale["x"], scale["y"], scale["z"])

                # Restore Lights
                for light_data in entity_data.get("lights", []):
                    light_type = light_data["type"]
                    light_color = light_data["color"]
                    light_pos = light_data["position"]

                    if light_type == "PointLight":
                        light = PointLight(name + "_light")
                    elif light_type == "Spotlight":
                        light = Spotlight(name + "_light")
                    elif light_type == "AmbientLight":
                        light = AmbientLight(name + "_light")
                    elif light_type == "DirectionalLight":
                        light = DirectionalLight(name + "_light")
                    else:
                        print(f"⚠️ Unknown light type: {light_type}")
                        continue

                    light.set_color((light_color["r"], light_color["g"], light_color["b"], 1))
                    light_np = entity_node.attach_new_node(light)
                    light_np.set_pos(light_pos["x"], light_pos["y"], light_pos["z"])
                    root_node.set_light(light_np)

                # Restore Particles
                for particle_data in entity_data.get("particles", []):
                    particle_name = particle_data["name"]
                    print(f"✨ Restoring particle effect: {particle_name} for {name}")
                    # TODO: Add actual particle loading logic here

                # Store entity reference
                entities.append(entity_node)
                print(f"✅ Entity {name} restored with lights and particles.")

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
    def __init__(self):
        pass
    def save_lights_to_toml(self, lights, file_path):
        """
        Save all lights in the scene to a TOML file.

        Args:
            lights (list): A list of NodePath objects with lights attached.
            file_path (str): Path to the TOML file to save.
        """
        lights_data = {}

        for i, light_node in enumerate(lights):
            light = light_node.node()
            light_data = {
                "type": "",
                "position": {
                    "x": light_node.getX(),
                    "y": light_node.getY(),
                    "z": light_node.getZ(),
                },
                "color": {
                    "r": light.getColor()[0],
                    "g": light.getColor()[1],
                    "b": light.getColor()[2],
                    "a": light.getColor()[3],
                },
            }

            if isinstance(light, PointLight):
                light_data["type"] = "point"
            if isinstance(light, AmbientLight):
                light_data["type"] = "ambient"
            elif isinstance(light, DirectionalLight):
                light_data["type"] = "directional"
                light_data["direction"] = {
                    "x": light_node.getQuat().getForward()[0],
                    "y": light_node.getQuat().getForward()[1],
                    "z": light_node.getQuat().getForward()[2],
                }
            elif isinstance(light, Spotlight):
                light_data["type"] = "spot"
                light_data["direction"] = {
                    "x": light_node.getQuat().getForward()[0],
                    "y": light_node.getQuat().getForward()[1],
                    "z": light_node.getQuat().getForward()[2],
                }
                light_data["fov"] = light.getLens().getFov()[0]

            lights_data[f"light_{i+1}"] = light_data

        with open(file_path, "w") as file:
            toml.dump(lights_data, file)
            
    def save_scene_to_toml(self, root_node: NodePath, output_folder: str):
        """Traverse the scene graph, extract entity data, and save each entity to a TOML file."""
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            
        lights = [node for node in root_node.find_all_matches('**/+Light')]

        self.save_lights_to_toml(self, lights, "/saves/lights.toml")

        for node in root_node.find_all_matches("**"):  # Traverse all nodes in the scene graph
            tags = node.get_python_tag_keys()
            if "id" in tags:
                entity_id = node.get_python_tag("id")
                model_path = node.get_python_tag("model_path")

                # Get transform properties
                position = node.get_pos()
                rotation = node.get_hpr()
                scale = node.get_scale()




                # Store entity data
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
                    "lights": lights,

                }

                # Convert dictionary to TOML
                file_name = f"{node.get_name()}_{entity_id}.toml"
                file_path = os.path.join(output_folder, file_name)
                with open(file_path, "w") as file:
                    toml.dump(entity_data, file)

                print(f"✅ Saved {file_name} including lights & particles to {output_folder}")
                
    def save_scene_to_map(self, directory, lights_directory, output_zip):
        """
        Zips TOML files from two directories:
          - TOML files in the top level of `directory`
          - TOML files in the top level of `lights_directory`

        Files from lights_directory will be stored in a subfolder (e.g., "lights")
        within the ZIP archive.

        Args:
            directory (str): Main directory to search for TOML files.
            lights_directory (str): Extra directory (e.g., "/saves/lights") to search for TOML files.
            output_zip (str): Output zip file name (with .zip extension, or .map if you prefer).
        """
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Process the main directory (only the top-level files)
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith('.toml'):
                        file_path = os.path.join(root, file)
                        # Store only the filename (or adjust if you need a subfolder)
                        zipf.write(file_path, arcname=file)
                # Break to avoid processing subdirectories
                break

            # Process the lights directory (only top-level files)
            for root, dirs, files in os.walk(lights_directory):
                for file in files:
                    if file.endswith('.toml'):
                        file_path = os.path.join(root, file)
                        # Store under a "lights" folder in the zip file
                        zipf.write(file_path, arcname=os.path.join("lights", file))
                # Break to avoid recursing into subdirectories
                break

    
    
                
    def save_scene_ui_to_toml(self, root_node: NodePath, output_folder: str, file_name: str):
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
            print(node)

            # Check if the node has an 'id' tag
            if "id" in tags:
                entity_id = node.get_python_tag("id")
                
                model_path = node.get_python_tag("model_path")
                widget_type = node.get_python_tag("widget_type")

                # Get transform properties
                position = node.get_pos()
                rotation = node.get_hpr()
                scale = node.get_scale()

                frame_color = node.get_python_tag("frameColor1")
                color = node.get_python_tag("text_fg1")

                action = node.get_python_tag("action")
                text = node.get_python_tag("text")
                image = node.get_python_tag("image")
                parent = node.get_python_tag("parent")
                isCanvas = node.get_python_tag("isCanvas")
                isLabel = node.get_python_tag("isLabel")
                isButton = node.get_python_tag("isButton")
                isImage = node.get_python_tag("isImage")
                
                # Get custom properties
                properties = {}
                for key in tags:
                    if key not in ("id",
                                   "pos",
                                   "hpr",
                                   "scale",
                                   "scripts",
                                   "text",
                                   "image",
                                   "parent",
                                   "action",
                                   "isCanvas",
                                   "isLabel",
                                   "isButton",
                                   "isImage",
                                   "frameColor1",
                                   "text_fg1",
                                   "frameColor",
                                   "text_fg",
                                   "ui_reference"):  # Exclude transform tags
                        properties[key] = node.get_python_tag(key)
                print(frame_color)
                # Create a dictionary to store entity data
                entity_data = {
                    "name": node.get_name(),
                    "id": entity_id,
                    "widget_type": widget_type,
                    "text1" : text,
                    "type": "script",
                    "action" : action,
                    "image" : image,
                    "parent" : parent,
                    "transform": {
                        "position": {"x": position.x, "y": position.y, "z": position.z},
                        "rotation": {"h": rotation.x, "p": rotation.y, "r": rotation.z},
                        "scale": {"x": scale.x, "y": scale.y, "z": scale.z},
                    },
                    "properties": properties,
                    "isCanvas": isCanvas,
                    "isLabel": isLabel,
                    "isButton": isButton,
                    "isImage": isImage,
                }
                # Conditionally add 'coloring' if widget_type == "l"
                if widget_type == "l":
                    entity_data["coloring"] = {
                        "frameColor1": {"r": frame_color["r"], "g": frame_color["g"], "b": frame_color["b"]},
                        "text_fg1": {"r": color["r"], "g": color["g"], "b": color["b"]},
                    }
                if widget_type == "b":
                    entity_data["coloring"] = {
                        "frameColor1": {"r": frame_color["r"], "g": frame_color["g"], "b": frame_color["b"]},
                        "text_fg1": {"r": color["r"], "g": color["g"], "b": color["b"]},
                    }

                # Convert dictionary to TOML string
                toml_string = toml.dumps(entity_data)
                # Save to a file with the node's name and ID
                file_name = f"{node.get_name()}_{entity_id}.toml"
                file_path = os.path.join(output_folder, file_name)
                with open(file_path, "w") as file:
                    file.write(toml_string)
        def zip_toml_files(source_dir, output_file):
            # Create a .zip file with the .ui extension
            with zipfile.ZipFile(output_file, 'w') as zipf:
                # Iterate through all files in the source directory
                for foldername, subfolders, filenames in os.walk(source_dir):
                    for filename in filenames:
                        # Check if the file has a .toml extension
                        if filename.endswith('.toml'):
                            filepath = os.path.join(foldername, filename)
                            # Write the .toml file to the .zip file
                            zipf.write(filepath, os.path.relpath(filepath, source_dir))
            print(f"Zipped all .toml files into: {output_file}")
        zip_toml_files("./saves/ui", file_name + ".ui")


                

                
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