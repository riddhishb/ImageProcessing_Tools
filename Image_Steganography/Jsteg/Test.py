#Trial to input a text string in the image file

import cv2
import sys
import numpy as np 
import math
from JSteg import JSteg
from matplotlib import pyplot as plt

str = "Sleep my friend and you will see, dream is my reality!"
carrier = cv2.imread("4.jpg")
#print carrier.dtype
steg = JSteg(carrier)
steg.hide(str)
steg.saveImage("res.png") #Image that contain data

im = cv2.imread("res.png")
print im.dtype
steg = JSteg(im)
print "Text value:",steg.unhide()
cv2.waitKey(0)