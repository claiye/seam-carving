from seamCarvingGUI import * 
from PIL import Image, ImageTk 
from threading import Thread

tc, tr = None, None
def inGivenBounds(x, y, x0, x1, y0, y1):
	xBound = x1 >= x and x0 <= x 
	yBound = y1 >= y and y0 <= y
	return xBound and yBound


def startDisplayCarving(cWidth, cHeight, data):
	# finds the number of seams carved in each direction and 
	# intialize the number of seams to be carved and how much has been doen 
	# starts two threads: one for carving in the back, the other for redrawing the canvas 
	verticalCarve = data.uncarved.size[0] - cWidth - 1
	horizontalCarve = data.uncarved.size[1] - cHeight - 1
	data.carving = data.uncarved
	data.seamsToBeCarved = abs(verticalCarve) + abs(horizontalCarve)
	data.seamCarvingPercent, data.seamsCurrentlyCarved = 0, 0
	threadCarve = Thread(target = processCarve, args=(data, verticalCarve, horizontalCarve))
	threadRedraw = Thread(target = displayCarvingRedrawAll, args = (data.canvas, data))
	data.redrawnImg = Image.new(data.editedImage.mode, data.editedImage.size)
	data.redrawnImgTk = ImageTk.PhotoImage(data.redrawnImg, master = data.canvas)
	global tc, tr
	tc, tr = threadCarve, threadRedraw
	threadRedraw.start()
	threadCarve.start()

def displayCarvingMousePressed(event, data):
	# changes image displayed on screen to the one with seams drawn on when 
	# user clicks on image 
	if data.seamCarvingPercent >= 100:
		imCarvedX, imCarvedY = data.carved.size
		imX0, imX1 = data.imageX-imCarvedX/2, data.imageX+imCarvedX/2
		imY0, imY1 = data.imageY-imCarvedY/2, data.imageY+imCarvedY/2
		if inGivenBounds(event.x, event.y, imX0, imX1, imY0, imY1):
			data.imageToDisplay = data.redrawnImgTk
	else:
		pass

def displayCarvingMouseReleased(event, data):
	if data.seamCarvingPercent >= 100: 
		if data.imageToDisplay == data.redrawnImgTk:
			data.imageToDisplay = data.carvedTk


def displayCarvingKeyPressed(event, data):
	if data.seamCarvingPercent >= 100:
		if event.keysym == "a":
			tr.join()
			data.mode = "carving"
	pass


def processCarve(data, verticalCarve, horizontalCarve):
	# Carving vertically first 
	# if image has never been carved, carve until reach right dimensions 
	if verticalCarve != 0:
		if len(data.verticalCarvedMemo) == 0:
			imageToCarve = data.editedImage
			verticalPixels, verticalSeams = deleteSeams(imageToCarve, verticalCarve, data)

	# if no more to carve then create the redrawn image with the seams 
	# and finish carving 

	if horizontalCarve == 0:
		data.redrawnPixels = redrawImg(verticalPixels, verticalSeams)
		data.redrawnImg.putdata(data.redrawnPixels)
		data.redrawnImgTk = ImageTk.PhotoImage(data.redrawnImg)
		data.verticalCarvedMemo = data.tempMemo
		seamsCarvedMemoize = {}
		data.carved = data.carving
		data.carvedTk = data.carvingTk
		data.imageToDisplay = data.carvedTk


	# Carving horizontally second 
	# similar to how image is carved vertically
	# redraws image accordingly with both horizontal and vertical seams 
	elif horizontalCarve != 0: 
		imageToCarve = data.carving.rotate(90, expand = True)
		horizontalPixels, horizontalSeams = deleteSeams(imageToCarve, horizontalCarve, data)
		data.carving = data.carving.rotate(-90, expand = True)
		data.carvingTk = ImageTk.PhotoImage(data.carving)

		data.carved = data.carving
		data.carvedTk = data.carvingTk
		data.imageToDisplay = data.carvedTk

		if verticalCarve == 0:
			data.redrawnPixels = redrawImg(horizontalPixels, horizontalSeams)
			newRedraw = Image.new(data.uploadedImage.mode, (imageToCarve.size))
			newRedraw.putdata(data.redrawnPixels)
			data.redrawnImg = newRedraw.rotate(-90, expand = True)
			data.redrawnImgTk = ImageTk.PhotoImage(data.redrawnImg)

		else:
			bothRedrawn = bothRedraw(verticalPixels, verticalSeams, horizontalPixels, horizontalSeams)
			data.redrawnPixels = bothRedrawn
			data.redrawImg = Image.new(data.uploadedImage.mode, (len(bothRedrawn[0]), len(bothRedrawn)))
			data.redrawnImg.putdata(convertPixelsToImage(bothRedrawn))
			data.redrawnImgTk = ImageTk.PhotoImage(data.redrawnImg)

	if data.seamCarvingPercent != 100:
		data.seamCarvingPercent = 100

def displayCarvingRedrawAll(canvas, data):
	# draws the percent done carving when the image hasnt finished carving 
	# and then displays either the carved image or the original image with seams 
	if data.seamCarvingPercent < 100:
		t = "%s%% done" % str(data.seamCarvingPercent)
		canvas.create_text(data.width / 2, data.height / 2, text = t, font = ("Helvetica", 30))
	else:
		canvas.create_image(data.imageX, data.imageY, image = data.imageToDisplay)

	