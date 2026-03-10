from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import math


class Algorithms:

    def getDistancePointEdge(self, q: QPointF, p1: QPointF, p2: QPointF):
        # Compute distance from point q to line segment p1-p2 in pixels
        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()

        # Degenerate edge (p1 == p2) -> return distance to vertex
        if dx == 0 and dy == 0:
            return math.hypot(q.x() - p1.x(), q.y() - p1.y())

        # Parameter t of nearest point on the infinite line
        t = ((q.x() - p1.x()) * dx + (q.y() - p1.y()) * dy) / (dx * dx + dy * dy)

        # Clamp t to [0, 1] to stay within the segment
        t = max(0.0, min(1.0, t))

        # Nearest point on segment
        nearest_x = p1.x() + t * dx
        nearest_y = p1.y() + t * dy

        return math.hypot(q.x() - nearest_x, q.y() - nearest_y)

    def getPointAndPolygonBoundary(self, q: QPointF, pol: QPolygonF):
        # Shared boundary check for both RC and WN algorithms
        # Returns:
        #   "vertex"  -> q is within VERTEX_TOL px of a polygon vertex
        #   "edge"    -> q is within EDGE_TOL px of a polygon edge
        #   None      -> q is not on boundary
        #
        # IMPORTANT: vertex loop runs first (all vertices), then edge loop.
        # This guarantees "vertex" always wins over "edge" even when q is
        # close to a vertex that also lies on two edges.

        VERTEX_TOL = 10.0    # pixel tolerance for vertex detection (~2.6 mm on 96 DPI)
        EDGE_TOL   = 5.0     # pixel tolerance for edge detection   (~1.3 mm on 96 DPI)

        n = len(pol)

        # --- Loop 1: check ALL vertices first ---
        for i in range(n):
            p1 = pol[i]
            dist_vertex = math.hypot(q.x() - p1.x(), q.y() - p1.y())
            if dist_vertex < VERTEX_TOL:
                return "vertex"

        # --- Loop 2: check ALL edges (only reached if no vertex matched) ---
        for i in range(n):
            p1 = pol[i]
            p2 = pol[(i + 1) % n]
            if self.getDistancePointEdge(q, p1, p2) < EDGE_TOL:
                return "edge"

        return None

    def getPointPolygonPositionWN(self, q: QPointF, pol: QPolygonF):
        # Analyze point and polygon position using Winding Number algorithm
        #
        # Returns:
        #   "vertex"  -> point is within 10 px of a vertex
        #   "edge"    -> point is within 5 px of an edge
        #    0        -> point is OUTSIDE
        #   !=0       -> point is INSIDE (value = winding number Omega)

        eps = 1.0e-10

        # --- Pass 1: boundary test (shared) ---
        boundary = self.getPointAndPolygonBoundary(q, pol)
        if boundary is not None:
            return boundary  # "vertex" or "edge"

        # --- Pass 2: Winding Number accumulation ---
        n = len(pol)
        omega_sum = 0.0

        for i in range(n):
            xi  = pol[i].x()
            yi  = pol[i].y()
            xi1 = pol[(i + 1) % n].x()
            yi1 = pol[(i + 1) % n].y()

            # Determinant t -> halfplane of q relative to directed edge p_i -> p_i+1
            t = (xi1 - xi) * (q.y() - yi) - (yi1 - yi) * (q.x() - xi)

            # Vectors from q to p_i and p_i+1
            ux = xi  - q.x();  uy = yi  - q.y()
            vx = xi1 - q.x();  vy = yi1 - q.y()

            # Absolute angle omega_i between the two vectors via atan2
            angle_u = math.atan2(uy, ux)
            angle_v = math.atan2(vy, vx)
            omega_i = angle_v - angle_u

            # Normalize to (-pi, pi]
            while omega_i >  math.pi: omega_i -= 2 * math.pi
            while omega_i <= -math.pi: omega_i += 2 * math.pi

            omega_i = abs(omega_i)

            # Accumulate with sign from halfplane
            if t > eps:
                omega_sum += omega_i   # left halfplane  -> +omega (CCW)
            else:
                omega_sum -= omega_i   # right halfplane -> -omega (CW)

        # Winding Number as integer (multiples of 2*pi)
        resultWN = int(round(omega_sum / (2 * math.pi)))

        return resultWN  # 0 = outside, non-zero = inside

    def getPointPolygonPositionRC(self, q: QPointF, pol: QPolygonF):
        # Analyze point and polygon position using Ray Crossing algorithm
        #
        # Returns:
        #   "vertex"  -> point is within 10 px of a vertex
        #   "edge"    -> point is within 5 px of an edge
        #    0        -> point is OUTSIDE
        #    1        -> point is INSIDE

        # --- Boundary test (shared) ---
        boundary = self.getPointAndPolygonBoundary(q, pol)
        if boundary is not None:
            return boundary  # "vertex" or "edge"

        # --- Ray Crossing accumulation ---
        k = 0
        n = len(pol)

        for i in range(n):
            xi  = pol[i].x() - q.x()
            yi  = pol[i].y() - q.y()
            xi1 = pol[(i + 1) % n].x() - q.x()
            yi1 = pol[(i + 1) % n].y() - q.y()

            # Find suitable segment (crosses horizontal ray to the right)
            if (yi1 > 0) and (yi <= 0) or (yi > 0) and (yi1 <= 0):
                xm = (xi1 * yi - xi * yi1) / (yi1 - yi)
                if xm > 0:
                    k = k + 1

        if k % 2 == 1:
            return 1   # inside

        return 0       # outside