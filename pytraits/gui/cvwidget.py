import cv2

# from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QBrush, QColor
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QFrame
from PyQt5 import QtCore


class CvWidget(QGraphicsView):
    """Qt Widget for opencv content"""

    # sendImageArea = pyqtSignal(int)  # image size in pixel

    def __init__(self, parent=None):
        super(CvWidget, self).__init__(parent)
        self._zoom = 0
        self._empty = True
        self._scene = QGraphicsScene(self)
        self._qpixmap = QGraphicsPixmapItem()
        self._scene.addItem(self._qpixmap)
        self.setScene(self._scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QBrush(QColor(30, 0, 0)))
        self.setFrameShape(QFrame.NoFrame)
        self._cvImage = None
        self.overlays = {}

    def setImage(self, img, src_is_bgr=True):
        """
        Set maintained image to opencv image img.
        Always makes a deep copy
        """
        height, width, byteValue = img.shape
        byteValue = byteValue * width
        self._zoom = 0
        self._empty = False
        self.setDragMode(QGraphicsView.ScrollHandDrag)

        self._cvImage = img.copy()
        if src_is_bgr:
            self._cvImage = cv2.cvtColor(self._cvImage, cv2.COLOR_BGR2RGB)
        pixmap = QPixmap(
            QImage(self._cvImage, width, height, byteValue, QImage.Format_RGB888)
        )
        self._qpixmap.setPixmap(pixmap)
        self.fitInView()
        # self.sendImageArea.emit( img.shape[0] * img.shape[1])

    def fitInView(self, scale=True):
        rect = QtCore.QRectF(self._qpixmap.pixmap().rect())
        # rect = self._scene.itemsBoundingRect()
        if not rect.isNull():
            self.setSceneRect(rect)
            if not self._empty and self.transform().isInvertible():
                unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(
                    viewrect.width() / scenerect.width(),
                    viewrect.height() / scenerect.height(),
                )
                self.scale(factor, factor)
            self._zoom = 0

    def wheelEvent(self, event):
        if not self._empty:
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0

    def resizeEvent(self, event):
        super(CvWidget, self).resizeEvent(event)
        s = event.size()
        if s.height() > 0 and s.width() > 0:
            self.fitInView()

    def updateOther(self, other_widget):
        '''Provide internal cv image for other CvWidget'''
        if self._cvImage is not None:
            other_widget.setImage(self._cvImage, False)

    def runFunction(self, func):
        return func(self._cvImage)
