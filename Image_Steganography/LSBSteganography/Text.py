#Trial to input a text string in the image file

import cv2.cv as cv
import sys
import numpy as np 
import math
from LSB_Stego import LSB_Stego
from matplotlib import pyplot as plt

str = "Sleep my friend and you will see, dream is my reality!"
carrier = cv.LoadImage("4.jpg")
steg = LSB_Stego(carrier)
steg.hide(str)
steg.saveImage("res.png") #Image that contain data

im = cv.LoadImage("res.png")
steg = LSB_Stego(im)
print "Text value:",steg.unhide()
