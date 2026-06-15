import pandas as pd
import glob
import os
 
# 1. Locate all ledger files in the directory
all_files = glob.glob("ledger_*.csv")

# 2. Compile into a list of DataFrames
df_list = []
for filename in all_files:
    df = pd.read_csv(filename)
    # Add a date column extracted from the filename so you don't lose the context
    date_part = filename.replace("ledger_", "").replace(".csv", "")
    df['Date'] = date_part
    df_list.append(df)

# 3. Concatenate and sort
master_df = pd.concat(df_list, axis=0)
master_df = master_df.sort_values(by=['Date', 'Time'])

# 4. Save to disk
master_df.to_csv("MASTER_LEDGER.csv", index=False)
print(f"Successfully aggregated {len(all_files)} files into 'MASTER_LEDGER.csv'.")
