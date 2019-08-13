from unittest import TestCase
import time
from PIL import Image
from PairsGilbertIntercepts import BFlexAngle

class TestBFlexAngle(TestCase):
    def setUp(self):
        self.tol = 3  # the angle tolerance is +- 3 degrees.

        self.test_3198 = BFlexAngle(
            Image.open(r"C:\Users\eric1\Google Drive\Verathon Medical\Gilbert's Photos\IMG_3198.jpg"))
        self.test_3208 = BFlexAngle(
            Image.open(r"C:\Users\eric1\Google Drive\Verathon Medical\Gilbert's Photos\IMG_3208.jpg"))
        self.test_3218 = BFlexAngle(
            Image.open(r"C:\Users\eric1\Google Drive\Verathon Medical\Gilbert's Photos\IMG_3218.jpg"))
        self.test_3450 = BFlexAngle(
            Image.open(r"C:\Users\eric1\Google Drive\Verathon Medical\Gilbert's Photos\IMG_3450.jpg"))
        self.test_3395 = BFlexAngle(
            Image.open(r"C:\Users\eric1\Google Drive\Verathon Medical\Gilbert's Photos\IMG_3395.jpg"))
        self.test_3435 = BFlexAngle(
            Image.open(r"C:\Users\eric1\Google Drive\Verathon Medical\Gilbert's Photos\IMG_3435.jpg"))
        self.test_3242 = BFlexAngle(
            Image.open(r"C:\Users\eric1\Google Drive\Verathon Medical\Gilbert's Photos\IMG_3242.jpg"))
        self.test_3254 = BFlexAngle(
            Image.open(r"C:\Users\eric1\Google Drive\Verathon Medical\Gilbert's Photos\IMG_3254.jpg"))
        self.test_3403 = BFlexAngle(
            Image.open(r"C:\Users\eric1\Google Drive\Verathon Medical\Gilbert's Photos\IMG_3403.jpg"))
        self.test_3400 = BFlexAngle(
            Image.open(r"C:\Users\eric1\Google Drive\Verathon Medical\Gilbert's Photos\IMG_3400.jpg"))
        self.test_3383 = BFlexAngle(
            Image.open(r"C:\Users\eric1\Google Drive\Verathon Medical\Gilbert's Photos\IMG_3383.jpg"))
        self.test_3237 = BFlexAngle(
            Image.open(r"C:\Users\eric1\Google Drive\Verathon Medical\Gilbert's Photos\IMG_3237.jpg"))
        self.test_3315 = BFlexAngle(
            Image.open(r"C:\Users\eric1\Google Drive\Verathon Medical\Gilbert's Photos\IMG_3315.jpg"))
        self.test_3194 = BFlexAngle(
            Image.open(r"C:\Users\eric1\Google Drive\Verathon Medical\Gilbert's Photos\IMG_3194.jpg"))

        ## Bugged tests
        # self.test_3383 = BFlexAngle(Image.open(r"C:\Users\eric1\Google Drive\Verathon Medical\Gilbert's Photos\IMG_3383.jpg"))
        # self.test_3353 = BFlexAngle(Image.open(r"C:\Users\eric1\Google Drive\Verathon Medical\Gilbert's Photos\IMG_3353.jpg"))
        # self.test_3263 = BFlexAngle(Image.open(r"C:\Users\eric1\Google Drive\Verathon Medical\Gilbert's Photos\IMG_3263.jpg"))
        # self.test_3257 = BFlexAngle(Image.open(r"C:\Users\eric1\Google Drive\Verathon Medical\Gilbert's Photos\IMG_3257.jpg"))
        # self.test_3176 = BFlexAngle(Image.open(r"C:\Users\eric1\Google Drive\Verathon Medical\Gilbert's Photos\IMG_3176.jpg"))

    def test_DriverFunction1(self):
        angle = self.test_3198.DriverFunction()
        stl = 172.89
        print("Calculated", angle, "Expected", stl)
        self.assertTrue(stl - self.tol < angle < stl + self.tol)

    def test_DriverFunction2(self):
        angle = self.test_3208.DriverFunction()
        stl = 168.14
        print("Calculated", angle, "Expected", stl)
        self.assertTrue(stl - self.tol < angle < stl + self.tol)

    def test_DriverFunction3(self):
        angle = self.test_3218.DriverFunction()
        stl = 176.45
        print("Calculated", angle, "Expected", stl)
        self.assertTrue(stl - self.tol < angle < stl + self.tol)

    def test_DriverFunction4(self):
        angle = self.test_3450.DriverFunction()
        stl = 172.48
        print("Calculated", angle, "Expected", stl)
        self.assertTrue(stl - self.tol < angle < stl + self.tol)

    def test_DriverFunction5(self):
        angle = self.test_3395.DriverFunction()
        stl = 154.94
        print("Calculated", angle, "Expected", stl)
        self.assertTrue(stl - self.tol < angle < stl + self.tol)

    def test_DriverFunction6(self):
        angle = self.test_3435.DriverFunction()
        stl = 160.91
        print("Calculated", angle, "Expected", stl)
        self.assertTrue(stl - self.tol < angle < stl + self.tol)

    def test_DriverFunction7(self):
        angle = self.test_3242.DriverFunction()
        stl = 172.48
        print("Calculated", angle, "Expected", stl)
        self.assertTrue(stl - self.tol < angle < stl + self.tol)

    def test_DriverFunction8(self):
        angle = self.test_3254.DriverFunction()
        stl = 164.31
        print("Calculated", angle, "Expected", stl)
        self.assertTrue(stl - self.tol < angle < stl + self.tol)

    def test_DriverFunction9(self):
        angle = self.test_3403.DriverFunction()
        stl = 180.00
        print("Calculated", angle, "Expected", stl)
        self.assertTrue(stl - self.tol < angle < stl + self.tol)

    def test_DriverFunction10(self):
        angle = self.test_3400.DriverFunction()
        stl = 173.37
        print("Calculated", angle, "Expected", stl)
        self.assertTrue(stl - self.tol < angle < stl + self.tol)

    def test_DriverFunction11(self):
        angle = self.test_3383.DriverFunction()
        stl = 139.18
        print("Calculated", angle, "Expected", stl)
        self.assertTrue(stl - self.tol < angle < stl + self.tol)

    def test_DriverFunction12(self):
        angle = self.test_3237.DriverFunction()
        stl = 165.50
        print("Calculated", angle, "Expected", stl)
        self.assertTrue(stl - self.tol < angle < stl + self.tol)

    def test_DriverFunction13(self):
        angle = self.test_3315.DriverFunction()
        stl = 178.88
        print("Calculated", angle, "Expected", stl)
        self.assertTrue(stl - self.tol < angle < stl + self.tol)

    def test_DriverFunction1(self):
        angle = self.test_3194.DriverFunction()
        stl = 161.32
        print("Calculated", angle, "Expected", stl)
        self.assertTrue(stl - self.tol < angle < stl + self.tol)
