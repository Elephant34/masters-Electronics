import logging
logger = logging.getLogger(__name__)
import tkinter as tk

class DisplayScreen(tk.Tk):
    """The root screen object controling the background cue
    """
    def __init__(self, *args, **kwargs):
        """Setup for the root screen object
        """

        tk.Tk.__init__(self, *args, **kwargs)

        # Makes the display fullscreen
        self.attributes("-fullscreen", True)

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
        # Default colours are just for testing
        self.left_rect = self.create_rectangle(0, 0, self.width/2, self.height)
        self.right_rect = self.create_rectangle(self.width/2, 0, self.width, self.height)
        self.set_rect_colours("dark", "light")
        
    
    def set_rect_colours(self, left_hex:str, right_hex:str):
        """Sets the rectangle colours

        Args:
            left_hex (str): A colour hex value, will also accept some custom colour strings
            right_hex (str): A colour hex value, will also accept some custom colour strings
        """
        # Ensures the colours are formated correctly
        left_hex = self.match_colour(left_hex)
        right_hex = self.match_colour(right_hex)

        self.itemconfig(self.left_rect, fill=left_hex, outline=left_hex)
        self.itemconfig(self.right_rect, fill=right_hex, outline=right_hex)
    
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

# For testing
if __name__ == "__main__":
    root = DisplayScreen()
    root.mainloop()