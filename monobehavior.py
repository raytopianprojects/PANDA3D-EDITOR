# monobehavior.py

from direct.task import Task
from main import input_manager_c

class MonoBehavior:
    def __init__(self, node):
        """
        Initialize the MonoBehavior with a reference to the node it's attached to.
        Registers the update task with Panda3D's task manager.
        """
        self.node = node
        self.started = False
        self.__builtin__ = False 
        taskMgr.add(self._update_task, f"update_{id(self)}")
        input_manager_c.register_behavior(self)
        
    

    def start(self):
        """Called once before the first update."""
        pass

    def update(self, dt):
        """Called every frame with delta time since last frame."""
        pass

    def _update_task(self, task):
        dt = globalClock.getDt()
        if not self.started:
            self.start()
            self.started = True
        self.update(dt)
        return Task.cont
