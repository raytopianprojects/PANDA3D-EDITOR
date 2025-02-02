import os

import sys

import toml
from direct.showbase.ShowBase import ShowBase
from Entity import load_all_entities_from_folder
from input_manager import InputManager, NetworkManager  # Import InputManager & NetworkManager

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

class GamePreviewApp(ShowBase):
    def __init__(self, network_manager):
        super().__init__()
        self.network_manager = network_manager  # ✅ Store the network manager
        self.disableMouse()
        self.entities = []

        # Load all entities from the 'saves' folder
        data_folder = "saves"
        self.input_manager = InputManager(network_manager=self.network_manager)
        self.entities = load_all_entities_from_folder(data_folder, self.render, self.network_manager, self.input_manager)


        # Set up networking based on the input configuration
        self.network_manager = self.setup_networking()
        

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
        self.entities = load_all_entities_from_folder("saves", self.render, self.network_manager, self.input_manager)
        
    

if __name__ == "__main__":
    if "--server" in sys.argv:
        print("Starting dedicated server...")
        from input_manager import NetworkManager
        
        network_manager = NetworkManager()
        network_manager.connect_to_server()
        
        # Run server without rendering the game
        while True:
            reactor.run(installSignalHandlers=False)
    if "--client" in sys.argv:
        server_ip = "127.0.0.1"  # Default to localhost
        if "--connect" in sys.argv:
            idx = sys.argv.index("--connect") + 1
            if idx < len(sys.argv):
                server_ip = sys.argv[idx]

        print(f"Connecting to server at {server_ip}...")
        
        from input_manager import NetworkManager

        network_manager = NetworkManager(server_address=(server_ip, 9000), is_client=True)
        app = GamePreviewApp(network_manager=network_manager)
        app.run()
    else:
    
        app = GamePreviewApp()
        app.run()
