from threading import Thread 
import copy

class ChangeTempThread(Thread):
	def __init__(self, seam, tempReDrawnImage, tempReDrawnPixels, seamJustCarved, seamsRemoved, pixels):
		self.seam = seam 
		self.tempReDrawnPixels = tempReDrawnPixels
		self.tempReDrawnImage = tempReDrawnImage
		self.seamJustCarved = seamJustCarved
		self.seamsRemoved = seamsRemoved
		self.pixels = pixels
		super(ChangeTempThread, self).__init__()

	def run(self):

		self.tempReDrawnPixels = copy.deepcopy(self.pixels)
		print(len(self.pixels[0]), len(self.pixels))

		for i in range(len(self.seamsRemoved) - 1, -1, -1):
			s = self.seamsRemoved[i]
			for p in s:
				row, col = p
				self.tempReDrawnPixels[row].insert(col, (255, 0, 0))
		redrawnRow, redrawnCol = len(self.tempReDrawnPixels[0]), len(self.tempReDrawnPixels)
		self.convertPixelsToImage()
		self.tempReDrawnImage.resize((len(self.pixels[0]) + len(self.seamsRemoved), len(self.pixels)))
		print((len(self.pixels[0]) + len(self.seamsRemoved), len(self.pixels)), (redrawnRow, redrawnCol))
		self.tempReDrawnImage.putdata(self.tempReDrawnPixels)

	def convertPixelsToImage(self):
		result = []
		for pRow in self.tempReDrawnPixels:
			for p in pRow:
				result.append(p)
		print("redrawn pixels:", len(self.tempReDrawnPixels))
		self.tempReDrawnPixels = result 

	def returnResults(self):
		return (self.tempReDrawnPixels, self.tempReDrawnImage)

