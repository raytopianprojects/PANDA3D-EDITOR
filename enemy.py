# entities/EnemyBehavior.py
from global_registry import GlobalRegistry
from monobehavior import MonoBehavior

class enemy(MonoBehavior):
    def __init__(self, node):
        super().__init__(node)
        self.public_health = 50     # Public variable
        self._private_state = "idle"  # Private variable

    def start(self):
        print(f"{self.node.getName()} EnemyBehavior started!")
        # Initialize global enemy health
        GlobalRegistry.set_value("enemy_health", self.public_health)

    def update(self, dt):
        print("update enemy!")
        # Example: Decrease health over time
        self.public_health -= 1 * dt
        GlobalRegistry.set_value("enemy_health", self.public_health)
        print(f"{self.node.getName()} Health: {self.public_health}")
        
        # Change state based on health
        if self.public_health < 25:
            self._private_state = "aggressive"
            print(f"{self.node.getName()} is now aggressive!")
