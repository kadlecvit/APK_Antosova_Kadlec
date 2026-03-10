from PyQt6 import QtCore, QtGui, QtWidgets
from draw import Draw
from algorithms import Algorithms

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
        icon3.addPixmap(QtGui.QPixmap("icons/clear.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
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
        
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuInput.addAction(self.actionPoint_polygon)
        self.menuInput.addSeparator()
        self.menuInput.addAction(self.actionClear)
        self.menuAnalyze.addAction(self.actionRay_Crossing)
        self.menuAnalyze.addAction(self.actionWinding_Number)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuInput.menuAction())
        self.menubar.addAction(self.menuAnalyze.menuAction())
        self.toolBar.addAction(self.actionOpen)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionRay_Crossing)
        self.toolBar.addAction(self.actionWinding_Number)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionPoint_polygon)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionClear)

        self.retranslateUi(MainForm)
        QtCore.QMetaObject.connectSlotsByName(MainForm)
        
        self.actionPoint_polygon.triggered.connect(self.changeStatusClick)
        self.actionClear.triggered.connect(self.clearClick)
        self.actionOpen.triggered.connect(self.openClick)
        self.actionRay_Crossing.triggered.connect(self.analyzePointAndPositionRCClick)
        self.actionWinding_Number.triggered.connect(self.analyzePointAndPositionWNClick)
        
    def openClick(self):
        self.Canvas.loadShapefile()

    def changeStatusClick(self):
        self.Canvas.changeStatus()
        
    def clearClick(self):
        self.Canvas.clearData()    
        
    def analyzePointAndPositionRCClick(self):
        q = self.Canvas.getQ()
        polygons = self.Canvas.getPol()
        a = Algorithms()

        highlighted_indices = []
        result_text = "Point is outside all polygons"
        
        # NOVÉ: Sledujeme, jestli byl bod alespoň v jednom min-max boxu
        in_any_bbox = False 

        for i, pol in enumerate(polygons):
            # Kontrola min-max boxu
            if a.isPointInMinMaxBox(q, pol):
                in_any_bbox = True
            else:
                continue

            resultRC = a.getPointPolygonPositionRC(q, pol)
            
            if resultRC == "vertex":
                highlighted_indices.append(i)
                result_text = "Point is on a vertex of the polygon(s)"
            elif resultRC == "edge":
                highlighted_indices.append(i)
                result_text = "Point is on an edge of the polygon(s)"
            elif resultRC == 1:
                highlighted_indices.append(i)
                result_text = f"Polygon {i + 1}: Point is inside the polygon"
                break 

        self.Canvas.setHighlighted(highlighted_indices)

        mb = QtWidgets.QMessageBox()
        mb.setWindowTitle('Point and polygon position (Ray Crossing)')
        
        # NOVÉ: Pokud bod nebyl v žádném min-max boxu, ukážeme speciální status
        if not in_any_bbox:
            result_text = "FAST REJECT: Point is completely outside the Min-Max boxes of all polygons."
            mb.setIcon(QtWidgets.QMessageBox.Icon.Information)
            
        mb.setText(result_text)
        mb.exec()


    def analyzePointAndPositionWNClick(self):
        q = self.Canvas.getQ()
        polygons = self.Canvas.getPol()
        a = Algorithms()

        highlighted_indices = []
        result_text = "Point is outside all polygons\nΩ = 0"
        
        # NOVÉ: Sledujeme, jestli byl bod alespoň v jednom min-max boxu
        in_any_bbox = False

        for i, pol in enumerate(polygons):
            # Kontrola min-max boxu
            if a.isPointInMinMaxBox(q, pol):
                in_any_bbox = True
            else:
                continue

            resultWN = a.getPointPolygonPositionWN(q, pol)
            
            if resultWN == "vertex":
                highlighted_indices.append(i)
                result_text = "Point is on a vertex of the polygon(s)\nΩ = vertex"
            elif resultWN == "edge":
                highlighted_indices.append(i)
                result_text = "Point is on an edge of the polygon(s)\nΩ = edge"
            elif resultWN != 0:
                highlighted_indices.append(i)
                result_text = f"Polygon {i + 1}: Point is inside the polygon\nΩ = {resultWN}"
                break

        self.Canvas.setHighlighted(highlighted_indices)

        mb = QtWidgets.QMessageBox()
        mb.setWindowTitle('Point and polygon position (Winding Number)')
        
        # NOVÉ: Speciální status pro min-max box
        if not in_any_bbox:
            result_text = "FAST REJECT: Point is completely outside the Min-Max boxes of all polygons.\nΩ = 0"
            mb.setIcon(QtWidgets.QMessageBox.Icon.Information)

        mb.setText(result_text)
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
        self.actionClear.setText(_translate("MainForm", "Clear"))
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