import json
import numpy as np
import os
import pandas as pd

# Function to process JSON files and save the resulting dataframe
def process_json_files(folder_path):
    # Create a list of strings for the column names
    col_names = ['frame', 'person']
    data_list = []
    for i in range(0, 25):
        col_names.append('KP_'+str(i)+'_x')
        col_names.append('KP_'+str(i)+'_y')
        col_names.append('KP_'+str(i)+'_confidence')
    
    # Create an empty dataframe with the above columns
    df = pd.DataFrame(columns=col_names)
    
    # Create a list of all the JSON files in the folder
    json_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".json"):
                json_files.append(os.path.join(root, file))
    
    for file in json_files:
        # Read file
        with open(file, 'r') as myfile:
            data = myfile.read()
        
        # Parse file
        obj = json.loads(data)
        
        # Retrieve pose_keypoints_2d as list of lists
        keypoints = []
        for i in range(0, len(obj["people"])):
            keypoints.append(np.reshape(obj["people"][i]["pose_keypoints_2d"], (25, 3)))
        
        # Enter each value to the corresponding column in the dataframe
        for j in range(0, len(obj["people"])):
            frame_data = {'frame': int(file[-27:-15]), 'person': str(j+1)}
            for i in range(0, 25):
                kp = keypoints[j][i]
                frame_data.update({
                    'KP_'+str(i)+'_x': kp[0],
                    'KP_'+str(i)+'_y': kp[1],
                    'KP_'+str(i)+'_confidence': kp[2]
                })
            data_list.append(frame_data)
    
    df = pd.DataFrame(data_list, columns=col_names)
    
    # Rearrange dataframe so that all frames for each person are together
    new_df = pd.DataFrame(columns=col_names)
    for j in range(0, len(obj["people"])):
        person_df = df[df['person'] == str(j+1)]
        new_df = pd.concat([new_df, person_df], ignore_index=True)
    
    # Save the dataframe as a CSV file
    main_output_folder = "keypoints"
    this_folder_name = folder_path.split(os.sep)[-1] + '.csv'
    output_file = os.path.join(main_output_folder, this_folder_name)
    new_df.to_csv(output_file, index=False)
    print(f"CSV file saved: {output_file}")

    return new_df
