import pandas as pd
import numpy as np


def calculate_pairwise_distance(data):
    """
    Calculate the pairwise distance between keypoints in each frame.

    This function takes a DataFrame containing keypoint coordinates and computes the pairwise distance
    between keypoints for each frame. The resulting distance data is returned as a DataFrame.

    Parameters:
        data (pd.DataFrame): DataFrame containing keypoint coordinates.
            The DataFrame should have columns for 'frame', 'person', and keypoints in the format 'KP_i_x' and 'KP_i_y',
            where 'i' represents the keypoint index.

    Returns:
        pd.DataFrame: DataFrame containing the pairwise distance data for each frame.
            The column names represent the pairs of keypoints for which the distance is calculated.
            The row index represents the frame number.
    """
    keypoints = [col for col in data.columns if col.endswith('_x')]
    num_keypoints = len(keypoints)
    num_frames = len(data)
    column_names = [f'{keypoints[i].replace("_x", "")}_{keypoints[j].replace("_x", "")}' for i in range(num_keypoints) for j in range(i+1, num_keypoints)]

    # Create an empty DataFrame to store the pairwise distance data
    distance_data = pd.DataFrame(columns=column_names, index=range(num_frames))

    # Loop through each frame in the input data
    for frame in range(num_frames):
        # Loop through each keypoint
        for i in range(num_keypoints):
            # Get the x and y coordinates of the first keypoint (KP_i_x and KP_i_y)
            x1, y1 = data[keypoints[i]].iloc[frame], data[keypoints[i].replace('_x', '_y')].iloc[frame]
            # Loop through the rest of the keypoints to calculate distances
            for j in range(i + 1, num_keypoints):
                # Get the x and y coordinates of the second keypoint (KP_j_x and KP_j_y)
                x2, y2 = data[keypoints[j]].iloc[frame], data[keypoints[j].replace('_x', '_y')].iloc[frame]

                # Check if any of the keypoint values are zero
                if x1 == 0 or x2 == 0 or y1 == 0 or y2 == 0:
                    # If any of the keypoints have a zero value, the distance is set to zero
                    distance = 0
                else:
                    # Calculate the Euclidean distance between the two keypoints
                    distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

                # Store the distance in the corresponding cell of the DataFrame
                col_name = f'{keypoints[i].replace("_x", "")}_{keypoints[j].replace("_x", "")}'
                distance_data.at[frame, col_name] = distance

    # Return the DataFrame containing the pairwise distance data
    return distance_data