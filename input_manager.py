from panda3d.core import KeyboardButton, MouseButton
from direct.showbase.DirectObject import DirectObject
import json
import sys
import toml
from PyQt5.QtWidgets import QApplication, QDialog, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QWidget, QComboBox, QMessageBox, QLabel
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import subprocess

class UDPClient(DatagramProtocol):
    def __init__(self, server_address):
        self.server_address = server_address

    def startProtocol(self):
        print(f"Attempting to connect to UDP Server at {self.server_address}")
    
    def send_data(self, data):
        """Send data to the UDP server with error handling."""
        try:
            self.transport.write(json.dumps(data).encode(), self.server_address)
        except Exception as e:
            print(f"Failed to send UDP data: {e}")
    
    def datagramReceived(self, data, addr):
        """Handle data received from the server."""
        print(f"Received from server: {data.decode()}")

class UDPServer(DatagramProtocol):
    def datagramReceived(self, data, addr):
        print(f"Received from {addr}: {data.decode()}")

class NetworkManager:
    _instance = None  # Singleton pattern

    def __new__(cls, *args, **kwargs):
        """Ensures only one instance exists."""
        if cls._instance is None:
            cls._instance = super(NetworkManager, cls).__new__(cls)
            cls._instance.__init_singleton__(*args, **kwargs)
        return cls._instance

    def __init_singleton__(self, server_address=("127.0.0.1", 9000), is_client=False):
        """Initialize networking for server or client mode."""
        self.server_address = server_address
        self.is_client = is_client
        self.udp_client = None
        self.behaviors = []

        if not is_client:
            self.start_network()
        else:
            self.connect_to_server()
            
    def register_behavior(self, behavior):
        """✅ Registers a behavior for network updates."""
        self.behaviors.append(behavior)

    def send_variable_update(self, entity_name, var_name, value, sync_type="udp"):
        """✅ Send a variable update to the network."""
        if self.is_client and self.udp_client:
            data = {"entity": entity_name, "variable": var_name, "value": value, "sync_type": sync_type}
            self.udp_client.send_data(data)
            print(f"📡 Sent {sync_type} update: {entity_name}.{var_name} = {value}")

    def start_network(self):
        """Start the server for multiplayer mode."""
        print("🟢 Starting UDP Server on port 9000...")
        reactor.listenUDP(9000, UDPServer())

    def connect_to_server(self):
        """Connect to the game server as a client."""
        print(f"🔵 Connecting to UDP Server at {self.server_address}...")
        self.udp_client = UDPClient(self.server_address)
        reactor.listenUDP(0, self.udp_client)



class InputManager(DirectObject):
    CONFIG_FILE = "input_config.toml"
    
    def __init__(self, network_manager=None):
        super().__init__()
        
        self.key_bindings, self.input_categories, self.network_mode = self.load_settings()
        self.pressed_keys = set()
        self.network_manager = network_manager if self.network_mode != "local" else None
        self.behaviors = []
        
        self.setup_key_listeners()
    
    def setup_key_listeners(self):
        """Binds key events dynamically based on the current key bindings."""
        for action, key in self.key_bindings.items():
            self.accept(key, self.handle_key_press, [action, True])
            self.accept(key + "-up", self.handle_key_press, [action, False])
    
    def handle_key_press(self, action, is_pressed):
        """Handles key press and forwards it to registered behaviors."""
        if is_pressed:
            self.pressed_keys.add(action)
        else:
            self.pressed_keys.discard(action)
        
        category = self.input_categories.get(action, "local")
        if self.network_manager:
            self.network_manager.send_input(action, category, is_pressed)

        # Notify all registered MonoBehavior scripts
        for behavior in self.behaviors:
            behavior.handle_input(action, is_pressed)
    
    def register_behavior(self, behavior):
        """Register a MonoBehavior script to receive input events."""
        self.behaviors.append(behavior)

    def handle_key_press(self, action, is_pressed):
        """Handles key press and forwards it to registered behaviors."""
        if is_pressed:
            self.pressed_keys.add(action)
        else:
            self.pressed_keys.discard(action)
        
        category = self.input_categories.get(action, "local")
        if self.network_manager:
            self.network_manager.send_input(action, category, is_pressed)

        # Notify all registered MonoBehavior scripts
        for behavior in self.behaviors:
            behavior.handle_input(action, is_pressed)
    
    def update(self):
        """Called every frame to process held keys."""
        for action in self.pressed_keys:
            category = self.input_categories.get(action, "local")
            if category == "udp" and self.network_manager:
                self.network_manager.send_input(action, "udp", True)

    def save_settings(self):
        """Saves keybindings and input categories to a TOML file."""
        config = {
            "key_bindings": self.key_bindings,
            "input_categories": self.input_categories,
            "network_mode": self.network_mode
        }
        with open(self.CONFIG_FILE, "w") as f:
            toml.dump(config, f)
        print("Input settings saved.")
    
    def load_settings(self):
        """Loads keybindings, input categories, and network mode from a TOML file."""
        try:
            with open(self.CONFIG_FILE, "r") as f:
                config = toml.load(f)
            print("Loaded input settings:", config)
            return (
                config.get("key_bindings", {}),
                config.get("input_categories", {}),
                config.get("network_mode", "local")
            )
        except FileNotFoundError:
            print("No input config found, using defaults.")
            return {
                "forward": "w",
                "left": "a",
                "back": "s",
                "right": "d",
                "jump": "space",
                "trade_request": "t",
            }, {
                "forward": "udp",
                "left": "udp",
                "back": "udp",
                "right": "udp",
                "jump": "udp",
                "trade_request": "tcp",
            }, "local"

class NetworkSettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Network Settings")
        self.setGeometry(100, 100, 400, 300)

        self.layout = QVBoxLayout()

        self.mode_label = QLabel("Select Game Mode:")
        self.mode_dropdown = QComboBox()
        self.mode_dropdown.addItems(["Singleplayer", "Local Host", "Dedicated Server"])
        
        self.sync_label = QLabel("Variable Sync Mode:")
        self.sync_dropdown = QComboBox()
        self.sync_dropdown.addItems(["Public", "Private", "Shared"])

        self.start_button = QPushButton("Start Game")
        self.start_button.clicked.connect(self.start_game)

        self.layout.addWidget(self.mode_label)
        self.layout.addWidget(self.mode_dropdown)
        self.layout.addWidget(self.sync_label)
        self.layout.addWidget(self.sync_dropdown)
        self.layout.addWidget(self.start_button)
        self.setLayout(self.layout)

    def start_game(self):
        selected_mode = self.mode_dropdown.currentText()
        sync_mode = self.sync_dropdown.currentText()

        # ✅ Save to a temporary config file
        with open("network_config.txt", "w") as f:
            f.write(f"mode={selected_mode}\nsync={sync_mode}")

        # ✅ Start the correct server mode
        if selected_mode == "Singleplayer":
            command = ["python", "preview_build.py"]
        elif selected_mode == "Local Host":
            command = ["python", "preview_build.py", "--server"]
        elif selected_mode == "Dedicated Server":
            command = ["python", "preview_build.py", "--server", "--headless"]

        subprocess.Popen(command, shell=True)
        QMessageBox.information(self, "Game Started", f"Game started in {selected_mode} mode.")


class InputSettingsWindow(QDialog):
    def __init__(self, input_manager):
        super().__init__()
        self.input_manager = input_manager
        self.setWindowTitle("Input Settings")
        self.setGeometry(100, 100, 500, 400)

        self.layout = QVBoxLayout()
        self.table = QTableWidget(len(self.input_manager.key_bindings), 3)
        self.table.setHorizontalHeaderLabels(["Action", "Key", "Category"])
        
        for row, (action, key) in enumerate(self.input_manager.key_bindings.items()):
            self.table.setItem(row, 0, QTableWidgetItem(action))
            self.table.setItem(row, 1, QTableWidgetItem(key))
            category_dropdown = QComboBox()
            category_dropdown.addItems(["local", "udp", "tcp"])
            category_dropdown.setCurrentText(self.input_manager.input_categories.get(action, "local"))
            self.table.setCellWidget(row, 2, category_dropdown)
        
        self.layout.addWidget(self.table)
        
        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self.save_bindings)
        
        self.layout.addWidget(self.save_button)
        self.setLayout(self.layout)
    
    def save_bindings(self):
        for row in range(self.table.rowCount()):
            action = self.table.item(row, 0).text()
            key = self.table.item(row, 1).text()
            category_dropdown = self.table.cellWidget(row, 2)
            category = category_dropdown.currentText()
            self.input_manager.key_bindings[action] = key
            self.input_manager.input_categories[action] = category
        self.input_manager.save_settings()
        print("Bindings Updated:", self.input_manager.key_bindings)
        print("Categories Updated:", self.input_manager.input_categories)

    
    def reset_bindings(self):
        self.input_manager.__init__()
        self.__init__(self.input_manager)
        self.show()
        
class SyncVariableSettings(QDialog):
    def __init__(self, behavior):
        super().__init__()
        self.behavior = behavior
        self.setWindowTitle("Sync Variables Settings")
        self.setGeometry(100, 100, 500, 400)

        self.layout = QVBoxLayout()
        self.table = QTableWidget(len(vars(behavior)), 2)
        self.table.setHorizontalHeaderLabels(["Variable", "Sync Type"])

        for row, var_name in enumerate(vars(behavior).keys()):
            self.table.setItem(row, 0, QTableWidgetItem(var_name))
            sync_dropdown = QComboBox()
            sync_dropdown.addItems(["none", "udp", "tcp"])
            sync_dropdown.setCurrentText(behavior.sync_variables.get(var_name, "none"))
            self.table.setCellWidget(row, 1, sync_dropdown)

        self.save_button = QPushButton("Save Sync Settings")
        self.save_button.clicked.connect(self.save_sync_settings)
        self.layout.addWidget(self.table)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

    def save_sync_settings(self):
        """Save selected sync settings for each variable."""
        for row in range(self.table.rowCount()):
            var_name = self.table.item(row, 0).text()
            sync_dropdown = self.table.cellWidget(row, 1)
            sync_type = sync_dropdown.currentText()

            if sync_type != "none":
                self.behavior.mark_variable_for_sync(var_name, sync_type)
        
        QMessageBox.information(self, "Saved", "Sync settings updated!")
