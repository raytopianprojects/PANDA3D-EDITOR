from panda3d.core import GeoMipTerrain, Shader, MouseWatcher, Point3
from panda3d.core import NodePath, CollisionRay, CollisionNode, CollisionHandlerQueue, CollisionTraverser
from direct.showbase.ShowBase import ShowBase
from panda3d.core import load_prc_file_data


from panda3d.core import PNMImage

from panda3d.core import Filename


from panda3d.core import LVecBase4f, PNMPainter, PNMBrush

# Initialize Panda3D app
load_prc_file_data('', '')  

class TerrainPainterApp(ShowBase):
    def __init__(self):
        # Initialize the base class
        ShowBase.__init__(self)

        # Create the terrain
        self.terrain = GeoMipTerrain('myTerrain')
        self.heightmap_image = PNMImage()
        self.heightmap_image.read(Filename('Heightmap.png'))  # Load heightmap file
        self.terrain.set_heightfield(self.heightmap_image)  
        self.terrain.generate()

        # Set up terrain node
        terrain_root = self.terrain.get_root()
        self.terrain_np = NodePath(terrain_root)  
        self.terrain_np.reparent_to(render)  
        self.terrain_np.set_pos(-100, -100, 0)
        self.terrain_np.set_scale(1, 1, 100)  

        # Enable collision geometry for the terrain
        self.terrain.set_bruteforce(True)  # Ensures all terrain tiles are generated
        self.terrain_root = self.terrain.get_root()
        self.terrain_root.set_collide_mask(1)  # Enable collisions

        # Set shader on terrain
        self.shader = Shader.make(Shader.SLGLSL,
            """
            #version 130
            in vec2 texcoord;
            out vec4 fragColor;
            uniform sampler2D tex0;
            uniform sampler2D tex1;
            void main() {
                vec4 texColor0 = texture(tex0, texcoord);
                vec4 texColor1 = texture(tex1, texcoord);
                fragColor = mix(texColor0, texColor1, 0.5);  // Blend the textures
            }
            """, """
            #version 130
            uniform mat4 p3d_ModelViewProjection;
            in vec4 p3d_Vertex;
            in vec2 p3d_Texcoord;
            out vec2 texcoord;
            void main() {
                texcoord = p3d_Texcoord;
                gl_Position = p3d_ModelViewProjection * p3d_Vertex;
            }
            """
        )
        self.terrain_np.set_shader(self.shader)
        self.terrain_np.set_shader_input("tex0", loader.load_texture('Grass.png'))
        self.terrain_np.set_shader_input("tex1", loader.load_texture('Dirt.png'))

        # Set up collision handling
        self.collision_traverser = CollisionTraverser()
        self.collision_handler = CollisionHandlerQueue()

        # Create a collision ray for mouse input
        self.mouse_ray = CollisionRay()

        # Create a CollisionNode to hold the ray
        self.mouse_node = CollisionNode('mouse_ray')
        
        # Add the ray to the CollisionNode using add_solid
        self.mouse_node.add_solid(self.mouse_ray)
        
        # Attach the CollisionNode to the scene graph (e.g., to the camera)
        self.mouse_node_path = self.camera.attach_new_node(self.mouse_node)

        # Add the CollisionNode to the traverser
        self.collision_traverser.add_collider(self.mouse_node_path, self.collision_handler)

        # Accept mouse click event
        self.accept('mouse1', self.on_mouse_click)

    def on_mouse_click(self):
        if not self.mouseWatcherNode.has_mouse():
            print("Mouse not detected!")
            return

        # Get mouse position
        mouse_pos = self.mouseWatcherNode.get_mouse()
        print(f"Mouse position: {mouse_pos}")

        # Update the ray with the new mouse position
        self.mouse_ray.set_from_lens(self.camNode, mouse_pos.get_x(), mouse_pos.get_y())
        print(f"Ray updated: origin={self.mouse_ray.get_origin()}, direction={self.mouse_ray.get_direction()}")

        # Traverse the collision system
        self.collision_traverser.traverse(render)

        # Check for collisions
        if self.collision_handler.get_num_entries() > 0:
            print("RAY detected collision!")
            entry = self.collision_handler.get_entry(0)
            hit_pos = entry.get_surface_point(render)
            print(f"Painted at position: {hit_pos}")
            self.paint_on_terrain(hit_pos)
        else:
            print("No collision detected.")



    
    def paint_on_terrain(self, hit_pos):
        # Map hit_pos to heightmap coordinates
        terrain_x = int((hit_pos.x - self.terrain_np.get_x()) / self.terrain_np.get_sx())
        terrain_y = int((hit_pos.y - self.terrain_np.get_y()) / self.terrain_np.get_sy())

        if 0 <= terrain_x < self.heightmap_image.get_x_size() and 0 <= terrain_y < self.heightmap_image.get_y_size():
            print(f"Painting at terrain position: {hit_pos} (heightmap coords: {terrain_x}, {terrain_y})")

            # Create a painter to modify the heightmap
            painter = PNMPainter(self.heightmap_image)

            # Create a circular brush with a soft edge
            radius = 5
            # Correct the brush size to use LVecBase4f
            brush_size = LVecBase4f(radius, radius, radius, radius)  # LVecBase4f instead of a tuple
            brush = PNMBrush.make_spot(brush_size, radius, 0.05)

            # Paint onto the heightmap (blend is implicit, brush directly modifies)
            painter.drawPoint(terrain_x, terrain_y)

            # Update the terrain
            self.terrain.set_heightfield(self.heightmap_image)
            self.terrain.generate()
        else:
            print("Click outside terrain bounds.")



# Run the application
app = TerrainPainterApp()
app.run()
