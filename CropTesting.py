import matplotlib.pyplot as plot
import numpy as np
import imageio
import os
import cv2
import math
import itertools
from PIL import Image

## please let this actually go to github
class learnHough:
    def __init__(self, png_img):
        self.png_img= png_img
        array_img1 = np.array(png_img)
        # crop = array_img1[1200:2600, 900:3700]
        # self.array_img = crop
        self.array_img=np.array(png_img)
        # self.array_img=cv2.addWeighted(self.array_img,.4,self.array_img,1,0)
        # self.array_img = cv2.cvtColor(self.array_img, cv2.COLOR_BGR2GRAY)
        # (thresh, self.array_img) = cv2.threshold(self.array_img, 165, 255, cv2.THRESH_BINARY)



    def getVectorForm(self, rho, theta):
        """
        :param rho: Radius from origin- this in defined in HoughLines function
        :param theta: Angle from HoughLines function
        :param tstep: How far lines should travel to get the direction vector
        :return: A new format for a line in an array, containing a start vector (location), and a travel vector(slope)
        in the described order.
        """
        tstep = 2
        xo = rho * np.cos(theta)
        yo = rho * np.sin(theta)
        start_vector = [xo, yo]
        xf = xo + tstep * -np.sin(theta)
        yf = yo + tstep * np.cos(theta)
        travel_vector = [(xf - xo), (yf - yo)]
        return [start_vector, travel_vector]

    def draw_line(self, line, red, green, blue):
        start_vector = line[0]
        travel_vector = line[1]
        pt1 = np.subtract(start_vector, np.multiply(travel_vector, 1500))
        pt2 = np.add(start_vector, np.multiply(travel_vector, 1500))
        cv2.line(self.array_img, (int(pt1[0]), int(pt1[1])), (int(pt2[0]), int(pt2[1])), (red, green, blue), 2)

    def HoughLines(self):
        # gray = cv2.cvtColor(self.array_img, cv2.COLOR_BGR2GRAY)
        gray=self.array_img
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 3)
        image_width = int(self.array_img.shape[1])
        image_height = int(self.array_img.shape[0])
        print(image_height, image_width)
        counter = 0
        while counter < 35:
            for rho, theta in lines[counter]:
                # print("Rho =", rho, "Theta =", theta)
                line = self.getVectorForm(rho, theta)
                # print("Line =", line)
                self.draw_line(line, 225, 225, 0)
            counter += 1

        plot.figure(figsize=(15, 15))
        plot.imshow(self.array_img)
        plot.show()

#C:\Users\eric1\Google Drive\Verathon Medical\Small B-flex

png_image =  Image.open(r"C:\Users\eric1\Google Drive\Verathon Medical\Gilbert's Photos\IMG_0474.jpg").rotate(90)

yeet= learnHough(png_image)
yeet.HoughLines()