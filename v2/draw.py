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

        self.__shp_polygons = []        
        self.__shp_loaded = False
        self.__highlighted_indices = [] 

    def loadShapefile(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Shapefile", "", "Shapefile (*.shp)")
        if not file_name:
            return

        try:
            shp = gpd.read_file(file_name)
            self.__loadGeometry(shp)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file:\n{str(e)}")

    def __loadGeometry(self, shp):
        self.__shp_polygons.clear()

        if shp is None or shp.empty:
            QMessageBox.critical(self, "Error", "Shapefile contains no geometry.")
            return

        min_x, min_y, max_x, max_y = shp.total_bounds
        w = self.width()
        h = self.height()

        def to_screen(x, y):
            sx = (float(x) - min_x) / (max_x - min_x) * w
            sy = (1.0 - (float(y) - min_y) / (max_y - min_y)) * h
            return QPointF(sx, sy)

        for geom in shp.geometry:
            if geom is None:
                continue

            if geom.geom_type == "Polygon":
                rings = [geom.exterior]
            elif geom.geom_type == "MultiPolygon":
                rings = [poly.exterior for poly in geom.geoms]
            else:
                continue  

            for ring in rings:
                pol = QPolygonF([to_screen(x, y) for x, y in ring.coords])
                self.__shp_polygons.append(pol)

        self.__shp_loaded = True
        self.__highlighted_indices.clear()
        self.repaint()

    def mousePressEvent(self, e: QMouseEvent):
        x = e.position().x()
        y = e.position().y()

        if self.__add_vertex:
            self.__pol.append(QPointF(x, y))
        else:
            self.__q.setX(x)
            self.__q.setY(y)
            self.__highlighted_indices.clear()

        self.repaint()

    def changeStatus(self):
        self.__add_vertex = not self.__add_vertex

    def clearData(self):
        self.__pol.clear()
        self.__shp_polygons.clear()
        self.__shp_loaded = False
        self.__q.setX(-25)
        self.__q.setY(-25)
        self.__highlighted_indices.clear()
        self.repaint()

    def setHighlighted(self, indices):
        self.__highlighted_indices = indices
        self.repaint()

    def paintEvent(self, e: QPaintEvent):
        qp = QPainter(self)
        qp.begin(self)

        if self.__shp_loaded and self.__shp_polygons:
            for i, pol in enumerate(self.__shp_polygons):
                if i in self.__highlighted_indices:
                    qp.setPen(QPen(Qt.GlobalColor.red, 2))
                    qp.setBrush(QBrush(QColor(255, 0, 0, 180), Qt.BrushStyle.FDiagPattern))
                else:
                    qp.setPen(QPen(Qt.GlobalColor.darkBlue, 1))
                    qp.setBrush(QColor(173, 216, 230, 180))  
                qp.drawPolygon(pol)

        elif not self.__pol.isEmpty():
            if 0 in self.__highlighted_indices:
                qp.setPen(QPen(Qt.GlobalColor.red, 2))
                qp.setBrush(QBrush(QColor(255, 0, 0, 180), Qt.BrushStyle.FDiagPattern))
            else:
                qp.setPen(QPen(Qt.GlobalColor.black, 1))
                qp.setBrush(QColor(255, 255, 0, 180))  
            qp.drawPolygon(self.__pol)

        r = 10
        qx = int(self.__q.x())
        qy = int(self.__q.y())
        if qx > 0 and qy > 0:
            qp.setPen(Qt.GlobalColor.black)
            qp.setBrush(Qt.GlobalColor.green)
            qp.drawEllipse(qx - r, qy - r, 2 * r, 2 * r)

        qp.end()

    def getQ(self):
        return self.__q

    def getPol(self):
        if self.__shp_loaded and self.__shp_polygons:
            return self.__shp_polygons
        return [self.__pol]

    def isShpLoaded(self):
        return self.__shp_loaded