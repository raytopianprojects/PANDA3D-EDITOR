from direct.task import Task
from global_registry import GlobalRegistry

class MonoBehavior:
    def __init__(self, node, network_manager, input_manager=None):
        """
        Initialize the MonoBehavior with a reference to the node it's attached to.
        Registers the update task with Panda3D's task manager.
        """
        self.network_manager = network_manager
        self.input_manager = input_manager  # ✅ Allow InputManager to manage inputs
        self.node = node
        self.started = False
        self.__builtin__ = False 
        self.sync_variables = {}  # Stores variables marked for syncing
        taskMgr.add(self._update_task, f"update_{id(self)}")
        network_manager.register_behavior(self)
        
        if self.input_manager:
            self.input_manager.register_behavior(self)  # ✅ Register for input events

    def mark_variable_for_sync(self, var_name, sync_type="udp"):
        """Mark a variable to be synced over the network."""
        self.sync_variables[var_name] = sync_type

    def send_synced_variables(self):
        """Send only changed variables over the network."""
        for var_name, sync_type in self.sync_variables.items():
            value = getattr(self, var_name, None)
            if value is not None:
                self.network_manager.send_variable_update(self.node.getName(), var_name, value, sync_type)
    
    def receive_synced_variable(self, var_name, value):
        """Update a synced variable when received from the network."""
        if var_name in self.sync_variables:
            setattr(self, var_name, value)
            
    def handle_input(self, action, is_pressed):
        """Called when an input event occurs."""
        if action == "forward" and is_pressed:
            print("Moving Forward!")
            self.node.setY(self.node.getY() + 1)  # ✅ Move player forward
        elif action == "jump" and is_pressed:
            print("Jump!")
            
    
    def start(self):
        """Called once before the first update."""
        pass

    def update(self, dt):
        """Called every frame with delta time since last frame."""
        self.send_synced_variables()  # ✅ Ensure variables are sent to the network

    def _update_task(self, task):
        dt = globalClock.getDt()
        if not self.started:
            self.start()
            self.started = True
        self.update(dt)
        return Task.cont
