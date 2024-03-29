from __future__ import division, unicode_literals, print_function, absolute_import

import platform
import sys
import warnings

import cv2
import math
import numpy as np
from PIL import Image
from PIL import ImageQt
from PySide2 import QtGui, QtCore, QtWidgets

from PairsGilbertIntercepts import BFlexAngle

warnings.filterwarnings("ignore", message="invalid value encountered in arccos")


# Use NSURL as a workaround to pyside/Qt4 behaviour for dragging and dropping on OSx
op_sys = platform.system()


class BFlexAngle:

    def __init__(self, png_img, lines_returned):
        self.message= ""
        png_img1 = png_img.rotate(-90)
        array_img1 = np.array(png_img1)
        crop = array_img1[1200:3100, 1060:4000] ##JIG CROPPER!!!
        # crop= array_img1
        #crop = array_img1[600:2000, 1200:4400]  # On Angle
        # crop = array_img1[0:1500, 1200:4000]  ## smal b-flex 498-500
        #crop = array_img1[800:2300, 1100:3750]  # small b flex 502-...
        # crop = array_img1[200:1200, 500:1900]  # small b flex screen clip
        #crop = array_img1[350:2300, 700:4200]  # verification clip
        # crop = array_img1[800:2700, 700:4400]  ## 4.61 MB images. IMG_0467,0468
        # crop = array_img1[500:1900, 500:3000]  ## 2.45 MB images, IMG_ 0469. 0470
        # crop = array_img1[250:1040, 270:1700]  ## 812 KB images, IMG 0471, 0472
        # crop = array_img1[50:330, 100:530]  ##  104 KB images, IMG_0473, 0474
        # crop = array_img1[300:1000, 300:1680]
        #crop = array_img1[1400:2700, 900:3700]  #goes y values, the x values. Was 1400:2700, 900:3700
        self.array_img = crop  # this will be used in all functions concerning open cv2
        self.png_img = Image.fromarray(
            self.array_img)  # this will be used in all funciions concerning pythons PIL image library
        self.gray=self.array_img
        self.masterlist = []  # This will contain the top HoughLines, in a list format containing two
        # vectors: start vector, and travel vector
        self.grouped_list = []  # This will contain lists (families) of similar lines
        self.width = self.array_img.shape[1]  #The width of the image in pixels
        self.height = self.array_img.shape[0] #The height of the image in pixels
        self.left_line=[]    #A  bin where the two left lines will be placed
        self.right_line=[]   #A bin where the two right lines will be placed.
        self.imgID=""        #A placeholder for the image ID. -1 is bending left, +1 is bending right.
        self.artic_angle=""  # A placeholder where the final articulation angle will be stored
        self.lines_returned=lines_returned   #VERY IMPORTANT- determines how many lines will be used form Hough Lines function. This variable increments if 2 viable pairs cannot be found.
        self.clean_pairs_list=""   #A placeholder for the cleaned list of pairs that has not duplicate line families.

    def incomingShaftSearch(self, pixelMap, runRight):  ##used to run along horizontally to find 5 consecutive white pixels
        """
        This function finds the incoming shaft. The function travels along the bottom of the image searching for
        5 consecutive white pixels, which define the incoming shaft.
        :param pixelMap: A pixel map loaded from the png image.
        :param runRight: If true, the shaft searcher will run from the left side of the image to the right side. If false,
                the shaft searcher will run from the right side of the image to the left.
        :return: If the incoming shaft is found, function returns the location of the incoming shaft as an integer +- the bounceback.
                If the incming shaft is not found, raises an error stating the image is blank.
        """
        white_count=0  # A counter that keeps a tally of how many white pixels are found in a row. If the streak breaks, goes back to zero
        bounceback=250  #Once the incoming shaft is found, move backwards/ by this value. Then go upwards to find distal tip in DistalTipSearch
        if runRight==True:
            count=0 # the starting index
            increment=5 # the incrementer for while loop
            bounceback=-1*bounceback
        else:
            count=self.png_img.size[0]-10  #start 10 pixels from the right edge, just in case there are some weird white reflections i the edge
            increment=-5  #increment is now negative, since we are travelling left (towards zero)
        white_found=False  #If True, means a white pixel is found
        shaft_found=False  #If True, means 5 consecutive white pixels are found
        image_end= self.png_img.size[1]-20  #The y-value to start running across at

        #Runs horizontally along y-location image_end, tyring to find incoming shaft
        while 0<=count<self.png_img.size[0] and shaft_found== False:
            pixel= pixelMap[count,image_end]  #loading pixelmap

            for check in pixel: #checking if pixels are white
                if check > 175: #Loop checks that the R,G and B values are all above 175
                    white_found=True
                else:
                    white_found=False
            if white_found==True:
                white_count+=1   #counts the number of consecutive white pixels.
            else:
                white_count=0  # if there are not consecutive white pixels, the white_count goes down to 0
            if white_count>5:
                shaft_found=True
            count=count+increment  #Loop only reads every 5 pixels to increase speed
        if shaft_found==False:
            self.message = self.message + " Error: Could not find incoming shaft. Image likely blank"
            raise ValueError("Could not find B-Flex in image! Image likely blank")
        if not 0<count+bounceback<self.png_img.size[0]:
            self.message= self.message + "Error- The image has to much glare. Cannot ID the B-flex. Measure on solidworks"
            raise ValueError("Too much glare!")
        return count+bounceback   # Returns the x-location where one should travel upwards to find distal tip

    def distalTipSearch(self,pixelMap, start_X_index):
        """
        Travels upwards from a specified location searching for the distal tip of a B-flex. The distal tip is defined by 5 consecutive white pixels.
        :param pixelMap: A pixel map loaded from the png image
        :param start_X_index: The x-location returned by IncomingShaftSearch. This is the point at which this function can travel upwards and expect to find
                              the distal tip
        :return: If the distal tip is found, return true. Otherwise, return false.
        """
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
        """
        Determines the if the B-flex articulates to the right or left, called the image Id. An articulation to the left
        sets the image ID as negative. An articulation to the right sets the image ID as positive.
        :param pixelMap: The pixel map loaded from a PNG image.
        If no distal tip is found, raises a value error.
        """
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
        :param line1: a line in array format containig a start vector and travel vector, in that order
        :param line2: a line in array format containig a start vector and travel vector, in that order
        :param rad_thresh: the maximum distance the starting points of each line can be from eachother, in pixels.
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
        :param line1: a line in array format containig a start vector and travel vector, in that order
        :param line2: a line in array format containig a start vector and travel vector, in that order
        :param angle_thresh: The minimum accepted angle difference between the two lines, in radians
        :return: True if the angle between the two lines is less than the angle threshold. False otherwise.
        """
        travel_vector1 = line1[1]
        travel_vector2 = line2[1]
        similar = False

        angle_diff = np.arccos(
            np.dot(travel_vector1, travel_vector2) / (np.linalg.norm(travel_vector1) * np.linalg.norm(travel_vector2)))
        ##TODO if the travel vectors are exactly the same, it's gonna return Nan- should return true.
        if np.isnan(angle_diff)==True:
            similar=True
        if angle_diff > np.pi / 2:
            angle_diff = np.pi - angle_diff
        if angle_diff < angle_thresh:
            similar = True
        return similar

    def draw_line(self, line, red, green, blue):
        """
        :param line: a line in an array containing a start vector and a travel vector, in that order
        :param red: Red colour value of pixel. Must be <255
        :param green: Green colour value of pixel. Must be <255
        :param blue: Blue colour value of pixel. Must be <255
        """
        start_vector = line[0]
        travel_vector = line[1]

        ## creates two points that the line will be drawn between.
        pt1 = np.subtract(start_vector, np.multiply(travel_vector, 1500))
        pt2 = np.add(start_vector, np.multiply(travel_vector, 1500))

        ##actually draws the line on image.
        cv2.line(self.array_img, (int(pt1[0]), int(pt1[1])), (int(pt2[0]), int(pt2[1])), (red, green, blue), 2)

    def get_bin_angle(self, list):
        """
        Represents an entire group of lines with a simgle line, called a line family.
        :param list: a group of lines
        :return: A single "line family". This is the average of the start vectors, slopes, and intercepts of each line.
        """

        ##Sets the initial values
        line1 = list[0]
        avg_start_vector = line1[0]
        avg_y_int = line1[2]
        ref_slope = line1[1]
        avg_slope = ref_slope
        index = 1
        while index < len(list):
            avg_start_vector = np.add(avg_start_vector, list[index][0])  ##making a  massive sum of start vectors
            avg_y_int = np.add(avg_y_int, list[index][2])                ## making a massive sum of y-intercept vectors.
            check_slope = list[index][1]
            angle = np.arccos(
                np.dot(ref_slope, check_slope) / (np.linalg.norm(ref_slope) * np.linalg.norm(check_slope))) + 0.0
            ##if the dot procuct gives an angle bigger that 90, this means the slope vector is facing the wrong way .
            if angle > np.pi / 2:
                check_slope = np.multiply(-1, check_slope)   #swaps the direction of the slope vector
            avg_slope = np.add(check_slope, avg_slope)       #Adds all the slope vectors up from every line in the group
            index += 1
        avg_start_vector = np.multiply(1 / index, avg_start_vector)  ## averages all the start vectors from the group
        avg_y_int = np.multiply(1 / index, avg_y_int)                ## averages all the intercept vectors from the group

        return [avg_start_vector, avg_slope, avg_y_int]

    def pls_group(self, bin_list):
        """
        Groups similar lines based on their slopes and location. Add each groupe to the self.grouped list.
        :param bin_list: A list of lines in the vector form- [[startx, starty],[slopex, slopey],[interceptX, interceotY]]
        """
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

    def find_y_int(self, line):
        """
        Find the point where the line intersects the y_intercept line. Help define the location of a line, since the start vector is inadequate.
        :param line: A line in vector form [[startX, startY],[slopeX, slopeY]]
        :return: Th point where the line intercects a horizontal line at 1/3 of image height. If the intersect does not take place on the image, return False.
        """
        line = np.array(line)
        y_int = self.array_img.shape[0] / 3
        y_int_line = [[self.width*.5, y_int], [1, 0]] #Draws the y- intecept lione.
        # self.draw_line(y_int_line, 50, 150, 200)
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

            ## Checks to make sure the point is not outside the bound of the image
            ##Since the start vector can have negative values, the bounds of the image extend equal and opposite in the negative direction,
            else:
                if not -1 * self.width <= point[0] <= self.width:
                    # print("No Y-Intercept found", point[0], self.array_img.shape[1])
                    return False
                if not -1 * self.height <= point[1] <= self.height:
                    # print("No Y-Intercept found", point[1], self.array_img.shape[0])
                    return False
        return point


    def findHorizontalIntercept(self, line):
        """

        :param line:  A line in vector form [[startX, startY],[slopeX, slopeY]]
        :return: The point at which the line intersects the right of left side of the image, based on the Image ID. If no horizontal intersect is found, returns the start vector.
        """
        start_vector_x= line[0][0]
        slope_x=line[1][0]
        slope_y=line[1][1]
        side=""
        copy_slope = np.array([slope_x, slope_y])
        if self.imgID==-1: ## dealing with cases where it articulates left. Makes is so that the slope vector will allow the line to intersect the LHS, if one starts at the start_vector.
            side=0
            if start_vector_x*slope_x>0:
                copy_slope= np.array([slope_x *-1, slope_y *-1])

        if self.imgID==1: #dealing with cases where it articulates right. Changes slope so travelling along line from start vecitr hits RHS
            side= self.array_img.shape[1] ## this is the rightmost side of the image
            if slope_x<0:
                copy_slope= np.array([slope_x *-1, slope_y *-1])

        point = np.array(line[0]).copy() ## should copy the start vector, so no issues about mutability.
        walk = np.divide(copy_slope, (np.linalg.norm(copy_slope)))  ## turns the slope vector into a unit vector
        hor_int_found =False
        counter=0
        while hor_int_found==False:
            point = np.add(point, walk * 2)
            if abs(point[0]-side)<3:
                hor_int_found=True
                return point   ## if the horizontal intercept is found (which it always should be...), return it

            if abs(counter)>self.array_img.shape[1]*3: ##If found some reason the horizontal intercept is not found (it should always be found), bounce out of loop and return start vector.
                hor_int_found=True
                print("horizontal intercept not found", line)
                self.draw_line(line,225,192,203)
            counter+=2
        return line[0]        # otherwise, return the start vector.

    def edgecase180(self, line1, line2):
        """

        :param line1:  A line in vector form [[startX, startY],[slopeX, slopeY]]
        :param line2:  A line in vector form [[startX, startY],[slopeX, slopeY]]
        :return: True if the angle should be greater than 180. This happens when both lines are pointing downwards, and get
                closer together.
        """
        # Adjusts slopes. Want to make both the lines positive- that is, going downwards in the picture.
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
        fyint1 = yint1 + line1[1] / (np.linalg.norm(line1[1])) * 10
        fyint2 = yint2 + line2[1] / (np.linalg.norm(line2[1])) * 10
        radius2 = np.linalg.norm(np.subtract(fyint1, fyint2))
        if radius2 < radius1:
            return True  ##Means the articulation angle is past 180
        else:
            return False  ## means articulation angle is not past 180

    def searchByNormalVector(self, ref_line, candidate_line):
        """
        Check how far apart, in the normal direction that 2 parallel lines are.

        :param ref_line: A line in form [[[startX, startY],[slopeX, slopeY];[interceptX, interceptY]],[family weight]]
        :param candidate_line: A line in form [[[startX, startY],[slopeX, slopeY];[interceptX, interceptY]],[family weight]]
        :return: True if the lines are roughly a B-flex width apart (between 120 and 310 pixels) False otherwise.
        """
        cand_pt=np.array(candidate_line[0][2])
        cand_slope=np.array(candidate_line[0][1])
        cand_slope = np.divide(cand_slope, (np.linalg.norm(cand_slope)))
        edge_found=False

        #Want to find a good spot to start walking from each time on candidate line, while looking for intercept.
        while edge_found==False:
            cand_pt=np.add(cand_pt,cand_slope*4)
            if self.edge_checker(cand_pt,10)==True:
                edge_found=True
                cand_slope=np.divide(cand_slope,-1)
        cand_start_pt=np.add(cand_pt, cand_slope*5)
        ref_start_pt= np.array(ref_line[0][2])
        ref_slope=ref_line[0][1]

        if self.searchIntersect(ref_start_pt,cand_start_pt,cand_slope,ref_slope)==False:  #This is the function call that actually checks the parallel distances.
            return False
        else:
            return True

    def searchIntersect(self, ref_pt,cand_pt, cand_slope, ref_slope):
        """

        :param ref_pt: a point in [x,y] format
        :param cand_pt: a point in the [x,y] format. This point will constanly be incremented and compared against ref point.
        :param cand_slope: slope of the candidate line in [x,y] format.
        :param ref_slope: slope of the reference line in [x,y] format.
        :return: True if the two line families have a parallel gap siimilar to the width of a b-flex. False otherwise.
        """
        baby = 0 ## makes sure the edgechecker returns false if the line is right at the edge.

        # checks to make sure the point on the candidate line isn't off the image.
        while self.edge_checker(cand_pt,baby) == False:
            cand_pt = np.add(cand_pt, cand_slope * 10)
            rad_vector=np.subtract(ref_pt, cand_pt)  # a direction vector from the reference pt to candidate pt
            radius = np.linalg.norm(rad_vector)
            angle = np.arccos(np.dot(ref_slope, rad_vector) / (np.linalg.norm(ref_slope) * np.linalg.norm(rad_vector)))
            if abs(np.pi/2-angle)<.52:  #The angle between rad_vector and ref_slop should be close to perpendicular if we want to find the true parallel gap distance.
                if 120<abs(radius) < 310: #120 is the minimum width, in pixels of a B-flex small. 310 is the maximum width in pixels of the B-Flex large.
                    return True  ##The two line families have a parallel gap siimilar to the width of a b-flex. They deserve to be pairs.
            baby += 1
        return False


    ##Checks to see if a point is close to any of the edges, used in searchByNormalVector method
    def edge_checker(self,point,baby):
        """

        :param point: a point in [x,y] form
        :param baby: A super old variable, can probably delete it TODO delete baby?
        :return:
        """
        if baby<3:
            return False
        if point[0]<0:
            return True
        if point[0]>self.array_img.shape[1]:
            return True
        if point[1]<0:
            return True
        if point[1]>self.array_img.shape[0]:
            return True
        return False

    def removeSimPairs(self,all_pairs_list):
        """
        A recursive algorithm that removes all the similar pairs from all_pairs_list. Similar pairs are two pairs that share a line family.
        The similar pair with a lower weight (amount of lines that went into creating the pair) is removed.
        :param all_pairs_list: a list full of pairs. Pairs are in the format: [line1, line2, pairWeight]
        [[[[startX, startY],[slopeX, slopeY],[interceptX, interceptY]],family weight], [[[startX, startY],[slopeX, slopeY],[interceptX, interceptY]],family weight]], pair_weight]
        """
        sim_pair_flag=False
        if len(all_pairs_list)<2:
            raise SystemError("Cannot find 2 pairs of lines!")

        pair1= all_pairs_list[0]
        pair2= all_pairs_list[1]
        a= pair1[0][0][0][0]
        b= pair1[1][0][0][0]
        c= pair2[0][0][0][0]
        d= pair2[1][0][0][0]
        if a==c or c==d:
            sim_pair_flag=True
        if b==c or b==d:
            sim_pair_flag= True
        if sim_pair_flag==True:
            if pair1[2]>=pair2[2]: ## remove pair 2 from all pairs list.
                i=0
                for pair in all_pairs_list:
                    if pair[0][0][0][0]==c and pair[1][0][0][0]==d:
                        del all_pairs_list[i]
                    i=i+1
            else: ## remove pair 1 from all pairs list.
                j = 0
                for pair in all_pairs_list:
                    if pair[0][0][0][0] == a and pair[1][0][0][0] == b:
                        del all_pairs_list[j]
                    j = j + 1
            self.removeSimPairs(all_pairs_list)
        else:
            self.clean_pairs_list= all_pairs_list



    def pairChecking(self, avg_fam_sized):
        """
        The purpose of pairChecking is to search for the 2 biggest pairs of line families. Once the 2 largest pairs are found,
        all 4 lines are sorted left to right by the x value in their intercept vector.

        :param avg_fam_sized: A list containing line families.
        :return Stores left two lines in self.left_line. Stores right two lines in self.right_line
        """
        i=0
        all_pairs_list=[]  ## this will hold all of the pairs
        #Looks for pairs
        ## two loops here to compare every element against on another in the list.
        while i<len(avg_fam_sized)-1:
            j=i+1
            ref_line=avg_fam_sized[i]
            while j<len(avg_fam_sized):
                check_line=avg_fam_sized[j]
                if self.similarSlope(ref_line[0],check_line[0],.10)==True:
                    if self.searchByNormalVector(ref_line,check_line)==True:  #Checks to see if the line groups are pairs
                        pair_size= ref_line[1]+check_line[1]  #says how many individual lines are involved in the specific pair.
                        pair=[ref_line,check_line,pair_size]
                        all_pairs_list.append(pair)  #if so, add them to the all pairs list.
                j+=1
            i+=1
        all_pairs_list.sort(reverse=True, key=lambda x: x[2])  #Finds the largest pairs, sorts them to the top of the list based on pair size
        if len(all_pairs_list)<2:
            self.message = "Cannot find 2 pairs of lines. Measure on SolidWorks"
            raise SystemError("Cannot find 2 pairs of lines!")
        self.removeSimPairs(all_pairs_list.copy()) ## makes sure there are no duplicates pairs ( 1 line family existing in 2 pairs.

        self.clean_pairs_list= self.clean_pairs_list[:2] #Takes the top 2 pairs from clean pairs list

        #Breaks apart the top 2 pairs. Sorts each family from left to right
        top_lines_list=[self.clean_pairs_list[0][0],self.clean_pairs_list[0][1], self.clean_pairs_list[1][0],self.clean_pairs_list[1][1]]
        top_lines_list.sort(key=lambda x: x[0][2][0])
        self.left_line.append([top_lines_list[0][0], top_lines_list[1][0]])
        self.right_line.append([top_lines_list[2][0], top_lines_list[3][0]])

    def getFinalAngle(self):
        """
        Takes a grouped list of lines, finds the 2 biggest pairs, and calculates the angle between the.
        :return: Stores the articulation angle in the class-wide variable self.artic_Angle.
        """
        self.grouped_list.sort(key=len, reverse=True)
        if len(self.grouped_list)<4:  ##This means there are not enough lines to make 2 pairs.
            self.message=self.message+" Not enough line groups found! Measure on Solidworks"
            raise SystemError(" Not enough line groups found! Measure on Solidworks")
        avg_fam_sized = []
        counter = 0

        while counter < 10 and counter < len(self.grouped_list):  #If the line group is less than the 10th largest, we don't want it. The two biggest pairs should not exist
                                                                    # outside of the top 10 groups. AFter the top ten, things get innaccurate.
            avg_fam_sized.append([self.get_bin_angle(self.grouped_list[counter]),len(self.grouped_list[counter])])   #place the line, and the group size (line weight) into array
            # self.draw_line(avg_fam_sized[counter][0], 0, 0, 255)  ##Used for debugging. Draws each line family in blue.
            counter += 1

        #Creates a list of the largest 4 line groups.
        average_family_list = avg_fam_sized.copy()
        average_family_list = average_family_list[:4]
        average_family_list.sort(key=lambda x: x[0][2][0])  #Sorts these lines from left to right based off the x value of their intercept vector.


        #Out of the top 4 lines, if the two leftmost and two rightmost lines are not similar
        # angles, the program prints a message letting the user know the angle may be inacccurate. The pairing algorithm has to be used.
        if self.similarSlope(average_family_list[0][0], average_family_list[1][0], .10) == False or self.similarSlope(average_family_list[2][0], average_family_list[3][0], .10) == False:
            self.message = self.message + " Angle may be innacurate. Look at the red and green lines on the image. If they do not match up with B-Flex, measure on Solidworks"
        #     self.pairChecking(avg_fam_sized)
        # else:
        #     self.left_line.append([average_family_list[0][0],average_family_list[1][0]])
        #     self.right_line.append([average_family_list[2][0],average_family_list[3][0]])
        #
        # self.left_line.append([average_family_list[0][0], average_family_list[1][0]])
        # self.right_line.append([average_family_list[2][0],average_family_list[3][0]])

        self.pairChecking(avg_fam_sized)  #Searches for the top 2 pairs

        left_line=self.left_line[0]
        right_line= self.right_line[0]
        #Draws the line families from the top 2 groups (used to calculate final angle) in yellow.
        self.draw_line(left_line[0],191,183,73);self.draw_line(left_line[1],191,183,73)
        self.draw_line(right_line[0],191,183,73);self.draw_line(right_line[1],191,183,73)

        actual_left = self.get_bin_angle(left_line) #combines the left 2 line families
        actual_right = self.get_bin_angle(right_line)  #combines the right 2 line families.
        self.draw_line(actual_left, 0, 255, 0)  #Draws left line in green
        self.draw_line(actual_right, 255, 0, 0)  #Draws right line in red.
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
        print(self.imgID)
        gray = cv2.cvtColor(self.array_img, cv2.COLOR_BGR2GRAY)  ## the binary threshold works better if the image goes grayscale first.
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
        #             if check < 155:
        #                 flag = 1
        #         if flag == 1:  # When the flag = 1, that means the pixel is not white/ fails colour similarity. Pixel is replaced with black.
        #             pixelMap[i, j] = (0, 0, 0)
        #         else:
        #             pixelMap[i, j] = (a[0], a[1], a[
        #                 2])  # new pixel is added to image. If failed colour sim, this new added pixel is black. Otherwise, it is unchanged.
        #         flag = 0
        # #self.getImgId(pixelMap)
        # self.array_img = np.array(self.png_img)
        #
        #
        # gray = cv2.cvtColor(self.array_img, cv2.COLOR_BGR2GRAY)
        # edges = cv2.Canny(gray, 50, 150, apertureSize=3)  # was 50, 150
        # # #edges = cv2.Canny(self.array_img, 50, 150, apertureSize=3) #was 50, 150

        lines = cv2.HoughLines(edges, 1, np.pi / 180, 3)  #returned the Hough lines in rho, theta form from the canny edge detection.

##Turning lines into bector form.
        counter = 0
        while counter < self.lines_returned:
            for rho, theta in lines[counter]:
                line = self.getVectorForm(rho, theta)
                intercept = self.find_y_int(line)
                if type(intercept) != bool and 0<intercept[0]<self.width:  ## if we were able to find a y=intercept on the image.
                    self.masterlist.append([line[0], line[1],
                                            intercept])
                    # self.draw_line(line, 225, 0, 225)
                else: ## this means the lines are pretty horizontal, so need to use new method of getting start vector.
                    intercept=self.findHorizontalIntercept(line)
                    self.masterlist.append([line[0], line[1], intercept])
                    # self.draw_line(line, 225, 0, 225)
            counter += 1

    def DriverFunction(self):
        """
        Acts as a wrapper function. Only this function needs to be called to get the articulation angle.
        :return: the final articulation angle.
        """
        self.imageFilter()
        binA = []
        binA.extend(self.masterlist)
        self.pls_group(binA)
        self.artic_angle = round(self.getFinalAngle()*self.imgID,1)
        # # # print("--- %s seconds ---" % (time.time() - start_time))
        # print(self.imgID)
        # plot.figure(figsize=(15, 15))
        # plot.text(5, 5, round(self.artic_angle, 1), bbox=dict(facecolor='red', alpha=0.9))
        # plot.imshow(self.array_img)
        # plot.show()
        # print(self.message)

        return self.artic_angle


# start_time = time.time()
# super_image = Image.open(r"C:\Users\eric1\Google Drive\Verathon Medical\Jig Verification 2\IMG_0657.jpg")
# # super_image = Image.open(r"C:\Users\ELyall\Pictures\Jig Pictures 2\IMG_0657.jpg")
# lines_returned=35
# yeet = BFlexAngle(super_image, lines_returned)
# try:
#     yeet.DriverFunction()
# except ValueError as err:
#     print(err.args)
# except SystemError as err:
#     print(err.args)



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