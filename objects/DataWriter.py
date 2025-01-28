from pathlib import Path
from time import strftime, localtime
from time import time as current_epoch
import csv

import logging
logger = logging.getLogger(__name__)

class DataWriter:
    """Class containing the methods to record the data of bird flights
    """

    def __init__(self, data_path:Path):
        """Opens the days data file

        Args:
            data_path (Path): Path leading to the data folder for the file to be writen to
        """

        self.data_blank = {
            "gate_id": None,
            "epoch_time": None,
            "trial_id": None
        }

        # Creates one data file per day, this may need adjusting depending on the RAM space of the pi and how much data is written
        self.data_file = data_path / "{file_name}.csv".format(
            file_name = strftime("%Y%m%d", localtime())
        )

        data_file_exists = self.data_file.exists() # Checks if the file already exists

        # Creates the parent file path if it does not exist
        self.data_file.parent.mkdir(parents=True, exist_ok=True)

        # Opens the data file
        self.open_file = self.data_file.open("a", newline="")

        # Allows for writing csv data to the file
        self.data_writer = csv.DictWriter(
            self.open_file,
            fieldnames=list(self.data_blank.keys())
        )
        # If the file did not already exist write the header
        if not data_file_exists:
            self.data_writer.writeheader()

        logging.info("Data writer open at file: {}".format(str(self.data_file.absolute())))

    def record_gate_crossed(self, gate_id:int, trial_id:int):
        """Write to csv file the gate_id and the time crossed

        Args:
            gate_id (int): The individual ID of the gate interacted with
            trial_id (int): The id number of the current trial setup
        """

        data = self.data_blank
        data["gate_id"] = gate_id
        data["epoch_time"] = current_epoch()
        data["trial_id"] = trial_id

        self.data_writer.writerow(data)

        self.open_file.flush()

        logging.info("Gate crossed: {}".format(data))
    
    def safe_exit(self):
        """Ensures the data file is closed and information is written to memory
        """

        logging.info("Data file closed")
        self.open_file.close()