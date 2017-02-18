from __future__ import print_function
from PIL import Image 
from numpy import * 
from math import * 
import copy
import sys 


# print(resizedImage.format, resizedImage.size, resizedImage.mode)

# test2 = Image.open("test2.jpg")
# print(test2.format, test2.size, test2.mode)
# pixels = asarray(test2)
# print(pixels)

test3 = Image.open("balloons.jpg")
print(test3.format, test3.size, test3.mode)
test3.show()
# print(list(test3.getdata()))
# print(pixels)



def deleteSeams(im, numSeamsToDelete=1):

	pixels = list(im.getdata())
	width, height = im.size
	mode = im.mode 
	pixels = [pixels[i * width:(i+1) * width] for i in range(height)]
	energy = [([None] * len(pixels[0])) for r in range(len(pixels))]
	energySeams = [([None] * len(pixels[0])) for r in range(len(pixels))]
	seamsRemoved = []



	### CALCULATE ENERGY OF IMAGE ### 

	def findRGBEnergy(row, col):

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
			if row >= height:
				return 
			else:
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

		# print(seam)
		return seam 

	def deleteSeam(seam):
		for s in seam:
			row, col = s
			pixels[row].pop(col)
			energySeams[row].pop(col)
			energy[row].pop(col)



	### RECALCULATE ENERGY ### 

	def recalculateAffectedPixels(seam):

		def recalculateIndividualPixel(r, c):
			if c == 0:
				tops = [energySeams[r-1][c], energySeams[r-1][c+1]]
			elif c == width - 1:
				tops = [energySeams[r-1][c-1], energySeams[r-1][c]]
			else:
				tops = [energySeams[r-1][c-1], energySeams[r-1][c], energySeams[r-1][c+1]]
			minTop = min(tops)
			energySeams[r][c] = energySeams[r][c] + minTop
		
		seamFirstRowCol = sorted(seam)[0][1]
		affectedCols = [seamFirstRowCol - 1, seamFirstRowCol]
		if seamFirstRowCol == width:
			affectedCols = [width - 1]
		elif seamFirstRowCol == 0:
			affectedCols = [0]

		for r in range(1, height):
			for c in affectedCols:
				recalculateIndividualPixel(r, c)
			if affectedCols[0] > 0:
				affectedCols.insert(0, affectedCols[0] - 1)
			if affectedCols[len(affectedCols) - 1] < width - 1:
				affectedCols.append(affectedCols[len(affectedCols) - 1] + 1)
	

	def removeOneSeam():
		currentSeam = findSeamWithGradient()
		deleteSeam(currentSeam)
		return currentSeam

	for seamsDeleted in range(numSeamsToDelete):
		print("removing seam", seamsDeleted)
		currentSeam = removeOneSeam()
		width, height = len(pixels[0]), len(pixels)
		recalculateAffectedPixels(currentSeam)
		seamsRemoved.append(currentSeam)



	return (pixels, seamsRemoved) 


