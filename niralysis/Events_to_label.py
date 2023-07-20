import pandas as pd

def events_to_labels (df: pd.DataFrame, T_Hold: int) -> pd.DataFrame:
   
# creating a new DF with index and timestamps, which are coulmns 0, 1 and new columns as the lables. will start with initialized value of 'False' per each label.    

    df_new = df.loc[:, ['timestamps']]
    df_new['TILT_R'] = False
    df_new['TILT_L'] = False
    df_new['ROUND_R'] = False
    df_new['ROUND_L'] = False
    df_new['LEAN_R'] = False
    df_new['LEAN_L'] = False
    print (df_new)

    # Iterate over rows in the df and update values in the df_new 
    for index, row in df.iterrows():
        # Check if the movement is RIGHT TILT or LEAN
        if (row['KP_0_x'] < 0 ) or (row['KP_15_y'] > 0) or (row['KP_17_y']>0):
            if (row['KP_5_KP_16']> T_Hold) or (row['KP_2_KP_15']< -T_Hold): # negative value mean the keypoins got closer
                df_new['TILT_R'] = True
            else: 
                df_new['LEAN_R'] = True
       
        # Check if the movement is LEFT TILT or LEAN
        if (row['KP_0_x'] > 0 ) or (row['KP_16_y'] > 0) or (row['KP_18_y'] > 0):
            if (row['KP_5_KP_16']< -T_Hold) or (row['KP_2_KP_15'] > T_Hold):
                df_new['TILT_L'] = True
            else: 
                df_new['LEAN_L']= True

        # Check if movement is ROUND LEFT/RIGHT #
        if row['KP_2_y']< -T_Hold:
            if (row['KP_0_x'] < 0 ) or (row['KP_16_x'] <0) or (row['KP_18_x']<0):
                df_new['ROUND_R'] = True 
        if row['KP_5_y']< -T_Hold:
            if (row['KP_0_x'] > 0) or (row['KP_15_x'] > 0) or (row['KP_17_x'] > 0):
                df_new['ROUND_L'] = True 

     # update class attribute with the new_df
    return df_new
    







