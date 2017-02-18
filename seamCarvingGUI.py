from PIL import Image, ImageTk
from math import * 
from numpy import *
import copy
import sys 
# import threading 
# from RecalculateThread import * 
# from ChangeTempThread import * 



def deleteSeams(im, numSeamsToDelete, data, i=0):

	pixels = list(im.getdata())
	width, height = im.size
	mode = im.mode 
	pixels = [pixels[i * width:(i+1) * width] for i in range(height)]
	energy = [([None] * len(pixels[0])) for r in range(len(pixels))]
	energySeams = [([None] * len(pixels[0])) for r in range(len(pixels))]

	### CALCULATE ENERGY OF IMAGE ### 

	def findRGBEnergy(row, col):

		# look left, right, up, down and calculate the difference in rgb values
		# in each axis 
		# use the differences to calculate the gradient or change in color 
		# for that pixel 

		def findLeftRight(row, col):
			if (col == 0):
				return [(row, width - 1), (row, col + 1)]
			elif (col == width - 1):
				return [(row, col - 1), (row, 0)]
			return [(row, col - 1), (row, col + 1)]

		def findUpDown(row, col):
			if (row == 0):
				return [(height - 1, col), (row + 1, col)]
			elif (row == height - 1):
				return [(row - 1, col), (0, col)]
			return [(row - 1, col), (row + 1, col)]

		def findPixelRGB(coords):
			result = []
			for pos in coords:
				rgb = pixels[pos[0]][pos[1]]
				result.append(rgb)
			return result 

		def findGrad(rgbList):
			# takes list of 2 rgb tuples and finds gradient difference 
			gradient = 0
			for val in range(3):
				diff = abs(rgbList[0][val] - rgbList[1][val])
				gradient += diff ** 2 
			return gradient

		leftRight = findLeftRight(row, col)
		upDown = findUpDown(row, col)
		# calculate yGrad and xGrad and return value 
		yPixels, xPixels = findPixelRGB(upDown), findPixelRGB(leftRight)
		yGrad, xGrad = findGrad(yPixels), findGrad(xPixels)
		return yGrad + xGrad 

	def dualGradientEnergy():

		for r in range(height):
			for c in range(width):
				rgbEnergy = findRGBEnergy(r, c)
				energy[r][c] = rgbEnergy

		energySeams = copy.deepcopy(energy)


		def calculateSeams(row):
			# base case: no more rows to calculate
			if row >= height:
				return 
			else:
			# looks to the row above and the pixels that determine the seam energy of the
			# current pixel, and add the one with the least amount of energy 
				for c in range(width):
					if c == 0:
						tops = [energySeams[row-1][c], energySeams[row-1][c+1]]
					elif c == width - 1:
						tops = [energySeams[row-1][c-1], energySeams[row-1][c]]
					else:
						tops = [energySeams[row-1][c-1], energySeams[row-1][c], energySeams[row-1][c+1]]
					minTop = min(tops)
					energySeams[row][c] = energySeams[row][c] + minTop
				calculateSeams(row+1)

		calculateSeams(1)

		return energySeams

	energySeams = dualGradientEnergy()


 
	### FIND AND DELETE A SEAM ### 

	def findSeamWithGradient():
		# find the seam of least energy by looking at the last row, finding the pixel with the least
		# amount of seam energy, and tracing up by determining which pixel in the proceeding row 
		# that topleft, topcenter or topright of the pixel has the least energy 
		# stores (row, col) information of each pixel of seam in a list 
		lastRow = energySeams[len(energySeams) - 1]
		seamEndIndex = lastRow.index(min(lastRow))

		def findUp(r, i):
			if i == 0:
				return {energySeams[r][0]: 0, energySeams[r][1]: 1}
			elif i == len(lastRow) - 1:
				return {energySeams[r][len(lastRow)-2]: len(lastRow)-2, energySeams[r][len(lastRow)-1]: len(lastRow)-1}
			result = {}
			for j in range(-1, 2):
				element = energySeams[r][i+j]
				if element not in result:
					result[element] = i+j
			return result

		seam = []
		seam.append((len(energySeams) - 1, seamEndIndex))

		for row in range(len(energySeams) - 1, 0, -1):
			above = findUp(row-1, seamEndIndex)
			colUp = min(list(above.keys()))
			seamEndIndex = above[colUp]
			seam.append((row-1, seamEndIndex))
		return seam 

	def deleteSeam(seam):
		# deletes seam by removing it from the matrix of pixels, energySeams, and energy 
		for s in seam:
			row, col = s
			pixels[row].pop(col)
			energySeams[row].pop(col)
			energy[row].pop(col)



	### RECALCULATE ENERGY ### 

	def recalculateAffectedPixels(seam):
		# recalculates energy by finding the correct pixels that have been affected
		# by removing a particular seam 

		newEnergy = copy.deepcopy(energy)
		newEnergySeams = copy.deepcopy(energySeams)
		rgbChanged, seamChanged = [], set()

		# change rgb energy value by looking at all the pixels that immediately 
		# surrounded the seam that was just removed 
		for s in sorted(seam): 
			row, col = s
			rgbcols = [col - 1, col]
			if col == 0:
				rgbcols = [0, col]
			elif col == width - 1 or col == width:
				rgbcols = [0, width - 1]
			for c in rgbcols:
				newEnergy[row][c] = findRGBEnergy(row, c)
				newEnergySeams[row][c] = findRGBEnergy(row, c)
				rgbChanged.append((row, c))

		# recalculate each individual pixel using the same method that they were first calculated above 
		def recalculateIndividualPixel(r, c):
			nonlocal newEnergySeams
			nonlocal newEnergy
			if c == 0:
				tops = [newEnergySeams[r-1][c], newEnergySeams[r-1][c+1]]
			elif c == width - 1:
				tops = [newEnergySeams[r-1][c-1], newEnergySeams[r-1][c]]
			else:
				tops = [newEnergySeams[r-1][c-1], newEnergySeams[r-1][c], newEnergySeams[r-1][c+1]]
			minTop = min(tops)
			newEnergySeams[r][c] = newEnergy[r][c] + minTop
			seamChanged.add((r, c))

		seamFirstRowCol = sorted(seam)[0][1]
		affectedCols = set()
		oppositeEnds = False


		# finds the two ends of the affect pixels tree that grows due to how seams are calculated 
		leftEnd, rightEnd = None, None

		for i in range(-2, 3):
			if i + seamFirstRowCol <= width - 1 and i + seamFirstRowCol >= 0:
				affectedCols.add(i + seamFirstRowCol)
				if oppositeEnds and leftEnd == None and i > 0:
					leftEnd = i + seamFirstRowCol
			elif i < 0:
				oppositeEnds = True 
				rightEnd = seamFirstRowCol + i + width
				affectedCols.add(seamFirstRowCol + i + width)
			elif i > 0:
				oppositeEnds = True 
				leftEnd = seamFirstRowCol + i - width
				if rightEnd == None:
					rightEnd = min(affectedCols)
				affectedCols.add(seamFirstRowCol + i - width)


		# recalculate all affected seams, including pixels whose rgb energies were changed above 
		for r in range(1, height):
			for c in sorted(affectedCols):
				recalculateIndividualPixel(r, c)
			for p in sorted(rgbChanged)[2*r:2*r+2]:
				row, col = p
				recalculateIndividualPixel(row, col)
			if not oppositeEnds:
				if 0 not in affectedCols:
					affectedCols.add(min(affectedCols) - 1)
				if width - 1 not in affectedCols:
					affectedCols.add(max(affectedCols) + 1)
			else:
				if rightEnd > 0: 
					rightEnd -= 1 
				if leftEnd < width - 1:
					leftEnd += 1 
				affectedCols.add(rightEnd)
				affectedCols.add(leftEnd)
			seamColPrev = sorted(seam)[r][1]
			if seamColPrev + 1  <= width - 1:
				affectedCols.add(seamColPrev + 1)

		return (newEnergySeams, newEnergy)

	def removeOneSeam():
		# find and remove seam 
		currentSeam = findSeamWithGradient()
		deleteSeam(currentSeam)
		return currentSeam

	seamsRemoved = []

	# old function that was used for displaying as each seam carved 
	# no longer in use 

	# def changeTemp(seam):
	# 	global tempReDrawnPixels, tempReDrawnImage, seamJustCarved
	# 	nonlocal seamsRemoved

	# 	seamJustCarved = seam 
	# 	tempReDrawnPixels = copy.deepcopy(pixels)

	# 	for s in seamsRemoved:
	# 		for p in s:
	# 			row, col = p
	# 			tempReDrawnPixels[row].insert(col, (255, 0, 0))
	# 	tempReDrawnImage.resize((len(pixels[0]), len(pixels)))
	# 	tempReDrawnImage.putdata(convertPixelsToImage(tempReDrawnPixels))


	for seamsDeleted in range(numSeamsToDelete):
		# iterates over how many seams that need ot be carved 
		# with parts needed for tkinter GUI such as updated the percentage of seams carved 
		currentSeam = removeOneSeam()
		seamsRemoved.append(currentSeam)
		width, height = len(pixels[0]), len(pixels)
		energySeams, energy = recalculateAffectedPixels(currentSeam)
		data.seamsCurrentlyCarved += 1
		data.seamCarvingPercent = int(data.seamsCurrentlyCarved / data.seamsToBeCarved * 100 )

	# creates finish and carved image and updates tkinter data 
	finishedImage = Image.new(im.mode, (len(pixels[0]), len(pixels)))
	finishedImage.putdata(convertPixelsToImage(pixels))
	data.carving = finishedImage
	data.carvingTk = ImageTk.PhotoImage(data.carving)

	return (pixels, seamsRemoved) 


