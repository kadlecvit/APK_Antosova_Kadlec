from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from qpoint3df import *
from random import *
from math import *

class Draw(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__points = []
        self.__DT = []
        self.__contours = []
        self.__main_contours = []
        self.__slope_triangles = []
        self.__aspect_triangles = []
        self.__file_loaded = False
        self.__show_DT = True
        self.__show_contours = True
        self.__show_slope = True
        self.__show_aspect = True
        self.__show_points = True


    def mousePressEvent(self, e):
        if self.__file_loaded:
            return

        #Get cursor coordinates
        x = e.position().x()
        y = e.position().y()

        #Get random z
        z_min = 200
        z_max = 600
        z = random() * (z_max - z_min) + z_min

        #Create new point
        p = QPoint3DF(x, y, z)

        #Add point to list
        self.__points.append(p)

        #Repaint
        self.repaint()


    def paintEvent(self, e):
        #Draw situation
        qp = QPainter(self)

        #Start draw
        qp.begin(self)

        #Create new pen
        pen = QPen()

        #Draw slope triangles 
        if self.__show_slope and self.__slope_triangles:
            pen.setWidth(0)
            pen.setColor(Qt.GlobalColor.transparent)
            qp.setPen(pen)

            for t in self.__slope_triangles:
                #Slope angle: 0 = white (flat), pi/2 = black (vertical)
                slope = t.getSlope()
                gray_value = int(255 * (1 - slope / (pi / 2)))
                gray_value = max(0, min(255, gray_value))
                color = QColor(gray_value, gray_value, gray_value)
                qp.setBrush(color)

                polygon = QPolygonF([t.getP1(), t.getP2(), t.getP3()])
                qp.drawPolygon(polygon)

        #Draw aspect triangles
        if self.__show_aspect and self.__aspect_triangles:
            pen.setWidth(0)
            pen.setColor(Qt.GlobalColor.transparent)
            qp.setPen(pen)

            for t in self.__aspect_triangles:
                aspect = t.getAspect()
                color = self.getAspectColor(aspect)
                qp.setBrush(color)

                polygon = QPolygonF([t.getP1(), t.getP2(), t.getP3()])
                qp.drawPolygon(polygon)

        #Draw DT edges
        if self.__show_DT:
            pen.setWidth(1)
            pen.setColor(Qt.GlobalColor.green)
            qp.setPen(pen)
            qp.setBrush(Qt.BrushStyle.NoBrush)

            for e in self.__DT:
                qp.drawLine(e.getStart(), e.getEnd())

        #Draw contour lines
        if self.__show_contours:
            pen.setWidth(1)
            pen.setColor(QColor(150, 75, 0)) 
            qp.setPen(pen)
            qp.setBrush(Qt.BrushStyle.NoBrush)

            for c in self.__contours:
                qp.drawLine(c.getStart(), c.getEnd())

            #Draw main contour lines
            pen.setWidth(2)
            pen.setColor(QColor(165, 42, 42))  
            qp.setPen(pen)

            for c in self.__main_contours:
                qp.drawLine(c.getStart(), c.getEnd())

        #Draw points
        if self.__show_points:
            pen.setWidth(5)
            pen.setColor(Qt.GlobalColor.black)
            qp.setPen(pen)
            qp.drawPoints(self.__points)

        #End draw
        qp.end()


    def getAspectColor(self, aspect):
        #Return color based on aspect azimuth (8 directions)

        deg = degrees(aspect)

        if deg < 22.5 or deg >= 337.5:
            return QColor(110, 200, 110)     
        elif deg < 67.5:
            return QColor(0, 200, 0)        
        elif deg < 112.5:
            return QColor(0, 0, 255)         
        elif deg < 157.5:
            return QColor(200, 0, 200)       
        elif deg < 202.5:
            return QColor(255, 105, 180)    
        elif deg < 247.5:
            return QColor(255, 0, 0)         
        elif deg < 292.5:
            return QColor(255, 165, 0)      
        else:
            return QColor(200, 200, 0)   
        
           
    #Setters / Getters
    def setDT(self, DT):
        self.__DT = DT

    def getDT(self):
        return self.__DT

    def getPoints(self):
        return self.__points

    def setPoints(self, points):
        self.__points = points

    def setSlopeTriangles(self, triangles):
        self.__slope_triangles = triangles

    def setAspectTriangles(self, triangles):
        self.__aspect_triangles = triangles

    def setContours(self, contours):
        self.__contours = contours

    def setMainContours(self, contours):
        self.__main_contours = contours

    def setFileLoaded(self, value):
        self.__file_loaded = value

    def setShowDT(self, value):
        self.__show_DT = value
        self.repaint()

    def setShowContours(self, value):
        self.__show_contours = value
        self.repaint()

    def setShowSlope(self, value):
        self.__show_slope = value
        self.repaint()

    def setShowAspect(self, value):
        self.__show_aspect = value
        self.repaint()

    def setShowPoints(self, value):
        self.__show_points = value
        self.repaint()


    #Clear methods
    def clearResult(self):
        self.__DT.clear()
        self.__contours.clear()
        self.__main_contours.clear()
        self.__slope_triangles.clear()
        self.__aspect_triangles.clear()

        self.repaint()

    def clearAll(self):
        self.__DT.clear()
        self.__contours.clear()
        self.__main_contours.clear()
        self.__slope_triangles.clear()
        self.__aspect_triangles.clear()
        self.__points.clear()
        self.__file_loaded = False

        self.repaint()