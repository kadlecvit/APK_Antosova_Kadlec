from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import geopandas as gpd
import math


class Draw(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__pol = QPolygonF()        # manual polygon
        self.__q = QPointF(-25, -25)    # query point (hidden by default)
        self.__add_vertex = True        # True = add polygon vertex, False = move point

        # SHP data
        self.__shp_polygons = []        # list of QPolygonF (exterior rings only, for hit-testing)
        self.__shp_holes = []           # list of list[QPolygonF] (interior rings per polygon)
        self.__shp_paths = []           # list of QPainterPath with holes (for drawing)
        self.__shp_loaded = False


    # ─────────────────────────────────────────
    #  File loading
    # ─────────────────────────────────────────

    def loadShapefile(self):
        # Open file dialog and load SHP
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Shapefile", "", "Shapefile (*.shp)"
        )
        if not file_name:
            return

        try:
            shp = gpd.read_file(file_name)
            self.__loadGeometry(shp)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file:\n{str(e)}")

    def __loadGeometry(self, shp):
        # Convert shapefile geometries to QPolygonF + QPainterPath (normalized to widget size)
        self.__shp_polygons.clear()
        self.__shp_holes.clear()
        self.__shp_paths.clear()

        if shp is None or shp.empty:
            QMessageBox.critical(self, "Error", "Shapefile contains no geometry.")
            return

        # Bounding box for normalization
        min_x, min_y, max_x, max_y = shp.total_bounds
        w = self.width()
        h = self.height()

        def to_screen(x, y):
            # Normalize geo coords to screen pixels, flip Y axis
            sx = (float(x) - min_x) / (max_x - min_x) * w
            sy = (1.0 - (float(y) - min_y) / (max_y - min_y)) * h
            return QPointF(sx, sy)

        def ring_to_polygon(ring):
            return QPolygonF([to_screen(x, y) for x, y in ring.coords])

        for geom in shp.geometry:
            if geom is None:
                continue

            # Collect simple Polygon objects (handle MultiPolygon too)
            if geom.geom_type == "Polygon":
                polys = [geom]
            elif geom.geom_type == "MultiPolygon":
                polys = list(geom.geoms)
            else:
                continue  # skip points, lines etc.

            for poly in polys:
                # Build QPainterPath with EvenOdd rule so interior rings become holes
                path = QPainterPath()
                path.setFillRule(Qt.FillRule.OddEvenFill)

                # Exterior ring
                exterior_pol = ring_to_polygon(poly.exterior)
                path.addPolygon(exterior_pol)
                path.closeSubpath()

                # Interior rings (holes)
                for interior in poly.interiors:
                    hole_pol = ring_to_polygon(interior)
                    path.addPolygon(hole_pol)
                    path.closeSubpath()

                self.__shp_paths.append(path)

                # Store exterior + holes for hit-testing
                holes = [ring_to_polygon(interior) for interior in poly.interiors]
                self.__shp_polygons.append(exterior_pol)
                self.__shp_holes.append(holes)

        self.__shp_loaded = True
        self.repaint()


    # ─────────────────────────────────────────
    #  Mouse & input
    # ─────────────────────────────────────────

    def mousePressEvent(self, e: QMouseEvent):
        x = e.position().x()
        y = e.position().y()

        if self.__add_vertex:
            # Add vertex to manual polygon
            self.__pol.append(QPointF(x, y))
        else:
            # Move query point
            self.__q.setX(x)
            self.__q.setY(y)

        self.repaint()

    def changeStatus(self):
        # Toggle between polygon vertex input and point input
        self.__add_vertex = not self.__add_vertex

    def clearData(self):
        # Clear everything
        self.__pol.clear()
        self.__shp_polygons.clear()
        self.__shp_holes.clear()
        self.__shp_paths.clear()
        self.__shp_loaded = False
        self.__q.setX(-25)
        self.__q.setY(-25)
        self.repaint()


    # ─────────────────────────────────────────
    #  Drawing
    # ─────────────────────────────────────────

    def paintEvent(self, e: QPaintEvent):
        qp = QPainter(self)
        qp.begin(self)

        # Draw SHP polygons (if loaded) - blue outline, light fill WITH holes
        if self.__shp_loaded and self.__shp_paths:
            qp.setPen(QPen(Qt.GlobalColor.darkBlue, 1))
            qp.setBrush(QColor(173, 216, 230, 180))  # light blue, semi-transparent
            for path in self.__shp_paths:
                qp.drawPath(path)

        # Draw manual polygon on top - black outline, yellow fill
        if not self.__pol.isEmpty():
            qp.setPen(QPen(Qt.GlobalColor.black, 1))
            qp.setBrush(QColor(255, 255, 0, 180))  # yellow, semi-transparent
            qp.drawPolygon(self.__pol)

        # Draw query point - green circle
        r = 4
        qx = int(self.__q.x())
        qy = int(self.__q.y())
        if qx > 0 and qy > 0:  # hide default off-screen point
            qp.setPen(Qt.GlobalColor.black)
            qp.setBrush(Qt.GlobalColor.green)
            qp.drawEllipse(qx - r, qy - r, 2 * r, 2 * r)

        qp.end()


    # ─────────────────────────────────────────
    #  Getters
    # ─────────────────────────────────────────

    def getQ(self):
        return self.__q

    def getPol(self):
        # Return manual polygon if no SHP loaded, otherwise return SHP polygons
        if self.__shp_loaded and self.__shp_polygons:
            return self.__shp_polygons
        return [self.__pol]

    def getPolWithHoles(self):
        # Returns list of (exterior QPolygonF, [hole QPolygonF, ...])
        # For manual polygon: no holes
        if self.__shp_loaded and self.__shp_polygons:
            return list(zip(self.__shp_polygons, self.__shp_holes))
        return [(self.__pol, [])]

    def isShpLoaded(self):
        return self.__shp_loaded