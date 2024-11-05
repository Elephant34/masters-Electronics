"""
Title: MBiol Project Electronic Controls
Author: Ambrose Hlustik-Smith
Description: The code controlling the mainloop of the electronics in my masters project
"""

import tkinter as tk
from random import randint

class TunnelElectronics:
    """Main class with control over the tunnel electronics
    """

    def __init__(self):
        """Setups the raspberry pi pins and modes to control the physical electronics
        """

        return
    
class TunnelDisplay(tk.Canvas):
    """The display screen used as the background brightness for the zebra finches
    """

    def __init__(self, width:int, height:int, *args, **kwargs):
        """Setsup the display canvas to show bright and dark background brightness

        Args:
            width (int): Screen Width
            height (int): Screen Height
        """
        tk.Canvas.__init__(self, *args, **kwargs)

        self.width = width
        self.height = height

        self.left_rect = self.create_rectangle(0, 0, self.width/2, self.height, fill="#ff00ff", outline="#ff00ff")
        self.right_rect = self.create_rectangle(self.width/2, 0, self.width, self.height, fill="#00ffff", outline="#00ffff")

        

        

def exit_mainloop():
    """Safley closes the program
    """
    # Gets the running variable from the 
    global running

    running = False

    return

DEBUG = False

# Mainloop of the electronics
if __name__ == "__main__":
    print("MBiol Electronics Running. Press ESC to exit")
    # Setups the display screen
    root = tk.Tk()
    root.attributes("-fullscreen", True)

    # Gets the width and height to draw the rectangles on screen
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()

    # The main display class showing the left and right rectangles
    td = TunnelDisplay(width, height, root, bg = "white", borderwidth=0, highlightthickness=0)
    td.pack(fill = "both", expand=True)

    # Controls the program mainloops
    running = True

    # Allows the application to be exited on <Escape> key press
    root.bind("<Escape>", lambda e: exit_mainloop())

    # Mainloop
    while running:
        # Updates the window, this is instead of me calling root.mainloop as that would freeze the other code
        root.update()
    
    # Exists the screen
    root.destroy()
    
    # If I need to see the consol output I can set debug to true to view it after exit
    if DEBUG:
        input("Debug mode on: leaving consol open until enter key pressed")
