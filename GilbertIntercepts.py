import matplotlib.pyplot as plot
import numpy as np
import imageio
import os
import cv2
import math
import itertools
import time
from PIL import Image


class BFlexAngle:

    def __init__(self, png_img):
        png_img1=png_img.rotate(90)
        array_img1 = np.array(png_img1)
        crop = array_img1[300:1000, 300:1680]
        #crop = array_img1[1400:2700, 900:3700]  #goes y values, the x values
        self.array_img = crop # this will be used in all functions concerning open cv2
        self.png_img=Image.fromarray(self.array_img)# this will be used in all funciions concerning pythons PIL image library
        self.masterlist = []  # This will contain the top HoughLines, in a list format containing two
        # vectors: start vector, and travel vector
        self.grouped_list = []  # This will contain lists (families) of similar lines

    def getVectorForm(self, rho, theta, tstep):
        """
        :param rho: Radius from origin- this in defined in HoughLines function
        :param theta: Angle from HoughLines function
        :param tstep: How far lines should travel to get the direction vector
        :return: A new format for a line in an array, containing a start vector (location), and a travel vector(slope)
        in the described order.
        """
        xo = rho * np.cos(theta)
        yo = rho * np.sin(theta)
        start_vector = [xo, yo]
        xf = xo + tstep * -np.sin(theta)
        yf = yo + tstep * np.cos(theta)
        travel_vector = [(xf - xo), (yf - yo)]
        return [start_vector, travel_vector]

    def similarOrigin(self, line1, line2, rad_thresh):
        """

        :param line1: a line in array format containg a start vector and travel vector, in that order
        :param line2: a line in array format containg a start vector and travel vector, in that order
        :param rad_thresh: the maximum distance the starting points of each line can be from eachother
        :return: if the two lines have similar starting points.
        """
        similar = False
        start_vector1 = line1[0]
        start_vector2 = line2[0]
        radius = np.linalg.norm(np.subtract(start_vector1, start_vector2))
        if radius < rad_thresh:
            similar = True
        return similar

    def similarSlope(self, line1, line2, angle_thresh):
        """

        :param line1: a line in array format containg a start vector and travel vector, in that order
        :param line2: a line in array format containg a start vector and travel vector, in that order
        :param angle_thresh: The minimum angle difference between the two lines
        :return: True if the angle between the two lines is less than the angle threshold. False otherwise.
        """
        travel_vector1 = line1[1]
        travel_vector2 = line2[1]
        similar = False
        angle_diff = np.arccos(
            np.dot(travel_vector1, travel_vector2) / (np.linalg.norm(travel_vector1) * np.linalg.norm(travel_vector2)))
        if angle_diff > np.pi / 2:
            angle_diff = np.pi - angle_diff
        if angle_diff < angle_thresh:
            similar = True
        return similar

    def draw_line(self, line, red, green, blue):
        start_vector = line[0]
        travel_vector = line[1]
        pt1 = np.subtract(start_vector, np.multiply(travel_vector, 1500))
        pt2 = np.add(start_vector, np.multiply(travel_vector, 1500))
        cv2.line(self.array_img, (int(pt1[0]), int(pt1[1])), (int(pt2[0]), int(pt2[1])), (red, green, blue), 2)

    def get_bin_angle(self, list):
        # takes in a list of all the lines defined in start, travel-vector format
        # Averagees uot the entire family, returning a list with just one start/ travel vector that represents
        # the whole family
        line1 = list[0]
        avg_start_vector = line1[0]
        ref_slope = line1[1]
        avg_slope = ref_slope
        index = 1
        while index < len(list):
            avg_start_vector = np.add(avg_start_vector, list[index][0])
            check_slope = list[index][1]
            angle = np.arccos(
                np.dot(ref_slope, check_slope) / (np.linalg.norm(ref_slope) * np.linalg.norm(check_slope))) + 0.0
            if angle > np.pi / 2:
                check_slope = np.multiply(-1, check_slope)
            avg_slope = np.add(check_slope, avg_slope)
            index += 1
        avg_start_vector = np.multiply(1 / index, avg_start_vector)
        return [avg_start_vector,
                avg_slope]  # This slope here is just a massive vector with all the travel vectors added up

    def pls_group(self, bin_list):
        if len(bin_list) > 1:
            initial_line = bin_list[0]  # intitial travel vector
            bin_list_copy = []
            bin_list_copy.extend(bin_list)
            binB = []
            counter = 1
            while counter < len(bin_list):
                check_line = bin_list[counter]
                if self.similarOrigin(initial_line, check_line, 120) == False or self.similarSlope(initial_line,
                                                                                                  check_line,
                                                                                                  .15) == False:  # IF the lines are not similar.....
                    binB.append(bin_list[counter])
                    bin_list_copy.remove(bin_list[counter])
                counter = counter + 1
            self.grouped_list.append(bin_list_copy)
            self.pls_group(binB)

    def find_y_int(self,line):
        #TODO Need to test this when there's no intercept.
        y_int=300
        start=-1
        travel=-1
        if line[0][1]>300:
            start=1
        if line[1][1]>0:
            travel=1
        if start*travel>0:
            line[1]=line[1]*-1
        int_found=False
        point= line[0]
        walk=line[1]/(np.linalg.norm(line[1]))
        while int_found==False:
            point=point+walk*2   ### need to do the normal vector here....
            if abs(point[1]-y_int)<3:
                int_found=True
            if point[0]>self.array_img.shape[1] or point[1]>self.array_img.shape[0]:   ##checking if in width, height values within picture range
                print("Error- no intercept found")
                return False
        return point

    def edgecase180(self, line1, line2):
        if line1[1][1]>0:
            line1[1]=line1[1]*-1
        if line2[1][1]>0:
            line2[1]=line2[1]*-1

        yint1=self.find_y_int(line1)   ## what if it's false...TODO this actuall mutates lines 1 and 2
        yint2=self.find_y_int(line2)
        if type(yint1)==bool or type(yint2)==bool: ## if either of them have no intercept, return false- the angle is probably not past 180
            return False
        radius1 = np.linalg.norm(np.subtract(yint1, yint2))
        fyint1=yint1+line1[1]/(np.linalg.norm(line1))*10
        fyint2=yint2+line2[1]/(np.linalg.norm(line2))*10
        radius2=np.linalg.norm(np.subtract(fyint1,fyint2))
        if radius2<radius1:
            return True ##Means the articulation angle is past 180
        else:
            return False ## means articulation angle is not past 180

    def getFinalAngle(self):
        self.grouped_list.sort(key=len, reverse=True)
        average_family_list = []
        counter = 0

        while counter < 4 and counter < len(self.grouped_list):
            # self.grouped_list[counter].sort(key=lambda y: y[0][1])
            # del self.grouped_list[counter][0]
            # del self.grouped_list[counter][len(self.grouped_list[counter])-1]
            average_family_list.append(self.get_bin_angle(self.grouped_list[counter]))
            self.draw_line(average_family_list[counter], 0, 0, 255)
            counter += 1
        average_family_list.sort(key=lambda x: x[0][0])  # TODO- this isn't good enough- need to also look for pairs.
        # Now, the first two are in one group, the second two in another.
        left_line = [average_family_list[0], average_family_list[1]]
        right_line = [average_family_list[2], average_family_list[3]]
        actual_left = self.get_bin_angle(left_line)
        #print("Left Line:",actual_left)
        actual_right = self.get_bin_angle(right_line)
        #print("Right Line",actual_right)
        self.draw_line(actual_left, 0, 255, 0)
        self.draw_line(actual_right, 255, 0, 0)
        if(actual_left[1][1]*actual_right[1][1]>0):  ##makes sure the 2 vectors are in opposite diretions, so the angle is the large one (170 rather than 10)
            actual_left[1]=actual_left[1]*-1            ## This makes angle calculations only valid if the actual angle is greater than 90
        final_angle = np.arccos(np.dot(actual_left[1], actual_right[1]) / (
                    np.linalg.norm(actual_left[1]) * np.linalg.norm(actual_right[1])))
        final_angle = final_angle * 180 / math.pi  # TODO need to make sure giving the correct angle here.
        if self.edgecase180(actual_left,actual_right)==True:
            final_angle=180+180-final_angle
        return final_angle

    def imageFilter(self):
        pixelMap = self.png_img.load()
        pixel_values = list(self.png_img.getdata())
        flag = 0
        for i in range(self.png_img.size[0]):  # for every pixel:
            for j in range(self.png_img.size[1]):
                new_list = list(pixelMap[i, j])
                average = (new_list[0] + new_list[1] + new_list[2]) / 3.0
                index = 0
                for check in new_list:
                    if abs(check - average) > 50 or check < 150:  ## was 50 and 150
                        flag = 1
                    index = index + 1
                if flag == 1:
                    new_list.clear()
                    new_list = [0, 0, 0]
                pixelMap[i, j] = (new_list[0], new_list[1], new_list[2])
                new_list.clear()
                flag = 0
        self.array_img = np.array(self.png_img)
        gray = cv2.cvtColor(self.array_img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 3)
        image_width = int(self.array_img.shape[1])
        image_height = int(self.array_img.shape[0])
        #print(image_height, image_width)
        counter = 0
        while counter < 50:
            for rho, theta in lines[counter]:
                line = self.getVectorForm(rho, theta, 2)
                self.masterlist.append(line)
                self.draw_line(line, 225, 0, 225)
            counter += 1


    def DriverFunction(self,start_time):
        self.imageFilter()
        binA = []
        binA.extend(self.masterlist)
        self.pls_group(binA)
        artic_angle = self.getFinalAngle()
        print("--- %s seconds ---" % (time.time() - start_time))
        plot.figure(figsize=(15, 15))
        plot.text(5, 5, artic_angle,bbox=dict(facecolor='red', alpha=0.9))
        # plot.text(5, 5, artic_angle, bbox=dict(facecolor='red', alpha=0.9))
        plot.imshow(self.array_img)
        plot.show()
        #return artic_angle


start_time = time.time()
super_image = Image.open(r"C:\Users\eric1\Google Drive\Verathon Medical\Gilbert's Photos\IMG_1994.jpg")
yeet = BFlexAngle(super_image)
yeet.DriverFunction(start_time)
