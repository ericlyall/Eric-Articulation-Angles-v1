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

class Error(Exception):
    "Base class for other custom exceptions"
    pass
class CannotFindPairs(Error):
    print(" Error: 2 pairs of lines could not be found! Measure on Solidworks. ")
    pass
class CannotFindArticulatingTip(Error):
    print(" Error: Could not find articulating tip. ")
    pass
class CannotFindIncomingShaft(Error):
    print("Error: Cannot find B-Flex in image. Image likely blank. ")
class NotEnoughLineGroups(Error):
    print("Error: Cannot find enough line groups Measure on Solidorks. ")


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
        image_valid=True  ## This just means the image is "showable". This does not mean there is a valid angle
        angle_error= False  ## If true, means algorithm unable to calculate angle.
        ## shows input image
        input_img = ImageQt.ImageQt(Image.open(self.fname).rotate(90))

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
            solve_img = BFlexAngle(png_img)
            try:
                solve_img.DriverFunction()

            # except UnboundLocalError as err:
            #     print("")
            except CannotFindIncomingShaft as err:
                print(err.args)
                image_valid=False
                angle_error=True
            except CannotFindArticulatingTip as err:
                print(err.args)
                image_Valid=False
                angle_error=True
            except CannotFindPairs as err:
                print(err.args)
                image_Valid=True ##This means you can show the image, but no angle will pop up
                angle_error=True
            except NotEnoughLineGroups as err:
                print(err.args)
                image_Valid=True ##This means you can show the image, but no angle will pop up
                angle_error=True

            #Makes the second calculated  image:
            img = ImageQt.ImageQt(Image.fromarray(solve_img.array_img))
            pixmap_2 = QtGui.QPixmap(img)
            pixmap_2 = pixmap_2.scaled(1000, 1500, QtCore.Qt.KeepAspectRatio)
            self.lbl_2.setPixmap(pixmap_2)

            ## Show text describing articulation angle
            if image_valid==True and angle_error==True:
                self.logOutput.setText(str(solve_img.message))
            if image_valid==True:
                self.logOutput.setText("The articulation angle is:" + str(solve_img.artic_angle)+ " degrees. " + str(solve_img.message))
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

