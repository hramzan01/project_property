import pandas as pd 
import os


'''FUNCTION TO MERGE MULTIPLE CSV FILES'''

def merge_csv_files(file_list):
    df_list = [pd.read_csv(f'data/processed_data/{file}') for file in file_list]
    merged_df = pd.concat(df_list, ignore_index=True)
    return merged_df

# make list of csv files ffom the processed_data folder
csv_files = os.listdir('data/processed_data')
merged_df = merge_csv_files(csv_files)

merged_df.to_csv('data/processed_data/merged_data.csv', index=False)
print(len(merged_df))
