from __future__ import division,unicode_literals,print_function,absolute_import
from PySide2 import QtGui, QtCore, QtWidgets
import sys
import platform
from YYGilbertIntercepts import BFlexAngle
import matplotlib.pyplot as plot
import numpy as np
import imageio
import os
import cv2
import math
import itertools
import time
from PIL import Image

# Use NSURL as a workaround to pyside/Qt4 behaviour for dragging and dropping on OSx
op_sys = platform.system()
if op_sys == 'Darwin':
    from Foundation import NSURL


class MainWindowWidget(QtWidgets.QWidget):
    """
    Subclass the widget and add a button to load images.

    Alternatively set up dragging and dropping of image files onto the widget
    """

    def __init__(self):
        super(MainWindowWidget, self).__init__()

        # Button that allows loading of images
        self.load_button = QtWidgets.QPushButton("Load image")
        self.load_button.clicked.connect(self.load_image_but)

        # Image viewing region
        self.lbl = QtWidgets.QLabel(self)

        # A horizontal layout to include the button on the left
        layout_button = QtWidgets.QHBoxLayout()
        layout_button.addWidget(self.load_button)

        self.logOutput = QtWidgets.QTextEdit(self)
        self.logOutput.setReadOnly(True)
        self.logOutput.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)

        font = self.logOutput.font()
        font.setFamily("Courier")
        font.setPointSize(10)

        layout_button.addWidget(self.logOutput)

        layout_button.addStretch()

        # A Vertical layout to include the button layout and then the image
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(layout_button)
        layout.addWidget(self.lbl)

        self.setLayout(layout)

        # Enable dragging and dropping onto the GUI
        self.setAcceptDrops(True)

        self.show()

    def load_image_but(self):
        """
        Open a File dialog when the button is pressed
        :return:
        """

        # Get the file location
        self.fname, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file')
        # Load the image from the location
        self.load_image()

    def load_image(self):
        """
        Set the image to the pixmap
        :return:
        """
        pixmap = QtGui.QPixmap(self.fname)
        pixmap = pixmap.scaled(500, 500, QtCore.Qt.KeepAspectRatio)
        self.lbl.setPixmap(pixmap)

        solve_img = BFlexAngle(Image.open(self.fname))
        self.logOutput.setText(str(solve_img.DriverFunction()))
        print(solve_img.DriverFunction())

    # The following three methods set up dragging and dropping for the app
    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls:
            e.accept()
        else:
            e.ignore()

    def dragMoveEvent(self, e):
        if e.mimeData().hasUrls:
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        """
        Drop files directly onto the widget
        File locations are stored in fname
        :param e:
        :return:
        """
        if e.mimeData().hasUrls:
            e.setDropAction(QtCore.Qt.CopyAction)
            e.accept()
            # Workaround for OSx dragging and dropping
            for url in e.mimeData().urls():
                if op_sys == 'Darwin':
                    fname = str(NSURL.URLWithString_(str(url.toString())).filePathURL().path())
                else:
                    fname = str(url.toLocalFile())




        else:
            e.ignore()

# Run if called directly
if __name__== "__main__":
    # Initialise the application
    app = QtWidgets.QApplication(sys.argv)
    # Call the widget
    ex = MainWindowWidget()
    sys.exit(app.exec_())

