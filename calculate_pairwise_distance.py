import pandas as pd
import numpy as np

def calculate_pairwise_distance(data):
    num_keypoints = len(data.columns) // 2
    num_frames = len(data)
    keypoints = [f'KP_{i}' for i in range(1, num_keypoints + 1)]
    distance_data = pd.DataFrame(columns=pd.MultiIndex.from_product([keypoints, keypoints]), index=range(num_frames))

    for frame in range(num_frames):
        for i in range(num_keypoints):
            for j in range(i + 1, num_keypoints):
                x1, y1 = data.iloc[frame, 2 * i], data.iloc[frame, 2 * i + 1]
                x2, y2 = data.iloc[frame, 2 * j], data.iloc[frame, 2 * j + 1]

                # Check if any of the keypoint values are zero
                if x1 == 0 or x2 == 0 or y1 == 0 or y2 == 0:
                    distance = 0
                else:
                    distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

                distance_data.iloc[frame, (i * num_keypoints) + j] = distance
                distance_data.iloc[frame, (j * num_keypoints) + i] = distance

    return distance_data

# Assuming "data" is the DataFrame containing the keypoint coordinates with columns like 'KP_1_x', 'KP_1_y', 'KP_2_x', 'KP_2_y', ..., 'KP_n_x', 'KP_n_y'
# Replace n with the total number of keypoints (e.g., 25)

# Call the function to calculate the pairwise distance and get the resulting DataFrame
distance_table = calculate_pairwise_distance(data)
