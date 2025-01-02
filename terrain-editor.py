from panda3d.core import (
    ShaderTerrainMesh, Shader, MouseWatcher, Point3,
    NodePath, CollisionRay, CollisionNode, CollisionHandlerQueue, CollisionTraverser,
    PNMImage, Filename, LVecBase4f, PNMPainter, PNMBrush, SamplerState, CollisionBox, BitMask32,
    Geom, GeomNode, GeomVertexFormat, GeomVertexData, GeomVertexWriter, GeomLines, Texture, LColorf
)
from direct.showbase.ShowBase import ShowBase
from panda3d.core import load_prc_file_data

from PIL import Image
from PIL import ImageEnhance

# Initialize Panda3D app
load_prc_file_data('', '')


class TerrainCollider:
    def __init__(self, terrain_size, subdivision):
        self.terrain_size = terrain_size
        self.subdivision = subdivision
        self.root = NodePath("TerrainColliders")
        self.root.reparent_to(render)

        self.create_collider_tree()

    def create_collider_tree(self):
        size = self.terrain_size
        step = size * 3  #// self.subdivision

        # Adjust the collision box size based on the step
        collision_box_size = step  # Use step directly as the size for the collision box

        for x in range(0, size, step):
            for y in range(0, size, step):
                collider_node = CollisionNode(f"Collider_{x}_{y}")
                collider_box = CollisionBox(Point3(x + step / 2, y + step / 2, 0), collision_box_size / 2,
                                            collision_box_size / 2, 50)
                collider_node.add_solid(collider_box)
                collider_node.set_from_collide_mask(BitMask32.bit(1))
                collider_node.set_into_collide_mask(BitMask32.bit(1))
                collider_np = self.root.attach_new_node(collider_node)

    def update_colliders(self, updated_area):
        # This is a placeholder for updating colliders dynamically
        print(f"Updating colliders in area: {updated_area}")


class TerrainPainterApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Load the heightmap image as a PNMImage
        self.heightmap_image = PNMImage(Filename("Heightmap.png"))

        self.heightmap_image = PNMImage(512, 512)  # Resize to 512x512

        # Create a texture for the heightmap and load the PNMImage into it
        self.heightmap_texture = Texture()
        self.heightmap_texture.load(self.heightmap_image)

        self.terrain_node = ShaderTerrainMesh()
        self.terrain_node.heightfield = self.loader.loadTexture("Heightmap.png")
        self.terrain_node.target_triangle_width = 10.0
        self.terrain_node.generate()

        self.terrain_np = self.render.attach_new_node(self.terrain_node)
        self.terrain_np.set_scale(512, 512, 100)
        self.terrain_np.set_pos(-512 // 2, -512 // 2, -70.0)

        terrain_shader = Shader.load(Shader.SL_GLSL, "terrain.vert.glsl", "terrain.frag.glsl")
        self.terrain_np.set_shader(terrain_shader)
        self.terrain_np.set_shader_input("camera", self.camera)

        grass_tex = self.loader.loadTexture("Grass.png")
        grass_tex.set_minfilter(SamplerState.FT_linear_mipmap_linear)
        grass_tex.set_anisotropic_degree(16)
        self.terrain_np.set_texture(grass_tex)

        self.collision_traverser = CollisionTraverser()
        self.collision_handler = CollisionHandlerQueue()

        self.accept("f3", self.toggleWireframe)

        self.mouse_ray = CollisionRay()
        self.mouse_node = CollisionNode('mouse_ray')
        self.mouse_node.add_solid(self.mouse_ray)
        self.mouse_node.set_from_collide_mask(BitMask32.bit(1))
        self.mouse_node.set_into_collide_mask(BitMask32.bit(1))
        self.mouse_node_path = self.camera.attach_new_node(self.mouse_node)

        self.collision_traverser.add_collider(self.mouse_node_path, self.collision_handler)

        self.terrain_np.set_collide_mask(BitMask32.bit(1))

        self.accept('mouse1', self.start_holding)
        self.accept('mouse1-up', self.stop_holding)

        self.terrain_collider = TerrainCollider(1024, 100)

        self.brush_selection = "b0.png"  #current brush Path

        self.intensity = 0.2  # out of a 100 2/100

        self.max_height = 1

    def start_holding(self):
        self.task_mgr.add(self.on_mouse_click, "on_mouse_click")
        self.height = 0.0
        self.holding = True

    def stop_holding(self):
        self.holding = False

    def adjust_speed_of_brush(self, brush_image, speed_factor):
        # Create a new PNMImage with the same size and data as the original
        new_brush_image = PNMImage(brush_image.get_x_size(), brush_image.get_y_size())
        new_brush_image.copy_sub_image(brush_image, 0, 0, 0, 0, brush_image.get_x_size(), brush_image.get_y_size())

        # Modify pixel values based on speed_factor
        for x in range(new_brush_image.get_x_size()):
            for y in range(new_brush_image.get_y_size()):
                # Get the pixel value at (x, y)
                r, g, b = new_brush_image.get_xel(x, y)

                # Adjust pixel intensity based on speed_factor
                r = int(r * speed_factor)
                g = int(g * speed_factor)
                b = int(b * speed_factor)

                # Ensure pixel values stay within the valid range (0-255)
                r = min(max(r, 0), 255)
                g = min(max(g, 0), 255)
                b = min(max(b, 0), 255)

                # Set the new pixel value
                new_brush_image.set_xel(x, y, r, g, b)

        return new_brush_image

    def on_mouse_click(self, Task):
        if not self.mouseWatcherNode.has_mouse():
            print("Mouse not detected!")
            return

        mouse_pos = self.mouseWatcherNode.get_mouse()
        self.mouse_ray.set_from_lens(self.camNode, mouse_pos.get_x(), mouse_pos.get_y())

        self.collision_handler.clear_entries()
        self.collision_traverser.traverse(self.render)

        if self.collision_handler.get_num_entries() > 0:
            self.collision_handler.sort_entries()
            entry = self.collision_handler.get_entry(0)
            hit_pos = entry.get_surface_point(self.render)
            print(f"Collision detected at: {hit_pos}")
            self.paint_on_terrain(hit_pos)
        else:
            print("No collision detected.")

        if not self.height >= self.max_height:
            self.height += 0.05

        if self.holding:
            return Task.cont
        else:
            return None

    def adjust_brightness_pillow(self, brush_image_path, brightness_factor):
        # Open the brush image using Pillow
        brush_image = Image.open(brush_image_path)
        enhancer = ImageEnhance.Brightness(brush_image)
        brush_image = enhancer.enhance(brightness_factor)

        # Save the modified image temporarily
        brush_image.save("Temp_Brush.png")

        # Convert it back to PNMImage if needed
        pnm_brush_image = PNMImage(Filename("Temp_Brush.png"))
        return pnm_brush_image

    def paint_on_terrain(self, hit_pos):
        # Map world position to heightmap coordinates
        terrain_x = int((hit_pos.x + 512) / 1024 * self.heightmap_image.get_x_size())
        terrain_y = int((hit_pos.y + 512) / 1024 * self.heightmap_image.get_y_size())

        # Flip the Y-axis if necessary
        terrain_y = self.heightmap_image.get_y_size() - terrain_y - 1

        if 0 <= terrain_x < self.heightmap_image.get_x_size() and 0 <= terrain_y < self.heightmap_image.get_y_size():
            print(f"Painting at heightmap coords: ({terrain_x}, {terrain_y})")

            self.adjust_brightness_pillow(self.brush_selection, self.height)

            # Load the brush image
            brush_image = PNMImage(Filename("Temp_Brush.png"))
            brush_width = brush_image.get_x_size()
            brush_height = brush_image.get_y_size()

            self.adjust_speed_of_brush(brush_image, self.intensity)

            # Calculate the top-left corner to center the brush
            start_x = terrain_x - brush_width // 2
            start_y = terrain_y - brush_height // 2

            # Apply the brush to the heightmap
            self.heightmap_image.blend_sub_image(
                brush_image,
                max(0, start_x),  # Clamp to ensure valid position
                max(0, start_y),
                0,  # Brush offset X
                0,  # Brush offset Y
                min(brush_width, self.heightmap_image.get_x_size() - start_x),  # Brush width
                min(brush_height, self.heightmap_image.get_y_size() - start_y)  # Brush height
            )

            # Update the texture with the modified heightmap
            self.heightmap_texture.load(self.heightmap_image)
            self.terrain_node.heightfield = self.heightmap_texture
            self.terrain_node.generate()

            # Update the collision system
            self.terrain_collider.update_colliders(updated_area=(terrain_x, terrain_y))
        else:
            print("Click outside terrain bounds.")


# Run the application
app = TerrainPainterApp()
app.run()
