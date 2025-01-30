import os
import toml
from direct.showbase.ShowBase import ShowBase
from Entity import load_all_entities_from_folder
from input_manager import InputManager, NetworkManager  # Import InputManager & NetworkManager

class GamePreviewApp(ShowBase):
    def __init__(self):
        super().__init__()
        self.disableMouse()
        self.entities = []

        # Load all entities from the 'saves' folder
        data_folder = "saves"
        self.entities = load_all_entities_from_folder(data_folder, self.render)

        # Set up networking based on the input configuration
        self.network_manager = self.setup_networking()
        
        # Load input manager with networking configuration
        self.input_manager = InputManager(network_manager=self.network_manager)

        self.setup_camera()
        self.taskMgr.add(self.update, "inputUpdateTask")

    def setup_camera(self):
        self.camera.setPos(0, -50, 20)
        self.camera.lookAt(0, 0, 0)

    def setup_networking(self):
        """Determines if networking should be enabled in preview mode."""
        try:
            with open("input_config.toml", "r") as f:
                config = toml.load(f)
                networking_enabled = any(cat in ["udp", "tcp"] for cat in config.get("input_categories", {}).values())
        except FileNotFoundError:
            networking_enabled = False  # Default to local-only

        return NetworkManager() if networking_enabled else None

    def update(self, task):
        """Live updates input settings dynamically during preview mode."""
        self.input_manager.update()
        return task.cont

    def recreate_entities(self):
        """Reload all entities when required (e.g., if settings change)."""
        for entity in self.entities:
            entity.node.removeNode()
        self.entities.clear()
        self.entities = load_all_entities_from_folder("saves", self.render)

if __name__ == "__main__":
    app = GamePreviewApp()
    app.run()
