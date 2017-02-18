from tkinter import *
from PIL import Image, ImageTk
from home import * 
from uploaded import *
from crop import * 
from rotate import * 
from carving import *
from displayCarving import * 


def init(data):
    data.pathToOGPic = None
    data.uploaded = False 
    data.mode = "home"
    data.modes = ["home", "uploaded", "crop", "rotate", "carving", "displayCarving"]
    data.helpPng = Image.open("help.png")
    data.helpPng.resize((30, 30))
    data.helpTk = ImageTk.PhotoImage(data.helpPng)
    data.displayHelp = False 
    data.homeHelp = Image.open("home.png")
    data.homeHelpTk = ImageTk.PhotoImage(data.homeHelp)
    data.uploadedHelp = Image.open("uploaded.png")
    data.uploadedHelpTk = ImageTk.PhotoImage(data.uploadedHelp)
    data.restart = False 

    # Home Mode # 
    data.uploadSize = data.width / 5
    data.uploadButtonX, data.uploadButtonY = data.width / 2 - data.uploadSize / 2, 5 * data.height / 8

    # Uploaded Mode # 
    data.uploadedImage = None
    data.displayedImage = None 
    data.editedImage = None
    data.scaleOfPic = 1
    data.resize = None 
    data.imWidth, data.imHeight = None, None 
    data.imDisplayWidth, data.imDisplayHeight = None, None
    data.imageX, data.imageY = data.width / 2, data.height / 2
    data.floater = None 
    data.displayedImageTk = None

    # Crop Mode # 
    data.uncropped = None
    data.uncroppedTk = None 
    data.croppedDimensions = (None, None)
    data.cropped = None 
    data.cropBars = []
    data.cropX0, data.cropX1 = None, None 
    data.cropY0, data.cropY1 = None, None 
    data.cropBarWidth, data.cropBarHeight = 7, 30 
    data.movingBar = False
    data.movingBarDir = None 
    data.verticalMid, data.horizontalMid = None, None 
    data.cropDimensionX, data.cropDimensionY = None, None 

    # Rotate Mode # 
    data.rotateAngle = 0
    data.unrotated = None 

    # Seam Carving # 
    data.uncarved = None 
    data.uncarvedTk = None 
    data.verticalSeams, data.horizontalSeams = 0, 0 
    data.verticalCarvedMemo, data.horizontalCarvedMemo = {}, {}
    data.carvingTk = None 
    data.carveX0, data.carveX1 = None, None 
    data.carveY0, data.carveY1 = None, None 
    data.carved, data.carvedRedrawn = None, None
    data.seamCarvingPercent = 0
    data.seamsToBeCarved, data.seamsCurrentlyCarved = 0, 0 

    # Display Carving Mode # 
    data.carvingCurrent = None 
    data.carvingTk = None 
    data.imageToDisplay = None 
    data.seamsDrawnImg = None 
    data.seamsDrawnImgTk = None 


    data.floatingEditor = None 



def mousePressed(event, data):
    if data.mode == "home":
        homeMousePressed(event, data)
    elif data.mode == "uploaded":
        uploadedMousePressed(event, data)
    elif data.mode == "crop":
        cropMousePressed(event, data)
    elif data.mode == "rotate":
        rotateMousePressed(event, data)
    elif data.mode == "carving":
        carvingMousePressed(event, data)
    elif data.mode == "displayCarving":
        displayCarvingMousePressed(event, data)
    if ((event.x > data.width - 30 and event.x < data.width) and 
    (event.y > 0 and event.y < 30) and 
    (data.mode == "home" or data.mode == "uploaded")):
        data.displayHelp = True 

def mouseReleased(event, data):
    if data.mode == "crop":
        cropMouseReleased(event, data)
    elif data.mode == "carving":
        carvingMouseReleased(event, data)
    elif data.mode == "displayCarving":
        displayCarvingMouseReleased(event, data)
    if data.displayHelp:
        data.displayHelp = False

def mouseInMotion(event, data):
    if data.mode == "crop":
        cropMouseInMotion(event, data)
    elif data.mode == "carving":
        carvingMouseInMotion(event, data)

def keyPressed(event, data):
    if data.mode == "home":
        homeKeyPressed(event, data)
    elif data.mode == "uploaded":
        uploadedKeyPressed(event, data)
    elif data.mode == "crop":
        cropKeyPressed(event, data)
    elif data.mode == "rotate":
        rotateKeyPressed(event, data)
    elif data.mode == "carving":
        carvingKeyPressed(event, data)
    elif data.mode == "displayCarving":
        displayCarvingKeyPressed(event, data)


def timerFired(data):
    if (data.uploaded):
        data.uploaded = False 
        data.mode = "uploaded"
        doUpload(data)
    if data.restart:
        savedPath = data.pathToOGPic
        doUpload(data)
        data.mode = "uploaded"
        data.restart = False

def redrawAll(canvas, data):
    canvas.create_image(data.width - 15, 15, image=data.helpTk)
    if data.mode == "home":
        homeRedrawAll(canvas, data)
    elif data.mode == "uploaded":
        uploadedRedrawAll(canvas, data)
    elif data.mode == "crop":
        cropRedrawAll(canvas, data)
    elif data.mode == "rotate":
        rotateRedrawAll(canvas, data)
    elif data.mode == "carving":
        carvingRedrawAll(canvas, data)
    elif data.mode == "displayCarving":
        displayCarvingRedrawAll(canvas, data)
    if data.displayHelp:
        if data.mode == "home":
            canvas.create_image(data.imageX, data.imageY, image=data.homeHelpTk)
        else:
            canvas.create_image(data.imageX, data.imageY, image=data.uploadedHelpTk)


def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def mouseReleasedWrapper(event, canvas, data):
        mouseReleased(event, data)
        redrawAllWrapper(canvas, data)

    def mouseInMotionWrapper(event, canvas, data):
        mouseInMotion(event, data)
        redrawAllWrapper(canvas, data)

    def mouseEnteredWrapper(event, canvas, data):
        mouseEntered(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds
    root = Tk()
    init(data)
    canvas = Canvas(root, width=data.width, height=data.height)
    data.canvas = canvas
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    root.bind("<ButtonRelease-1>", lambda event: 
                            mouseReleasedWrapper(event, canvas, data))
    root.bind("<B1-Motion>", lambda event:
                            mouseInMotionWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed

run(1000, 800)