def deleteSeamsSlow(im, numSeamsToDelete=1):

	pixels = list(im.getdata())
	width, height = im.size
	mode = im.mode 
	pixels = [pixels[i * width:(i+1) * width] for i in range(height)]
	energy = [([None] * len(pixels[0])) for r in range(len(pixels))]
	energySeams = [([None] * len(pixels[0])) for r in range(len(pixels))]
	seamsRemoved = []



	### CALCULATE ENERGY OF IMAGE ### 

	def findRGBEnergy(row, col):

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
			if row >= height:
				return 
			else:
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

		# print(seam)
		return seam 

	def deleteSeam(seam):
		for s in seam:
			row, col = s
			pixels[row].pop(col)
			energySeams[row].pop(col)
			energy[row].pop(col)



	### RECALCULATE ENERGY ### 

	def recalculateAffectedPixels(seam):
		nonlocal energySeams
		nonlocal energy

		for s in seam: 
			row, col = s
			rgbcols = [col - 1, col]
			if col == 0:
				rgbcols = [col]
			elif col == width:
				rgbcols = [0, width - 1]
			# print(width, col, rgbcols)
			for c in rgbcols:
				energy[row][c] = findRGBEnergy(row, c)
				energySeams[row][c] = findRGBEnergy(row, c)

		def recalculateIndividualPixel(r, c):
			if c == 0:
				tops = [energySeams[r-1][c], energySeams[r-1][c+1]]
			elif c == width - 1:
				tops = [energySeams[r-1][c-1], energySeams[r-1][c]]
			else:
				tops = [energySeams[r-1][c-1], energySeams[r-1][c], energySeams[r-1][c+1]]
			minTop = min(tops)
			energySeams[r][c] = energySeams[r][c] + minTop
		
		seamFirstRowCol = sorted(seam)[0][1]
		affectedCols = {seamFirstRowCol - 1, seamFirstRowCol}
		if seamFirstRowCol == width:
			affectedCols = {width - 1}
		elif seamFirstRowCol == 0:
			affectedCols = {0}

		for r in range(1, height):
			for c in sorted(affectedCols):
				recalculateIndividualPixel(r, c)
			if 0 not in affectedCols:
				affectedCols.add(min(affectedCols) - 1)
			if width - 1 not in affectedCols:
				affectedCols.add(max(affectedCols) + 1)
			seamColPrev = sorted(seam)[r][1]
			if seamColPrev + 1  <= width - 1:
				affectedCols.add(seamColPrev + 1)


	def removeOneSeam():
		currentSeam = findSeamWithGradient()
		deleteSeam(currentSeam)
		return currentSeam

	for seamsDeleted in range(numSeamsToDelete):
		print("removing seam", seamsDeleted)
		currentSeam = removeOneSeam()
		width, height = len(pixels[0]), len(pixels)
		recalculateAffectedPixels(currentSeam)
		seamsRemoved.append(currentSeam)


	return (pixels, seamsRemoved) 


def convertPixelsToImage(pixels):
	result = []
	for pRow in pixels:
		for p in pRow:
			result.append(p)
	return result


def print2D(L):
	result = ""
	for r in range(len(L)):
		row = ""
		for c in range(len(L[0])):
			row = row + str(L[r][c]) + " "
		result = result + row + "\n"
	return result 

# test3Energy = (dualGradientEnergy(test3))
# print(len(test3Energy[0]), len(test3Energy[0][0]))
# print(len(test3Energy[1]), len(test3Energy[1][0]))
# print(print2D(test3Energy[0]), "\n\n" + print2D(test3Energy[1]))
# testSeam = findSeamWithGradient(test3Energy[1])
# print(testSeam, len(testSeam))

pixels, seamsRemoved = deleteSeams(test3, 50)
# pixels2, seamsRemoved2 = deleteSeamsSlow(test3, 50)
reDrawn1 = copy.deepcopy(pixels)
print(len(pixels[0]), len(pixels) )
# print(len(pixels2[0]), len(pixels2))
# print(pixels)
for i in range(len(seamsRemoved) - 1, -1, -1):
	seam = seamsRemoved[i]
	for p in seam:
		row, col = p 
		reDrawn1[row].insert(col, (255, 0, 0))
# for i in range(len(seamsRemoved2) - 1, -1, -1):
# 	seam = seamsRemoved[i]
# 	for p in seam:
# 		row, col = p 
# 		reDrawn2[row].insert(col, (255, 0, 0))
result1 = Image.new(test3.mode, (len(pixels[0]), len(pixels)))
pixelRaw = convertPixelsToImage(pixels)
result1.putdata(pixelRaw)
result1.show()

# result2 = Image.new(test3.mode, (len(pixels2[0]), len(pixels2)))
# pixelRaw = convertPixelsToImage(pixels2)
# result2.putdata(pixelRaw)
# result2.show()

reDrawnImg1 = Image.new(test3.mode, (test3.size))
reDrawnImg1.putdata(convertPixelsToImage(reDrawn1))
reDrawnImg1.show()

# reDrawnImg2 = Image.new(test3.mode, (test3.size))
# reDrawnImg2.putdata(convertPixelsToImage(reDrawn2))
# reDrawnImg2.show()

# answer = Image.open("balloons_resized_150.jpg")
# answer.show()
# answerP = list(answer.getdata())



# diff = 0 
# for i in range(len(answerP)):
# 	if answerP[i] != pixelRaw[i]:
# 		diff += 1 
# 		print(i // len(pixels[0]), i % len(pixels[0]))

# print("total diff", diff, "out of", str(len(pixelRaw)))
