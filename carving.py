from displayCarving import startDisplayCarving
# refer ot crop.py for comments on each function 

def carvingMousePressed(event, data):
	if inVerticalBar(event.x, event.y, data) != False:
		data.movingBarDir = "V"
		data.movingBar = inVerticalBar(event.x, event.y, data) 
	elif inHorizontalBar(event.x, event.y, data) != False:
		data.movingBarDir = "H"
		data.movingBar = inHorizontalBar(event.x, event.y, data) 

def carvingMouseInMotion(event, data):
	def inBounds():
		marginX, marginY = (data.width - data.uncarved.size[0]) / 2, (data.height - data.uncarved.size[1]) / 2
		return ((event.x < data.width - marginX and event.x > marginX) and 
				(event.y  < data.height - marginY and event.y > marginY))
	if data.movingBar != None and inBounds():
		if data.movingBarDir == "V":
			if data.movingBar == "x0":
				data.carveX0 = event.x 
			elif data.movingBar == "x1":
				data.carveX1 = event.x 
			data.horizontalMidCarve = int((data.carveX1 + data.carveX0) / 2 )
		elif data.movingBarDir == "H":
			if data.movingBar == "y0":
				data.carveY0 = event.y
			elif data.movingBar == "y1":
				data.carveY1 = event.y
			data.verticalMidCarve = int((data.carveY1 + data.carveY0) / 2)

def carvingMouseReleased(event, data):
	data.movingBar = None
	data.movingBarDir = None 

def findRealDimensions(data):
	if data.scaleOfPic != 1:
		scaledX, scaledY = data.carveX1 - data.carveX0, data.carveY1 - data.carveY0
		return (int(scaledX / data.scaleOfPic), int(scaledY / data.scaleOfPic))
	return (int(data.carveX1 - data.carveX0), int(data.carveY1 - data.carveY0))

def findRealCorners(data):
	uncarvedW, uncarvedY = data.uncarved.size 
	cx0, cx1 = data.carveX0-(data.width-uncarvedW)/2, data.carveX1-(data.width-uncarvedW)/2
	cy0, cy1 = data.carveY0-(data.height-uncarvedY)/2, data.carveY1-(data.height-uncarvedY)/2
	if data.scaleOfPic != 1:
		cx0, cx1 = cx0 / data.scaleOfPic, cx1 / data.scaleOfPic
		cy0, cy1 = cy0 / data.scaleOfPic, cy1 / data.scaleOfPic
	return ((cx0, cy0, cx1, cy1))

def inVerticalBar(x, y, data):
	cw, ch = data.cropBarWidth, data.cropBarHeight 
	w, h = data.width / 2, data.verticalMidCarve
	x0, x1 = data.carveX0, data.carveX1
	x0bound = (x < x0 + cw / 2 and x > x0 - cw / 2)
	x1bound = (x < x1 + cw / 2 and x > x1 - cw / 2)
	y = (y < h + ch / 2 and y > h - ch / 2)
	if y:
		if x0bound: return "x0"
		elif x1bound: return "x1"
	return False

def inHorizontalBar(x, y, data):
	cw, ch = data.cropBarWidth, data.cropBarHeight 
	w, h = data.horizontalMidCarve, data.height / 2
	y0, y1 = data.carveY0, data.carveY1
	x = (x < w + cw / 2 and x > w - cw / 2)
	y0bound = (y < y0 + ch / 2 and y > y0 - ch / 2)
	y1bound = (y < y1 + ch / 2 and y > y1 - ch / 2)
	if x:
		if y0bound: return "y0"
		elif y1bound: return "y1"
	return False

def carvingKeyPressed(event, data):
	if (event.keysym == "Return"):
		finishCarve(data)

def finishCarve(data):
	data.mode = "displayCarving"
	carveXDimensions, carveYDimensions = findRealDimensions(data)
	# starts carving 
	startDisplayCarving(carveXDimensions, carveYDimensions, data)

def carvingRedrawAll(canvas, data):
	data.canvas.create_image(data.imageX, data.imageY, image=data.uncarvedTk)
	cw, ch = data.cropBarWidth, data.cropBarHeight 
	w, h = data.horizontalMidCarve, data.verticalMidCarve

	def createVerticalBar(x):
		canvas.create_rectangle(x-cw/2, h-ch/2, x+cw/2, h+ch/2, fill="black")

	def createHorizontalBar(y):
		canvas.create_rectangle(w-ch/2, y-cw/2, w+ch/2, y+cw/2, fill="black")

	createVerticalBar(data.carveX0)
	createVerticalBar(data.carveX1)
	createHorizontalBar(data.carveY0)
	createHorizontalBar(data.carveY1)

	canvas.create_line(data.carveX0, data.carveY0, data.carveX1, data.carveY0, fill="black")
	canvas.create_line(data.carveX0, data.carveY1, data.carveX1, data.carveY1, fill="black")
	canvas.create_line(data.carveX0, data.carveY0, data.carveX0, data.carveY1, fill="black")
	canvas.create_line(data.carveX1, data.carveY0, data.carveX1, data.carveY1, fill="black") 

	if data.movingBar != None: 
		if data.movingBarDir == "V":
			horizontalDimensions = findRealDimensions(data)[0]
			if data.movingBar == "x0":
				canvas.create_text(data.carveX0-cw/2 - 15, h, text=str(horizontalDimensions))
			elif data.movingBar == "x1":
				canvas.create_text(data.carveX1+cw/2 + 15, h, text=str(horizontalDimensions))
		if data.movingBarDir == "H":
			verticalDimensions = findRealDimensions(data)[1]
			if data.movingBar == "y0":
				canvas.create_text(w, data.cropY0-cw/2-15, text=str(verticalDimensions))
			elif data.movingBar == "y1":
				canvas.create_text(w, data.cropY1+cw/2+15, text=str(verticalDimensions))
