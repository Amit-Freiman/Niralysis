import pandas as pd
import numpy as np

def calculate_pairwise_distance(data):
    keypoints = [col for col in data.columns if col.endswith('_x')]
    num_keypoints = len(keypoints)
    num_frames = len(data)
    column_names = [f'{keypoints[i].replace("_x", "")}_{keypoints[j].replace("_x", "")}' for i in range(num_keypoints) for j in range(i+1, num_keypoints)]

    distance_data = pd.DataFrame(columns=column_names, index=range(num_frames))

    for frame in range(num_frames):
        for i in range(num_keypoints):
            x1, y1 = data[keypoints[i]].iloc[frame], data[keypoints[i].replace('_x', '_y')].iloc[frame]
            for j in range(i + 1, num_keypoints):
                x2, y2 = data[keypoints[j]].iloc[frame], data[keypoints[j].replace('_x', '_y')].iloc[frame]

                # Check if any of the keypoint values are zero
                if x1 == 0 or x2 == 0 or y1 == 0 or y2 == 0:
                    distance = 0
                else:
                    distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

                col_name = f'{keypoints[i].replace("_x", "")}_{keypoints[j].replace("_x", "")}'
                distance_data.at[frame, col_name] = distance

    return distance_data

# Assuming "data" is the DataFrame containing the keypoint coordinates with columns like 'frame', 'person', 'KP_0_x', 'KP_0_y', 'KP_1_x', 'KP_1_y', ..., 'KP_n_x', 'KP_n_y'
# Replace n with the total number of keypoints

# Call the function to calculate the pairwise distance and get the resulting DataFrame
distance_table = calculate_pairwise_distance(data)
