from pathlib import Path
from time import strftime, localtime
from time import time as current_epoch

class DataWriter:
    """Class containing the methods to record the data of bird flights
    """

    def __init__(self, data_path:Path):
        """Opens the days data file

        Args:
            data_path (Path): Path leading to the data folder for the file to be writen to
        """

        self.data_file = data_path / "{file_name}.txt".format(file_name = strftime("%Y%m%d", localtime()))

        self.data_file.mkdir(parents=True, exist_ok=True)

    def record_gate_crossed(self, gate_id:int):
        """_summary_

        Args:
            gate_id (int): _description_
        """

        print(current_epoch())