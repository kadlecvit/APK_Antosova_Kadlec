from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from qpoint3df import *
from math import *
from edge import *
from triangle import *

class Algorithms:
    
    def __init__(self):
        
        pass
    
    def getPointLinePosition(self, a, b, p):
        #Analyze point and aline position (half plane test)
        tolerance = 1.0e-6
        
        #Components of vectors
        ux = b.x() - a.x()
        uy = b.y() - a.y()
        vx = p.x() - a.x()
        vy = p.y() - a.y()
        
        #Test criterion
        t = ux*vy - vx*uy
        
        #Point in the left half plane
        if t > tolerance:
            return 1
        
        #Point in the right half plane
        if t < -tolerance:
            return 0
    
        #Point on the line
        return -1
        
    
    def getNearestPoint(self, p, points):
        #Find point nearest to p in points
        p_nearest = None
        d_min = inf
        
        #Process all points
        for p_i in points:
            
            #Point p different from p_i
            if p != p_i:            
                #Coordinate differences
                dx = p.x() - p_i.x()
                dy = p.y() - p_i.y()
                      
                #Compute distance          
                dist = sqrt(dx**2 + dy**2)
                
                #Update minimum
                if dist < d_min:
                    d_min = dist
                    p_nearest = p_i
                    
        return p_nearest
    
    
    def get2LinesAngle(self, p1:QPointF, p2:QPointF, p3:QPointF, p4:QPointF):
        #Angle between two lines
        ux = p2.x() - p1.x()    
        uy = p2.y() - p1.y()
        
        vx = p4.x() - p3.x()
        vy = p4.y() - p3.y()    
        
        #Dot product
        dot = ux*vx + uy*vy
        
        #Norms
        nu = (ux**2 + uy**2)**0.5
        nv = (vx**2 + vy**2)**0.5
        
        #Correct interval
        arg = dot/(nu*nv)
        arg = max(-1, min(1,arg)) 
        
        return acos(arg)
    
    
    def findDelaunayPoint(self, p1, p2, points):
        #Find Delaunay point to the edge
        p_dt = None
        phi_max = 0

        #Process all points
        for p_i in points:
            
            #Point pi different from p1 and p2
            if p_i != p1 and p_i != p2:
                
                #Point in the left halfplane
                if self.getPointLinePosition (p_i, p1, p2) == 1:
                    
                    #Compute phi
                    phi = self.get2LinesAngle(p_i, p2, p_i, p1)
                    
                    #Update maximum
                    if phi > phi_max:
                        phi_max = phi
                        p_dt = p_i
        return p_dt
                    
    def createDT(self, points):
        #Create Delaunay triangulation                 
        DT = []
        AEL = [] 
        
        #Find pivot
        q = min(points, key = lambda k: k.y())   
        
        #Find point nearest to q
        qn = self.getNearestPoint(q, points)       
        
        #Create new edges
        e = Edge(q, qn)
        es = Edge(qn, q)  
        
        #Edges to AEL
        AEL.append (e)
        AEL.append (es) 
        
        #Repeat until AEL is empty             
        while AEL:
            #Take first edge
            e1 = AEL.pop()
            
            #Switch orientation
            e1s = e1.switchOrientation()
            
            #Find Delaunay point
            p_dt = self.findDelaunayPoint(e1s.getStart(), e1s.getEnd(), points)
            
            #Jump to the next iteration
            if p_dt == None:
                continue
            
            #Create new edges
            e2 = Edge(e1s.getEnd(), p_dt)
            e3 = Edge(p_dt, e1s.getStart())
            
            #Add new edges to DT
            DT.append(e1s)
            DT.append(e2)
            DT.append(e3)
                 
            #Update AEL
            self.updateAEL(e2,AEL)
            self.updateAEL(e3,AEL)
            
        return DT
    
    
    def updateAEL(self, e, AEL):
        #Verify if e in AEL with diffferent orientation
        es = e.switchOrientation()
        
        #Edge e in AEL, remove
        if es in AEL:
            AEL.remove(es)
            
        #Add e to AEL
        else:
            AEL.append(e) 
            
            
    def getContourPoint(self, p1, p2, z):
        #Compute intersection line and plane
        xb = (p2.x() - p1.x())/(p2.z() - p1.z()) * (z - p1.z()) + p1.x()
        yb = (p2.y() - p1.y())/(p2.z() - p1.z()) * (z - p1.z()) + p1.y()
        
        return QPoint3DF(xb, yb, z)
    
    
    def createContourLines(self, DT, z_min, z_max, dz):
        #Create contour lines using linear interpolation
        contour_lines = []
        
        #Process all contour lines
        for z in range(z_min, z_max, dz):
            
            #Traverse dt triangles one by one
            for i in range(0, len(DT), 3):
                
                #Triangle vertices
                p1 = DT[i].getStart()
                p2 = DT[i+1].getStart()
                p3 = DT[i+1].getEnd()
                
                #Height differences
                dz1 = z - p1.z()
                dz2 = z - p2.z()
                dz3 = z - p3.z()
                
                #Skip triangle
                if dz1 == 0 and dz2 == 0 and dz3 == 0:
                    continue
                
                #Edge (p1, p2) is colinear
                elif dz1 == 0 and dz2 == 0:
                    contour_lines.append(DT[i])
                    
                #Edge (p2, p3) is colinear
                elif dz2 == 0 and dz3 == 0:
                    contour_lines.append(DT[i+1])
                
                #Edge (p3, p1) is colinear
                elif dz3 == 0 and dz1 == 0:
                    contour_lines.append(DT[i+2])
                    
                #Edges (p1, p2) and (p2, p3) intersected by plane
                elif (dz1*dz2 <= 0) and (dz2*dz3 <= 0):
                    self.createContourLineSegment(p1, p2, p3, z, contour_lines)   
                  
                #Edges (p3, p1) and (p1, p2) intersected by plane      
                elif (dz2*dz3 <= 0) and (dz3*dz1 <= 0):
                    self.createContourLineSegment(p2, p3, p1, z, contour_lines)
                
                #Edges (p3, p1) and (p1, p2) intersected by plane
                elif (dz3*dz1 <= 0) and (dz1*dz2 <= 0):
                    self.createContourLineSegment(p3, p1, p2, z, contour_lines)
                    
        return contour_lines
    
    
    def createContourLineSegment(self, p1, p2, p3, z, contour_lines):
        #Create contour line segment
        
        #Line and plane intersection
        a = self.getContourPoint(p1, p2, z)
        b = self.getContourPoint(p2, p3, z)
        
        #Create edge, contour
        e = Edge(a, b)
    
        #Add contour to the list
        contour_lines.append(e)


    def getPlaneNormal(self, p1, p2, p3):
        #Compute normal vector (a, b, c) of plane through 3 points
        #Vectors u = p2-p1, v = p3-p1
        ux = p2.x() - p1.x()
        uy = p2.y() - p1.y()
        uz = p2.z() - p1.z()

        vx = p3.x() - p1.x()
        vy = p3.y() - p1.y()
        vz = p3.z() - p1.z()

        #Normal vector n = u x v
        a = uy*vz - uz*vy
        b = uz*vx - ux*vz
        c = ux*vy - uy*vx

        return a, b, c


    def analyzeSlope(self, DT):
        #Analyze slope for each triangle in DT
        #Slope = angle between triangle plane rho and horizontal plane pi
        #Formula from lecture: phi = arccos(c / |n|)
        #where n = (a, b, c) is normal vector of the triangle plane
        triangles = []

        #Process all triangles (each triangle = 3 edges in DT)
        for i in range(0, len(DT), 3):

            #Triangle vertices
            p1 = DT[i].getStart()
            p2 = DT[i+1].getStart()
            p3 = DT[i+1].getEnd()

            #Create triangle object
            t = Triangle(p1, p2, p3)

            #Get plane normal vector (a, b, c)
            a, b, c = self.getPlaneNormal(p1, p2, p3)

            #Norm of normal vector |n1|
            n = sqrt(a**2 + b**2 + c**2)

            #Compute slope angle phi = arccos(c / |n1|)
            #n2 = (0, 0, 1) is normal of horizontal plane, so n1*n2 = c
            if n > 0:
                slope = acos(abs(c) / n)
            else:
                slope = 0

            #Set slope and add triangle
            t.setSlope(slope)
            triangles.append(t)

        return triangles


    def analyzeAspect(self, DT):
        #Analyze aspect (exposition) for each triangle in DT
        #Aspect = azimuth of gradient projection onto xy plane
        #From lecture: v = (a, b, 0), A = arctan(a/b) measured from y-axis
        triangles = []

        #Process all triangles (each triangle = 3 edges in DT)
        for i in range(0, len(DT), 3):

            #Triangle vertices
            p1 = DT[i].getStart()
            p2 = DT[i+1].getStart()
            p3 = DT[i+1].getEnd()

            #Create triangle object
            t = Triangle(p1, p2, p3)

            #Get plane normal vector (a, b, c)
            a, b, c = self.getPlaneNormal(p1, p2, p3)

            #Azimuth A = atan2(a, b) measured from y-axis
            #Use atan2 for correct quadrant detection
            aspect = atan2(a, -b)

            #Normalize to interval [0, 2*pi]
            if aspect < 0:
                aspect += 2 * pi

            #Set aspect and add triangle
            t.setAspect(aspect)
            triangles.append(t)

        return triangles