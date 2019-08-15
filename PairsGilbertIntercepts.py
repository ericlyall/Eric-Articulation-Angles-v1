import matplotlib.pyplot as plot
import numpy as np
import imageio
import os
import cv2
import math
import itertools
import time
from PIL import Image
import warnings

warnings.filterwarnings("ignore", message="invalid value encountered in arccos")
# Hello. I love GitHub!!
# class Error(Exception):
#     "Base class for other custom exceptions"
#     pass
# class CannotFindPairs(Error):

class BFlexAngle:

    def __init__(self, png_img):
        self.message= ""
        png_img1 = png_img.rotate(90)
        array_img1 = np.array(png_img1)
        # crop= array_img1
        #crop = array_img1[600:2000, 1200:4400]  # On Angle
        # crop = array_img1[0:1500, 1200:4000]  ## smal b-flex 498-500
        #crop = array_img1[800:2300, 1100:3850]  # small b flex 502-...
        # crop = array_img1[200:1200, 500:1900]  # small b flex screen clip
        #crop = array_img1[350:2300, 700:4200]  # verification clip
        # crop = array_img1[800:2700, 700:4400]  ## 4.61 MB images. IMG_0467,0468
        # crop = array_img1[500:1900, 500:3000]  ## 2.45 MB images, IMG_ 0469. 0470
        # crop = array_img1[250:1040, 270:1700]  ## 812 KB images, IMG 0471, 0472
        # crop = array_img1[50:330, 100:530]  ##  104 KB images, IMG_0473, 0474
        # crop = array_img1[300:1000, 300:1680]
        crop = array_img1[1400:2700, 900:3700]  #goes y values, the x values. This crop is used for most photos. Was 1400:2700, 900:3700# #for  1990-1997  #goes y values, the x values. This crop is used for most photos. Was 1400:2700, 900:3700
        self.array_img = crop  # this will be used in all functions concerning open cv2
        self.png_img = Image.fromarray(
            self.array_img)  # this will be used in all funciions concerning pythons PIL image library
        self.gray=self.array_img
        self.masterlist = []  # This will contain the top HoughLines, in a list format containing two
        # vectors: start vector, and travel vector
        self.grouped_list = []  # This will contain lists (families) of similar lines
        self.width = self.array_img.shape[1]
        self.height = self.array_img.shape[0]
        self.left_line=[]
        self.right_line=[]
        self.imgID=1
        self.artic_angle=""

    def incomingShaftSearch(self, pixelMap, runRight):  ##used to run along horizontally to find 5 consecutive white pixels

        white_count=0  # A counter that keeps a tally of how many white pixels are found in a row. If the streak breaks, goes back to zero
        bounceback=100  #Once the incoming shaft is found, move backwards by this value. Then go upwards to find distal tip in DistalTipSearch
        if runRight==True:
            count=0 # the starting index
            increment=5 # the incrementer for while loop
            bounceback=-1*bounceback
        else:
            count=self.png_img.size[0]-10
            increment=-5
        white_found=False  #means a white pixel is found
        shaft_found=False  #means 5 consecutive white pixels are found
        image_end= self.png_img.size[1]-20  #The y-value to start running across at

        #Runs horizontally along y-location image_end, tyring to find incoming shaft
        while 0<=count<self.png_img.size[0] and shaft_found== False:
            pixel= pixelMap[count,image_end]  #loading pixelmap

            for check in pixel: #checking if pixels are white
                if check > 165:
                    white_found=True
                else:
                    white_found=False
            if white_found==True:
                white_count+=1
            else:
                white_count=0
            if white_count>5:
                shaft_found=True
            count=count+increment  #Loop only reads every 5 pixels
        if shaft_found==False:
            self.message = self.message + " Error: Could not find incoming shaft. Image likely blank"
            raise ValueError("Could not find B-Flex in image! Image likely blank")

        return count+bounceback   # Returns the x-location where one shouldl travel upwards to find distal tip

    def distalTipSearch(self,pixelMap, start_X_index):
        white_count = 0
        Y_index=self.png_img.size[1]-20
        white_found = False
        shaft_found = False
        image_end=0
        while Y_index>0 and shaft_found==False:
            pixel=pixelMap[start_X_index,Y_index]
            for check in pixel:
                if check > 165:
                    white_found=True
                else:
                    white_found=False
            if white_found==True:
                white_count+=1
            else:
                white_count=0
            if white_count>5:
                shaft_found=True
            Y_index=Y_index-5
        return shaft_found

    def getImgId(self,pixelMap):
        start_X_index=self.incomingShaftSearch(pixelMap,True) ##True indicates that we start by runnning to the right - increasing x vals
        if self.distalTipSearch(pixelMap,start_X_index)==True:
            self.imgID=-1  #Articulates to the left
        else:                                                       #Test for right articulation
            start_X_index= self.incomingShaftSearch(pixelMap,False)
            if self.distalTipSearch(pixelMap,start_X_index)==True:
                self.imgID=1 #articulates to the right
            else:
                self.message=self.message +" Could not find articulating tip."
                raise ValueError(" Could not find articulating tip")
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
        avg_y_int = line1[2]
        ref_slope = line1[1]
        avg_slope = ref_slope
        index = 1
        while index < len(list):
            avg_start_vector = np.add(avg_start_vector, list[index][0])
            avg_y_int = np.add(avg_y_int, list[index][2])
            check_slope = list[index][1]
            angle = np.arccos(
                np.dot(ref_slope, check_slope) / (np.linalg.norm(ref_slope) * np.linalg.norm(check_slope))) + 0.0
            if angle > np.pi / 2:
                check_slope = np.multiply(-1, check_slope)
            avg_slope = np.add(check_slope, avg_slope)
            index += 1
        avg_start_vector = np.multiply(1 / index, avg_start_vector)
        avg_y_int = np.multiply(1 / index, avg_y_int)
        return [avg_start_vector,
                avg_slope, avg_y_int]  # This slope here is just a massive vector with all the travel vectors added up

    def pls_group(self, bin_list):
        if len(bin_list) > 1:
            initial_line = bin_list[0]  # intitial travel vector
            bin_list_copy = []
            bin_list_copy.extend(bin_list)
            binB = []
            counter = 1
            while counter < len(bin_list):
                check_line = bin_list[counter]
                if self.similarOrigin(initial_line, check_line, 170) == False or self.similarSlope(initial_line,
                                                                                                  check_line,
                                                                                                  .15) == False:  # IF the lines are not similar.....
                    binB.append(bin_list[counter])
                    bin_list_copy.remove(bin_list[counter])
                counter = counter + 1
            self.grouped_list.append(bin_list_copy)
            self.pls_group(binB)

    def find_y_int(self, line):
        """
        @param line: need a line consisting of start vector, travel vector.
        @return: the point of the y- intercept for the given line in the form: [x,y]. If no y- intercept is found, returns false.
        """
        line = np.array(line)
        y_int = self.array_img.shape[0] / 3
        y_int_line = [[1500, y_int], [1, 0]] ##TODO why 1500 here
        self.draw_line(y_int_line, 50, 150, 200)
        start = -1
        travel = -1
        travel_vect = np.array(line[1])

        ## makes sure the travel vector is pointing downwards.
        if line[0][1] > y_int:
            start = 1
        if line[1][1] > 0:
            travel = 1
        if start * travel > 0:
            a = line[1][0]
            b = line[1][1]
            travel_vect = np.array([a * -1, b * -1])
        int_found = False
        point = np.array(line[0])
        walk = np.divide(travel_vect, (np.linalg.norm(travel_vect)))
        while int_found == False:
            point = np.add(point, walk * 2)
            if abs(point[1] - y_int) < 3:
                int_found = True
            else:  ## Checks to make sure the point is not outside the bound of the image.
                if not -1 * self.width <= point[0] <= self.width:
                    # print("No Y-Intercept found", point[0], self.array_img.shape[1])
                    return False
                if not -1 * self.height <= point[1] <= self.height:
                    # print("No Y-Intercept found", point[1], self.array_img.shape[0])
                    return False
        return point

    def edgecase180(self, line1, line2):
        # Want to make both the lines positive- that is, going downwards in the picture.
        if line1[1][1] < 0:
            line1[1] = line1[1] * -1
        if line2[1][1] < 0:
            line2[1] = line2[1] * -1

        yint1 = self.find_y_int(line1)  ## what if it's false...
        yint2 = self.find_y_int(line2)
        if type(yint1) == bool or type(
                yint2) == bool:  ## if either of them have no intercept, return false- the angle is probably not past 180
            return False
        radius1 = np.linalg.norm(np.subtract(yint1, yint2))
        fyint1 = yint1 + line1[1] / (np.linalg.norm(line1)) * 10
        fyint2 = yint2 + line2[1] / (np.linalg.norm(line2)) * 10
        radius2 = np.linalg.norm(np.subtract(fyint1, fyint2))
        if radius2 < radius1:
            return True  ##Means the articulation angle is past 180
        else:
            return False  ## means articulation angle is not past 180

    def search(self, initial_index, line, avg_fam_sized):
        initial_index
        index=0
        while index < len(avg_fam_sized):
            if self.similarSlope(line, avg_fam_sized[
                index][0],.12) == True and initial_index !=avg_fam_sized[index][1]:  ##TODO avg family list needs to be sorted by size first
                return index
            else:
                index += 1
        return index

