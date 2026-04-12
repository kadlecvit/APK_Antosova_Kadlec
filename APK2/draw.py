from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import geopandas as gpd

class Draw(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__building = QPolygonF()
        self.__buildings = []
        self.__mbr = QPolygonF()
        self.__mbrs = []

        
    def mousePressEvent(self, e):
        # Get cursor coordinates 
        x = e.position().x()
        y = e.position().y()
        
        # Create new point and add to polygon
        p = QPointF(x,y)
        self.__building.append(p)
        
        # Repaint
        self.repaint()


    def loadShapefile(self, file_name):
        # Load input data from SHP file
        shp = gpd.read_file(file_name)
        
        # Clear previous data
        self.__buildings.clear()
        self.__building.clear()
        self.__mbrs.clear()
        self.__mbr.clear()
        
        # Get bounding box and canvas size
        min_x, min_y, max_x, max_y = shp.total_bounds
        w = self.width()
        h = self.height()
        
        # Compute data dimensions
        data_w = max_x - min_x
        data_h = max_y - min_y
        
        # Avoid division by zero
        if data_w == 0 or data_h == 0:
            return
        
        # Compute uniform scale to preserve aspect ratio
        padding = 20
        scale = min((w - 2 * padding) / data_w, (h - 2 * padding) / data_h)
        
        # Compute offsets to center data in canvas
        offset_x = (w - data_w * scale) / 2
        offset_y = (h - data_h * scale) / 2
        
        # Iterate through SHP geometries
        for geom in shp.geometry:
            if geom is None:
                continue
            
            # Collect polygons
            polys = []
            if geom.geom_type == "Polygon":
                polys.append(geom)
            if geom.geom_type == "MultiPolygon":
                for p in geom.geoms:
                    polys.append(p)
            
            # Transform each polygon to screen coordinates
            for poly in polys:
                building_pol = QPolygonF()
                for coord in poly.exterior.coords:
                    x = coord[0]
                    y = coord[1]
                    sx = (float(x) - min_x) * scale + offset_x
                    sy = (max_y - float(y)) * scale + offset_y
                    building_pol.append(QPointF(sx, sy))
                
                # Add building to list
                self.__buildings.append(building_pol)
        
        # Repaint
        self.repaint()
        

    def paintEvent(self, e):
        # Initialize painter
        qp = QPainter(self)
        qp.begin(self)
        
        # Draw single building (manual input)
        qp.setPen(Qt.GlobalColor.black)
        qp.setBrush(Qt.GlobalColor.yellow)
        qp.drawPolygon(self.__building)
        
        # Draw all loaded buildings from shapefile
        for building in self.__buildings:
            qp.setPen(Qt.GlobalColor.black)
            qp.setBrush(Qt.GlobalColor.yellow)
            qp.drawPolygon(building)
        
        # Draw generalized rectangles (MBR)
        qp.setPen(QPen(Qt.GlobalColor.red, 2))
        qp.setBrush(Qt.GlobalColor.transparent)
        qp.drawPolygon(self.__mbr)
        
        for mbr in self.__mbrs:
            qp.drawPolygon(mbr)
        
        # End draw
        qp.end()
        
        
    def setMBR(self, mbr:QPolygonF):
        # Set single MBR for drawing
        self.__mbr = mbr
        
    def setMBRs(self, mbrs:list):
        # Set list of MBRs for drawing
        self.__mbrs = mbrs

    def getBuilding(self):
        # Get manually drawn building
        return self.__building
    
    def getBuildings(self):
        # Get all loaded buildings from shapefile
        return self.__buildings
    
    def clearResult(self):
        # Clear generalization results only
        self.__mbr.clear()
        self.__mbrs.clear()
        
        # Repaint screen
        self.repaint()
    
    def clearAll(self):
        # Clear all data (buildings and results)
        self.__building.clear()
        self.__buildings.clear()
        self.__mbr.clear()
        self.__mbrs.clear()
        
        # Repaint screen
        self.repaint()