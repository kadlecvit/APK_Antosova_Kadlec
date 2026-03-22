from PyQt6 import QtCore, QtGui, QtWidgets
from draw import Draw
from algorithms import *

class Ui_MainForm(object):
    def setupUi(self, MainForm):
        MainForm.setObjectName("MainForm")
        MainForm.resize(1043, 948)
        self.centralwidget = QtWidgets.QWidget(parent=MainForm)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.Canvas = Draw(parent=self.centralwidget)
        self.Canvas.setObjectName("Canvas")
        self.horizontalLayout.addWidget(self.Canvas)
        MainForm.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainForm)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1043, 33))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(parent=self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuInput = QtWidgets.QMenu(parent=self.menubar)
        self.menuInput.setObjectName("menuInput")
        self.menuAnalyze = QtWidgets.QMenu(parent=self.menubar)
        self.menuAnalyze.setObjectName("menuAnalyze")
        MainForm.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainForm)
        self.statusbar.setObjectName("statusbar")
        MainForm.setStatusBar(self.statusbar)
        self.toolBar = QtWidgets.QToolBar(parent=MainForm)
        self.toolBar.setObjectName("toolBar")
        MainForm.addToolBar(QtCore.Qt.ToolBarArea.TopToolBarArea, self.toolBar)
        self.actionOpen = QtGui.QAction(parent=MainForm)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons/open_file.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.actionOpen.setIcon(icon)
        self.actionOpen.setObjectName("actionOpen")
        self.actionExit = QtGui.QAction(parent=MainForm)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("icons/exit.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.actionExit.setIcon(icon1)
        self.actionExit.setObjectName("actionExit")
        self.actionPoint_polygon = QtGui.QAction(parent=MainForm)
        self.actionPoint_polygon.setCheckable(True)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("icons/pointpol.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.actionPoint_polygon.setIcon(icon2)
        self.actionPoint_polygon.setObjectName("actionPoint_polygon")
        self.actionClear = QtGui.QAction(parent=MainForm)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("icons/clear_all.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.actionClear.setIcon(icon3)
        self.actionClear.setObjectName("actionClear")
        self.actionRay_Crossing = QtGui.QAction(parent=MainForm)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("icons/ray.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.actionRay_Crossing.setIcon(icon4)
        self.actionRay_Crossing.setObjectName("actionRay_Crossing")
        self.actionWinding_Number = QtGui.QAction(parent=MainForm)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap("icons/winding.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.actionWinding_Number.setIcon(icon5)
        self.actionWinding_Number.setObjectName("actionWinding_Number")
        self.actionClear_Results = QtGui.QAction(parent=MainForm)
        icon_cr = QtGui.QIcon()
        icon_cr.addPixmap(QtGui.QPixmap("icons/clear.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.actionClear_Results.setIcon(icon_cr)
        self.actionClear_Results.setObjectName("actionClear_Results")
        self.actionClear_Results.setText("Clear results")

        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuInput.addAction(self.actionPoint_polygon)
        self.menuInput.addSeparator()
        self.menuInput.addAction(self.actionClear_Results)
        self.menuInput.addAction(self.actionClear)
        self.menuAnalyze.addAction(self.actionRay_Crossing)
        self.menuAnalyze.addAction(self.actionWinding_Number)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuInput.menuAction())
        self.menubar.addAction(self.menuAnalyze.menuAction())
        self.toolBar.addAction(self.actionOpen)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionExit)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionRay_Crossing)
        self.toolBar.addAction(self.actionWinding_Number)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionPoint_polygon)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionClear_Results)
        self.toolBar.addAction(self.actionClear)

        self.retranslateUi(MainForm)
        QtCore.QMetaObject.connectSlotsByName(MainForm)

        # Connect signals and slots
        self.actionPoint_polygon.triggered.connect(self.changeStatusClick)
        self.actionClear_Results.triggered.connect(self.clearResultsClick)
        self.actionClear.triggered.connect(self.clearClick)
        self.actionRay_Crossing.triggered.connect(self.rayCrossingClick)
        self.actionWinding_Number.triggered.connect(self.windingNumberClick)
        self.actionOpen.triggered.connect(self.openClick)
        self.actionExit.triggered.connect(MainForm.close)

    def openClick(self):
        # Open shapefile
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Open Shapefile", "", "Shapefile (*.shp)")
        if file_name:
            self.Canvas.loadShapefile(file_name)
            # Disable polygon drawing, allow only point placement
            self.actionPoint_polygon.setChecked(True)
            self.actionPoint_polygon.setEnabled(False)

    def changeStatusClick(self):
        # Change source
        self.Canvas.changeStatus()

    def clearResultsClick(self):
        # Clear only the point and highlights
        self.Canvas.clearResults()
        
    def clearClick(self):
        # Clear data
        self.Canvas.clearData()
        # Re-enable polygon drawing
        self.actionPoint_polygon.setEnabled(True)
        self.actionPoint_polygon.setChecked(False)

    def rayCrossingClick(self):
        # Run analysis using Ray Crossing algorithm
        self.analyzePointAndPositionClick("rc")

    def windingNumberClick(self):
        # Run analysis using Winding Number algorithm
        self.analyzePointAndPositionClick("wn")

    def analyzePointAndPositionClick(self, method):
        # Get point
        q = self.Canvas.getQ()

        # Check if point exists
        if q.x() < 0:
            QtWidgets.QMessageBox.warning(None, "Warning", "Place a point first.")
            return

        a = Algorithms()

        # Input data from canvas
        polygons_data = self.Canvas.getPolygonsData()
        highlighted = []

        point_status = 0  # 0 = outside, 1 = inside, -1 = vertex, -2 = edge
        inside_bbox_found = False

        # Process all polygons
        for i in range(len(polygons_data)):
            pol = polygons_data[i][0]
            holes = polygons_data[i][1]

            # Fast polygon search using Min-Max Box
            if a.isPointInMinMaxBox(q, pol):
                inside_bbox_found = True

                # Analyze point and polygon position
                if method == "rc":
                    res = a.getPointPolygonPositionRC(q, pol)
                else:
                    res = a.getPointPolygonPositionWN(q, pol)

                # Check main polygon results and singularities
                if res == -1 or res == -2:
                    highlighted.append(i)
                    point_status = res

                # Note: The nested logic for evaluating point position inside holes and boundary singularities was developed with the help of Claude Sonnet 4.6
                elif res == 1:
                    in_hole = False
                    on_hole_boundary = False

                    for hole in holes:
                        if method == "rc":
                            hole_res = a.getPointPolygonPositionRC(q, hole)
                        else:
                            hole_res = a.getPointPolygonPositionWN(q, hole)

                        if hole_res == -1 or hole_res == -2:
                            on_hole_boundary = True
                            # Hole edge/vertex treated as singularity
                            point_status = hole_res
                        elif hole_res == 1:
                            in_hole = True

                    if on_hole_boundary:
                        highlighted.append(i)
                        break
                    elif not in_hole:
                        # Inside polygon, not in hole
                        highlighted.append(i)
                        point_status = 1
                        # Polygon found, stop searching
                        break

        # Highlight all matching polygons
        self.Canvas.setHighlighted(highlighted)

        # Create message box
        mb = QtWidgets.QMessageBox()
        mb.setWindowTitle('Point and polygon position')

        # Set results based on status
        if not inside_bbox_found:
            mb.setText("Point is outside (rejected by Min-Max Box).")
        elif point_status == 1:
            mb.setText("Point is inside the polygon.")
        elif point_status == -1:
            mb.setText("Point is on the vertex of the polygon.")
        elif point_status == -2:
            mb.setText("Point lies on the edge of the polygon.")
        else:
            mb.setText("Point is outside the polygon.")

        # Show message box
        mb.exec()

    def retranslateUi(self, MainForm):
        _translate = QtCore.QCoreApplication.translate
        MainForm.setWindowTitle(_translate("MainForm", "Analyze point and polygon positiom"))
        self.menuFile.setTitle(_translate("MainForm", "File"))
        self.menuInput.setTitle(_translate("MainForm", "Input"))
        self.menuAnalyze.setTitle(_translate("MainForm", "Analyze"))
        self.toolBar.setWindowTitle(_translate("MainForm", "toolBar"))
        self.actionOpen.setText(_translate("MainForm", "Open"))
        self.actionOpen.setToolTip(_translate("MainForm", "Open file"))
        self.actionExit.setText(_translate("MainForm", "Exit"))
        self.actionExit.setToolTip(_translate("MainForm", "Close application"))
        self.actionPoint_polygon.setText(_translate("MainForm", "Point / polygon"))
        self.actionPoint_polygon.setToolTip(_translate("MainForm", "Switch point / polygon input"))
        self.actionClear.setText(_translate("MainForm", "Clear data"))
        self.actionClear.setToolTip(_translate("MainForm", "Clear data"))
        self.actionRay_Crossing.setText(_translate("MainForm", "Ray Crossing"))
        self.actionRay_Crossing.setToolTip(_translate("MainForm", "Analyze point and polygon position using Ray Crossing algorithm"))
        self.actionWinding_Number.setText(_translate("MainForm", "Winding Number"))
        self.actionWinding_Number.setToolTip(_translate("MainForm", "Analyze point and polygon position using Winding Number algorithm"))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainForm = QtWidgets.QMainWindow()
    ui = Ui_MainForm()
    ui.setupUi(MainForm)
    MainForm.show()
    sys.exit(app.exec())