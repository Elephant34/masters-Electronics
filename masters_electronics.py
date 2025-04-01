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

from waiting import wait, ANY

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
# Attempts to import GPIO, but for laptop testing imports Mock.GPIO instead
try:
    import RPi.GPIO as GPIO # type: ignore
except:
    import Mock.GPIO as GPIO
    logging.warning("Mock.GPIO used. This is probally due to laptop testing but if not this is a problem!")

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

        # Basic control variables
        # =======================
        self.config = config

        self.running = None

        self.change_obstacle_state = False

        self.entrance_gate_crossed = False
        self.exit_gate_crossed = False

        # Debugging random reproducibility
        # ================================
        if "setseed" in self.config["DEBUG"].lower(): random.seed(0)

        # Experiment constants
        # ====================
        self.set_experiment_constants()
        logging.info("Set experiment constants")

        # Screen setup
        # ============
        self.display = DisplayScreen()
        logging.info("Set display screen")

        # Data writer setup
        # =================
        self.data_writer = DataWriter(Path(self.config["data_path"]))
        logging.info("Set data writer")

        # GPIO setup
        # ==========
        self.setup_gpio()
        self.setup_gpio_callbacks()
        logging.info("Set GPIO pins")

        # Keybinds setup
        # ==============
        self.setup_keybinds()
        logging.info("Set keybinds")

        # Obstacle setup
        # ==============
        self.current_trial = self.EXPERIMENT_BLANK
        self.change_obstacle()
        logging.info("Set up of obstacle positioning")

        logging.info("Setup complete")

        return

    def set_experiment_constants(self):
        """Loads the constants used to control the experiment
        """

        # A blank dictionary of a model experimental trial
        self.EXPERIMENT_BLANK = {
            "trial_id": None,
            "left_bg": None,
            "right_bg": None,
            "left_fg": None,
            "right_fg": None
        }

        # List of dictionaries of valid obstacle positions
        self.VALID_OBSTACLES = [
            {
                "left_fg": "white",
                "right_fg": "white"
            },
            {
                "left_fg": "black",
                "right_fg": "black"
            },
            {
                "left_fg": "white",
                "right_fg": "black"
            },
            {
                "left_fg": "black",
                "right_fg": "white"
            }
        ]

        # List of the experimental trial setups
        # Foreground and background use different colour terminology to avoid confusion in the logs, but this is otherwise unncessary
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

        # Error checking
        # ==============
        # As the above constants are set by the experimentor, check as far as possible they are valid

        # Ensures that all experiment trials match the keys of the blank
        for trial in self.EXPERIMENTAL_TRIALS.values():
            if not trial.keys() == self.EXPERIMENT_BLANK.keys():
                try:
                    logging.warning(
                        "Trial {trial_id} keys do not match the experiment blank".format(
                            trial_id = trial["trial_id"]
                        )
                    )
                except (KeyError, AttributeError):
                    logging.warning(
                        "Unknown experiment keys do not match the experiment blank. Please check experiment keys and relaunch"
                    )
                
                # Exits the program immedietly if the experimental trials is not formatted correctly
                self.exit_mainloop()
                return
        
        # Checks that all the trials have valid obstacle states
        for trial in self.EXPERIMENTAL_TRIALS.values():
            if(not any(
                valid_obstacle["left_fg"] == trial["left_fg"] and 
                valid_obstacle["right_fg"] == trial["right_fg"]
                for valid_obstacle in self.VALID_OBSTACLES
            )):
                logging.warning(
                    "Trial {trial_id} keys do not match any valid obstacle state".format(
                        trial_id = trial["trial_id"]
                    )
                )
                # Exits the program immedietly if the experimental trials is not formatted correctly
                self.exit_mainloop()
                return
        
        logging.info("Experiment Trials List: {}".format(self.EXPERIMENTAL_TRIALS))

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
            [self.config["right_gate_pin"], self.config["left_gate_pin"], self.config["entrance_gate_pin"]],
            GPIO.IN,
            pull_up_down=GPIO.PUD_UP
        )
    
    def setup_gpio_callbacks(self):
        """Configures the callbacks to record gate crossing events and change the experiment setup as needed
        """

        GPIO.add_event_detect(
            int(self.config["entrance_gate_pin"]),
            GPIO.FALLING,
            callback=lambda x: self.gate_crossed("entrance"),
            bouncetime=10
        )
        GPIO.add_event_detect(
            int(self.config["left_gate_pin"]),
            GPIO.FALLING,
            callback=lambda x: self.gate_crossed("left"),
            bouncetime=10
        )
        GPIO.add_event_detect(
            int(self.config["right_gate_pin"]),
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

        # Binds "c" to change the obstacle rotation (pressing c again will confirm the change)
        self.display.bind("c", lambda e: self.change_obstacle())

        # Specific debug related keybinds
        if self.config["DEBUG"]:
            # Binds <tab> to rotate experimental setups
            self.display.bind("<Tab>", lambda e: self.next_trial())

            # Binds 1,2,3 keys to mimic gate interaction
            self.display.bind("1", lambda e: self.gate_crossed("entrance"))
            self.display.bind("2", lambda e: self.gate_crossed("right"))
            self.display.bind("3", lambda e: self.gate_crossed("left"))
    
    def next_trial(self):
        """Randomises the next trial and configures configure it
        Will only do so if the program is not paused
        """
        if self.paused:
            logging.info("Attempt to switch trial inturrputed by experiment pause")
            return
        
        self.current_trial = self.generate_trial_state()
        logging.info("Changed trial to: {}".format(self.current_trial))

        self.set_main_rects()
        return

    def set_main_rects(self, left_rect=None, right_rect=None):
        """Sets the colours of the rectangles. By default this will be to the current trial state
        """

        # If specific colours are not given uses the current trial colours
        if not left_rect: left_rect = self.current_trial["left_bg"]
        if not right_rect: right_rect = self.current_trial["right_bg"]

        self.display.canvas.set_experiment_rect_colours(left_rect, right_rect)

        return

    def exit_mainloop(self):
        """Will cause the mainloop to exit safley ensuring all data is saved
        """
        self.running = False

        try:
            self.display.destroy()
        except AttributeError:
            pass

        return

    def toggle_pause(self, pause_state:bool=None):
        """Toggles pause state of experiment. When paused the screen changes to vivid colours to make the state obvious.
        Data will not be recorded when the experiment is paused.

        Args:
            pause_state (bool, optional): When provided the pause state will explicity change to this value. Defaults to None to toggle paused state
        """
        if self.change_obstacle_state:
            logging.info("Please confirm obstacle change with 'c' to unpause. Pause change inturrputed")
            return
        
        # Toggles pause if pause_state not explict
        if pause_state is None:
            self.paused = not self.paused
        else:
            self.paused = pause_state
        

        if self.paused:
            # Resets the gate crossing states- a bird might be half way through the setup when paused
            self.reset_gate_crossing("all")

            logging.info("Program paused")
            self.set_main_rects("orchid2", "cyan2") # Sets bright pause colours
        else:
            self.set_main_rects() # Sets the background back to the current trial state
            logging.info("Program resumed")

        return

    def change_obstacle(self):
        """Generates the next obstacle position and places it on screen for the experimenter to roate the obstical around
        """

        # Checks if this is the second "c" press to confirm obstacle rotation change
        if self.change_obstacle_state:
            self.change_obstacle_state = False

            # Resets the gate crossing states- a bird might have been halfway through when paused
            self.reset_gate_crossing("all")

            # Hides the obstacle setting rectangles
            self.display.canvas.toggle_obstacle_visibility()

            logging.info(
                "Changed obstacle to {left}, {right}".format(
                    left = self.current_trial["left_fg"],
                    right = self.current_trial["right_fg"]
                )
            )

            # Sets a valid trial state, this is only important when the program frist starts
            self.current_trial = self.generate_trial_state()

            # Resumes the program and moves to the next valid trial
            self.toggle_pause(False)
            self.next_trial()
            return
        
        self.toggle_pause(True)

        # Used to determin if this is setup or confirmation keypress
        self.change_obstacle_state = True

        # Picks a random obstacle state
        random_trial = random.choice(self.VALID_OBSTACLES)

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

            # Record if a gate set has been crossed
            if gate_id.lower() == "entrance":
                try:
                    self.display.after_cancel(self.entrance_reset)
                except AttributeError:
                    pass
                self.entrance_gate_crossed = True
                self.entrance_reset = self.display.after(int(self.config["crossing_timeout"]), self.reset_gate_crossing, gate_id.lower())
            if gate_id.lower() in ["right", "left"]:
                try:
                    self.display.after_cancel(self.exit_reset)
                except AttributeError:
                    pass
                self.exit_gate_crossed = True
                self.exit_reset = self.display.after(int(self.config["crossing_timeout"]), self.reset_gate_crossing, gate_id.lower())
            

            # Records the data to the CSV file
            self.data_writer.record_gate_crossed(gate_id, self.current_trial["trial_id"])

            # Automatic trial rotation
            if self.entrance_gate_crossed and self.exit_gate_crossed:
                self.reset_gate_crossing("all")

                self.next_trial()
        else:
            # Adds a warning log if the gates are crossed while the program is paused and data is not written
            logging.warning(
                "Gate {gate_id} crossed in trial state {trial_id} while paused".format(
                    gate_id = gate_id,
                    trial_id = self.current_trial["trial_id"]
                )
            )
    
    def reset_gate_crossing(self, gate_id):
        """Resets the gate crossed variables to faulse
        """
        

        if gate_id.lower() == "entrance":
            try:
                self.display.after_cancel(self.entrance_reset)
                logging.info("Gate {} timeout".format(gate_id))
            except AttributeError:
                pass
        
            self.entrance_gate_crossed = False
        elif gate_id.lower() in ["right", "left"]:
            try:
                self.display.after_cancel(self.exit_reset)
                logging.info("Gate {} timeout".format(gate_id))
            except AttributeError:
                pass

            self.exit_gate_crossed = False
        elif gate_id.lower() == "all":
            logging.info("Gate {} timeout".format(gate_id))
            try:
                self.display.after_cancel(self.entrance_reset)
            except AttributeError:
                pass
            try:
                self.display.after_cancel(self.exit_reset)
            except AttributeError:
                pass
        
            self.entrance_gate_crossed = False
            self.exit_gate_crossed = False
        else:
            logging.warning(
                "Attempted to reset unknown gate \"{}\". Please check gate_id or code!".format(gate_id)
            )

        return


# Mainloop of the electronics
if __name__ == "__main__":
    logging.info("Program started")
    setup = masters_Electronics(config)

    # Waits until the obstacle state has been set before starting mainloop
    logging.info("Waiting for obstacle setup to be completed")
    wait(
        ANY([
            lambda: setup.change_obstacle_state is False,
            lambda: setup.running is False # Will ensure a clean exit even before setup completed
        ]),
        sleep_seconds=0.1,
        on_poll=lambda:setup.display.update()
    )

    # Checks for error conditions before starting mainloop
    if setup.running is None:
        setup.running = True # By default will start running
    else:
        # If running has been toggled before the program starts exit immediatly
        setup.running = False
        logging.warning("Program exiting before starting")

    # If the program should start then enter mainloop
    if setup.running:
        setup.display.mainloop()

    # Methods to ensure the experiment exits without failure
    setup.data_writer.safe_exit()
    logging.info("Mainloop exited")

    if "slowexit" in config["DEBUG"].lower():
        input("Press <Enter> to Exit")
    
    logging.info("Program exited successfully- goodbye!")

