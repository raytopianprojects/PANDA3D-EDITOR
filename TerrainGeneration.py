import terrainEditor

class GenerateTerrain():
    def __init__(self):

        self.terrain_painter = terrainEditor.TerrainPainterApp()

    def set_hold(self):
        self.terrain_painter.start_holding()
    
    def stop_hold(self):
        self.terrain_painter.stop_holding()
