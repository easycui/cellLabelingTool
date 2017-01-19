__author__ = 'easycui'
from PyQt4 import QtCore,QtGui
class Marks():
    """
    self.position is a
    """
    def __init__(self,position,ispos,scale, offsetX,offsetY):
        """
        the position is the central point of the mark
        """
        self.ispos=ispos
        self.position=self.centerPosition(position,offsetX,offsetY,scale)
        if self.ispos:
            self.pixmap=QtGui.QPixmap("positive.png")
            self.item=QtGui.QGraphicsPixmapItem(self.pixmap)
        else:
            self.pixmap=QtGui.QPixmap("negative.png")
            self.item=QtGui.QGraphicsPixmapItem(self.pixmap)

    def centerPosition(self,position,offsetX,offsetY,scale):
        """
        here the position is the position of left top point on the original image

        """
        x=((position.x()-6+offsetX)/scale)
        y=((position.y()-6+offsetY)/scale)

        pos=QtCore.QPoint()

        pos.setX(x)
        pos.setY(y)

        return pos
    def setPosition(self,x,y):
        self.position.setX(x)
        self.position.setY(y)

    def getPosition(self):
        return self.position
    def getItem(self):
        return self.item
    def centerX(self):
        return self.X()+6
    def centerY(self):
        return self.Y()+6

    def getIspos(self):
        return self.ispos
    def X(self):
        return self.position.x()
    def Y(self):
        return self.position.y()

