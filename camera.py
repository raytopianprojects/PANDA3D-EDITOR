from direct.showbase.DirectObject import DirectObject
from QPanda3D.Panda3DWorld import Panda3DWorld


class FlyingCamera(DirectObject):
    def __init__(self, world: Panda3DWorld):
        """A simple class that allows for flying based navigation in the viewport."""
        # Todo: Page up and down, mouse wheel for speed, smooth camera rotation
        super().__init__()
        self.world = world
        self.cam = world.cam
        self.mx, self.my, self.x, self.y = 0, 0, 0, 0
        self.move_speed = 1

        # Enable controls
        self.keys = ("w", "s", "q", "e", "a", "d", "mouse2", "arrow_left", "arrow_up", "arrow_down", "arrow_right",
                     "page_up", "page_down")
        self.input = {}
        for i in self.keys:
            self.input[i] = False
            self.accept(i, self.update, extraArgs=[i, True])
            self.accept(i + "-up", self.update, extraArgs=[i, False])

        # Mouse position
        self.accept("mouse-move", self.mouse_move)

        # Camera speed
        # self.accept("wheel_up", self.mouse_up)
        # self.accept("wheel_down", self.mouse_up)

        # Enable movement
        self.move_task = self.add_task(self.move)

    def mouse_up(self, *args):
        print("uo", args)

    def mouse_move(self, evt: dict):
        self.x, self.y = evt['x'], evt['y']

    def update(self, key, value, *args):
        self.input[key] = value

        # Reseat mouse position
        if args and value:
            args = args[0]
            self.x, self.y = args['x'], args['y']
            self.mx, self.my = self.x, self.y

    def move(self, task):
        # Mouse Rotation
        if self.world.mouseWatcherNode.hasMouse():
            if self.input["mouse2"]:
                dx, dy = self.mx - self.x, self.my - self.y

                self.cam.set_p(self.cam, dy * 0.25 * self.move_speed)
                self.cam.set_h(self.cam, dx * 0.25 * self.move_speed)

                self.mx, self.my = self.x, self.y

        # Keyboad Movement
        if self.input["q"] or self.input["page_up"]:
            self.cam.set_z(self.cam, 1 * self.move_speed)

        if self.input["e"] or self.input["page_down"]:
            self.cam.set_z(self.cam, -1 * self.move_speed)

        if self.input["w"] or self.input["arrow_up"]:
            self.cam.set_y(self.cam, 1 * self.move_speed)

        if self.input["s"] or self.input["arrow_down"]:
            self.cam.set_y(self.cam, -1 * self.move_speed)

        if self.input["d"] or self.input["arrow_right"]:
            self.cam.set_x(self.cam, 1 * self.move_speed)

        if self.input["a"] or self.input["arrow_left"]:
            self.cam.set_x(self.cam, -1 * self.move_speed)

        return task.cont
