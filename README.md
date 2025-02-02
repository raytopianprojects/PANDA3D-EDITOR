# Panda3D Editor Documentation

## Overview

This documentation provides an in-depth guide to the components of the Panda3D Editor, covering entity management, game preview functionality, and the behavior system.

---

# 1. **Game Preview System**

## `Preview_build.py`

This module is responsible for **initializing and running** the preview build of the Panda3D game. It loads entities, manages networking, and updates inputs dynamically.

### **GamePreviewApp Class**

#### **Methods:**

- `__init__(self, network_manager)`: Initializes the game preview system, loads all entities, and sets up networking.
- `setup_camera(self)`: Configures the camera’s position and orientation.
- `setup_networking(self)`: Reads networking settings from a TOML file and initializes networking if enabled.
- `update(self, task)`: Continuously updates input settings during preview mode.
- `recreate_entities(self)`: Reloads all entities dynamically when settings change.

### **Command-Line Arguments:**
- `--server`: Starts a dedicated server without rendering the game.
- `--client`: Connects to a server.
- `--connect <IP>`: Specifies the server IP to connect to.

#### **Usage Example:**

```sh
python Preview_build.py --server  # Start a server
python Preview_build.py --client --connect 127.0.0.1  # Connect to a server
```

#### **Usage in Python:**

```python
app = GamePreviewApp()
app.run()
```

---

# 2. **Entity System**

## `Entity.py`

This module defines how **3D objects** (entities) are created, loaded, and managed in the Panda3D editor.

### **Entity Class**

#### **Attributes:**

- `name`: Name of the entity.
- `entity_model`: Path to the 3D model file.
- `entity_id`: Unique identifier.
- `properties`: Dictionary containing custom properties.
- `transform`: Stores position, rotation, and scale.
- `node`: Represents the **Panda3D NodePath** of the entity.
- `behavior_instances`: Stores attached scripts.
- `network_manager`: Handles networking (if applicable).

#### **Methods:**

- `load(self, render)`: Loads the **3D model**, applies transformations, and attaches scripts.
- `load_behaviors(self)`: Loads and attaches behaviors dynamically from Python script files.

### **LightEntity Class**

Manages **light objects** in the scene.

#### **Attributes:**

- `light_type`: Determines the light type (`directional`, `spot`, `point`).
- `color`: Sets light color.
- `position`: Defines the light's position.

#### **Example Usage:**

```python
entity = Entity(data, input_manager)
entity.load(render)
```

---

# 3. **Behavior System**

## `monobehavior.py`

The **MonoBehavior system** is responsible for handling scripts dynamically, updating them per frame, and syncing variables over the network.

### **Variable Management in MonoBehavior**
- **Public Variables**: Available to all scripts, can be modified externally.
- **Shared Variables**: Synced across all networked clients.
- **Local Variables**: Exist only in the local instance.
- **Private Variables**: Used internally within the script.

### **MonoBehavior Class**

#### **Attributes:**

- `sync_variables`: Dictionary storing variables that are synchronized over the network.

#### **Methods:**

- `mark_variable_for_sync(self, var_name, sync_type)`: Marks a variable for network synchronization. Sync types:
  - **shared**: Synced across all clients.
  - **local**: Only exists locally on the player's machine.
  - **private**: Only accessible by the specific entity.
- `send_synced_variables(self)`: Sends changed variables over the network.
- `receive_synced_variable(self, var_name, value)`: Updates a variable received over the network.
- `handle_input(self, action, is_pressed)`: Handles input events dynamically.
- `start(self)`: Called once before the first update.
- `update(self, dt)`: Called every frame with the time delta.

#### **Example Usage:**

```python
class PlayerBehavior(MonoBehavior):
    def start(self):
        print("Player Spawned!")
        self.mark_variable_for_sync("health", "shared")  # Syncs health across all clients
    
    def update(self, dt):
        print("Updating Player")
```

### **Public, Shared, and Local Variables Example**

```python
from panda3d.core import NodePath, Vec3
from global_registry import GlobalRegistry
from monobehavior import MonoBehavior

class script_inspector_example(MonoBehavior):
    def __init__(self, node, input_manager, network_manager=None):
        super().__init__(node, network_manager, input_manager)
        self.node = node
        self.network_manager = network_manager  # ✅ Ensure correct networking instance
        self.input_manager = input_manager
        self._private_speed = 5.0  # Private variable
        self.public_health = 100    # Public variable
        self._current_pos = self.node.getPos()
        self.velocity = 0
        
        # ✅ Register the behavior with InputManager
        if self.input_manager:
            self.input_manager.register_behavior(self)

    def handle_input(self, action, is_pressed):
        """Handles player input for movement"""
        if action == "forward":
            self.node.setY(self.speed if is_pressed else 0)
        elif action == "back":
            self.node.setY(-self.speed if is_pressed else 0)
        elif action == "left":
            self.node.setX(-self.speed if is_pressed else 0)
        elif action == "right":
            self.node.setX(self.speed if is_pressed else 0)

    def move_forward(self):
        """Moves the player forward based on orientation."""
        forward_vector = self.node.getQuat().getForward()
        new_pos = self._current_pos + (forward_vector * self._private_speed)
        self.node.setPos(new_pos)
        print(f"Moving Forward! New Position: {new_pos}")

    def start(self):
        """Called when the script starts."""
        print(f"{self.node.getName()} PlayerBehavior started!")
        GlobalRegistry.set_value("player", self)

    def update(self, dt):
        """Handles continuous updates per frame."""
        self._current_pos = self.node.getPos()
        
        # Example: Sync health data if networking is enabled
        if self.network_manager:
            self.network_manager.send_variable_update(self.node.getName(), "health", self.public_health, "udp")
```

---

