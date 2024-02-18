from typing import Optional
import pandas as pd
import pathlib
import numpy as np
from snirf import Snirf


class Storm:
    def __init__(self, snirf_fname):

        self.snirf_fname = snirf_fname
        self.old_sourc_loc = None
        self.old_detc_loc = None
        self.storm_fname = None
        self.storm_data = None
        pass

    def check_storm_fname(self, storm_fname):
        # check if storm_fname is a path
        if type(storm_fname) == pathlib.WindowsPath:
            storm_fname = str(storm_fname)
        # check if storm_fname is a string
        if type(storm_fname) != str:
            raise TypeError("storm_fname must be a string")
        # check if storm_fname is a txt file
        if not storm_fname.endswith('.txt'):
            raise ValueError("Not a txt file.")
        # check if storm_fname exists
        if not pathlib.Path(storm_fname).exists():
            raise ValueError("storm_fname does not exist")
        # check if storm_fname is empty
        if storm_fname is None:
            raise ValueError("storm_fname cannot be empty")

    def storm(self, storm_fname, user_input: bool = False):
        """
    Update SNIRF probe locations with STORM data.
    If the STORM data is valid and the update is successful, the method prints a confirmation message.

    Parameters:
        storm_fname (str): The file path of the STORM.txt file.
        user_input (bool): The user can choose to view the updated source and detector optode locations or they can skip the preview . Default is set to False.

    Raises:
        ValueError: If the STORM file does not exist.

    Updates:
        snirf_detc_loc (numpy.ndarray): Updates the detector optode locations with the STORM data.
        snirf_sourc_loc (numpy.ndarray): Updates the source optode locations with the STORM data.
        old_detc_loc (numpy.ndarray): Stores the original detector optode locations if not already stored.
        old_sourc_loc (numpy.ndarray): Stores the original source optode locations if not already stored.
        """
        # check storm_fname input
        self.check_storm_fname(storm_fname)
        # check if user_input is an integer
        if type(user_input) != int:
            raise TypeError("user_input must be an integer")
        # check if user_input is 0 or 1
        if user_input != 0 and user_input != 1:
            raise ValueError("user_input must be either 0 or 1")
        # check if user_input is empty
        if user_input is None:
            raise ValueError("user_input cannot be empty")

        try:
            data = Snirf(rf'{self.snirf_fname}', 'r+')
            data_backup = data
            self.snirf_detc_loc = data.nirs[0].probe.detectorPos3D[:, :]
            self.snirf_sourc_loc = data.nirs[0].probe.sourcePos3D[:, :]
            self.set_storm_file(storm_fname)
            self.snirf_with_storm_prob(data)

            print("Your snirf file has been updated.")

            if user_input == True:
                place = Snirf(rf'{self.snirf_fname}', 'r+')
                print("The updated sources' locations: \n")
                print(place.nirs[0].probe.sourcePos3D[:, :])
                print("The updated detectors' locations: \n")
                print(place.nirs[0].probe.detectorPos3D[:, :])
            else:
                pass

        except OSError as error:
            print(error)
            data_backup.save(rf'{self.snirf_fname}')
            print('We took care of it, please try again')

    def set_storm_file(self, storm_fname: str):
        """
        Set the STORM file for STORM analysis.

        Parameters:
            storm_fname (str): The file path of the STORM.txt file.

        Updates:
            storm_fname (pathlib.Path): The file path of the STORM.txt file.
        """
        self.storm_fname = pathlib.Path(storm_fname)
        self.storm_data = Storm.read_storm_to_DF(storm_fname)

    def read_storm_to_DF(storm_fname):
        """
        Read the STORM data from the provided STORM.txt file and return it as a pandas DataFrame.

        Parameters:
            storm_fname (str): The file path of the STORM.txt file.

        Returns:
            pd.DataFrame: The STORM data loaded from the file.
        """
        storm_data = pd.read_csv(storm_fname, delim_whitespace=True, index_col=0, header=None)
        storm_data.index.name = None
        return storm_data

    ###### Processing STORM file ######

    def storm_prob(self):
        """
        Extract the STORM source and detector optode locations from the STORM data.

        Returns:
            Tuple[pandas.DataFrame, pandas.DataFrame]: A tuple containing the STORM source and detector optode locations as pandas DataFrames.

        Raises:
            ValueError: If the STORM data does not contain valid source or detector optode locations.
        """

        # Extract the STORM source and detector optode locations based on the index pattern

        storm_sourc_loc = self.storm_data[self.storm_data.index.astype(str).str.contains(r'^s\d+$')]
        storm_detc_loc = self.storm_data[self.storm_data.index.astype(str).str.contains(r'^d\d+$')]

        # Check if the extracted STORM data contains valid source and detector optode locations

        if len(storm_sourc_loc) == 0 or len(storm_detc_loc) == 0:
            raise ValueError("Invalid STORM data. Check your STORM file.")

        return storm_sourc_loc, storm_detc_loc

    ###### validation STORM file ######

    def is_storm_valid(self):
        """
        Validate the STORM data to ensure it contains valid source and detector optode locations.

        Raises:
            ValueError: If the STORM data contains NaN values or any integer columns, or if the number of STORM source or detector optode locations
                    does not match the number of optode locations in the SNIRF data."""

        # Get the STORM source and detector optode locations

        storm_sourc_loc, storm_detc_loc = self.storm_prob()

        # Check if the STORM data contains NaN values

        if storm_sourc_loc.isnull().values.any() or storm_detc_loc.isnull().values.any():
            raise ValueError("Invalid STORM data. Check your STORM file.")

        # Check if any column in the STORM data is of integer data type

        if any(storm_sourc_loc.dtypes == int or storm_detc_loc.dtypes == int):
            raise ValueError("STORM data contains integer column(s). All columns should have float data type.")

        # Check if the number of STORM source or detector optode locations matches the number in the SNIRF data
        num_storm_sourc = np.shape(storm_sourc_loc)
        num_storm_detc = np.shape(storm_detc_loc)

        num_snirf_sourc = np.shape(self.snirf_sourc_loc)[0]
        num_snirf_detc = np.shape(self.snirf_detc_loc)[0]

        if num_snirf_sourc != num_storm_sourc or num_snirf_detc != num_storm_detc:
            raise ValueError("Invalid STORM data. Check your STORM file.")

    def snirf_with_storm_prob(self, data):
        """
        Update the SNIRF data with STORM optode locations and save the modified data back to the original SNIRF file.

        Parameters:
            data (Snirf): The SNIRF data to be updated with STORM optode locations.

        Updates:
            data (Snirf): The updated SNIRF data.
        """
        # Validate the STORM data
        try:
            self.is_storm_valid()
        except ValueError as error:
            print(error)
        # check if data is a Snirf object
        if type(data) != Snirf:
            raise TypeError("data must be a Snirf object")
        # check if data is empty
        if data is None:
            raise ValueError("data cannot be empty")

        storm_sourc_loc, storm_detc_loc = self.storm_prob()

        # Store the old optode locations if not already stored
        if self.old_sourc_loc is None:
            self.old_sourc_loc = np.copy(data.nirs[0].probe.sourcePos3D)
        if self.old_detc_loc is None:
            self.old_detc_loc = np.copy(data.nirs[0].probe.detectorPos3D)

        # Update the SNIRF file with the STORM data
        data.nirs[0].probe.sourcePos3D[:, :] = storm_sourc_loc
        data.nirs[0].probe.detectorPos3D[:, :] = storm_detc_loc

        data.save(rf'{self.snirf_fname}')
        data.close()

    def get_old_probe_locations(self):
        """
        Get the original probe locations before updating with STORM data.

        Returns:
            Tuple[numpy.ndarray or None, numpy.ndarray or None]: A tuple containing the original source and detector optode locations.
        """

        return self.old_sourc_loc, self.old_detc_loc

    def euclidean_dist(self):
        """
        Calculate the Euclidean distance between the optode locations before and after the STORM data update.

        Returns:
            Tuple[numpy.ndarray, numpy.ndarray]: A tuple containing the Euclidean distances between the updated and original
                source optode locations and the updated and original detector optode locations."""

        # Retrieve the original source and detector optode locations
        self.old_sourc_loc, self.old_detc_loc = self.get_old_probe_locations()

        # Retrieve the current STORM source and detector optode locations
        storm_sourc_loc, storm_detc_loc = self.storm_prob()

        # Compute the Euclidean distances between the updated and original optode locations
        sourc_euclidean_dist = np.linalg.norm(storm_sourc_loc - self.old_sourc_loc, axis=1)
        detc_euclidean_dist = np.linalg.norm(storm_detc_loc - self.old_detc_loc, axis=1)

        return sourc_euclidean_dist, detc_euclidean_dist

    def invalid_sourc(self, thresh: int = 20):
        """
        Identify the source optode locations that have a Euclidean distance greater than or equal to the specified threshold
        from the original source optode locations.

        Parameters:
            thresh (float): The threshold value for the Euclidean distance. Default is set to 20 mm.

        Returns:
            numpy.ndarray: A NumPy array containing the source optode locations that crossed the Euclidean distance threshold, and therefore are off-place and invalid.
            """
        # check if thresh is an integer
        if type(thresh) != int:
            raise TypeError("thresh must be an integer")
        # check if thresh is positive
        if thresh < 0:
            raise ValueError("thresh must be a positive integer")
        # check if thresh is greater than 30 (the maximum distance between two optodes) if so, give a warning
        if thresh > 30:
            print(
                "Warning: thresh is greater than 30 mm. This is the maximum distance between two adjacent optodes. Please check your input.")

        # Obtain the STORM source optode locations and the Euclidean distances
        storm_sourc_loc = self.storm_prob()[0]
        sourc_euclidean_dist = self.euclidean_dist()[0]
        sourc_euclidean_dist = np.array(sourc_euclidean_dist)

        # Filter the STORM source optode locations based on the Euclidean distance threshold
        invalid_sourc = storm_sourc_loc[sourc_euclidean_dist >= thresh]

        return invalid_sourc

    def invalid_detec(self, thresh: int = 20):
        """
        Identify the detector optode locations that have a Euclidean distance greater than or equal to the specified threshold
        from the original detector optode locations.

        Parameters:
            thresh (float): The threshold value for the Euclidean distance. Default is set to 10.

        Returns:
            numpy.ndarray: A NumPy array containing the detector optode locations that crossed the Euclidean
              distance threshold, and are therefore off-place and invalid.
        """
        # check if thresh is an integer
        if type(thresh) != int:
            raise TypeError("thresh must be an integer")
        # check if thresh is positive
        if thresh < 0:
            raise ValueError("thresh must be a positive integer")
        # check if thresh is greater than 30 (the maximum distance between two optodes) if so, give a warning
        if thresh > 30:
            print(
                "Warning: thresh is greater than 30 mm. This is the maximum distance between two adjacent optodes. Please check your input.")

        # Obtain the STORM detector optode locations and the Euclidean distances
        storm_detc_loc = self.storm_prob()[1]
        detc_euclidean_dist = self.euclidean_dist()[1]
        detc_euclidean_dist = np.array(detc_euclidean_dist)

        # Filter the STORM detector optode locations based on the Euclidean distance threshold
        invalid_detec = storm_detc_loc[detc_euclidean_dist >= thresh]
        return invalid_detec

    