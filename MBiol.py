"""
Title: MBiol Project Electronic Controls
Author: Ambrose Hlustik-Smith
Description: The code controlling the mainloop of the electronics in my masters project
"""

# Load librarys
import tkinter as tk
import random
from dotenv import dotenv_values
# Attempts to import GPIO but for laptop testing imports Mock.GPIO instead
try:
    import RPi.GPIO as GPIO
except:
    import Mock.GPIO as GPIO

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
        self.left_rect = self.create_rectangle(0, 0, self.width/2, self.height, fill="#ffffff", outline="#ffffff")
        self.right_rect = self.create_rectangle(self.width/2, 0, self.width, self.height, fill="#000000", outline="#000000")

        
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

    return trials_list
        

def exit_mainloop():
    """Safley closes the program
    """
    # Gets the running variable from global scope
    global running

    # Sets to false to cause the program to exit
    running = False

    return

def next_trial():
    return

config = dotenv_values(".env")

# List of the experimental trial setups
EXPERIMENTAL_TRIALS:dict = {
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
# Boolean or a string flags containing specifics of what is required
# Options:  True- will use a set seed and allow skipping of trials using the enter key; this is true with all debug options
#           "slowEscape"- will not exit the consol when the window is closed until the enter key is pressed
DEBUG = config["DEBUG"]

# Number of each trial that should be run as part of each balanced random set
# This will be multiplies by the number of experimental trials
TRIAL_SET_N:int = 100

# Loop variables
running = True # Controls when to exit the mainloop
trials = [] # List of trials to run

# Mainloop of the electronics
if __name__ == "__main__":

    print("MBiol Electronics Running. Press ESC to exit")

    # Display Setup
    # =============

    # Setups the root
    root = tk.Tk()
    root.attributes("-fullscreen", True)

    # Gets the width and height to draw the rectangles on screen
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()

    # The main display class showing the left and right rectangles
    td = TunnelDisplay(width, height, root, bg = "white", borderwidth=0, highlightthickness=0)
    td.pack(fill = "both", expand=True)

    # Key Binds
    # =========

    # Allows Esc key to exit the program
    root.bind("<Escape>", lambda e: exit_mainloop())
    # Allows rotation of trials during debugging
    if DEBUG: root.bind("<Enter>", lambda e: next_trial())

    # For debugging purposes set the random seed
    if DEBUG:
        random.seed = 0
        
    # Mainloop
    while running:
        # If the list of trials is empty, generate a new one
        if not trials:
            trials = generate_trial_list()

        # Updates the window, this is instead of me calling root.mainloop as that would freeze the other code
        root.update()
    
    # Exists the screen
    root.destroy()
    
    # If I need to see the consol output I can set debug to "slow exit" to view it after exit
    try:
        if "slowexit" in DEBUG.lower():
            input("Debug mode on: leaving consol open until enter key pressed")
    except AttributeError:
        pass
