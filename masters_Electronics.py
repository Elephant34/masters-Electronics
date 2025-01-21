"""
Title: MBiol Project Electronic Controls
Author: Ambrose Hlustik-Smith
Description: The code controlling the mainloop of the electronics in my masters project
"""
# Generic libraries
# =================
from pathlib import Path
from time import strftime, localtime

# Environment variables setup
# ===========================
from dotenv import dotenv_values
config = dotenv_values(".env")

# Logging setup
# =============
import logging
logger = logging.getLogger(__name__)
# Checks the path exists
Path(config["log_path"]).mkdir(parents=True, exist_ok=True)
if "limitlogs" in config["DEBUG"].lower():
    # Deletes all old log files leaving only latest
    log_files = list(Path(config["log_path"]).glob("*.log"))
    for log in log_files:
        log.unlink()
# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        # Saves log messages to file
        logging.FileHandler(
            Path("{path}/{filename}.log".format(
                path=config["log_path"],
                filename=strftime("%Y%m%d%H%M%S", localtime())
                )
            )
        ),
        # Output log messgaes to console
        logging.StreamHandler()
    ]
)
    
# GPIO
# ====
# Attempts to import GPIO but for laptop testing imports Mock.GPIO instead
try:
    import RPi.GPIO as GPIO
except:
    import Mock.GPIO as GPIO
    logging.warning("Mock.GPIO used. This is probally due to testing but if not here is your problem!")

# Custom objects
# ==============
from objects.DisplayScreen import DisplayScreen


class masters_Electronics:
    """Main class with control over the tunnel electronics
    """

    # List of the experimental trial setups
    EXPERIMENTAL_TRIALS:dict = {
        # Experiment Set 1 (see method notes)
        1: {
            "left_rect": "light",
            "right_rect": "dark",
            "obstacle": "WW"
        },
        2: {
            "left_rect": "dark",
            "right_rect": "light",
            "obstacle": "WW"
        },
        3: {
            "left_rect": "bright",
            "right_rect": "light",
            "obstacle": "BB"
        },
        4: {
            "left_rect": "dark",
            "right_rect": "light",
            "obstacle": "BB"
        },
        # Experiment Set 2 (see method notes)
        5: {
            "left_rect": "light",
            "right_rect": "light",
            "obstacle": "WB"
        },
        6: {
            "left_rect": "light",
            "right_rect": "light",
            "obstacle": "BW"
        },
        7: {
            "left_rect": "dark",
            "right_rect": "dark",
            "obstacle": "WB"
        },
        8: {
            "left_rect": "dark",
            "right_rect": "dark",
            "obstacle": "BW"
        },
    }

    def __init__(self, config):
        """Calls the setup for all necessary objects
        """

        self.config = config
        self.running = False

        # Screen setup
        self.display = DisplayScreen()

        # Data writer setup

        # GPIO setup
        self.setup_gpio()
        self.setup_gpio_callbacks()

        # Keybinds setup
        self.setup_keybinds()

        return

    def setup_gpio(self):
        """Configures the gpio pins
        """
    
    def setup_gpio_callbacks(self):
        """Configures the callbacks to record events and change the experiment setup as needed
        """

    def setup_keybinds(self):
        """Setups keybinds to interact with the program while it's fullscreen
        """

        # Binds Esc key to exit the program
        self.display.bind("<Escape>", lambda e: self.exit_mainloop())

        # Specific debug related keybinds
        if self.config["DEBUG"]:
            # Binds <enter> to rotate experimental setups
            self.display.bind("<Enter>", lambda e: self.next_trial())

    def mainloop(self):
        self.running = True
        while self.running:
            # Keeps the display refreshing
            self.display.update()
        
        self.display.destroy()

        return
    
    def next_trial(self):
        """Randomises the next trial and calls the functions to configure it
        """
        return

    def exit_mainloop(self):
        """Will cause the mainloop to exit safley ensuring all data is saved
        """
        self.running = False

        return



# Mainloop of the electronics
if __name__ == "__main__":
    setup = masters_Electronics(config)
    setup.mainloop()

    if "slowexit" in config["DEBUG"].lower():
        input("Press <Enter> to Exit")