##The purpose of pairChecking is to remove outliers
    def pairChecking(self, avg_fam_sized,may_inacc_flag):
        if len(avg_fam_sized)<4:
            self.message= " 2 pairs of lines could not be found! Measure on Solidworks"
            raise ValueError(" 2 pairs of lines could not be found! Measure on Solidworks")
        flag=0
        average_family_list=avg_fam_sized.copy()
        average_family_list=average_family_list[:4]
        average_family_list.sort(key=lambda x: x[0][2][0])
        a = 0; b = 1; c = 2; d = 3
        if self.similarSlope(average_family_list[a][0], average_family_list[b][0], .10) == False:
            flag=1 ## Very important variable. Determines if function should be called again (recursion)
            print("Error, articulation angle may inaccurate. Measure on Solidworks if needed")
            if may_inacc_flag==False:
                self.message = self.message + "Articulation angle may be innaccurate. Look as solved image, measure on solidworks if needed. "
                may_inacc_flag=True
            a_index = self.search(average_family_list[a][1], average_family_list[a][0], avg_fam_sized)
            b_index = self.search(average_family_list[b][1], average_family_list[b][0], avg_fam_sized)
            if a_index<b_index:  #remove b from average fam sized list, it's an outlier
                count=0
                for w in avg_fam_sized:
                    if w[1] == average_family_list[b][1]:
                        del avg_fam_sized[count]
                        break
                    count+=1
            else:
                if b_index<a_index:
                    count = 0
                    for x in avg_fam_sized:
                        if x[1] == average_family_list[a][1]:
                            del avg_fam_sized[count]
                            break
                        count += 1
                if a_index==b_index:
                    count=0
                    for y in avg_fam_sized:
                        if y[1] == average_family_list[a][1]:
                            del avg_fam_sized[count]
                            break
                        count += 1
                    count=0
                    for z in avg_fam_sized:
                        if z[1] == average_family_list[b][1]:
                            del avg_fam_sized[count]
                            break
                        count += 1


        if self.similarSlope(average_family_list[c][0], average_family_list[d][0], .10) == False:
            flag=1
            print("Error, articulation angle inaccurate. Measure on Solidworks")
            if may_inacc_flag==False:
                self.message = "Articulation angle may be innaccurate. Look at solved image, measure on solidworks if needed. "
                may_inacc_flag=True
            c_index = self.search(average_family_list[c][1], average_family_list[d][0], avg_fam_sized)
            d_index = self.search(average_family_list[c][1], average_family_list[d][0], avg_fam_sized)
            if c_index<d_index:  #remove b from average fam sized list, it's an outlier
                count = 0
                for x in avg_fam_sized:
                    if x[1] == average_family_list[d][1]:
                        del avg_fam_sized[count]
                        break
                    count += 1
            else:
                if d_index<c_index:
                    count = 0
                    for x in avg_fam_sized:
                        if x[1] == average_family_list[c][1]:
                            del avg_fam_sized[count]
                            break
                        count += 1
                if c_index==d_index:
                    count=0
                    for y in avg_fam_sized:
                        if y[1] == average_family_list[c][1]:
                            del avg_fam_sized[count]
                            break
                        count += 1
                    count=0
                    for z in avg_fam_sized:
                        if z[1] == average_family_list[d][1]:
                            del avg_fam_sized[count]
                            break
                        count += 1
        if flag==1:
            self.pairChecking(avg_fam_sized, may_inacc_flag)

        flag=0
        self.left_line.append([average_family_list[a][0], average_family_list[b][0]])
        self.right_line.append([average_family_list[c][0], average_family_list[d][0]])

    def getFinalAngle(self):
        self.grouped_list.sort(key=len, reverse=True)  #TODO if the grouped list is too small, increase the # of hough lines returned
        if len(self.grouped_list)<4:
            self.message=self.message+"Not enough line groups found! Measure on Solidworks"
            raise SystemError("Not enough line groups found! Measure on Solidworks")
        avg_fam_sized = []
        counter = 0

        while counter < 7 and counter < len(self.grouped_list):
            avg_fam_sized.append([self.get_bin_angle(self.grouped_list[counter]),counter])
            # self.draw_line(avg_fam_sized[counter][0], 0, 0, 255)
            counter += 1
        self.pairChecking(avg_fam_sized,False)
        left_line=self.left_line[0]
        right_line= self.right_line[0]
        self.draw_line(left_line[0],191,183,73);self.draw_line(left_line[1],191,183,73)
        self.draw_line(right_line[0],191,183,73);self.draw_line(right_line[1],191,183,73)

        actual_left = self.get_bin_angle(left_line)
        actual_right = self.get_bin_angle(right_line)
        self.draw_line(actual_left, 0, 255, 0)
        self.draw_line(actual_right, 255, 0, 0)
        if (actual_left[1][1] * actual_right[1][
            1] > 0):  ##makes sure the 2 vectors are in opposite diretions, so the angle is the large one (170 rather than 10)
            actual_left[1] = actual_left[
                                 1] * -1  ## This makes angle calculations only valid if the actual angle is greater than 90
        final_angle = np.arccos(np.dot(actual_left[1], actual_right[1]) / (
                np.linalg.norm(actual_left[1]) * np.linalg.norm(actual_right[1])))
        final_angle = final_angle * 180 / math.pi  # TODO need to make sure giving the correct angle here.
        if self.edgecase180(actual_left, actual_right) == True:
            final_angle = 180 + 180 - final_angle
        return final_angle

    def imageFilter(self):
        """
The purpose of this method is to "filter" the image, making everything that's not the colour of the bronchoscope (mostly white)
black.
        """
        # self.array_img=cv2.addWeighted(self.array_img,50,self.array_img,1,0)
        # self.array_img=cv2.cvtColor(self.array_img, cv2.COLOR_BGR2GRAY)
        #
        # gray = cv2.cvtColor(self.array_img, cv2.COLOR_BGR2GRAY)
        #(thresh,self.array_img)=cv2.threshold(self.array_img, 165, 255, cv2.THRESH_BINARY)

        self.getImgId(self.png_img.load())
        gray = cv2.cvtColor(self.array_img, cv2.COLOR_BGR2GRAY)
        (thresh,gray)=cv2.threshold(gray, 165, 255, cv2.THRESH_BINARY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)  # was 50, 150

        # pixelMap = self.png_img.load()
        # pixel_values = list(self.png_img.getdata())
        # flag = 0
        # for i in range(self.png_img.size[0]):  # for every pixel:
        #     for j in range(self.png_img.size[1]):
        #         a = pixelMap[i, j]
        #         # average=(a[0]+a[1]+a[2])/3
        #         for check in a:  # This acts as a colout similarity test
        #             # the first number checks to make sure r,g,b are all close to eachother.
        #             # second number ensures rgb vals are high, like the colour white.
        #             # if abs(check-average)>50 or check < 150:   # was 50 and 150. 165 now working well
        #             if check < 165:
        #                 flag = 1
        #         if flag == 1:  # When the flag = 1, that means the pixel is not white/ fails colour similarity. Pixel is replaced with black.
        #             pixelMap[i, j] = (0, 0, 0)
        #         else:
        #             pixelMap[i, j] = (a[0], a[1], a[
        #                 2])  # new pixel is added to image. If failed colour sim, this new added pixel is black. Otherwise, it is unchanged.
        #         flag = 0
        # #self.getImgId(pixelMap)
        # self.array_img = np.array(self.png_img)


        # gray = cv2.cvtColor(self.array_img, cv2.COLOR_BGR2GRAY)
        # # #edges = cv2.Canny(gray, 50, 150, apertureSize=3)  # was 50, 150
        # edges = cv2.Canny(self.array_img, 50, 150, apertureSize=3) #was 50, 150

        lines = cv2.HoughLines(edges, 1, np.pi / 180, 3)
        image_width = int(self.array_img.shape[1])
        image_height = int(self.array_img.shape[0])
        # print(image_height, image_width)
        counter = 0
        while counter < 35:
            for rho, theta in lines[counter]:
                line = self.getVectorForm(rho, theta)
                intercept = self.find_y_int(line)
                if type(intercept) != bool:
                    self.masterlist.append([line[0], line[1],
                                            intercept])  # could make it so if horizontal line, put start vetor as y int vector
                    self.draw_line(line, 225, 0, 225)
                else:
                    self.masterlist.append([line[0], line[1], line[
                        0]])  # if the lines are pretty horizontal, make the y-int vector same as start vector.
                    self.draw_line(line, 225, 0, 225)
            counter += 1

    def DriverFunction(self):
        self.imageFilter()
        binA = []
        binA.extend(self.masterlist)
        self.pls_group(binA)
        self.artic_angle = round(self.getFinalAngle()*self.imgID,1)
        # print("--- %s seconds ---" % (time.time() - start_time))
        # print(self.imgID)
        # plot.figure(figsize=(15, 15))
        # plot.text(5, 5, round(self.artic_angle,1), bbox=dict(facecolor='red', alpha=0.9))
        # plot.imshow(self.array_img)
        # plot.show()
        # print(self.message)
        return self.artic_angle


# start_time = time.time()
# super_image = Image.open(r"C:\Users\eric1\Google Drive\Verathon Medical\Gilbert's Photos\IMG_3278.jpg")
# super_image = Image.open(r"C:\Users\eric1\Google Drive\Verathon Medical\Small B-flex\IMG_0504.jpg")
# yeet = BFlexAngle(super_image)
# try:
#     yeet.DriverFunction()
# except ValueError as err:
#     print(err.args)
# except SystemError as err:
#     print(err.args)