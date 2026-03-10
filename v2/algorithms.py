from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import math

class Algorithms:

    def isPointInMinMaxBox(self, q: QPointF, pol: QPolygonF):
        if pol.isEmpty():
            return False
            
        min_x = min(p.x() for p in pol)
        max_x = max(p.x() for p in pol)
        min_y = min(p.y() for p in pol)
        max_y = max(p.y() for p in pol)
        
        return min_x <= q.x() <= max_x and min_y <= q.y() <= max_y

    def getDistancePointEdge(self, q: QPointF, p1: QPointF, p2: QPointF):
        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()

        if dx == 0 and dy == 0:
            return math.hypot(q.x() - p1.x(), q.y() - p1.y())

        t = ((q.x() - p1.x()) * dx + (q.y() - p1.y()) * dy) / (dx * dx + dy * dy)
        t = max(0.0, min(1.0, t))

        nearest_x = p1.x() + t * dx
        nearest_y = p1.y() + t * dy

        return math.hypot(q.x() - nearest_x, q.y() - nearest_y)

    def getPointAndPolygonBoundary(self, q: QPointF, pol: QPolygonF):
        VERTEX_TOL = 10.0
        EDGE_TOL   = 5.0
        n = len(pol)

        for i in range(n):
            p1 = pol[i]
            if math.hypot(q.x() - p1.x(), q.y() - p1.y()) < VERTEX_TOL:
                return "vertex"

        for i in range(n):
            p1 = pol[i]
            p2 = pol[(i + 1) % n]
            if self.getDistancePointEdge(q, p1, p2) < EDGE_TOL:
                return "edge"

        return None

    def getPointPolygonPositionWN(self, q: QPointF, pol: QPolygonF):
        boundary = self.getPointAndPolygonBoundary(q, pol)
        if boundary is not None:
            return boundary

        n = len(pol)
        omega_sum = 0.0
        eps = 1.0e-10

        for i in range(n):
            xi  = pol[i].x()
            yi  = pol[i].y()
            xi1 = pol[(i + 1) % n].x()
            yi1 = pol[(i + 1) % n].y()

            t = (xi1 - xi) * (q.y() - yi) - (yi1 - yi) * (q.x() - xi)
            ux = xi  - q.x()
            uy = yi  - q.y()
            vx = xi1 - q.x()
            vy = yi1 - q.y()

            omega_i = math.atan2(vy, vx) - math.atan2(uy, ux)

            while omega_i >  math.pi: omega_i -= 2 * math.pi
            while omega_i <= -math.pi: omega_i += 2 * math.pi

            omega_i = abs(omega_i)

            if t > eps:
                omega_sum += omega_i
            else:
                omega_sum -= omega_i

        return int(round(omega_sum / (2 * math.pi)))

    def getPointPolygonPositionRC(self, q: QPointF, pol: QPolygonF):
        boundary = self.getPointAndPolygonBoundary(q, pol)
        if boundary is not None:
            return boundary

        k = 0
        n = len(pol)

        for i in range(n):
            xi  = pol[i].x() - q.x()
            yi  = pol[i].y() - q.y()
            xi1 = pol[(i + 1) % n].x() - q.x()
            yi1 = pol[(i + 1) % n].y() - q.y()

            if (yi1 > 0) and (yi <= 0) or (yi > 0) and (yi1 <= 0):
                xm = (xi1 * yi - xi * yi1) / (yi1 - yi)
                if xm > 0:
                    k = k + 1

        if k % 2 == 1:
            return 1
            
        return 0