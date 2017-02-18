from PIL import ImageTk


def cropMousePressed(event, data):
	# if the mouse clicked inside a bar, then there is a moving bar 
	if inVerticalBar(event.x, event.y, data) != False:
		data.movingBarDir = "V"
		data.movingBar = inVerticalBar(event.x, event.y, data) 
	elif inHorizontalBar(event.x, event.y, data) != False:
		data.movingBarDir = "H"
		data.movingBar = inHorizontalBar(event.x, event.y, data) 


def cropMouseInMotion(event, data):
	# moves the bar set in data.movingBar according to where the mouse drags it 
	def inBounds():
		marginX, marginY = (data.width - data.uncropped.size[0]) / 2, (data.height - data.uncropped.size[1]) / 2
		return ((event.x < data.width - marginX and event.x > marginX) and 
				(event.y  < data.height - marginY and event.y > marginY))
	if data.movingBar != None and inBounds():
		if data.movingBarDir == "V":
			if data.movingBar == "x0":
				data.cropX0 = event.x 
			elif data.movingBar == "x1":
				data.cropX1 = event.x 
			data.horizontalMidCrop = int((data.cropX1 + data.cropX0) / 2 )
		elif data.movingBarDir == "H":
			if data.movingBar == "y0":
				data.cropY0 = event.y
			elif data.movingBar == "y1":
				data.cropY1 = event.y
			data.verticalMidCrop = int((data.cropY1 + data.cropY0) / 2)

def cropMouseReleased(event, data):
	# once mouse is released, no more moving bar 
	data.movingBar = None
	data.movingBarDir = None 

def findRealDimensions(data):
	# finds the real dimensions of the image according to the user's cropping 
	# live updates 
	if data.scaleOfPic != 1:
		scaledX, scaledY = data.cropX1 - data.cropX0, data.cropY1 - data.cropY0
		return (int(scaledX / data.scaleOfPic), int(scaledY / data.scaleOfPic))
	return (int(data.cropX1 - data.cropX0), int(data.cropY1 - data.cropY0))

def findRealCorners(data):
	# used to find where to crop the image 
	# once the user finishes 
	uncroppedW, uncroppedY = data.uncropped.size 
	cx0, cx1 = data.cropX0-(data.width-uncroppedW)/2, data.cropX1-(data.width-uncroppedW)/2
	cy0, cy1 = data.cropY0-(data.height-uncroppedY)/2, data.cropY1-(data.height-uncroppedY)/2
	if data.scaleOfPic != 1:
		cx0, cx1 = cx0 / data.scaleOfPic, cx1 / data.scaleOfPic
		cy0, cy1 = cy0 / data.scaleOfPic, cy1 / data.scaleOfPic
	return ((cx0, cy0, cx1, cy1))

def inVerticalBar(x, y, data):
	# checks if (x, y) is inside a vertical bar 
	cw, ch = data.cropBarWidth, data.cropBarHeight 
	w, h = data.width / 2, data.verticalMidCrop
	x0, x1 = data.cropX0, data.cropX1
	x0bound = (x < x0 + cw / 2 and x > x0 - cw / 2)
	x1bound = (x < x1 + cw / 2 and x > x1 - cw / 2)
	y = (y < h + ch / 2 and y > h - ch / 2)
	if y:
		if x0bound: return "x0"
		elif x1bound: return "x1"
	return False

def inHorizontalBar(x, y, data):
	# checks if (x, y) is inside a horizontal bar 
	cw, ch = data.cropBarWidth, data.cropBarHeight 
	w, h = data.horizontalMidCrop, data.height / 2
	y0, y1 = data.cropY0, data.cropY1
	x = (x < w + cw / 2 and x > w - cw / 2)
	y0bound = (y < y0 + ch / 2 and y > y0 - ch / 2)
	y1bound = (y < y1 + ch / 2 and y > y1 - ch / 2)
	if x:
		if y0bound: return "y0"
		elif y1bound: return "y1"
	return False

