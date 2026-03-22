from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import geopandas as gpd

class Draw(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__pol = QPolygonF()
        self.__q = QPointF(-25, -25)
        self.__add_vertex = True

        # Shapefile data
        self.__shp_paths = []
        self.__shp_polygons = []
        self.__shp_holes = []
        self.__highlighted_indices = []

    def mousePressEvent(self, e):
        # Get cursor coordinates
        x = e.position().x()
        y = e.position().y()

        # Add vertex to polygon
        if self.__add_vertex:
            p = QPointF(x, y)
            self.__pol.append(p)
        # Set new q coordinates, clear highlights
        else:
            self.__q.setX(x)
            self.__q.setY(y)
            self.__highlighted_indices.clear()

        # Repaint
        self.repaint()

    def loadShapefile(self, file_name):
        # Load input data from SHP
        shp = gpd.read_file(file_name)

        # Clear previous data
        self.__shp_paths.clear()
        self.__shp_polygons.clear()
        self.__shp_holes.clear()

        # Get bounding box and canvas size for coordinate transformation
        min_x, min_y, max_x, max_y = shp.total_bounds
        w = self.width()
        h = self.height()

        # Iterate through SHP geometries
        for geom in shp.geometry:
            if geom is None:
                continue

            polys = []
            if geom.geom_type == "Polygon":
                polys.append(geom)
            if geom.geom_type == "MultiPolygon":
                for p in geom.geoms:
                    polys.append(p)

            for poly in polys:
                # Exterior polygon
                exterior_pol = QPolygonF()
                for x, y in poly.exterior.coords:
                    sx = (x - min_x) / (max_x - min_x) * w
                    sy = (1.0 - (y - min_y) / (max_y - min_y)) * h
                    exterior_pol.append(QPointF(sx, sy))

                # Note: The logic for rendering polygons with holes using QPainterPath and OddEvenFill was developed with the help of Claude Sonnet 4.6
                path = QPainterPath()
                path.setFillRule(Qt.FillRule.OddEvenFill)
                path.addPolygon(exterior_pol)
                path.closeSubpath()

                # Process interior rings (holes) and add to painter path
                holes = []
                for interior in poly.interiors:
                    hole_pol = QPolygonF()
                    for x, y in interior.coords:
                        sx = (x - min_x) / (max_x - min_x) * w
                        sy = (1.0 - (y - min_y) / (max_y - min_y)) * h
                        hole_pol.append(QPointF(sx, sy))

                    path.addPolygon(hole_pol)
                    path.closeSubpath()
                    holes.append(hole_pol)

                # Store polygon data for analysis and drawing
                self.__shp_polygons.append(exterior_pol)
                self.__shp_holes.append(holes)
                self.__shp_paths.append(path)

        # Switch to point-only mode after loading shapefile
        self.__add_vertex = False
        self.__highlighted_indices.clear()
        self.repaint()

    def paintEvent(self, e):
        # Initialize painter
        qp = QPainter(self)
        qp.begin(self)

        # Draw shp polygons
        for i in range(len(self.__shp_paths)):
            path = self.__shp_paths[i]
            qp.setPen(QPen(Qt.GlobalColor.black))

            # Highlight selected polygon using cyan colour
            if i in self.__highlighted_indices:
                qp.setBrush(Qt.GlobalColor.cyan)
            else:
                qp.setBrush(Qt.GlobalColor.gray)

            qp.drawPath(path)

        # Draw manual polygon
        if not self.__pol.isEmpty():
            qp.setPen(Qt.GlobalColor.black)
            qp.setBrush(Qt.GlobalColor.yellow)
            qp.drawPolygon(self.__pol)

        # Draw point
        if self.__q.x() > 0 and self.__q.y() > 0:
            qp.setBrush(Qt.GlobalColor.red)
            r = 5
            qp.drawEllipse(int(self.__q.x() - r), int(self.__q.y() - r), 2 * r, 2 * r)

        # End draw
        qp.end()

    def changeStatus(self):
        # Input source: point or polygon
        self.__add_vertex = not self.__add_vertex

    def clearData(self):
        # Clear data
        self.__pol.clear()
        self.__shp_paths.clear()
        self.__shp_polygons.clear()
        self.__shp_holes.clear()
        self.clearResults()

    def clearResults(self):
        # Reset point to off-screen position
        self.__q.setX(-25)
        self.__q.setY(-25)
        self.__highlighted_indices.clear()
        self.repaint()

    def getQ(self):
        return self.__q

    def getPolygonsData(self):
        # Return data for analysis
        if len(self.__shp_polygons) > 0:
            data = []
            for i in range(len(self.__shp_polygons)):
                data.append((self.__shp_polygons[i], self.__shp_holes[i]))
            return data
        else:
            return [(self.__pol, [])]

    def setHighlighted(self, indices):
        # Set highlighted polygons and redraw
        self.__highlighted_indices = indices
        self.repaint()