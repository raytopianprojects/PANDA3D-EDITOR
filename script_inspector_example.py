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

        # Access a global variable
        enemy_health = GlobalRegistry.get_value("enemy_health")
        if enemy_health is not None:
            print(f"Enemy Health: {enemy_health}")
