# pokemon-comp-analysis
Analysis of competitive Pokemon usage stats against other relevant metrics

To run this project, you need usage stat data. You can find this at https://www.smogon.com/stats/. Pick a month and scroll to the tier "gen9ou-1500" (which represents the usage in Gen 9 OverUsed at 1500+ ELO).

Copy all contents of the page and insert it into a txt file with the naming convention `usage_yyyy_mm.txt`. Place these in a folder in your directory labeled `usagestats`.

Then, open your terminal and run the processing script `convert_pokemon_usage.py` by running one of these commands:

- Convert a single usage file:
  ```powershell
  python processing_scripts\convert_pokemon_usage.py usagestats\usage_2025_08.txt
  ```

- Convert a single usage file and save to a custom CSV path:
  ```powershell
  python processing_scripts\convert_pokemon_usage.py usagestats\usage_2025_08.txt output\usage_2025_08.csv
  ```

- Convert all `.txt` usage files in a folder:
  ```powershell
  python processing_scripts\convert_pokemon_usage.py --directory usagestats
  ```

The generated CSV file will have a `name` column and a usage column name that matches the source txt filename stem (for example, `usage_2025_08`).

