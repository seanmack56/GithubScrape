import pandas as pd

df = pd.read_csv("True_Updated_repo_calcs.csv")
#duplicate_rows = df[df.duplicated(subset=[df.columns[0]])]
# Identify duplicate rows based on the first column, keeping the first occurrence
duplicate_rows = df[df.duplicated(subset=[df.columns[0]], keep='first')]

# Remove duplicate rows
df_no_duplicates = df.drop(duplicate_rows.index)
df_no_duplicates.to_csv('final_list.csv', index=False)

#duplicate_rows.to_csv("tester3.csv", index=False)