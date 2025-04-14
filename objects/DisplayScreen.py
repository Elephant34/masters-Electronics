import tkinter as tk
import logging
logger = logging.getLogger(__name__)


class DisplayScreen(tk.Tk):
    """The root screen object controling the background cue and obstacle setup screen
    """
    def __init__(self, *args, **kwargs):
        """Setup for the root screen object
        """

        tk.Tk.__init__(self, *args, **kwargs)

        # Makes the display fullscreen
        self.attributes("-fullscreen", True)
        # Makes the cursor invisible
        self.config(cursor="none")
        # Names the screen
        self.title("masters_electronics")

        # Gets the width and height
        self.width = self.winfo_screenwidth()
        self.height = self.winfo_screenheight()

        # The main display splitting the screen into left and right rectangles
        self.canvas = ExperimentCanvas(self.width, self.height, self, bg = "white", borderwidth=0, highlightthickness=0)
        self.canvas.pack(fill = "both", expand=True)

class ExperimentCanvas(tk.Canvas):
    """The canvas controling the colour of the left vs right side of the screen
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
        self.left_experiment_rect = self.create_rectangle(0, 0, self.width/2, self.height)
        self.right_experiment_rect = self.create_rectangle(self.width/2, 0, self.width, self.height)
        self.set_experiment_rect_colours("#ff00ff", "#00ffff") # Silly colours to make sure they are overwitten by the experiment

        
        # Makes the rectangles in the middle of each half to make obstacle settup easy
        self.obstalce_rect_size = 200
        self.left_obstalce_rect = self.create_rectangle(
            ((self.width/4)-(self.obstalce_rect_size/2)), 
            ((self.height/2)-(self.obstalce_rect_size/2)),
            ((self.width/4)+(self.obstalce_rect_size/2)), 
            ((self.height/2)+(self.obstalce_rect_size/2))
        )
        self.right_obstalce_rect = self.create_rectangle(
            ((self.width * (3/4))-(self.obstalce_rect_size/2)), 
            ((self.height/2)-(self.obstalce_rect_size/2)),
            ((self.width * (3/4))+(self.obstalce_rect_size/2)), 
            ((self.height/2)+(self.obstalce_rect_size/2))
        )
        self.set_obstacle_colours("#00ff00", "#ffff00") # Silly colours to make it clear if it goes wrong
        self.toggle_obstacle_visibility(False)

        # Pixel to keep the TV from displaying a screensaver
        self.jiggle_state = True
        self.jiggle_timer_ms = 1000
        self.jiggle_rect = self.create_rectangle(
            5,
            5,
            15,
            15,
            fill="orange",
            outline="orange"
        )
        self.jiggle()
    
    def set_experiment_rect_colours(self, left_hex:str, right_hex:str):
        """Sets the rectangle colours

        Args:
            left_hex (str): A colour hex value, will also accept some custom colour strings
            right_hex (str): A colour hex value, will also accept some custom colour strings
        """
        # Ensures the colours are formated correctly
        left_hex = self.match_colour(left_hex)
        right_hex = self.match_colour(right_hex)

        self.itemconfig(self.left_experiment_rect, fill=left_hex, outline=left_hex)
        self.itemconfig(self.right_experiment_rect, fill=right_hex, outline=right_hex)
    
    def set_obstacle_colours(self, left_hex:str, right_hex:str):
        """Sets the obstacle rect colours

        Args:
            left_hex (str): A colour hex value, will also accept some custom colour strings
            right_hex (str): A colour hex value, will also accept some custom colour strings
        """

        # Ensures the colours are formated correctly
        left_hex = self.match_colour(left_hex)
        right_hex = self.match_colour(right_hex)

        self.itemconfig(self.left_obstalce_rect, fill=left_hex, outline=left_hex)
        self.itemconfig(self.right_obstalce_rect, fill=right_hex, outline=right_hex)
    
    def toggle_obstacle_visibility(self, forced_state:bool=None):
        """Switches the visibility of the obstacle setup rectangles

        Args:
            force_state (bool, optional): If the current state of the rect visibilty must be forced use True/False. Defaults to None.
        """

        # If forced state not set toggle the current state
        if forced_state is None:
            self.current_obstacle_visibility = not self.current_obstacle_visibility
        else:
            self.current_obstacle_visibility = forced_state

        # Converts the true and false to string values for the item configurations
        if self.current_obstacle_visibility:
            current_obstacle_state = "normal"
        else:
            current_obstacle_state = "hidden"

        self.itemconfigure(self.left_obstalce_rect, state=current_obstacle_state)
        self.itemconfigure(self.right_obstalce_rect, state=current_obstacle_state)
    
    def match_colour(self, colour:str):
        """Will match specific colour names to hex values.
        This function allows arbirotry colour names in the experimental trials to make experiment clear

        Args:
            colour (str): A colour hex code or string description
        """
        match colour.lower():
            case "dark"|"black":
                colour = "#000000"
            case "light"|"white":
                colour = "#ffffff"
            case pause_colour if(pause_colour in ["orchid2", "cyan2"]): # Special case for pause colours
                colour = colour
            case hex if(hex.startswith("#") and len(hex) == 7):
                colour = colour
            case _:
                logging.info(f"Colour string not recognised and not hex. Returning input: {colour}")
                colour = colour
        
        return colour
    
    def jiggle(self) -> None:
        """Moves the jiggle pixel back and forward to stop the TV from going to sleep
        """
        x_shift = 0 # Ensures a value exists

        if self.jiggle_state:
            x_shift = 50
        else:
            x_shift = -50

        self.move(self.jiggle_rect, x_shift, 0)

        if self.coords(self.jiggle_rect)[0] >= self.width:
            self.jiggle_state = False # Move pixel backwards
        elif self.coords(self.jiggle_rect)[0] <= 0:
            self.jiggle_state = True # Moves pixel forwards

        self.after(self.jiggle_timer_ms, self.jiggle) # Move pixel again after delay


# For testing
if __name__ == "__main__":
    root = DisplayScreen()
    root.mainloop()