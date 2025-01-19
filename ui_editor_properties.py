from panda3d.core import NodePath, Texture
import ui_editor
class Script():
    def __init__(self):
        self.isCanvas = False
        
        self.isLabel = False
        if self.isCanvas:
            self.create_canvas()
        
        if self.isLabel:
            self.label()
    def create_canvas(self):
        self.BUTTON = {"Create..." : "label"}
    
    def label(self):
        
        self.INPUTS = {"Text" : "Name", "Scale" : 0.1}