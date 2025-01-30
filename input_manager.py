from panda3d.core import KeyboardButton, MouseButton
from direct.showbase.DirectObject import DirectObject
import json
import sys
from PyQt5.QtWidgets import QApplication, QDialog, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QWidget, QComboBox, QMessageBox
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import toml

class InputManager(DirectObject):
    CONFIG_FILE = "input_config.toml"  # Store keybindings persistently


    def __init__(self, network_manager=None):
        super().__init__()
        
        self.key_bindings, self.input_categories = self.load_settings()
        
        self.pressed_keys = set()
        self.network_manager = network_manager
        self.behaviors = []
        
        self.setup_key_listeners()
        

    def save_settings(self):
        """Saves keybindings and input categories to a TOML file."""
        config = {
            "key_bindings": self.key_bindings,
            "input_categories": self.input_categories
        }
        with open(self.CONFIG_FILE, "w") as f:
            toml.dump(config, f)
        print("Input settings saved.")

    def load_settings(self):
        """Loads keybindings and input categories from a TOML file."""
        try:
            with open(self.CONFIG_FILE, "r") as f:
                config = toml.load(f)
            print("Loaded input settings:", config)
            return config.get("key_bindings", {}), config.get("input_categories", {})
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
            }
    
    def setup_key_listeners(self):
        """Binds key events dynamically based on the current key bindings."""
        for action, key in self.key_bindings.items():
            self.accept(key, self.handle_key_press, [action, True])
            self.accept(key + "-up", self.handle_key_press, [action, False])
    
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



class UDPClient(DatagramProtocol):
    def __init__(self, server_address):
        self.server_address = server_address

    def startProtocol(self):
        print(f"Connected to UDP Server at {self.server_address}")

    def send_data(self, data):
        """Send data to the remote UDP server."""
        self.transport.write(json.dumps(data).encode(), self.server_address)

    def datagramReceived(self, data, addr):
        """Handle data received from the server."""
        print(f"Received from server: {data.decode()}")

class NetworkManager:
    def __init__(self, server_address=("127.0.0.1", 9000)):
        self.server_address = server_address
        self.udp_client = UDPClient(server_address)

        # Instead of listening, we connect and send data
        reactor.listenUDP(0, self.udp_client)  # Client sends data, does not host a server
    
    def send_input(self, action, category, is_pressed):
        """Sends the input to the remote server based on its category."""
        data = {"action": action, "state": is_pressed}

        if category == "udp":
            self.udp_client.send_data(data)

class InputSettingsWindow(QWidget):
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
        
        self.save_button = QPushButton("Save Bindings")
        self.save_button.clicked.connect(self.save_bindings)
        
        self.reset_button = QPushButton("Reset to Defaults")
        self.reset_button.clicked.connect(self.reset_bindings)
        
        self.layout.addWidget(self.table)
        self.layout.addWidget(self.save_button)
        self.layout.addWidget(self.reset_button)
        
        self.setLayout(self.layout)
    
    def save_bindings(self):
        for row in range(self.table.rowCount()):
            action = self.table.item(row, 0).text()
            key = self.table.item(row, 1).text()
            category_dropdown = self.table.cellWidget(row, 2)
            category = category_dropdown.currentText()
            
            if category in ["udp", "tcp"]:
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setText("Warning: Enabling networked input can introduce latency and security risks. Proceed with caution.")
                msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                response = msg_box.exec_()
                if response == QMessageBox.Cancel:
                    return
            
            self.input_manager.key_bindings[action] = key
            self.input_manager.input_categories[action] = category
        print("Bindings Updated:", self.input_manager.key_bindings)
        print("Categories Updated:", self.input_manager.input_categories)
    
    def reset_bindings(self):
        self.input_manager.__init__()
        self.__init__(self.input_manager)
        self.show()

