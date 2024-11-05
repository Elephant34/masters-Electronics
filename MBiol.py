"""
Title: MBiol Project Electronic Controls
Author: Ambrose Hlustik-Smith
Description: The code controlling the mainloop of the electronics in my masters project
"""

import tkinter as tk
import random

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

        # Makes the rectangles which will be configured to white or black depending on the trial
        # Default colours are just for testing
        self.left_rect = self.create_rectangle(0, 0, self.width/2, self.height, fill="#ff00ff", outline="#ff00ff")
        self.right_rect = self.create_rectangle(self.width/2, 0, self.width, self.height, fill="#00ffff", outline="#00ffff")

        
def generate_trial_list() -> list:
    """Generates a list of trials with the same number of each trial but displayed in a random order.
    This allows for balanced randomness where each trial is random but equal numbers of each trial occur

    Returns:
        list: Ordered list of trials to be run
    """
    global TRIAL_SET_N
    global EXPERIMENTAL_TRIALS

    trial_names = EXPERIMENTAL_TRIALS.keys()

    trials_list = list(trial_names) * TRIAL_SET_N
    random.shuffle(trials_list)

    print(trials_list.count(1))

    return trials_list
        

def exit_mainloop():
    """Safley closes the program
    """
    # Gets the running variable from global scope
    global running

    # Sets to false to cause the program to exit
    running = False

    return

# List of the experimental trial setups
EXPERIMENTAL_TRIALS = {
    # Experiment Set 1 (see method notes)
    1: {
        "left_rect": "bright",
        "right_rect": "dark",
        "obstacle": "WW"
    },
    2: {
        "left_rect": "dark",
        "right_rect": "bright",
        "obstacle": "WW"
    },
    3: {
        "left_rect": "bright",
        "right_rect": "dark",
        "obstacle": "PP"
    },
    4: {
        "left_rect": "dark",
        "right_rect": "bright",
        "obstacle": "PP"
    },
    # Experiment Set 2 (see method notes)
    5: {
        "left_rect": "bright",
        "right_rect": "bright",
        "obstacle": "WP"
    },
    6: {
        "left_rect": "bright",
        "right_rect": "bright",
        "obstacle": "PW"
    },
    7: {
        "left_rect": "dark",
        "right_rect": "dark",
        "obstacle": "WP"
    },
    8: {
        "left_rect": "dark",
        "right_rect": "dark",
        "obstacle": "PW"
    },
}


# Allows for a debug mode during testing
DEBUG:bool = False

# Number of each trial that should be run as part of each balanced random set
TRIAL_SET_N:int = 100

# Mainloop of the electronics
if __name__ == "__main__":
    print("MBiol Electronics Running. Press ESC to exit")

    if DEBUG:
        random.seed = 0

    # Setups the display screen
    root = tk.Tk()
    root.attributes("-fullscreen", True)

    # Gets the width and height to draw the rectangles on screen
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()

    # The main display class showing the left and right rectangles
    td = TunnelDisplay(width, height, root, bg = "white", borderwidth=0, highlightthickness=0)
    td.pack(fill = "both", expand=True)

    # Loop variables
    running = True # Controls when to exit the mainloop
    trials = [] # List of trials to run

    # Allows the application to be exited on <Escape> key press
    root.bind("<Escape>", lambda e: exit_mainloop())

    # Mainloop
    while running:
        # If the list of trials is empty, generate a new one
        if not trials:
            trials = generate_trial_list()

        # Updates the window, this is instead of me calling root.mainloop as that would freeze the other code
        root.update()
    
    # Exists the screen
    root.destroy()
    
    # If I need to see the consol output I can set debug to true to view it after exit
    if DEBUG:
        input("Debug mode on: leaving consol open until enter key pressed")
