from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from math import *
import numpy as np
import numpy.linalg as np2

class Algorithms:
    
    def __init__(self):
        pass
    
    def get2VectorsAngle(self, p1:QPointF, p2:QPointF, p3:QPointF, p4:QPointF):
        # Angle between two vectors
        ux = p2.x() - p1.x()    
        uy = p2.y() - p1.y()
        
        vx = p4.x() - p3.x()
        vy = p4.y() - p3.y()    
        
        # Dot product
        dot = ux*vx + uy*vy
        
        # Norms
        nu = (ux**2 + uy**2)**0.5
        nv = (vx**2 + vy**2)**0.5
        
        # Check zero length vector
        if nu == 0 or nv == 0: return 0.0

        # Correct interval
        arg = dot/(nu*nv)
        arg = max(-1, min(1,arg)) 
        
        return acos(arg)
    
    def removeDuplicatePoints(self, pol:QPolygonF):
        # Remove duplicate points from polygon
        pol_clean = QPolygonF()

        # Check each point against already added points
        for i in range(len(pol)):
            duplicate = False
            
            for j in range(len(pol_clean)):
                if pol[i] == pol_clean[j]:
                    duplicate = True
                    break

            # Add only unique points
            if not duplicate:
                pol_clean.append(pol[i])
                
        return pol_clean
    
    def arePointsCollinear(self, pol:QPolygonF):
        # Check if all points are collinear using cross product
        n = len(pol)
        if n < 3:
            return True

        # If any cross product is nonzero, points are not collinear
        for i in range(2, n):
            cross = self.getPointLinePosition(pol[i], pol[0], pol[1])
            
            if abs(cross) > 1e-6:
                return False
            
        return True
    
    def createCHJ(self, pol:QPolygonF):
        # Create Convex Hull using Jarvis Scan
        ch = QPolygonF()

        # Remove duplicates
        pol = self.removeDuplicatePoints(pol)
        
        # Check singularities
        if len(pol) < 3:
            return ch
        
        if self.arePointsCollinear(pol):
            return ch
        
        # Find pivot q with minimum y (if tie, minimum x)
        q = min(pol, key = lambda k: (k.y(), k.x()))

        # Find left-most point (minimize x)
        s = min(pol, key = lambda k: k.x())
        
        # Initial segment
        pj = q
        pj1 = QPointF(s.x(), q.y())

        # Add to CH
        ch.append(pj)
        
        # Find all points of CH
        while True:
            omega_max = 0
            index_max = -1
            
            # Browse all points 
            for i in range(len(pol)):
                
                # Different points
                if pj != pol[i]:
                    
                    # Compute omega
                    omega = self.get2VectorsAngle(pj, pj1, pj, pol[i])
                    
                    # Actualize maximum
                    if(omega > omega_max):
                        omega_max = omega
                        index_max = i
            
            # Add point to the convex hull
            ch.append(pol[index_max])

            # Reassign points
            pj1 = pj
            pj = pol[index_max]
            
            # Stopping condition
            if pj == q:
                break
        return ch
    
    def calculateDistance(self, p1:QPointF, p2:QPointF):
        # Euclidean distance between two points
        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()
        
        return (dx**2 + dy**2)**0.5
    
    def getPointLinePosition(self, p:QPointF, p1:QPointF, p2:QPointF):
        # Determine point and line position using Half-plane test
        ux = p2.x() - p1.x()
        uy = p2.y() - p1.y()
        vx = p.x() - p1.x()
        vy = p.y() - p1.y()

        return ux * vy - uy * vx
    
    def createCHG(self, pol:QPolygonF):
        # Create Convex Hull using Graham Scan
        ch = QPolygonF()

        # Remove duplicates 
        pol = self.removeDuplicatePoints(pol)
        n = len(pol)
        
        # Check singularities
        if n < 3:
            return ch
        
        if self.arePointsCollinear(pol):
            return ch
        
        # Find pivot q with minimum y
        q = min(pol, key = lambda k: k.y())

        # Create extra point to create horizontal reference vector
        extra_point = QPointF(q.x() + 1, q.y())

        # Add to CH
        ch.append(q)
        angles_dict = {}
        
        # Compute angles from pivot to all other points
        for i in range(n):
            
            # Skip pivot
            if q == pol[i]:
                continue
            
            ang = self.get2VectorsAngle(q, extra_point, q, pol[i])

            # If same angle, keep the point farther from pivot
            if ang in angles_dict.keys():
                prev_point_dist = self.calculateDistance(q, pol[angles_dict[ang]])
                current_point_dist = self.calculateDistance(q, pol[i])
                
                if current_point_dist < prev_point_dist:
                    continue
                
            angles_dict[ang] = i
        
        # Sort indices by angle ascending
        
        sorted_angles = sorted(angles_dict.keys())
        sorted_indices = []
        
        for angle in sorted_angles:
            index = angles_dict[angle]
            sorted_indices.append(index)
        

        # Add first sorted point to CH
        ch.append(pol[sorted_indices[0]])
        
        # Process remaining sorted points
        for j in range(1, len(sorted_indices)):
            current_point = pol[sorted_indices[j]]

            # Remove points that make a clockwise turn
            while len(ch) > 1:
                position = self.getPointLinePosition(current_point, ch[len(ch) - 2], ch[len(ch) - 1])
                if position > 0:
                    break
                ch.remove(len(ch) - 1)
                
            # Add current point
            ch.append(current_point)
            
        return ch
    
    def createMMB(self, pol:QPolygonF):
        # Create min max box and compute its area

        # Points with extreme coordinates 
        p_xmin = min(pol, key = lambda k: k.x())
        p_xmax = max(pol, key = lambda k: k.x())
        p_ymin = min(pol, key = lambda k: k.y())
        p_ymax = max(pol, key = lambda k: k.y())
        
        # Create vertices 
        v1 = QPointF(p_xmin.x(), p_ymin.y())
        v2 = QPointF(p_xmax.x(), p_ymin.y())
        v3 = QPointF(p_xmax.x(), p_ymax.y())
        v4 = QPointF(p_xmin.x(), p_ymax.y())
        
        # Create new polygon 
        mmb = QPolygonF([v1, v2, v3, v4])
        
        # Area of MMB
        area = (v2.x() - v1.x()) * (v3.y() - v2.y())
        
        return mmb, area
     
    def rotatePolygon(self, pol:QPolygonF, sig:float):
        # Rotate polygon by a given angle 
        pol_rot = QPolygonF()
        
        # Process all polygon vertices
        for i in range(len(pol)):
            
            # Rotate point
            x_rot = pol[i].x() * cos(sig) - pol[i].y() * sin(sig)
            y_rot = pol[i].x() * sin(sig) + pol[i].y() * cos(sig)
            
            # Create QPoint
            vertex = QPointF(x_rot, y_rot)
            
            # Add vertex to rotated polygon
            pol_rot.append(vertex)
            
        return pol_rot
    
    def createMBR(self, building:QPolygonF, use_graham:bool = False):
        # Create minimum bounding rectangle using repeated construction of MMB
        sigma_min = 0

        # Convex hull using selected method
        if use_graham: 
            ch = self.createCHG(building)
        else: 
            ch = self.createCHJ(building)
        
        # Initialization
        mmb_min, area_min = self.createMMB(ch)
        
        # Process all edges of convex hull
        n = len(ch)
        for i in range(n):
            # Coordinate differences
            dx = ch[(i+1)%n].x() - ch[i].x()
            dy = ch[(i+1)%n].y() - ch[i].y()

            # Compute direction of edge
            sigma = atan2(dy, dx)
            
            # Rotate convex hull
            ch_r = self.rotatePolygon(ch, -sigma)
            
            # Compute min-max box
            mmb, area = self.createMMB(ch_r)
            
            # Did we find a better min-max box?
            if area < area_min:    
                area_min = area
                mmb_min = mmb
                sigma_min = sigma
        
        # Back rotation 
        return self.rotatePolygon(mmb_min, sigma_min), sigma_min

    def getArea(self, pol:QPolygonF):
        # Compute area
        area = 0
        n = len(pol)
        
        # Process all vertices
        for i in range(n):
            area += pol[i].x() * (pol[(i + 1) % n].y() - pol[(i - 1 + n) % n].y())
            
        return abs(area)/2    
        
    def resizeRectangle(self, building:QPolygonF, mbr: QPolygonF):
        # Resize rectangle area to match building area
        
        # Area of the rectangle
        A = self.getArea(mbr)
        
        # Area of the building
        Ab = self.getArea(building)
        
        # Fraction of both areas
        k = Ab / A
        
        # Compute centroid of the rectangle
        x_c = (mbr[0].x()+mbr[1].x()+mbr[2].x()+mbr[3].x()) / 4
        y_c = (mbr[0].y()+mbr[1].y()+mbr[2].y()+mbr[3].y()) / 4
        
        # Compute vectors from centroid to vertices
        v1_x = mbr[0].x() - x_c
        v1_y = mbr[0].y() - y_c 
        
        v2_x = mbr[1].x() - x_c
        v2_y = mbr[1].y() - y_c 

        v3_x = mbr[2].x() - x_c
        v3_y = mbr[2].y() - y_c 
        
        v4_x = mbr[3].x() - x_c
        v4_y = mbr[3].y() - y_c
        
        # Resize vectors by square root of area ratio
        v1_x_res = v1_x * sqrt(k)
        v1_y_res = v1_y * sqrt(k)
        
        v2_x_res = v2_x * sqrt(k)
        v2_y_res = v2_y * sqrt(k)
        
        v3_x_res = v3_x * sqrt(k)
        v3_y_res = v3_y * sqrt(k)
        
        v4_x_res = v4_x * sqrt(k)
        v4_y_res = v4_y * sqrt(k)
        
        # Compute new vertex positions
        p1_x = v1_x_res + x_c  
        p1_y = v1_y_res + y_c 
        
        p2_x = v2_x_res + x_c  
        p2_y = v2_y_res + y_c 
        
        p3_x = v3_x_res + x_c  
        p3_y = v3_y_res + y_c 
        
        p4_x = v4_x_res + x_c  
        p4_y = v4_y_res + y_c
        
        # Create new vertices
        p1 = QPointF(p1_x,  p1_y)
        p2 = QPointF(p2_x,  p2_y)
        p3 = QPointF(p3_x,  p3_y)
        p4 = QPointF(p4_x,  p4_y)   
        
        # Create polygon
        mbr_res = QPolygonF()
        mbr_res.append(p1)
        mbr_res.append(p2)
        mbr_res.append(p3)
        mbr_res.append(p4)
       
        return mbr_res
    
    def simplifyBuildingMBR(self, building:QPolygonF, use_graham:bool = False):
        # Simplify building using MBR
        mbr, sigma = self.createMBR(building, use_graham)
        
        # Resize rectangle
        mbr_res = self.resizeRectangle(building, mbr)
        
        return mbr_res, sigma
    
    def simplifyBuildingPCA(self, building:QPolygonF):
        # Simplify building using PCA
        X, Y = [], []

        # Convert polygon vertices to matrix
        for p in building:
            X.append(p.x())
            Y.append(p.y())
        
        # Create A
        A = np.array([X, Y])
        
        # Compute covariance matrix
        C = np.cov(A)

        # Singular Value Decomposition
        [U, S, V] = np2.svd(C)

        # Compute direction of the principal component
        sigma = atan2(V[0][1], V[0][0])

        # Rotate building by -sigma
        build_rot = self.rotatePolygon(building, -sigma)
        
        # Create MMB
        mmb, area = self.createMMB(build_rot)
        
        # Rotate MMB by sigma
        mbr = self.rotatePolygon(mmb, sigma)

        # Resize MMB
        mbr_res = self.resizeRectangle(building, mbr)
        
        return mbr_res, sigma  
    
    def simplifyBuildingLE(self, building:QPolygonF):
        # Simplify building using Longest Edge
        n = len(building)
        longest_edge = 0
        a, b = building[0], building[1]
        
        # Find the longest edge of the building
        for i in range(n):
            edge_length = self.calculateDistance(building[i], building[(i+1)%n])
            if edge_length > longest_edge:
                longest_edge = edge_length
                a = building[i]
                b = building[(i+1)%n]
        
        # Compute direction of the longest edge
        sigma = atan2(b.y() - a.y(), b.x() - a.x())

        # Rotate building by -sigma
        build_rot = self.rotatePolygon(building, -sigma)
        
        # Create MMB 
        mmb, area = self.createMMB(build_rot)
        
        # Rotate MMB by sigma
        mbr = self.rotatePolygon(mmb, sigma)

        # Resize MMB
        mbr_res = self.resizeRectangle(building, mbr)
        
        return mbr_res, sigma  

    def simplifyBuildingWA(self, building:QPolygonF):
        # Simplify building using Wall Average
        n = len(building)

        # Compute directions of all edges
        sigmas = []
        for i in range(n):
            dx = building[(i+1)%n].x() - building[i].x()
            dy = building[(i+1)%n].y() - building[i].y()
            sigmas.append(atan2(dy, dx))
        
        # Reference direction (first edge)
        sigma_12 = sigmas[0]

        # Initialize weighted sums
        rs_sum = 0
        s_sum = 0
        
        # Process all vertices
        for i in range(n):
            # Compute inner angle at vertex
            omega_i = abs(sigmas[i] - sigmas[(i-1+n)%n])

            # Compute k and oriented remainder
            k_i = 2 * omega_i / pi
            r_i = (k_i - floor(k_i)) * pi / 2

            # Correct sign if remainder > pi/4
            if r_i > pi / 4: 
                r_i = r_i - pi / 2
            
            # Accumulate weighted remainder by edge length
            s_i = self.calculateDistance(building[i], building[(i+1)%n])
            rs_sum = rs_sum + (r_i * s_i)
            s_sum = s_sum + s_i
        
        # Compute final direction as weighted average
        sigma = sigma_12 + rs_sum / s_sum

        # Rotate building by -sigma
        build_rot = self.rotatePolygon(building, -sigma)
        
        # Create MMB 
        mmb, area = self.createMMB(build_rot)
        
        # Rotate MMB by sigma
        mbr = self.rotatePolygon(mmb, sigma)

        # Resize MMB
        mbr_res = self.resizeRectangle(building, mbr)
        
        return mbr_res, sigma  

    def simplifyBuildingWB(self, building:QPolygonF):
        # Simplify building using Weighted Bisector
        n = len(building)

        # Polygon must have at least 4 vertices for diagonals
        if n < 4:
            return self.simplifyBuildingMBR(building)
        
        # Find all diagonals and compute their lengths
        potential_diagonals = {}
        for i in range(n-1):
            for j in range(i+1, n):
                
                # Skip adjacent vertices (edges, not diagonals)
                if abs(i - j) <= 1 or abs(i - j) > n - 2: 
                    continue
                
                a = building[i]
                b = building[j]
                diag_id = ((a.x(), a.y()), (b.x(), b.y()))
                length = self.calculateDistance(a, b)
                potential_diagonals[diag_id] = length
        
        # Sort diagonals by length descending
        sorted_diagonals = dict(sorted(potential_diagonals.items(), key = lambda item: item[1], reverse = True))

        # Store two longest valid diagonals
        two_diag_len = []
        two_diag_dir = []
        
        # Check each diagonal for intersection with polygon edges
        for (a_coords, b_coords), length in sorted_diagonals.items():
            a, b = QPointF(*a_coords), QPointF(*b_coords)
            intersects = False

            # Test against all edges of the polygon
            for i in range(n):
                c, d = building[i], building[(i+1)%n]

                # Skip edges sharing a vertex with diagonal
                if a == c or a == d or b == c or b == d: 
                    continue
                
                # Half-plane tests for segment intersection
                ta = self.getPointLinePosition(a, c, d)
                tb = self.getPointLinePosition(b, c, d)
                tc = self.getPointLinePosition(c, a, b)
                td = self.getPointLinePosition(d, a, b)
                
                # Segments intersect if points are on opposite sides
                if ta * tb < 0 and tc * td < 0:
                    intersects = True
                    break
            
            # If diagonal does not intersect any edge, it is valid
            if not intersects:
                sigma0 = atan2(b.y() - a.y(), b.x() - a.x())
                two_diag_len.append(length)
                two_diag_dir.append(sigma0)
            
            # After finding two valid diagonals, compute weighted average
            if len(two_diag_len) == 2:
                sigma = (two_diag_len[0] * two_diag_dir[0] + two_diag_len[1] * two_diag_dir[1]) / sum(two_diag_len)

                # Rotate building by -sigma
                build_rot = self.rotatePolygon(building, -sigma)
                
                # Create MMB 
                mmb, area = self.createMMB(build_rot)
                
                # Rotate MMB by sigma
                mbr = self.rotatePolygon(mmb, sigma)

                # Resize MMB
                mbr_res = self.resizeRectangle(building, mbr)
                
                return mbr_res, sigma  
        
        # If less than 2 valid diagonals found, use MBR
        return self.simplifyBuildingMBR(building)

    def computeDeltaSigma(self, building:QPolygonF, sigma: float):
        # Compute Mean Square Error (MSE) of the building's angles
        n = len(building)
        if n < 3: 
            return 0.0
        
        # Sum of squared remainders
        sq_sum = 0
        for i in range(n):
            # Direction of edge
            dx = building[(i+1)%n].x() - building[i].x()
            dy = building[(i+1)%n].y() - building[i].y()
            sigma_i = atan2(dy, dx)
            
            # Difference from main direction
            dif = abs(sigma_i - sigma)

            # Compute k and remainder
            k_i = 2 * dif / pi
            r_i = (k_i - floor(k_i)) * (pi / 2)
            
            # Correct sign
            if r_i > pi / 4: 
                r_i = r_i - pi / 2
            
            sq_sum = sq_sum + r_i ** 2
        
        # Delta sigma formula (convert to degrees)
        delta_sigma = (pi / (2 * n)) * sqrt(sq_sum)
        return delta_sigma * 180 / pi