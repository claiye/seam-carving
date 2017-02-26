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

test3 = Image.open("test4 copy.jpg")
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
		newEnergySeams = dualGradientEnergy()
		# printResult = "for seam " + str(seam) + "\n"
		# for r in range(len(newEnergySeams)):
		# 	for c in range(len(newEnergySeams[0])):
		# 		if energySeams[r][c] != newEnergySeams[r][c]:
		# 			printResult += "*  "
		# 		else:
		# 			printResult += "-  "
		# 	printResult += "\n"
		# print(printResult)


		testEnergy = copy.deepcopy(energy)
		testEnergySeams = copy.deepcopy(energySeams)
		rgbChanged, seamChanged = [], set()

		for s in sorted(seam): 
			row, col = s
			rgbcols = [col - 1, col]
			if col == 0:
				rgbcols = [0, col]
			elif col == width - 1 or col == width:
				rgbcols = [0, width - 1]
			print(width, col, rgbcols)
			for c in rgbcols:
				testEnergy[row][c] = findRGBEnergy(row, c)
				testEnergySeams[row][c] = findRGBEnergy(row, c)
				rgbChanged.append((row, c))


		def recalculateIndividualPixel(r, c):
			# print("recalculating", r, c)
			nonlocal testEnergySeams
			if c == 0:
				tops = [testEnergySeams[r-1][c], testEnergySeams[r-1][c+1]]
			elif c == width - 1:
				tops = [testEnergySeams[r-1][c-1], testEnergySeams[r-1][c]]
			else:
				tops = [testEnergySeams[r-1][c-1], testEnergySeams[r-1][c], testEnergySeams[r-1][c+1]]
			minTop = min(tops)
			testEnergySeams[r][c] = testEnergy[r][c] + minTop
			seamChanged.add((r, c))

		seamFirstRowCol = sorted(seam)[0][1]
		affectedCols = set()
		oppositeEnds = False

		leftEnd, rightEnd = None, None

		for i in range(-2, 3):
			if i + seamFirstRowCol <= width - 1 and i + seamFirstRowCol >= 0:
				affectedCols.add(i + seamFirstRowCol)
				if oppositeEnds and leftEnd == None and i > 0:
					leftEnd = i + seamFirstRowCol
			elif i < 0:
				oppositeEnds = True 
				rightEnd = seamFirstRowCol + i + width
				# print("setting right end", rightEnd)
				affectedCols.add(seamFirstRowCol + i + width)
			elif i > 0:
				oppositeEnds = True 
				leftEnd = seamFirstRowCol + i - width
				if rightEnd == None:
					rightEnd = min(affectedCols)
				affectedCols.add(seamFirstRowCol + i - width)
		# print("firstrowcol:", seamFirstRowCol, "affectedCols:", affectedCols, "width and height", width, height)


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
				# print("left and right ends", leftEnd, rightEnd)
				affectedCols.add(rightEnd)
				affectedCols.add(leftEnd)
			seamColPrev = sorted(seam)[r][1]
			if seamColPrev + 1  <= width - 1:
				affectedCols.add(seamColPrev + 1)

		printResult2 = "for seam if r,c changed" + str(seam) + "\n"
		for r in range(len(newEnergySeams)):
			for c in range(len(newEnergySeams[0])):
				if newEnergySeams[r][c] != testEnergySeams[r][c]:
					if (r, c) in rgbChanged and (r,c) not in seamChanged:
						printResult2 += "m  " # missed
					elif (r, c) in seamChanged:
						printResult2 += "s  " # seam changed
					# else:
					# 	printResult2 += "w  "
					elif (r, c) in rgbChanged and (r, c) in seamChanged:
						printResult2 += "b  "
				elif (r,c) in rgbChanged:
					printResult2 += "r  "
				elif (r,c) in seamChanged:
					printResult2 += "c  "
				else:
					printResult2 += "-  "
			printResult2 += "\n"
		print(printResult2)

		# print3 = "correct tops for seam " + str(seam) + "\n"
		# for r in range(len(newEnergySeams)):
		# 	for c in range(len(newEnergySeams[0])):
		# 		if c == 0:
		# 			tops = [newEnergySeams[row-1][c], newEnergySeams[row-1][c+1]]
		# 		elif c == width - 1:
		# 			tops = [newEnergySeams[row-1][c-1], newEnergySeams[row-1][c]]
		# 		else:
		# 			tops = [newEnergySeams[row-1][c-1], newEnergySeams[row-1][c], newEnergySeams[row-1][c+1]]
		# 		minTop = min(tops)
		# 		print3 += str(minTop) + "  "
		# 	print3 += "\n"
		# print(print3)

		print4 = "test tops for seam " + str(seam) + "\n"
		for r in range(len(testEnergySeams)):
			for c in range(len(testEnergySeams[0])):
				if testEnergySeams[r][c] != newEnergySeams[r][c]:
					if c == 0:
						tops = [testEnergySeams[row-1][c], testEnergySeams[row-1][c+1]]
					elif c == width - 1:
						tops = [testEnergySeams[row-1][c-1], testEnergySeams[row-1][c]]
					else:
						tops = [testEnergySeams[row-1][c-1], testEnergySeams[row-1][c], testEnergySeams[row-1][c+1]]
					minTop = min(tops)
					print4 += str(minTop) + "  "
				else:
					print4 += "* "
			print4 += "\n"
		print(print4)
		return (testEnergySeams, testEnergy)


	def removeOneSeam():
		currentSeam = findSeamWithGradient()
		deleteSeam(currentSeam)
		return currentSeam

	seamsRemoved = []

	for seamsDeleted in range(numSeamsToDelete):
		print("removing seam", seamsDeleted)
		currentSeam = removeOneSeam()
		seamsRemoved.append(currentSeam)
		width, height = len(pixels[0]), len(pixels)
		energySeams, energy = recalculateAffectedPixels(currentSeam)

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

pixels, seamsRemoved = deleteSeams(test3, 10)
print(len(pixels[0]), len(pixels) )
# print(pixels)
result = Image.new(test3.mode, (len(pixels[0]), len(pixels)))
pixelRaw = convertPixelsToImage(pixels)
result.putdata(pixelRaw)
result.show()
reDrawn = pixels

for i in range(len(seamsRemoved) - 1, -1, -1):
	seam = seamsRemoved[i]
	for p in seam:
		row, col = p 
		reDrawn[row].insert(col, (255, 0, 0))

reDrawnImg = Image.new(test3.mode, test3.size)
reDrawnImg.putdata(convertPixelsToImage(reDrawn))
reDrawnImg.show()

# answer = Image.open("balloons_resized_150.jpg")
# answer.show()
# for i in range(len(answerP)):
# answerP = list(answer.getdata())

# diff = 0
# 	if answerP[i] == pixelRaw[i]:
# 		diff += 1 

# print(diff, "out of", len(answerP))
