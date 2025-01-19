# preview_build.py

import os
import toml
from direct.showbase.ShowBase import ShowBase
from Entity import load_all_entities_from_folder

class GamePreviewApp(ShowBase):
    def __init__(self):
        super().__init__()
        self.disableMouse()  # Disable default camera controls
        self.entities = []

        # Load all entities from the 'saves' folder
        data_folder = "saves"
        self.entities = load_all_entities_from_folder(data_folder, self.render)

        self.setup_camera()

    def setup_camera(self):
        # Position the camera to view the scene
        self.camera.setPos(0, -50, 20)
        self.camera.lookAt(0, 0, 0)

    def recreate_entities(self):
        """
        Recreate all entities from the scene data.
        Useful for resetting the scene or reloading.
        """
        # Remove existing entities
        for entity in self.entities:
            entity.node.removeNode()
        self.entities.clear()

        # Reload entities
        self.entities = load_all_entities_from_folder("saves", self.render)

if __name__ == "__main__":
    app = GamePreviewApp()
    app.run()
