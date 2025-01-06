from panda3d.core import Texture
class Script:
    def __init__(self, node=None):
        self.node = node
        self.texture = Texture("Dirt.png")