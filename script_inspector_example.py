from panda3d.core import NodePath, Texture

class script_inspector_example():
    def __init__(self, node):
        self.node = NodePath("Root")
        self.rotation_h = 0
        self.node.setH(self.rotation_h)
        self.texture = Texture("Dirt.png")