def convertPixelsToImage(pixels):
	# change 2d list to simple list so that the Image module 
	# can make it into a picture 
	result = []
	for pRow in pixels:
		for p in pRow:
			result.append(p)
	return result

def rotatePixels(pixels):
	# rotate pixels -90 degrees 
	result = []
	for c in range(len(pixels[0])):
		result.append([])
		for r in range(len(pixels)):
			result[c].insert(0, pixels[r][c])
	return result 

def redrawImg(pixels, seamsRemoved):
	# redraws image given the list of seams removed and 
	# draws the removed seams on to the image 
	redrawn = copy.deepcopy(pixels)
	for i in range(len(seamsRemoved) - 1, -1, -1):
		seam = seamsRemoved[i]
		for p in seam:
			row, col = p 
			redrawn[row].insert(col, (255, 0, 0))
	redrawnPixels = convertPixelsToImage(redrawn)
	return redrawnPixels


def bothRedraw(verticalPixels, verticalSeams, horizontalPixels, horizontalSeams):
	# redraws both horizontal and vertical seams 
	horizontalDraw = horizontalPixels
	for i in range(len(horizontalSeams) - 1, -1, -1):
		seam = horizontalSeams[i]
		for p in seam:
			row, col = p
			horizontalDraw[row].insert(col, (255, 0, 0))

	rotatedHorizontal = rotatePixels(horizontalDraw)

	for i in range(len(verticalSeams) - 1, -1, -1):
		seam = verticalSeams[i]
		for p in seam:
			row, col = p
			rotatedHorizontal[row].insert(col, (255, 0, 0))

	return rotatedHorizontal

