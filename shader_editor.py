import os
from panda3d.core import *
from direct.showbase.ShowBase import messenger
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from QPanda3D.Panda3DWorld import Panda3DWorld
from QPanda3D.QPanda3DWidget import QPanda3DWidget
from direct.stdpy.file import open, isdir, isfile

names = {"Vertex": ".vert", "Fragment": '.frag', "Geometry": ".geom", "Tess Hull": ".hull", "Tess Domain": ".dom"}


class ShaderEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.name = None
        self.shaders: dict[str, QPlainTextEdit] = {}
        self.h = QHBoxLayout()
        self.setLayout(self.h)
        self.tb = QTabWidget(self)
        self.h.addWidget(self.tb)

        for x, y in {"Vertex": """#version 150

// Uniform inputs
uniform mat4 p3d_ModelViewProjectionMatrix;

// Vertex inputs
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;

// Output to fragment shader
out vec2 texcoord;

void main() {
  gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
  texcoord = p3d_MultiTexCoord0;
}""", "Fragment": """#version 150

uniform sampler2D p3d_Texture0;

// Input from vertex shader
in vec2 texcoord;

// Output to the screen
out vec4 p3d_FragColor;

void main() {
  vec4 color = texture(p3d_Texture0, texcoord);
  p3d_FragColor = color;
}""",
                     "Geometry": "",
                     "Tess Hull": "",
                     "Tess Domain": "", }.items():
            self.add_tab(x, y)

        newAct = QAction('Save', self)
        newAct.triggered.connect(self.save)
        newAct.setShortcut(QKeySequence("Ctrl+S"))
        self.addAction(newAct)
        self.node = NodePath("shader_node")
        self.node.reparent_to(render)
        self.node.set_z(-3)
        e = base.loader.load_model("environment")
        e.reparent_to(self.node)
        #self.hide_nodes()
        self.apply_shaders()

    def hide_nodes(self):
        self.node.show()
        for c in render.get_children():
            print(c, type(c.node()))
            if c.node() != self.node.node() and type(c.node()) not in (AmbientLight, DirectionalLight, PointLight,
                                                                       Spotlight, Camera) and c.name not in ("threeaxisgrid"
                                                                                                   "-parentnode",
                                                                                                       "camera"):
                c.hide()

    def show_nodes(self):
        for c in render.get_children():
            if c != self.node.node():
                c.show()
        self.node.hide()

    def open(self):
        if not isdir("shaders"):
            os.mkdir("shaders")

        value, ok = QInputDialog().getText(self, "Shader Name", "Shader Name:")
        self.name = value
        messenger.send("name", sentArgs=[value])

        for x in ["Vertex", "Fragment", "Geometry", "Tess Hull", "Tess Domain"]:
            _x = names[x]
            if isfile(f"shaders/{self.name}{_x}"):
                with open(f"shaders/{self.name}{_x}", "r") as f:
                    try:
                        text = f.read()
                        self.shaders[x].setPlainText(text)
                    except:
                        pass
            else:
                self.save()
                return

    def save(self):
        if self.name:
            if not isdir("shaders"):
                os.mkdir("shaders")
            for x in ["Vertex", "Fragment", "Geometry", "Tess Hull", "Tess Domain"]:
                _x = names[x]
                text = self.shaders[x].toPlainText()
                if text.strip():
                    with open(f"shaders/{self.name}{_x}", "w") as f:
                        try:
                            f.write(text)
                        except:
                            pass

    def add_tab(self, name, default):
        t = QPlainTextEdit(self)
        t.setPlainText(default)
        self.shaders[name] = t
        t.textChanged.connect(self.apply_shaders)
        t.textChanged.connect(self.save)
        self.tb.addTab(t, name)

    def apply_shaders(self):
        try:
            shaders = {"vertex": self.shaders["Vertex"].toPlainText(),
                       "fragment": self.shaders["Fragment"].toPlainText(),
                       "geometry": self.shaders["Geometry"].toPlainText(),
                       "tess_control": self.shaders["Tess Hull"].toPlainText(),
                       "tess_evaluation": self.shaders["Tess Domain"].toPlainText()}
            kwargs = {}
            for key, value in shaders.items():
                if value != "":
                    kwargs[key] = value
            self.node.set_shader(Shader.make(Shader.SL_GLSL, **kwargs))
            print("Shader Successful")
        except:
            pass
