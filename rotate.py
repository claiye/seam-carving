from PIL import ImageTk
from tkinter import *
import PIL.Image as Image

def rotateMousePressed(event, data):
	doRotate(data, 90)

def rotateKeyPressed(event, data):
	if (event.keysym == "Left"):
		doRotate(data, 90)
	elif (event.keysym == "Right"):
		doRotate(data, -90)
	elif (event.keysym == "Return"):
		finishRotate(data)

def rotateRedrawAll(canvas, data):
	canvas.create_image(data.imageX, data.imageY, image=data.displayedImageTk)
	canvas.pack()

def doRotate(data, angle):
	# uses data.rotateAngle to keep track of how many times the image has been rotated 
	# and how it should display on the screen 
	# resizes image to fit as necessary 
	data.rotateAngle += angle 
	if abs(data.rotateAngle) > 360:
		data.rotateAngle %= 360 
	data.displayedImage = data.editedImage.rotate(data.rotateAngle, resample=Image.BICUBIC, expand=True)
	data.imDisplayWidth, data.imDisplayHeight = data.displayedImage.size
	if data.scaleOfPic < 1: 
		if data.imDisplayWidth > data.width or data.imDisplayHeight > data.height: 
			unscaled = max(data.imDisplayWidth / data.width, data.imDisplayHeight / data.height)
			scaleDown = 1 / unscaled 
			data.scaleOfPic = scaleDown 
			data.imDisplayWidth, data.imDisplayHeight = int(data.imDisplayWidth * scaleDown), int(data.imDisplayHeight * scaleDown)
		elif data.imDisplayWidth < data.width and data.imDisplayHeight < data.height: 
			unscaled = max(data.imDisplayWidth / data.width, data.imDisplayHeight / data.height)
			scaleUp = 1 / unscaled 
			data.scaleOfPic = scaleUp 
			data.imDisplayWidth, data.imDisplayHeight = int(data.imDisplayWidth * scaleUp), int(data.imDisplayHeight * scaleUp)
	data.displayedImage = data.displayedImage.resize((data.imDisplayWidth, data.imDisplayHeight))
	data.displayedImageTk = ImageTk.PhotoImage(data.displayedImage)

def finishRotate(data):
	# finalizes rotation, updates variables in data so that when the user enters 
	# crop or carve they will be editting the rotated image, not the original one 
	data.editedImage = data.editedImage.rotate(data.rotateAngle, resample=Image.BICUBIC, expand=True)
	data.uncropped, data.uncarved = data.editedImage, data.editedImage
	data.uncroppedTk, data.uncarvedTk = ImageTk.PhotoImage(data.uncropped), ImageTk.PhotoImage(data.uncarved)
	
	data.displayedImage = data.editedImage
	data.imDisplayWidth, data.imDisplayHeight = data.displayedImage.size
	data.displayedImageTk = ImageTk.PhotoImage(data.displayedImage)
	data.carveX0, data.carveX1 = data.width / 2 - data.imDisplayWidth / 2, data.width / 2 + data.imDisplayWidth / 2
	data.carveY0, data.carveY1 = data.height / 2 - data.imDisplayHeight / 2, data.height / 2 + data.imDisplayHeight / 2
	data.cropX0, data.cropX1 = (data.width - data.imDisplayWidth) / 2, data.width - (data.width - data.imDisplayWidth) / 2 
	data.cropY0, data.cropY1 = (data.height - data.imDisplayHeight) / 2, data.height - (data.height - data.imDisplayHeight) / 2 
	data.mode = "uploaded"