import tkinter as tk

from config import BACKGROUND_COLOR, TEXT_COLOR_PRIMARY
from colour import Color
from screens.device_selection_screen import DeviceSelectionScreen


# Fade out over ~1 sec at 60 fps
class SplashScreen(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        self.background_image = []

        for i in range(12):
            self.background_image.append(tk.PhotoImage(file='assets/splash_bg_{}.png'.format(i)))

        self.background_label = tk.Label(parent, image=self.background_image[0])
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.pack()
        self.animation = 0
        self.animate()

    def animate(self):
        if self.animation > 11:
            self.pack_forget()
            self.destroy()

            DeviceSelectionScreen(self.parent).tkraise()
            return

        self.background_label.configure(image=self.background_image[self.animation])
        self.background_label.image = self.background_image[self.animation]
        self.animation += 1
        self.after(100, self.animate)
