from __future__ import division,unicode_literals,print_function,absolute_import
from PySide2 import QtGui, QtCore, QtWidgets
import sys
import platform
from PairsGilbertIntercepts import BFlexAngle

import matplotlib.pyplot as plot
import numpy as np
import imageio
import os
import cv2
import math
import itertools
import time
from PIL import Image, ImageQt
import warnings
warnings.filterwarnings("ignore", message="invalid value encountered in arccos")


# Use NSURL as a workaround to pyside/Qt4 behaviour for dragging and dropping on OSx
op_sys = platform.system()


class MainWindowWidget(QtWidgets.QWidget):
    """
    Subclass the widget and add a button to load images.
    Alternatively set up dragging and dropping of image files onto the widget
    """

    def __init__(self):
        super(MainWindowWidget, self).__init__()
        # QtWidgets.QWidget.showFullScreen(MainWindowWidget)
        # Button that allows loading of images
        self.load_button = QtWidgets.QPushButton("Load Bronchoscope image")
        self.load_button.clicked.connect(self.load_image_but)

        # Image viewing region 1
        self.lbl_1 = QtWidgets.QLabel(self)

        # Image viewing region 2
        self.lbl_2 = QtWidgets.QLabel(self)

        # A horizontal layout to include the button on the left
        layout_button = QtWidgets.QHBoxLayout()
        layout_button.addWidget(self.load_button)
        #layout_button.addWidget(self.lbl_2) #Adding some space for lbl_2


        #This is to make the text box
        self.logOutput = QtWidgets.QTextEdit(self)
        self.logOutput.setReadOnly(True)
        self.logOutput.setLineWrapMode(QtWidgets.QTextEdit.WidgetWidth)
        self.logOutput.resize(200,100)

        font = self.logOutput.font()
        font.setFamily("Courier")
        font.setPointSize(15)

        # This adds the textbox to the layout
        layout_button.addWidget(self.logOutput)

        # layout_button.addStretch()

        # A Vertical layout to include the button layout and then the image
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(layout_button)
        #layout.addWidget(self.lbl_1) #Adding some space for lbl_1
        layout_button2 = QtWidgets.QHBoxLayout()
        layout.addLayout(layout_button2)
        layout_button2.addWidget(self.lbl_2)
        layout_button2.addWidget(self.lbl_1)
        self.setLayout(layout)

        # Enable dragging and dropping onto the GUI
        self.setAcceptDrops(True)

        # self.showMaximized()
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
        ## shows input image
        input_img = ImageQt.ImageQt(Image.open(self.fname).rotate(-90))

        pixmap_1 = QtGui.QPixmap(input_img)
        pixmap_1 = pixmap_1.scaled(800, 1000, QtCore.Qt.KeepAspectRatio)
        self.lbl_1.setPixmap(pixmap_1)

        ## Sets the font
        newfont = QtGui.QFont("Times", 15, QtGui.QFont.Bold)
        self.logOutput.setFont(newfont)

        ## Runs the angle calculations, and loads it. Writes the angle to the GUI window.
        png_img= Image.open(self.fname)
        if png_img.size[0] * png_img.size[1] < 20000000:
            self.logOutput.setText("Error: Image quality too low. Camera image quality was not set to large. "
                                   "Review test plan. To test angles with this image quality, contact someone who can edit the program. "
                                   "Otherwise, measure angle on Solidworks.")


        else:
            lines_returned=30 ##Number of lines analyzed from the houghlines function
            keep_going=True ## describes if the program should keep trying to find a valid angle by returning more lines
            while lines_returned<=110 and keep_going==True:
                solve_img = BFlexAngle(png_img,lines_returned)
                image_valid=True
                try:
                    solve_img.DriverFunction()

                except ValueError as err: ##Value errors are if the image cannot find the articulating tip, or b flex in image.
                    print(err.args)
                    image_valid=False
                    keep_going=False
                except SystemError as err:  ## A system error only shows when either not enough pairs could be found, or not enough line families are returned.
                    print(err.args)
                    lines_returned+=20 ## try repeating everything with more lines.
                    print("trying again. ", lines_returned, " lines returned")
                    image_valid=False
                if image_valid==True: ## If no errors were thrown, proceed onwards.
                    keep_going=False

            #Makes the second calculated  image:
            img = ImageQt.ImageQt(Image.fromarray(solve_img.array_img))
            pixmap_2 = QtGui.QPixmap(img)
            pixmap_2 = pixmap_2.scaled(1000, 1500, QtCore.Qt.KeepAspectRatio)
            self.lbl_2.setPixmap(pixmap_2)

            ## Show text describing articulation angle
            if image_valid==True:
                self.logOutput.setText("The articulation angle is:" + str(solve_img.artic_angle) + str(solve_img.message))
            if image_valid==False:
                self.logOutput.setText("Error:"+ str(solve_img.message))


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
