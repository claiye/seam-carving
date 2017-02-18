from threading import Thread 
import copy



class GetRecalculatedThread(Thread):
	def __init__(self, seam, energy, energySeams, pixels):
		self.recalculated = None 
		self.seam = seam
		self.energy = energy
		self.energySeams = energySeams
		self.pixels = pixels
		super(GetRecalculatedThread, self).__init__()

	def run(self):
		newEnergy = copy.deepcopy(self.energy)
		newEnergySeams = copy.deepcopy(self.energySeams)
		rgbChanged, seamChanged = [], set()
		width, height = len(newEnergy[0]), len(newEnergy)

		for s in sorted(self.seam): 
			row, col = s
			rgbcols = [col - 1, col]
			if col == 0:
				rgbcols = [0, col]
			elif col == width - 1 or col == width:
				rgbcols = [0, width - 1]
			for c in rgbcols:
				newEnergy[row][c] = self.findRGBEnergy(row, c)
				newEnergySeams[row][c] = self.findRGBEnergy(row, c)
				rgbChanged.append((row, c))


		def recalculateIndividualPixel(r, c):
			# print("recalculating", r, c)
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

		seamFirstRowCol = sorted(self.seam)[0][1]
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
			seamColPrev = sorted(self.seam)[r][1]
			if seamColPrev + 1  <= width - 1:
				affectedCols.add(seamColPrev + 1)

		self.recalculated = (newEnergySeams, newEnergy)

	def findRGBEnergy(self, row, col):
		width, height = len(self.energySeams[0]), len(self.energySeams)
		pixels = self.pixels

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


	def returnResults(self):
		return self.recalculated