import glob

import pandas as pd

file_pattern = '*.csv'
file_paths = [file for file in glob.glob(file_pattern) if "_info" not in file]

all_data = []
for file in file_paths:
    df = pd.read_csv(file, low_memory=False)
    all_data.append(df)

combined_data = pd.concat(all_data, ignore_index=True)
combined_data.to_csv('WT20Is.csv')