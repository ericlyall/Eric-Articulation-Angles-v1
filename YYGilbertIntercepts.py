import matplotlib.pyplot as plot
import numpy as np
import imageio
import os
import cv2
import math
import itertools
import time
from PIL import Image

#Hello. I love GitHub!!
class BFlexAngle:

    def __init__(self, png_img):
        png_img1=png_img.rotate(90)
        array_img1 = np.array(png_img1)
        # crop= array_img1
        crop = array_img1[600:2000, 1200:4400]  # On Angle
        #crop = array_img1[0:1500, 1200:4000]  ## smal b-flex 498-500
        #crop = array_img1[800:2300, 1100:3850]  # small b flex 502-...
        # crop = array_img1[200:1200, 500:1900]  # small b flex screen clip
        #crop = array_img1[350:2300, 700:4200]  # verification clip
        #crop = array_img1[800:2700, 700:4400]  ## 4.61 MB images. IMG_0467,0468
        #crop = array_img1[500:1900, 500:3000]  ## 2.45 MB images, IMG_ 0469. 0470
        #crop = array_img1[250:1040, 270:1700]  ## 812 KB images, IMG 0471, 0472
        #crop = array_img1[50:330, 100:530]  ##  104 KB images, IMG_0473, 0474
        #crop = array_img1[300:1000, 300:1680]  #for  1990-1997
        #crop = array_img1[1400:2700, 900:3700]  #goes y values, the x values. This crop is used for most photos. Was 1400:2700, 900:3700
        self.array_img = crop # this will be used in all functions concerning open cv2
        self.png_img=Image.fromarray(self.array_img)# this will be used in all funciions concerning pythons PIL image library
        self.masterlist = []  # This will contain the top HoughLines, in a list format containing two
        # vectors: start vector, and travel vector
        self.grouped_list = []  # This will contain lists (families) of similar lines
        self.width= self.array_img.shape[1]
        self.height=self.array_img.shape[0]


    def getVectorForm(self, rho, theta):
        """
        :param rho: Radius from origin- this in defined in HoughLines function
        :param theta: Angle from HoughLines function
        :param tstep: How far lines should travel to get the direction vector
        :return: A new format for a line in an array, containing a start vector (location), and a travel vector(slope)
        in the described order.
        """
        tstep=2
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
        start_vector1 = line1[2]
        start_vector2 = line2[2]
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
        avg_y_int=line1[2]
        ref_slope = line1[1]
        avg_slope = ref_slope
        index = 1
        while index < len(list):
            avg_start_vector = np.add(avg_start_vector, list[index][0])
            avg_y_int=np.add(avg_y_int,list[index][2])
            check_slope = list[index][1]
            angle = np.arccos(
                np.dot(ref_slope, check_slope) / (np.linalg.norm(ref_slope) * np.linalg.norm(check_slope))) + 0.0
            if angle > np.pi / 2:
                check_slope = np.multiply(-1, check_slope)
            avg_slope = np.add(check_slope, avg_slope)
            index += 1
        avg_start_vector = np.multiply(1 / index, avg_start_vector)
        avg_y_int=np.multiply(1/index,avg_y_int)
        return [avg_start_vector,
                avg_slope,avg_y_int]  # This slope here is just a massive vector with all the travel vectors added up

    def pls_group(self, bin_list):
        if len(bin_list) > 1:
            initial_line = bin_list[0]  # intitial travel vector
            bin_list_copy = []
            bin_list_copy.extend(bin_list)
            binB = []
            counter = 1
            while counter < len(bin_list):
                check_line = bin_list[counter]
                if self.similarOrigin(initial_line, check_line,85) == False or self.similarSlope(initial_line,
                                                                                                  check_line,
                                                                                                  .15) == False:  # IF the lines are not similar.....
                    binB.append(bin_list[counter])
                    bin_list_copy.remove(bin_list[counter])
                counter = counter + 1
            self.grouped_list.append(bin_list_copy)
            self.pls_group(binB)

    def find_y_int(self,line):
        """

        @param line: need a line consisting of start vector, travel vector.
        @return: the point of the y- intercept for the given line in the form: [x,y]. If no y- intercept is found, returns false.
        """
        #TODO Need to test this when there's no intercept.
        line= np.array(line)
        y_int=self.array_img.shape[0]/3
        y_int_line=[[1500,y_int],[1,0]]
        self.draw_line(y_int_line,50,150,200)
        start=-1
        travel=-1
        travel_vect=np.array(line[1])

        ## makes sure the travel vector is pointing downwards.
        if line[0][1]>y_int:
            start=1
        if line[1][1]>0:
            travel=1
        if start*travel>0:### Da fuck happens here. 2nd part of the array just got deleted. whaaaaa
            a=line[1][0]
            b=line[1][1]
            travel_vect=np.array([a*-1,b*-1])
        int_found=False
        point= np.array(line[0])
        walk=np.divide(travel_vect,(np.linalg.norm(travel_vect)))
        while int_found==False:
            point=np.add(point,walk*2)
            if abs(point[1]-y_int)<3:
                int_found=True
            else: ## Checks to make sure the point is not outside the bound of the image.
                if not -1*self.width <= point[0] <= self.width :
                    print("No Y-Intercept found", point[0], self.array_img.shape[1])
                    return False
                if not -1 * self.height <= point[1] <= self.height:
                    print("No Y-Intercept found", point[1], self.array_img.shape[0])
                    return False
        return point

    def edgecase180(self, line1, line2):
        #Want to make both the lines positive- that is, going downwards in the picture.
        if line1[1][1]<0:
            line1[1]=line1[1]*-1
        if line2[1][1]<0:
            line2[1]=line2[1]*-1

        yint1=self.find_y_int(line1)   ## what if it's false...
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

    def search(self,start_index, line,avg_fam_sized):
        while start_index<len(avg_fam_sized):
            if self.similarSlope(line,avg_fam_sized[start_index])==True: ##TODO avg family list needs to be sorted by size first
                return start_index
            else:
                start_index+=1
        return start_index

    def getFinalAngle(self):
        self.grouped_list.sort(key=len, reverse=True)
        average_family_list = []
        counter = 0

        while counter < 7 and counter < len(self.grouped_list):
            average_family_list.append(self.get_bin_angle(self.grouped_list[counter]))
            self.draw_line(average_family_list[counter], 0, 0, 255)
            counter += 1
        avg_fam_sized=average_family_list.copy()
        average_family_list = average_family_list[:4]
        average_family_list.sort(key=lambda x: x[2][0])  # TODO- this isn't good enough- need to also look for pairs.
        # Now, the first two are in one group, the second two in another.
        a=0;b=1;c=2;d=3

        if self.similarSlope(average_family_list[a],average_family_list[b],.15)==False:
            print("Error, articulation angle inaccurate. Measure on Solidworks")
        if self.similarSlope(average_family_list[c],average_family_list[d],.15)==False:
            print("Error, articulation angle inaccurate. Measure on Solidworks")

        left_line = [average_family_list[a], average_family_list[b]]
        right_line = [average_family_list[c], average_family_list[d]]

        self.draw_line(left_line[0], 191, 183, 73);
        self.draw_line(left_line[1], 191, 183, 73)
        self.draw_line(right_line[0], 191, 183, 73);
        self.draw_line(right_line[1], 191, 183, 73)

        actual_left = self.get_bin_angle(left_line)
        actual_right = self.get_bin_angle(right_line)
        self.draw_line(actual_left, 0, 255, 0)
        self.draw_line(actual_right, 255, 0, 0)
        if(actual_left[1][1]*actual_right[1][1]>0):  ##makes sure the 2 vectors are in opposite diretions, so the angle is the large one (170 rather than 10)
            actual_left[1]=actual_left[1]*-1            ## This makes angle calculations only valid if the actual angle is greater than 90
        final_angle = np.arccos(np.dot(actual_left[1], actual_right[1]) / (
                    np.linalg.norm(actual_left[1]) * np.linalg.norm(actual_right[1])))
        final_angle = final_angle * 180 / math.pi  #TODO need to make sure giving the correct angle here.
        if self.edgecase180(actual_left,actual_right)==True:
            final_angle=180+180-final_angle
        return final_angle

    def imageFilter(self):
        """
The purpose of this method is to "filter" the image, making everything that's not the colour of the bronchoscope (mostly white)
black.
        """
        # self.array_img=cv2.addWeighted(self.array_img,50,self.array_img,1,0)
        # self.array_img=cv2.cvtColor(self.array_img, cv2.COLOR_BGR2GRAY)
        #
        # (thresh,self.array_img)=cv2.threshold(self.array_img, 165, 255, cv2.THRESH_BINARY)

        pixelMap = self.png_img.load()
        pixel_values = list(self.png_img.getdata())
        flag = 0
        for i in range(self.png_img.size[0]):  # for every pixel:
            for j in range(self.png_img.size[1]):
                a = pixelMap[i, j]
                # average=(a[0]+a[1]+a[2])/3
                for check in a:  # This acts as a colout similarity test
                    # the first number checks to make sure r,g,b are all close to eachother.
                    # second number ensures rgb vals are high, like the colour white.
                    # if abs(check-average)>50 or check < 150:   # was 50 and 150. 165 now working well
                    if check < 165:
                        flag = 1
                if flag == 1:  # When the flag = 1, that means the pixel is not white/ fails colour similarity. Pixel is replaced with black.
                    pixelMap[i, j] = (0, 0, 0)
                else:
                    pixelMap[i, j] = (a[0], a[1], a[
                        2])  # new pixel is added to image. If failed colour sim, this new added pixel is black. Otherwise, it is unchanged.
                flag = 0
        self.array_img = np.array(self.png_img)


        # pixelMap = self.png_img.load()
        # pixel_values = list(self.png_img.getdata())
        # flag = 0
        # for i in range(self.png_img.size[0]):  # for every pixel:
        #     for j in range(self.png_img.size[1]):
        #         new_list = list(pixelMap[i, j])
        #         average = (new_list[0] + new_list[1] + new_list[2]) / 3.0
        #         index = 0
        #         for check in new_list:  #This acts as a colout similarity test
        #             # the first number checks to make sure r,g,b are all close to eachother.
        #             # second number ensures rgb vals are high, like the colour white.
        #             if abs(check - average) > 50 or check < 165:   # was 50 and 150. 165 now working well
        #                 flag = 1
        #             index = index + 1
        #         if flag == 1:  #When the flag = 1, that means the pixel is not white/ fails colour similarity. Pixel is replaced with black.
        #             new_list.clear()
        #             new_list = [0, 0, 0]
        #         pixelMap[i, j] = (new_list[0], new_list[1], new_list[2])  # new pixel is added to image. If failed colour sim, this new added pixel is black. Otherwise, it is unchanged.
        #         new_list.clear()
        #         flag = 0
        # self.array_img = np.array(self.png_img)
        gray = cv2.cvtColor(self.array_img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3) #was 50, 150
        #edges = cv2.Canny(self.array_img, 50, 150, apertureSize=3) #was 50, 150

        lines = cv2.HoughLines(edges, 1, np.pi / 180, 3)
        image_width = int(self.array_img.shape[1])
        image_height = int(self.array_img.shape[0])
        #print(image_height, image_width)
        counter = 0
        while counter < 35:
            for rho, theta in lines[counter]:
                line = self.getVectorForm(rho, theta)
                intercept= self.find_y_int(line)
                if type(intercept)!=bool:
                    self.masterlist.append([line[0],line[1],intercept]) #could make it so if horizontal line, put start vetor as y int vector
                    self.draw_line(line, 225, 0, 225)
                else:
                    self.masterlist.append([line[0],line[1],line[0]]) # if the lines are pretty horizontal, make the y-int vector same as start vector.
                    self.draw_line(line, 225, 0, 225)
            counter += 1

    def DriverFunction(self):
        self.imageFilter()
        binA = []
        binA.extend(self.masterlist)
        self.pls_group(binA)
        artic_angle = self.getFinalAngle()
        print("--- %s seconds ---" % (time.time() - start_time))
        plot.figure(figsize=(15, 15))
        plot.text(5, 5, artic_angle, bbox=dict(facecolor='red', alpha=0.9))
        plot.imshow(self.array_img)
        plot.show()
        return artic_angle


start_time = time.time()
#super_image = Image.open(r"C:\Users\eric1\Google Drive\Verathon Medical\Gilbert's Photos\IMG_3188.jpg")
super_image = Image.open(r"C:\Users\eric1\Google Drive\Verathon Medical\On Angle\IMG_0318.jpg")
yeet = BFlexAngle(super_image)
yeet.DriverFunction()