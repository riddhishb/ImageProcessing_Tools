# A python function for the JSteg algorithm of Image Steganography

import cv2
import sys
import numpy as np 
import math
from matplotlib import pyplot as plt

quant_matrix = [
  [
  [16,  11,  10,  16,  24,  40,  51,  61],
  [12,  12,  14,  19,  26,  58,  60,  55],
  [14,  13,  16,  24,  40,  57,  69,  56],
  [14,  17,  22,  29,  51,  87,  80,  62],
  [18,  22,  37,  56,  68, 109, 103,  77],
  [24,  35,  55,  64,  81, 104, 113,  92],
  [49,  64,  78,  87, 103, 121, 120, 101],
  [72,  92,  95,  98, 112, 100, 103,  99]
  ],
  [
  [17,  18,  24,  47,  99,  99,  99,  99],
  [18,  21,  26,  66,  99,  99,  99,  99],
  [24,  26,  56,  99,  99,  99,  99,  99],
  [47,  66,  99,  99,  99,  99,  99,  99],
  [99,  99,  99,  99,  99,  99,  99,  99],
  [99,  99,  99,  99,  99,  99,  99,  99],
  [99,  99,  99,  99,  99,  99,  99,  99],
  [99,  99,  99,  99,  99,  99,  99,  99]
  ],
  [
  [17,  18,  24,  47,  99,  99,  99,  99],
  [18,  21,  26,  66,  99,  99,  99,  99],
  [24,  26,  56,  99,  99,  99,  99,  99],
  [47,  66,  99,  99,  99,  99,  99,  99],
  [99,  99,  99,  99,  99,  99,  99,  99],
  [99,  99,  99,  99,  99,  99,  99,  99],
  [99,  99,  99,  99,  99,  99,  99,  99],
  [99,  99,  99,  99,  99,  99,  99,  99]
  ]
]


class SteganographyException(Exception):
	pass

class JSteg():
	def __init__(prop,img):
		prop.image = img
		[prop.width,prop.height,prop.channels] = img.shape
		prop.size = prop.width * prop.height
		temp = np.zeros((prop.height,prop.width,3), np.uint8)
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
		cv2.imwrite(filename,prop.image)

	def putBinaryValue(prop,bits):					   
		#For putting the bits in the image
		for c in bits:
			val = list(prop.image[prop.row,prop.col])				   #Get the pixel value as a list for the R G and B channels

			if int(c) == 1:
				val[prop.chan] = int(val[prop.chan]) | prop.maskONE	 #OR with maskONE
			else:
				val[prop.chan] = int(val[prop.chan]) & prop.maskZERO	#AND with maskZERO
			
			prop.image[prop.row,prop.col] = tuple(val)
			prop.nextSpace() 											#Move "cursor" to the next space

	def nextSpace(prop):
		# Proper order of what should come next 
		if prop.chan == prop.channels-1: 								#Next Space is the following channel
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
		binval = bin(val)[2:]			 #Integer to binary string ignoring the 0b prefix to the conversion
		if len(binval) > bitsize:
			raise SteganographyException, "binary value larger than the expected size"
		while len(binval) < bitsize:
			binval = "0"+binval		   #Higher Bits to zero
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

	def DCTnQuantize(prop):
		#To take the DCT of the image
		img = prop.image

		iHeight, iWidth = img.shape[:2]
		
		print "size:", iWidth, "x", iHeight
		# set size to multiply of 8
		if (iWidth % 8) != 0:
			filler = img[:,iWidth-1:,:]
				#print "width filler size", filler.shape
			for i in range(8 - (iWidth % 8)):
				img = np.append(img, filler, 1)
		if (iHeight % 8) != 0:
			filler = img[iHeight-1:,:,:]
			#print "height filler size", filler.shape
			for i in range(8 - (iHeight % 8)):
				img = np.append(img, filler, 0)

		iHeight, iWidth = img.shape[:2]
		print "new size:", iWidth, "x", iHeight

		# convert to YCrCb, Y=luminance, Cr/Cb=red/blue-difference chrominance
		img = cv2.cvtColor(img, cv2.COLOR_BGR2YCR_CB)

		# array as storage for DCT + quant.result
		img2 = np.empty(shape=(iHeight, iWidth, 3))
		# FORWARD ----------------
		# do calc. for each 8x8 non-overlapping blocks
		
		for startY in range(0, iHeight, 8):
			for startX in range(0, iWidth, 8):
				for c in range(0, 3):
					block = img[startY:startY+8, startX:startX+8, c:c+1].reshape(8,8)

					# apply DCT for a block
					blockf = np.float32(block)	 # float conversion
					dst = cv2.dct(blockf)		  # dct
				  
					# quantization of the DCT coefficients
					blockq = np.around(np.divide(dst, quant_matrix[c]))
					blockq = np.multiply(blockq, quant_matrix[c])
					# store the result
					for y in range(8):
						for x in range(8):
							img2[startY+y, startX+x, c] = blockq[y, x]
		
		prop.image = img2

#		print prop.image.dtype

	def IDCTnDequantize(prop):
		#To dequantize
		img3 = prop.image
		iHeight, iWidth = img3.shape[:2]
		img2 = np.zeros((iHeight,iWidth,3), np.uint8)
		#print img2.dtype

		for startY in range(0, iHeight, 8):
			for startX in range(0, iWidth, 8):
				for c in range(0, 3):
					block = img3[startY:startY+8, startX:startX+8, c:c+1].reshape(8,8)
			   
					blockf = np.float32(block)	 # float conversion
					dst = cv2.idct(blockf)		 # inverse dct
					np.place(dst, dst>255.0, 255.0)	 # saturation
					np.place(dst, dst<0.0, 0.0)		 # grounding 
					block = np.uint8(np.around(dst)) 

					# store the results
					for y in range(8):
						for x in range(8):
							img2[startY+y, startX+x, c] = block[y, x]
		
		# convert to BGR
		img2 = cv2.cvtColor(img2, cv2.COLOR_YCR_CB2BGR)

		prop.image = img2


	def hide(prop, txt):
		l = len(txt)					  #Length of the string
		prop.DCTnQuantize()
		prop.image = np.uint8(prop.image)
		#print temp.shape
		binl = prop.binValue(l, 16)	     #Length coded on 2 bytes so the text size can be up to 65536 bytes long
		prop.putBinaryValue(binl)		 #Put text length coded on 4 bytes
		
		for char in txt:				  #And put all the chars
			c = ord(char)				  # Convert to ASCII 
			prop.putBinaryValue(prop.byteValue(c))

		prop.image = np.float32(prop.image)	
		prop.IDCTnDequantize()
		#cv2.imshow("Booya",prop.image)	

	def unhide(prop):
		prop.DCTnQuantize()
		prop.image = np.uint8(prop.image)
		temp1 = prop
		ls = temp1.readBits(16)			#Read the text size in bytes
		l = int(ls,2)
		i = 0
		Txt = ""
		
		while i < l:					  #Read all bytes of the text
			tmp = temp1.readByte()		 #So one byte
			i += 1
			Txt += chr(int(tmp,2))		#Every chars concatenated to str
		
		return Txt	