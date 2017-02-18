from tkinter import filedialog

def homeMousePressed(event, data):
	# asks for upload and uploads the image into the app  
	left, right = data.uploadButtonX, data.uploadButtonX + data.uploadSize
	up, down = data.uploadButtonY, data.uploadButtonY + data.uploadSize
	if ((event.x <= right and event.x >= left) and 
		(event.y >= up and event.y <= down)):
		pathName = filedialog.askopenfile(initialdir = "/",title = "Select file",
	filetypes = (("jpeg files","*.jpg"),("png files", "*.png"),("all files","*.*")))
		data.pathToOGPic = pathName.name
		data.uploaded = True 

def homeKeyPressed(event, data):
	pass 

def homeRedrawAll(canvas, data):
	# home screen
	x0, x1 = data.uploadButtonX, data.uploadButtonX + data.uploadSize
	y0, y1 = data.uploadButtonY, data.uploadButtonY + data.uploadSize
	canvas.create_rectangle(x0, y0, x1, y1)
	tx, ty = (x1 + x0) / 2, (y0 + y1) / 2
	canvas.create_text(tx, ty, text="Upload an image", anchor = "center")
	tix, tiy = data.width / 2, data.height - 2 * data.uploadSize
	canvas.create_text(tix, tiy, text="Live Seam Carving App", anchor = "center", font = ("Helvetica", 50))
