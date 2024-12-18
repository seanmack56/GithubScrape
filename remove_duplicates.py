import pandas as pd

df = pd.read_csv("ADD_CSVFILE_HERE.csv")
# Identify duplicate rows based on the first column, keeping the first occurrence
duplicate_rows = df[df.duplicated(subset=[df.columns[0]], keep='first')]

# Remove duplicate rows
df_no_duplicates = df.drop(duplicate_rows.index)
df_no_duplicates.to_csv('OUTPUTFILE.csv', index=False)
