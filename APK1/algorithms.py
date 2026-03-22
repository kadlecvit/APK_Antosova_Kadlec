from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import math

class Algorithms:
    
    # Pixel tolerance for vertex detection
    TOL = 3.0  

    def isPointInMinMaxBox(self, q: QPointF, pol: QPolygonF):
        # Fast bounding box check
        if pol.isEmpty():
            return False
        
        min_x = pol[0].x()
        max_x = pol[0].x()
        min_y = pol[0].y()
        max_y = pol[0].y()
        
        for p in pol:
            if p.x() < min_x:
                min_x = p.x()
            if p.x() > max_x:
                max_x = p.x()
            if p.y() < min_y:
                min_y = p.y()
            if p.y() > max_y:
                max_y = p.y()
        
        if q.x() >= min_x and q.x() <= max_x and q.y() >= min_y and q.y() <= max_y:
            return True
        return False

    def isPointOnVertex(self, q: QPointF, p: QPointF):
        # Check singularity: point on vertex using pixel tolerance
        if abs(q.x() - p.x()) < self.TOL and abs(q.y() - p.y()) < self.TOL:
            return True
        return False

    def getHalfPlane(self, q: QPointF, p1: QPointF, p2: QPointF):
        # Determinant for Half-plane test
        return (p2.x() - p1.x()) * (q.y() - p1.y()) - (p2.y() - p1.y()) * (q.x() - p1.x())

    def getAngle(self, q: QPointF, p1: QPointF, p2: QPointF):
        # Angle between vectors q->p1 and q->p2
        ux = p1.x() - q.x()
        uy = p1.y() - q.y()
        vx = p2.x() - q.x()
        vy = p2.y() - q.y()
        
        omega = math.atan2(vy, vx) - math.atan2(uy, ux)
        
        while omega > math.pi: 
            omega = omega - 2 * math.pi
        while omega <= -math.pi: 
            omega = omega + 2 * math.pi
            
        return abs(omega)

    def getPointPolygonPositionRC(self, q: QPointF, pol: QPolygonF):
        # Analyze point and polygon position using Ray Crossing algorithm (Two Rays Method)
        k_l = 0
        k_r = 0
        n = len(pol)
        
        # Vertex singularity
        for i in range(n):
            if self.isPointOnVertex(q, pol[i]):
                return -1 
            

        # Process all polygon edges with coordinates shifted to q
        for i in range(n):
            xi = pol[i].x() - q.x()
            yi = pol[i].y() - q.y()
            
            xi1 = pol[(i+1)%n].x() - q.x()
            yi1 = pol[(i+1)%n].y() - q.y()
            
            if (yi1 - yi) == 0:
                continue
                
            xm = (xi1 * yi - xi * yi1) / (yi1 - yi)
            
            # Left ray
            if (yi1 < 0) != (yi < 0) and xm < 0:
                k_l += 1
                
            # Right ray
            if (yi1 > 0) != (yi > 0) and xm > 0:
                k_r += 1
                    
        # Mathematical edge fallback 
        if k_l % 2 != k_r % 2:
            return -2 
            
        # Inside
        if k_r % 2 == 1:
            return 1
            
        # Outside
        return 0

    def getPointPolygonPositionWN(self, q: QPointF, pol: QPolygonF):
        # Analyze point position using Winding Number
        omega_sum = 0.0
        n = len(pol)
        
        # Vertex singularity
        for i in range(n):
            if self.isPointOnVertex(q, pol[i]):
                return -1 
    

        # Calculate angles and accumulate
        for i in range(n):
            p1 = pol[i]
            p2 = pol[(i + 1) % n]
            
            t = self.getHalfPlane(q, p1, p2)
            omega = self.getAngle(q, p1, p2)
            
            # Edge check: normalize t by edge length for scale-independence
            edge_len = math.hypot(p2.x() - p1.x(), p2.y() - p1.y())
            e = 0.05
            if edge_len > 0 and abs(t) / edge_len < e and abs(omega - math.pi) < e:
                return -2

            if t > 0:
                omega_sum += omega
            else:
                omega_sum -= omega

        result = int(round(omega_sum / (2 * math.pi)))
        
        # Inside
        if result != 0:
            return 1 
            
        # Outside
        return 0