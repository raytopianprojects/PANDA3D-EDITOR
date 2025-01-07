import os
from panda3d.core import *
from direct.showbase.ShowBase import messenger, DirectObject
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from direct.stdpy.file import open, isdir, isfile
from copy import copy
import io
from contextlib import redirect_stdout


names = {"Vertex": ".vert", "Fragment": '.frag', "Geometry": ".geom", "Tess Hull": ".hull", "Tess Domain": ".dom"}


class ShaderEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.name = None
        self.shaders: dict[str, QPlainTextEdit] = {}
        self.last_shaders = None
        self.do = DirectObject.DirectObject()
        self.do.accept("save", self.save)

        self.node = NodePath("shader_node")
        self.node.reparent_to(render)
        self.node.set_z(-3)
        e = base.loader.load_model("environment")
        e.reparent_to(self.node)

        self.h = QHBoxLayout()
        self.setLayout(self.h)

        self.meshes = ("environment", "panda", "smiley")
        self.mesh_select = QComboBox(self)
        self.mesh_select.currentIndexChanged.connect(self.change_mesh)
        for m in self.meshes:
            self.mesh_select.addItem(m)


        self.tb = QTabWidget(self)
        self.viewport_splitter = QSplitter(Qt.Vertical)

        self.h.addWidget(self.viewport_splitter)

        self.error_scroll = QScrollArea(self)
        self.error_scroll.setWidgetResizable(True)

        self.error_box = QLabel("")
        self.error_box.setWordWrap(True)

        self.error_scroll.setWidget(self.error_box)

        self.viewport_splitter.addWidget(self.mesh_select)
        self.viewport_splitter.addWidget(self.tb)
        self.viewport_splitter.addWidget(self.error_scroll)

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



        self.apply_shaders()

    def hide_nodes(self):
        self.node.show()
        for c in render.get_children():
            if c.node() != self.node.node() and type(c.node()) not in (AmbientLight, DirectionalLight, PointLight,
                                                                       Spotlight, Camera) and c.name not in (
            "threeaxisgrid"
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
        f = io.StringIO()
        with redirect_stdout(f):
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
                self.last_shaders = copy(kwargs)
            except:
                if self.last_shaders:
                    self.node.set_shader(Shader.make(Shader.SL_GLSL, **self.last_shaders))
        self.error_box.setText(f.getvalue() + self.error_box.text())

    def change_mesh(self, index):
        c: NodePath = None
        for c in self.node.getChildren():
            c.remove_node()
        e = base.loader.load_model(self.meshes[index])
        e.reparent_to(self.node)

        if index != 0:
            self.node.set_z(3)
        else:
            self.node.set_z(-3)

