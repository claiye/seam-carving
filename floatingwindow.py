from tkinter import *

class App(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.floater = FloatingWindow(self)


class FloatingWindow(Toplevel):
    def __init__(self, data, *args, **kwargs):
        Toplevel.__init__(self, *args, **kwargs)
        self.overrideredirect(True)
        self.num = 1

        self.grip = Label(self, bitmap="gray25")
        self.grip.pack(side="top", fill="y")

        self.crop = Label(self, text="Crop")
        self.crop.pack(fill="y", expand=True)

        self.rotate = Label(self, text="Rotate")
        self.rotate.pack(fill="y", expand=True)
        self.rotate.bind("<ButtonPress-1>", self.toRotate)

        self.carve = Label(self, text="Carve")
        self.carve.pack(fill="y", expand=True)

        self.save = Label(self, text="Save")
        self.save.pack(fill="y", expand=True)

        self.revert = Label(self, text="Revert")
        self.revert.pack(fill="y", expand=True)

        self.uploadNew = Label(self, text="Upload")
        self.uploadNew.pack(fill="y", expand=True)

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
        data.mode = "rotate"
        print("rotate")


app=App()
app.mainloop()