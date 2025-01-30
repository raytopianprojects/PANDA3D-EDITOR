from panda3d.core import NodePath, Texture
from global_registry import GlobalRegistry
from monobehavior import MonoBehavior

class script_inspector_example(MonoBehavior):
    def __init__(self, node):
        super().__init__(node)
        self.node = node
        self._private_speed = 5.0  # Private variable
        self.public_health = 100    # Public variable
        
    def handle_input(self, action, is_pressed):
        """Called when an input event occurs."""
        if action == "forward" and is_pressed:
            print("Moving Forward!")
            self.node.set_y(self.node.getQuat().getForward() + 1)  # Move player forward
        elif action == "jump" and is_pressed:
            print("Jump!")

    def start(self):
        print(f"{self.node.getName()} PlayerBehavior started!")
        # Register player in the global registry
        GlobalRegistry.set_value("player", self)

    def update(self, dt):
        # Example: Move the player forward continuously
        self._current_pos = self.node.getPos()
        #new_pos = current_pos + (self.node.getQuat().getForward() * self._private_speed * dt)
        #self.node.setPos(new_pos)

        # Access a global variable
        enemy_health = GlobalRegistry.get_value("enemy_health")
        if enemy_health is not None:
            print(f"Enemy Health: {enemy_health}")
