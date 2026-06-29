# pokemon-comp-analysis
Analysis of competitive Pokemon usage stats against other relevant metrics.

## Overview
This project converts raw Smogon usage text data into analysis-ready CSV files, merges those files with Pokemon base stats and typing data, and produces a final `full_data.csv` dataset for notebook exploration.

## Data Preparation
1. Download monthly usage data from https://www.smogon.com/stats/.
2. Select a month and copy the table for the desired tier (for example `gen9ou-1500`).
3. Save the copied output into a text file named using the pattern:
   - `usage_yyyy_mm.txt`
4. Put those usage text files into the local `usagestats` folder.

## Processing Scripts
The repository contains three processing scripts in `processing_scripts/`:

### 1. `convert_pokemon_usage.py`
Convert Smogon usage text files into CSV files.

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

The generated CSV file will include:
- `name`: Pokemon name
- `usage_yyyy_mm`: a usage column that matches the source text filename stem, for example `usage_2025_08`

### 2. `process_pokemon_data.py`
Extract Pokemon base stats, typing, and tier data from local HTML and list files.

Expected inputs:
- `all.html` (the HTML table source)
- `pokemon_list.txt` (tier assignments)
- `alternate_names.txt` (optional alternate name mappings)

Run it from the repo root with:
```powershell
python processing_scripts\process_pokemon_data.py
```

This script generates `bst_typing/pokemon_competitive_stats.csv`, which contains:
- `pokemon_name`
- base stats: `hp`, `atk`, `def`, `spa`, `spd`, `spe`, `bst`
- type indicator columns: `type_fire`, `type_water`, etc.
- tier indicator columns: `tier_OU`, `tier_UU`, `tier_PU`, etc.

### 3. `generate_dataframe.py`
Merge the usage CSVs with the competitive stats CSV and produce the final dataset.

Run:
```powershell
python processing_scripts\generate_dataframe.py
```

This script reads all CSV files in `usagestats/`, merges them on `name`, and then joins the merged usage data with `bst_typing/pokemon_competitive_stats.csv` to produce:
- `full_data.csv`

## Notebook Analysis
A basic notebook is provided at `full_data_analysis.ipynb`.

This notebook demonstrates how to:
- load `full_data.csv`
- compute type combinations from type indicator columns
- calculate total and average base stats
- plot average usage by type combination
- visualize stat total vs usage with scatter and regression plots
- compute and display a correlation matrix for base stats and usage
- compare average usage across competitive tiers

The notebook uses `pandas`, `matplotlib`, and `seaborn` to make these analyses interactive and easy to extend.

## Recommended Workflow
1. Prepare usage files in `usagestats/`.
2. Convert usage text files:
   ```powershell
   python processing_scripts\convert_pokemon_usage.py --directory usagestats
   ```
3. Extract Pokemon base stats and tiers:
   ```powershell
   python processing_scripts\process_pokemon_data.py
   ```
4. Merge all data into the final file:
   ```powershell
   python processing_scripts\generate_dataframe.py
   ```
5. Open `full_data_analysis.ipynb` and run the notebook cells to explore the merged dataset.

## Notes
- If a usage file is named `usage_2025_08.txt`, the output column is `usage_2025_08`.
- The notebook assumes `full_data.csv` exists in the repo root.
- You can customize or add more usage files by placing them in the `usagestats/` folder and rerunning the conversion and merge steps.
