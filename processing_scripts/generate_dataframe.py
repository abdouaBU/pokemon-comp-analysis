import pandas as pd
import os
from pathlib import Path

namelis = []

altfile = "alternate_names.txt"
with open(altfile, 'r') as file:
    for line in file:
        namelis.append(line)

for i in range(len(namelis)):
    namelis[i] = namelis[i].strip("\n")
    namelis[i] = (namelis[i][:namelis[i].index(",")], namelis[i][namelis[i].index(",")+2:])


usage_files = os.listdir('usagestats')
print(usage_files)

csvlis = []

for file in usage_files:
    csvlis.append(pd.read_csv("usagestats/"+file))

df_usage = csvlis[0]

for i in range(1, len(csvlis)):
    df_usage = pd.merge(df_usage, csvlis[i], how = "outer", on = "name")

df_usage = df_usage.sort_values(by='usage_2025_06', ascending=False)

for nametup in namelis:
    for row in df_usage.itertuples():
        if row.name == nametup[1]:
            df_usage.at[row.Index, 'name'] = nametup[0]

df_stats = pd.read_csv("bst_typing/pokemon_competitive_stats.csv")

df_full = pd.merge(df_stats, df_usage, how = "left", on="name")
df_full = df_full.fillna(0)

df_full.to_csv("full_data.csv")