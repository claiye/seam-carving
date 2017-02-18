from PIL import ImageTk
import PIL.Image
from tkinter import * 
from tkinter import filedialog



def doUpload(data):
    # save uploaded picture 
    data.uploadedImage = PIL.Image.open(data.pathToOGPic)
    # initialize edited, uncropped, and uncarved images as uploaded pic
    # change how the picture is displayed based on how big it is (and scale down appropriately)
    # displayedImage is what is shown, a representation of the real edited picture 
    data.displayedImage = data.uploadedImage
    data.imWidth, data.imHeight = data.uploadedImage.size
    data.imDisplayWidth, data.imDisplayHeight = data.imWidth, data.imHeight
    if data.imWidth > (data.width - 20) or data.imHeight > (data.height - 20): 
            unscaled = max(data.imWidth / (data.width - 20), data.imHeight / (data.height - 20))
            scaleDown = 1 / unscaled
            data.scaleOfPic = scaleDown 
            data.imDisplayWidth, data.imDisplayHeight = int(data.imWidth * scaleDown), int(data.imHeight * scaleDown)
            data.displayedImage = data.displayedImage.resize((data.imDisplayWidth, data.imDisplayHeight))
    data.displayedImageTk = ImageTk.PhotoImage(data.displayedImage)

    data.editedImage, data.uncropped, data.uncarved, data.carved = data.uploadedImage, data.uploadedImage, data.uploadedImage, data.uploadedImage
    data.editedDisplay, data.uncroppedDisplay, data.uncarvedDisplay = data.displayedImage, data.displayedImage, data.displayedImage
    data.editedTK, data.uncroppedTk, data.uncarvedTk, data.carvingTk = data.displayedImageTk, data.displayedImageTk, data.displayedImageTk, data.displayedImageTk

    # updates where the cropping bars start out in carving and cropping mode 
    data.cropX0, data.cropX1 = (data.width - data.imDisplayWidth) / 2, data.width - (data.width - data.imDisplayWidth) / 2 
    data.cropY0, data.cropY1 = (data.height - data.imDisplayHeight) / 2, data.height - (data.height - data.imDisplayHeight) / 2 
    data.carveX0, data.carveX1, data.carveY0, data.carveY1 = data.cropX0, data.cropX1, data.cropY0, data.cropY1
    data.verticalMidCrop, data.horizontalMidCrop = data.height /  2, data.width / 2 
    data.verticalMidCarve, data.horizontalMidCarve = data.height /  2, data.width / 2 

    data.cropDimensionX, data.cropDimensionY = data.imWidth, data.imHeight
    if not data.restart:
        data.floatingEditor = FloatingWindow(data)


def uploadedMousePressed(event, data):
    pass
 

def uploadedKeyPressed(event, data):
    if (event.keysym == "c"):
        data.mode = "crop"
    elif (event.keysym in "rR"):
        data.mode = "rotate"
    elif (event.keysym in "sS"):
        data.mode = "carving"


def uploadedRedrawAll(canvas, data):
    canvas.create_image(data.imageX, data.imageY, image=data.displayedImageTk)
    canvas.pack()




# taken from Stack Overflow 
# http://stackoverflow.com/questions/4055267/python-tkinter-mouse-drag-a-window-without-borders-eg-overridedirect1

class FloatingWindow(Toplevel):
    def __init__(self, data, *args, **kwargs):
        Toplevel.__init__(self, *args, **kwargs)
        self.overrideredirect(True)
        self.data = data

        self.grip = Label(self, bitmap="gray25")
        self.grip.pack(side="top", fill="y")

        self.crop = Label(self, text="Crop")
        self.crop.pack(fill="y", expand=True)
        self.crop.bind("<ButtonPress-1>", self.toCrop)

        self.rotate = Label(self, text="Rotate")
        self.rotate.pack(fill="y", expand=True)
        self.rotate.bind("<ButtonPress-1>", self.toRotate)

        self.carve = Label(self, text="Carve")
        self.carve.pack(fill="y", expand=True)
        self.carve.bind("<ButtonPress-1>", self.toCarving)

        self.save = Label(self, text="Save")
        self.save.pack(fill="y", expand=True)
        self.save.bind("<ButtonPress-1>", self.toSave)

        self.revert = Label(self, text="Revert")
        self.revert.pack(fill="y", expand=True)
        self.revert.bind("<ButtonPress-1>", self.revertToOriginal)

        self.uploadNew = Label(self, text="Upload")
        self.uploadNew.pack(fill="y", expand=True)
        self.uploadNew.bind("<ButtonPress-1>", self.uploadNewImage)

        self.grip.bind("<ButtonPress-1>", self.StartMove)
        self.grip.bind("<ButtonRelease-1>", self.StopMove)
        self.grip.bind("<B1-Motion>", self.OnMotion)

    def StartMove(self, event):
        self.x = event.x
        self.y = event.y

    def StopMove(self, event):
        self.x = None
        self.y = None

    def OnMotion(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry("+%s+%s" % (x, y))

    def toRotate(self, event):
        self.data.mode = "rotate"

    def toCrop(self, event):
        self.data.mode = "crop"

    def toCarving(self, event):
        self.data.mode = "carving"

    def revertToOriginal(self, event):
        self.data.restart = True 

    def uploadNewImage(self, event):
        self.data.pathToOGPic = None 
        self.data.mode = "home"
        self.data.floatingEditor = None 
        self.destroy()

    def toSave(self, event):
        savePath = filedialog.asksaveasfilename(initialdir = "/", title = "Choose a folder to save it in", defaultextension=".jpg")
        self.data.carved.save(savePath)



