__author__ = 'easycui'
#!/usr/bin/env python

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QApplication, QCursor,QPainter,QPen,QBrush,QColor,QImage,qRgb
from PyQt4.QtCore import QPoint
from Marks import *
from util import *
import cv2
class CellSegmentation(QtGui.QMainWindow):
    def __init__(self):
        super(CellSegmentation, self).__init__()

        self.printer = QtGui.QPrinter()
        self.scaleFactor = 0.0
        self.moveFlag=False
        self.sample=0

        """
        posSample is a list of positive marks, negSample is a list of negative marks
        """
        self.Samples=[]
        self.pixmap_item=[]
        self.scene = QtGui.QGraphicsScene()
        self.view = QtGui.QGraphicsView(self.scene)
        self.view.mousePressEvent=self.mousePress
        self.view.mouseMoveEvent = self.mouseMove
        self.view.mouseReleaseEvent = self.mouseRelease
        self.view.mouseDoubleClickEvent = self.doubleClick
        self.setCentralWidget(self.view)
        self.createActions()
        self.createMenus()
        self.createToolbar()
        self.prePos=QPoint()
        self.setWindowTitle("cell segmentation")
        self.resize(800, 600)
        self.status=self.statusBar()
        self.status.showMessage("Please open an image file")
        self.size_label = QtGui.QLabel("Size:100%")
        self.position_label = QtGui.QLabel("X:0,Y:0")
        self.color_label = QtGui.QLabel("R:0,g:0,b:0")
        self.status.addPermanentWidget(self.size_label)
        self.status.addPermanentWidget(self.position_label)
        self.status.addPermanentWidget(self.color_label)

    def resizeEvent(self, QResizeEvent):
        self.fitToWindow(self.current_pixmap)
        print "resize"

    def mouseMove(self, event):
        print 'move'
        if self.moveFlag:
            if event.buttons() == QtCore.Qt.LeftButton:
                pos=event.pos()
                print "Left click drag"
                print self.prePos.x()-pos.x(),self.prePos.y()-pos.y()
                self.horiBarValue= self.view.horizontalScrollBar().value()
                self.vertBarValue= self.view.verticalScrollBar().value()
                shiftX=self.prePos.x()-pos.x()
                shiftY=self.prePos.y()-pos.y()
                self.view.horizontalScrollBar().setValue(self.horiBarValue+shiftX)
                self.view.verticalScrollBar().setValue(self.vertBarValue+shiftY)
                self.prePos=pos

    def mouseRelease(self, QMouseEvent):
        if self.moveFlag:

            if QMouseEvent.button() == QtCore.Qt.LeftButton:
                self.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
                print 'release'

    def mousePress(self, e):

        print 'press'
        offsetX=self.view.horizontalScrollBar().value()
        offsetY=self.view.verticalScrollBar().value()
        currentX=int(e.pos().x()+offsetX)
        currentY=int(e.pos().y()+offsetY)
        self.position_label.setText("X:"+str(currentX)+",Y:"+str(currentY))


        tempColorRgb=self.current_pixmap.toImage().pixel(currentX,currentY)
        tempColor=QColor(tempColorRgb)
        print type(tempColor)
        self.color_label.setText("R:"+str(tempColor.red())+",G:"+str(tempColor.green())+",B:"+str(tempColor.blue()))
        print e.pos().x(), e.pos().y()
        if self.moveFlag:
            if e.button() == QtCore.Qt.LeftButton:
                self.setCursor(QtGui.QCursor(QtCore.Qt.ClosedHandCursor))
                self.prePos=e.pos()

    def doubleClick(self, QMouseEvent):
        if self.sample==1:

            if QMouseEvent.button() == QtCore.Qt.LeftButton:
                print 'positive sample'
                self.addSample(QMouseEvent,True)
        if self.sample==-1:

            if QMouseEvent.button() == QtCore.Qt.LeftButton:
                print 'negative sample'
                self.addSample(QMouseEvent,False)

        if self.sample==2:
            offsetX=self.view.horizontalScrollBar().value()
            offsetY=self.view.verticalScrollBar().value()
            item=self.scene.itemAt(QMouseEvent.pos().x()+offsetX,QMouseEvent.pos().y()+offsetY)
            if item==self.pixmap_item:
                print "background"
            else:
                for i in self.Samples:
                    if i.getItem()==item:
                        self.scene.removeItem(item)
                        self.Samples.remove(i)
            print item

    def addSample(self,e,positive):
        offsetX=self.view.horizontalScrollBar().value()
        offsetY=self.view.verticalScrollBar().value()
        mark=Marks(e.pos(),positive,self.scaleFactor,offsetX,offsetY)
        self.Samples.append(mark)
        self.scene.addItem(mark.getItem())

        mark.getItem().setPos(mark.X()*self.scaleFactor,mark.Y()*self.scaleFactor)
        mark.getItem().setZValue(20)
        print e.pos().x(), e.pos().y()

    def open(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self, "Open File", '',
                                                     'Images (*.png *.xpm *.jpg *.tiff)',None,QtGui.QFileDialog.DontUseNativeDialog)
        if fileName:
            image = QtGui.QImage(fileName)
            if image.isNull():
                QtGui.QMessageBox.information(self, "Image Viewer",
                        "Cannot load %s." % fileName)
                return
            print fileName
            self.pixmap=QtGui.QPixmap(fileName)
            self.current_pixmap=self.pixmap
            if not isinstance(self.pixmap_item,list):
                self.scene.removeItem(self.pixmap_item)
            self.pixmap_item=QtGui.QGraphicsPixmapItem(self.pixmap)
            self.scene.addItem(self.pixmap_item)
            self.fitToWindow(self.pixmap)
            self.pixmap_item.setZValue(10)
            self.scaleFactor = 1.0
            self.size_label.setText("Size:100%")
            self.position_label.setText("X:0,Y:0")
            self.enableActs()
            self.updateActions()
            if not self.fitToWindowAct.isChecked():
                self.view.adjustSize()
            self.status.showMessage("Use the toolbar to mark the cells")

    def enableActs(self):
        self.moveflagAct.setEnabled(True)
        self.posAct.setEnabled(True)
        self.negAct.setEnabled(True)
        self.printAct.setEnabled(True)
        self.fitToWindowAct.setEnabled(True)
        self.delAct.setEnabled(True)
        self.clearAct.setEnabled(True)
        self.undoAct.setEnabled(True)
        self.segmentAct.setEnabled(True)

    def print_(self):
        dialog = QtGui.QPrintDialog(self.printer, self)
        if dialog.exec_():
            painter = QtGui.QPainter(self.printer)
            rect = painter.viewport()
            size = self.imageLabel.pixmap().size()
            size.scale(rect.size(), QtCore.Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(self.imageLabel.pixmap().rect())
            painter.drawPixmap(0, 0, self.imageLabel.pixmap())

    def zoomIn(self):
        self.scaleImage(1.25)
        self.size_label.setText("Size:"+str(self.scaleFactor*100)+"%")


    def zoomOut(self):
        self.scaleImage(0.8)
        self.size_label.setText("Size:"+str(self.scaleFactor*100)+"%")


    def normalSize(self):
        self.imageLabel.adjustSize()
        self.scaleFactor = 1.0

    def setMove(self):
        if not self.moveFlag:
            self.moveFlag=True
            self.sample=0
            self.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
            print self.moveFlag
            self.posAct.setChecked(False)
            self.negAct.setChecked(False)
            self.moveflagAct.setChecked(True)
            self.delAct.setChecked(False)
        else:
            self.moveFlag=False
            self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
            self.moveflagAct.setChecked(False)

    def setPos(self):
        self.sample=1
        self.moveFlag=False
        self.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.posAct.setChecked(True)
        self.negAct.setChecked(False)
        self.moveflagAct.setChecked(False)
        self.delAct.setChecked(False)

    def setNeg(self):
        self.sample=-1
        self.moveFlag=False
        self.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.negAct.setChecked(True)
        self.moveflagAct.setChecked(False)
        self.posAct.setChecked(False)
        self.delAct.setChecked(False)

    def clearMarks(self):
        for i in self.Samples:
            self.scene.removeItem(i.getItem())
        self.Samples=[]
        print 'clearMarks'

    def undo(self):
        end=len(self.Samples)-1
        self.scene.removeItem(self.Samples[end].getItem())
        self.Samples=self.Samples[:-1]
        print 'undo'

    def setDelMarks(self):
        self.sample=2
        self.moveFlag=False
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.negAct.setChecked(False)
        self.moveflagAct.setChecked(False)
        self.posAct.setChecked(False)
        self.delAct.setChecked(True)
        print 'delMarks'

    def fitToWindow(self,pixmap):

        if self.view.size().width()>pixmap.size().width() or self.view.size().height()>pixmap.size().height():
            self.scene.setSceneRect(0,0,self.view.size().width(),self.view.size().height())
        else:
            self.scene.setSceneRect(0,0,pixmap.size().width(),pixmap.size().height())

    def about(self):
        QtGui.QMessageBox.about(self, "About cell segmentation",
                "<p></p>")

    def createActions(self):
        self.openAct = QtGui.QAction("&Open...", self, shortcut="Ctrl+O",
                triggered=self.open)

        self.printAct = QtGui.QAction("&Print...", self, shortcut="Ctrl+P",
                enabled=False, triggered=self.print_)

        self.exitAct = QtGui.QAction("E&xit", self, shortcut="Ctrl+Q",
                triggered=self.close)

        self.zoomInAct = QtGui.QAction(QtGui.QIcon('icos/zoomin.ico'),"Zoom &In (25%)", self,
                                       shortcut="Ctrl++", enabled=False, triggered=self.zoomIn)

        self.zoomOutAct = QtGui.QAction(QtGui.QIcon('icos/zoomout.ico'),"Zoom &Out (25%)", self,
                                        shortcut="Ctrl+-", enabled=False, triggered=self.zoomOut)

        self.normalSizeAct = QtGui.QAction("&Normal Size", self,
                shortcut="Ctrl+S", enabled=False, triggered=self.normalSize)

        self.fitToWindowAct = QtGui.QAction("&Fit to Window", self,
                enabled=False, checkable=True, shortcut="Ctrl+F",
                triggered=self.fitToWindow)

        self.moveflagAct = QtGui.QAction(QtGui.QIcon('icos/hand.ico'),"drag and move the image",
                self, shortcut="Ctrl+M", enabled=False,checkable=True,triggered=self.setMove)

        self.posAct = QtGui.QAction(QtGui.QIcon('icos/green.jpg'),"mark the positive sample",
                self, shortcut="Ctrl+P", enabled=False,checkable=True,triggered=self.setPos)

        self.negAct = QtGui.QAction(QtGui.QIcon('icos/red.ico'),"mark the negative sample",
                self, shortcut="Ctrl+N", enabled=False,checkable=True,triggered=self.setNeg)

        self.delAct = QtGui.QAction(QtGui.QIcon('icos/del.png'),"del one mark",
                self, shortcut="Ctrl+D", enabled=False,checkable=True,triggered=self.setDelMarks)

        self.clearAct = QtGui.QAction(QtGui.QIcon('icos/clear.jpg'),"clear the marks",
                self, shortcut="Ctrl+C", enabled=False,triggered=self.clearMarks)

        self.undoAct =  QtGui.QAction(QtGui.QIcon('icos/undo.jpg'),"undo the mark",
                self, shortcut="Ctrl+U", enabled=False,triggered=self.undo)

        self.aboutAct = QtGui.QAction("&About", self, triggered=self.about)

        self.settingsAct = QtGui.QAction("&setting",
                self, shortcut="Ctrl+S", enabled=True,triggered=self.opensetting)

        self.importMarksAct = QtGui.QAction("import the marks",
                self, shortcut="Ctrl+I", enabled=True,triggered=self.importMarks)

        self.exportMarksAct = QtGui.QAction("export the marks",
                self, shortcut="Ctrl+E", enabled=True,triggered=self.exportMarks)

        self.exportResultAct = QtGui.QAction("export the results",
                self, shortcut="Ctrl+E", enabled=True,triggered=self.exportResult)

        self.saveResultImageAct = QtGui.QAction("save the results",
                self, shortcut="Ctrl+E", enabled=True,triggered=self.saveResult)

        self.aboutQtAct = QtGui.QAction("About &Qt", self,
                triggered=QtGui.qApp.aboutQt)

        self.segmentAct = QtGui.QAction(QtGui.QIcon('icos/check.png'),"click to Segment the cells",
                self, shortcut="Ctrl+D", enabled=False,triggered=self.segmentTheImage)

    def segmentTheImage(self):
        self.status.showMessage("start segmentation")
        self.segmentAct.setEnabled(False)
        img=pixmap2array(self.pixmap)
        self.status.showMessage("processing")

        self.result=seg(img,self.Samples)
        #segOne(img,self.Samples)
        #cv2.namedWindow("result",cv2.WINDOW_OPENGL)
        #cv2.imshow("result",self.result)
        cv2.imwrite("1.jpg",self.result)
        self.status.showMessage("segmenatation done")
        self.segmentAct.setEnabled(True)
        #cv2.waitKey(0)



    def opensetting(self):
        return 0
    def importMarks(self):
        return 0
    def exportMarks(self):
        return 0
    def exportResult(self):
        return 0
    def saveResult(self):

        filename=QtGui.QFileDialog.getSaveFileName(self, "Open File",
                QtCore.QDir.currentPath())
        if filename:
            cv2.imwrite(str(filename),self.result)
        return 0
    def createMenus(self):
        self.fileMenu = QtGui.QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.settingsAct)
        self.fileMenu.addAction(self.importMarksAct)
        self.fileMenu.addAction(self.exportMarksAct)
        self.fileMenu.addAction(self.exportResultAct)
        self.fileMenu.addAction(self.saveResultImageAct)
        self.fileMenu.addAction(self.printAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.viewMenu = QtGui.QMenu("&View", self)
        self.viewMenu.addAction(self.zoomInAct)
        self.viewMenu.addAction(self.zoomOutAct)
        self.viewMenu.addAction(self.normalSizeAct)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.fitToWindowAct)

        self.helpMenu = QtGui.QMenu("&Help", self)
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.viewMenu)
        self.menuBar().addMenu(self.helpMenu)

    def createToolbar(self):

        self.toolbar = self.addToolBar('toolbar')
        self.toolbar.addAction(self.moveflagAct)
        self.toolbar.addAction(self.zoomInAct)
        self.toolbar.addAction(self.zoomOutAct)
        self.toolbar.addAction(self.posAct)
        self.toolbar.addAction(self.negAct)
        self.toolbar.addAction(self.clearAct)
        self.toolbar.addAction(self.delAct)
        self.toolbar.addAction(self.undoAct)
        self.toolbar.addAction(self.segmentAct)

    def updateActions(self):
        self.zoomInAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.zoomOutAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.normalSizeAct.setEnabled(not self.fitToWindowAct.isChecked())

    def scaleImage(self, factor):
        self.scaleFactor *= factor
        self.scene.removeItem(self.pixmap_item)
        self.current_pixmap=self.pixmap.scaled(self.scaleFactor * self.pixmap.size())
        self.pixmap_item=QtGui.QGraphicsPixmapItem(self.current_pixmap)
        self.pixmap_item.setZValue(10)
        self.scene.addItem(self.pixmap_item)
        self.fitToWindow(self.current_pixmap)

        self.adjustScrollBar(self.view.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.view.verticalScrollBar(), factor)
        self.zoomInAct.setEnabled(self.scaleFactor < 4.0)
        self.zoomOutAct.setEnabled(self.scaleFactor > 0.25)
        self.relocateTheSamples()

    def relocateTheSamples(self):
        for i in self.Samples:
            x=i.X()*self.scaleFactor
            y=i.Y()*self.scaleFactor
            i.getItem().setPos(x,y)


    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value()
                                + ((factor - 1) * scrollBar.pageStep()/2)))
if __name__ == '__main__':

    import sys
    app = QtGui.QApplication(sys.argv)
    imageViewer = CellSegmentation()
    imageViewer.show()
    sys.exit(app.exec_())