def cropKeyPressed(event, data):
	if (event.keysym == "Return"):
		finishCrop(data)

def cropRedrawAll(canvas, data):
	data.canvas.create_image(data.imageX, data.imageY, image=data.uncroppedTk)
	cw, ch = data.cropBarWidth, data.cropBarHeight 
	w, h = data.horizontalMidCrop, data.verticalMidCrop

	def createVerticalBar(x):
		canvas.create_rectangle(x-cw/2, h-ch/2, x+cw/2, h+ch/2, fill="black")

	def createHorizontalBar(y):
		canvas.create_rectangle(w-ch/2, y-cw/2, w+ch/2, y+cw/2, fill="black")

	# draws crop bars and crop box 
	createVerticalBar(data.cropX0)
	createVerticalBar(data.cropX1)
	createHorizontalBar(data.cropY0)
	createHorizontalBar(data.cropY1)

	canvas.create_line(data.cropX0, data.cropY0, data.cropX1, data.cropY0, fill="black")
	canvas.create_line(data.cropX0, data.cropY1, data.cropX1, data.cropY1, fill="black")
	canvas.create_line(data.cropX0, data.cropY0, data.cropX0, data.cropY1, fill="black")
	canvas.create_line(data.cropX1, data.cropY0, data.cropX1, data.cropY1, fill="black")

	# display dimensions that crop bar is showing when it is moving 
	if data.movingBar != None: 
		if data.movingBarDir == "V":
			horizontalDimensions = findRealDimensions(data)[0]
			if data.movingBar == "x0":
				canvas.create_text(data.cropX0-cw/2 - 15, h, text=str(horizontalDimensions))
			elif data.movingBar == "x1":
				canvas.create_text(data.cropX1+cw/2 + 15, h, text=str(horizontalDimensions))
		if data.movingBarDir == "H":
			verticalDimensions = findRealDimensions(data)[1]
			if data.movingBar == "y0":
				canvas.create_text(w, data.cropY0-cw/2-15, text=str(verticalDimensions))
			elif data.movingBar == "y1":
				canvas.create_text(w, data.cropY1+cw/2+15, text=str(verticalDimensions))

def finishCrop(data):	
	# crops the image according to how the user positined the crop box 
	# sets relevant variables in data to the cropped image in order to edit the cropped image 
	# in other modes instead of the original one 
	data.cropped = data.uncropped.crop(findRealCorners(data))
	data.editedImage, data.uncarved, data.carved = data.cropped, data.cropped, data.cropped
	data.displayedImage = data.editedImage
	data.imDisplayWidth, data.imDisplayHeight = data.displayedImage.size
	if (data.width - 20 < data.imDisplayWidth or data.height - 20 < data.imDisplayHeight): 
		unscaled = max(data.imDisplayWidth / (data.width - 20), data.imDisplayHeight / (data.height - 20))
		scaleDown = 1 / unscaled
		data.scaleOfPic = scaleDown 
		data.imDisplayWidth, data.imDisplayHeight = int(data.imDisplayWidth * scaleDown), int(data.imDisplayHeight * scaleDown)
		data.displayedImage = data.displayedImage.resize((data.imDisplayWidth, data.imDisplayHeight))
	data.uncarved = data.displayedImage
	data.displayedImageTk = ImageTk.PhotoImage(data.displayedImage)
	data.uncarvedTk, data.carvingTk = data.displayedImageTk, data.displayedImageTk
	# changed so that the carving box is not bigger than the cropped image 
	data.carveX0, data.carveX1 = data.width / 2 - data.imDisplayWidth / 2, data.width / 2 + data.imDisplayWidth / 2
	data.carveY0, data.carveY1 = data.height / 2 - data.imDisplayHeight / 2, data.height / 2 + data.imDisplayHeight / 2
	data.mode = "uploaded"
