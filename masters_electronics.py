"""
Title: MBiol Project Electronic Controls
Author: Ambrose Hlustik-Smith
Description: The code controlling the mainloop of the electronics in my masters project
"""
# Generic libraries
# =================
import random
from pathlib import Path
from time import strftime, localtime

from waiting import wait

# Environment variables setup
# ===========================
from dotenv import dotenv_values
config = dotenv_values(".env")
assert len(config) >= 5, ".env file does not have correct arguments" # Quick check that a .env file has been added

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
from objects.DataWriter import DataWriter


class masters_Electronics:
    """Main class with control over the tunnel electronics
    """

    def __init__(self, config):
        """Calls the setup for all necessary objects
        """

        self.config = config
        self.running = None
        self.change_obstacle_state = False

        if "setseed" in self.config["DEBUG"].lower(): random.seed(0) # Debugging with reproducability

        # Experiment variables
        self.set_experiment_variables()

        # Screen setup
        self.display = DisplayScreen()

        # Data writer setup
        self.data_writer = DataWriter(Path(self.config["data_path"]))

        # GPIO setup
        self.setup_gpio()
        self.setup_gpio_callbacks()

        # Keybinds setup
        self.setup_keybinds()

        # Gets the experimenter to set the obstacle start position and randomises the starting trial
        self.current_trial = self.EXPERIMENT_BLANK
        self.change_obstacle()

        return

    def set_experiment_variables(self):
        """Loads the variables used to control the experiment
        """
        self.EXPERIMENT_BLANK = {
            "trial_id": None,
            "left_bg": None,
            "right_bg": None,
            "left_fg": None,
            "right_fg": None
        }

        # List of the experimental trial setups
        # Foreground and background use different terminology to avoid confusion
        self.EXPERIMENTAL_TRIALS:dict = {
            # Experiment Set 1 (see method notes)
            1: {
                "trial_id": 1,
                "left_bg": "light",
                "right_bg": "dark",
                "left_fg": "white",
                "right_fg": "white"
            },
            2: {
                "trial_id": 2,
                "left_bg": "dark",
                "right_bg": "light",
                "left_fg": "white",
                "right_fg": "white"
            },
            3: {
                "trial_id": 3,
                "left_bg": "light",
                "right_bg": "dark",
                "left_fg": "black",
                "right_fg": "black"
            },
            4: {
                "trial_id": 4,
                "left_bg": "dark",
                "right_bg": "light",
                "left_fg": "black",
                "right_fg": "black"
            },
            # Experiment Set 2 (see method notes)
            5: {
                "trial_id": 5,
                "left_bg": "light",
                "right_bg": "light",
                "left_fg": "white",
                "right_fg": "black"
            },
            6: {
                "trial_id": 6,
                "left_bg": "dark",
                "right_bg": "dark",
                "left_fg": "white",
                "right_fg": "black"
            },
            7: {
                "trial_id": 7,
                "left_bg": "light",
                "right_bg": "light",
                "left_fg": "black",
                "right_fg": "white"
            },
            8: {
                "trial_id": 8,
                "left_bg": "dark",
                "right_bg": "dark",
                "left_fg": "black",
                "right_fg": "white"
            },
        }

        # Ensures that all experiment trials have the needed keys
        for trial in self.EXPERIMENTAL_TRIALS.values():
            if not trial.keys() == self.EXPERIMENT_BLANK.keys():
                try:
                    logging.warning(
                        "Experiment {trial_id} keys do not match the experiment blank".format(
                            trial_id = trial["trial_id"]
                        )
                    )
                except (KeyError, AttributeError):
                    logging.warning(
                        "Unknown experiment keys do not match the experiment blank. Please check experiment keys and relaunch"
                    )
                
                self.exit_mainloop()

        return
        
    
    def generate_trial_state(self) -> dict:
        """Generates a random valid trial based on the obstalce state. The current trial must have an obstacle position set

        Returns:
            dict: Returns an random valid trial state
        """
        
        valid_trials = []
        for trial_setup in list(self.EXPERIMENTAL_TRIALS.values()):
            if self.current_obstacle["left_fg"].lower() == trial_setup["left_fg"].lower(): # Checks the left obstacle colour
                if self.current_obstacle["right_fg"].lower() == trial_setup["right_fg"].lower(): # Checks the right obstacle colour
                    valid_trials.append(trial_setup)
        return random.choice(valid_trials)


    def setup_gpio(self):
        """Configures the gpio pins
        """

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(
            [config["right_gate_pin"], config["left_gate_pin"], config["entrance_gate_pin"]],
            GPIO.IN,
            pull_up_down=GPIO.PUD_UP
        )
    
    def setup_gpio_callbacks(self):
        """Configures the callbacks to record events and change the experiment setup as needed
        """

        GPIO.add_event_detect(
            int(config["entrance_gate_pin"]),
            GPIO.FALLING,
            callback=lambda x: self.gate_crossed("entrance"),
            bouncetime=10
        )
        GPIO.add_event_detect(
            int(config["left_gate_pin"]),
            GPIO.FALLING,
            callback=lambda x: self.gate_crossed("left"),
            bouncetime=10
        )
        GPIO.add_event_detect(
            int(config["right_gate_pin"]),
            GPIO.FALLING,
            callback=lambda x: self.gate_crossed("right"),
            bouncetime=10
        )

    def setup_keybinds(self):
        """Setups keybinds to interact with the program while it's fullscreen
        """

        # Binds Esc key to exit the program
        self.display.bind("<Escape>", lambda e: self.exit_mainloop())

        # Binds Space key to pause
        self.display.bind("<space>", lambda e: self.toggle_pause())

        # Binds "c" to change the obstacle rotation
        self.display.bind("c", lambda e: self.change_obstacle())

        # Specific debug related keybinds
        if self.config["DEBUG"]:
            # Binds <tab> to rotate experimental setups
            self.display.bind("<Tab>", lambda e: self.next_trial())

            # Binds 1,2,3 keys to mimic gate interaction
            self.display.bind("1", lambda e: self.gate_crossed("enterance"))
            self.display.bind("2", lambda e: self.gate_crossed("right"))
            self.display.bind("3", lambda e: self.gate_crossed("left"))

    def mainloop(self):
        """Enters the mainloop to update the graphics and run the experiment
        """

        # Checks for error conditions before starting mainloop
        if self.running is None:
            self.running = True # By default will start running
        else:
            # If running has been toggled before the program starts exit immediatly
            self.running = False
            logging.warning("Program exiting before starting")

        while self.running:
            # Keeps the display refreshing
            self.display.update()

        # Methods to ensure the experiment exits without failure
        self.display.destroy()
        setup.data_writer.safe_exit()

        return
    
    def next_trial(self):
        """Randomises the next trial and calls the functions to configure it
        Will only do so if the program is not paused
        """
        if self.paused:
            logging.warning("Attempt to switch trial inturrputed by experiment pause")
            return
        
        self.current_trial = self.generate_trial_state()
        logging.info("Changed trial to: {}".format(self.current_trial))

        self.set_main_rects()
        return

    def set_main_rects(self, left_rect=None, right_rect=None):
        """Sets the colours of the rectangles. By default this will be to the current trial state
        """
        if not left_rect: left_rect = self.current_trial["left_bg"]
        if not right_rect: right_rect = self.current_trial["right_bg"]

        self.display.canvas.set_experiment_rect_colours(left_rect, right_rect)

        return

    def exit_mainloop(self):
        """Will cause the mainloop to exit safley ensuring all data is saved
        """
        self.change_obstacle_state = False
        self.running = False

        return

    def toggle_pause(self, pause_state:bool=None):
        """Toggles pause state of experiment. When paused both screens will be pink and the obstacle roations can be changed.
        Data will not be recorded when the experiment is paused.

        Args:
            pause_state (bool, optional): When provided the pause state will explicity change to this value. Defaults to None to toggle paused state
        """
        
        if pause_state:
            self.paused = pause_state
        else:
            self.paused = not self.paused
        
        if self.change_obstacle_state:
            logging.info("Pause change overwritten- please confirm obstacle change with 'c' to unpause")
            self.paused = True
            return
        

        if self.paused:
            logging.info("Program paused")
            self.set_main_rects("orchid2", "cyan2")
        else:
            self.set_main_rects()
            logging.info("Program resumed")

        return

    def change_obstacle(self):
        """Generates the next obstacle position and places it on screen for the experimenter to roate the obstical around
        """

        if self.change_obstacle_state:
            # When "c" is pressed again will confirm the obstacle has changed
            self.change_obstacle_state = False
            self.display.canvas.toggle_obstacle_visibility()
            logging.info(
                "Changed obstacle to {left}, {right}".format(
                    left = self.current_trial["left_fg"],
                    right = self.current_trial["right_fg"]
                )
            )
            # Sets a valid trial state when the program first starts to remove an exception being raised
            self.current_trial = self.generate_trial_state()

            self.toggle_pause(False)
            self.next_trial()
            return
        
        self.toggle_pause(True)

        self.change_obstacle_state = True

        # As the obstacle states are evenly distributed between the trials will set obstacle state to that of a random trial
        random_trial = random.choice(list(self.EXPERIMENTAL_TRIALS.values()))

        self.current_obstacle = {
            "left_fg":random_trial["left_fg"],
            "right_fg": random_trial["right_fg"]
        }
        self.display.canvas.set_obstacle_colours(
            self.current_obstacle["left_fg"],
            self.current_obstacle["right_fg"]
        )
        self.display.canvas.toggle_obstacle_visibility()

        return

    def gate_crossed(self, gate_id):
        """Callback for when the entry gate is crossed to write data and change experimental trial if necessary
        """

        # Only write data when the program is not paused
        if not self.paused:
            self.data_writer.record_gate_crossed(gate_id, self.current_trial["trial_id"])
        else:
            # Adds a warning log if the gates are crossed while the program is paused and data is not written
            logging.warning(
                "Gate {gate_id} crossed in trial state {trial_id} while paused".format(
                    gate_id = gate_id,
                    trial_id = self.current_trial["trial_id"]
                )
            )



# Mainloop of the electronics
if __name__ == "__main__":
    logging.info("Program started")
    setup = masters_Electronics(config)

    # Waits until the obstacle state has been set before starting mainloop
    logging.info("Waiting for obstacle setup to be completed")
    wait(lambda: setup.change_obstacle_state is False, sleep_seconds=0.1, on_poll=lambda:setup.display.update())

    setup.mainloop()
    logging.info("Mainloop exited")

    if "slowexit" in config["DEBUG"].lower():
        input("Press <Enter> to Exit")
    
    logging.info("Program exited successfully- goodbye!")

