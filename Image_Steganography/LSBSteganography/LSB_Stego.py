#A function for LSB Steganography in Images with Text

import cv2.cv as cv
import sys
import numpy as np 
import math
from matplotlib import pyplot as plt

class SteganographyException(Exception):
	pass

class LSB_Stego():
	def __init__(prop,img):
		prop.image = img
		prop.width = img.width
		prop.height = img.height
		prop.size = prop.width * prop.height
		prop.nbchannels = img.channels

		prop.maskONEValues = [1,2,4,8,16,32,64,128]
		#Mask used to put one ex:1->00000001, 2->00000010 .. associated with OR bitwise
		prop.maskONE = prop.maskONEValues.pop(0) #Will be used to do bitwise operations
		prop.maskZEROValues = [254,253,251,247,239,223,191,127]
		#Mak used to put zero ex:254->11111110, 253->11111101 .. associated with AND bitwise
		prop.maskZERO = prop.maskZEROValues.pop(0)

		prop.row = 0
		prop.col = 0
		prop.chan = 0

	def saveImage(prop,filename):
		# Save the image using the given filename
		cv.SaveImage(filename, prop.image)

	def putBinaryValue(prop,bits):                       
		#For putting the bits in the image
		for c in bits:
			val = list(prop.image[prop.row,prop.col])                   #Get the pixel value as a list for the R G and B channels

			if int(c) == 1:
				val[prop.chan] = int(val[prop.chan]) | prop.maskONE     #OR with maskONE
			else:
				val[prop.chan] = int(val[prop.chan]) & prop.maskZERO    #AND with maskZERO
			
			prop.image[prop.row,prop.col] = tuple(val)
			prop.nextSpace() 											#Move "cursor" to the next space

	def nextSpace(prop):
		# Proper order of what should come next 
		if prop.chan == prop.nbchannels-1: 								#Next Space is the following channel
			prop.chan = 0
			if prop.row == prop.width-1: 								#Or the first channel of the next pixel of the same line
				prop.row = 0
				if prop.col == prop.height-1:							#Or the first channel of the first pixel of the next line
					prop.col = 0
					if prop.maskONE == 128: 							#Mask 1000000, so the last mask
						raise SteganographyException, "Image filled"
					else: 												#Or instead of using the first bit start using the second and so on..
						prop.maskONE = prop.maskONEValues.pop(0)
						prop.maskZERO = prop.maskZEROValues.pop(0)
				else:
					prop.col +=1
			else:
				prop.row +=1
		else:
			prop.chan +=1
	

	def byteValue(prop,val):
		return prop.binValue(val, 8)

	def binValue(prop,val,bitsize):
		binval = bin(val)[2:]             #Integer to binary string ignoring the 0b prefix to the conversion
		if len(binval) > bitsize:
			raise SteganographyException, "binary value larger than the expected size"
		while len(binval) < bitsize:
			binval = "0"+binval           #Higher Bits to zero
		return binval

	def readBit(prop):
		# To read a single bit in the image
		val = prop.image[prop.row,prop.col][prop.chan]
		val = int(val) & prop.maskONE
		prop.nextSpace()
		if val > 0:
			return "1"
		else:
			return "0"

	def readBits(prop,nob):
		bits = ""
		for i in range(nob):
			bits += prop.readBit()
		return bits

	def readByte(prop):
		return prop.readBits(8)

	def hide(prop, txt):
		l = len(txt)                      #Length of the string
		binl = prop.binValue(l, 16)       #Length coded on 2 bytes so the text size can be up to 65536 bytes long
		prop.putBinaryValue(binl)         #Put text length coded on 4 bytes
		
		for char in txt:                  #And put all the chars
			c = ord(char)    			  # Convert to ASCII 
			prop.putBinaryValue(prop.byteValue(c))

	def unhide(prop):
		ls = prop.readBits(16)            #Read the text size in bytes
		l = int(ls,2)
		i = 0
		Txt = ""
		
		while i < l:                      #Read all bytes of the text
			tmp = prop.readByte()         #So one byte
			i += 1
			Txt += chr(int(tmp,2))        #Every chars concatenated to str
		return Txt	