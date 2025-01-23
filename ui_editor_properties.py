from panda3d.core import NodePath, Texture
import ui_editor
from monobehavior import MonoBehavior
class ui_editor_properties(MonoBehavior):
    def __init__(self, node):
        super().__init__(node)
        self.node = node
        
        self.__builtin__ = True
        
        self._private_isCanvas = False
        self._private_isLabel = False
        self.current_text = "Label 1"
        self.button = {}
        self.inputs = {}
    def start(self):
        pass
    
    
    def create_label(self):
        ui_editor.Drag_and_drop_ui_editor.label("Label 1", parent=self.node)
    
    def update_label(self):
        self.node['text'] = self.current_text
    def update(self, dt):
        if self._private_isCanvas:
            self.button = {
                "create label" : self.create_label()
            }
        if self._private_isLabel:
            self.inputs = {
                "Text" : self.update_label()
            }