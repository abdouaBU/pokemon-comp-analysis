"""
Convert Pokemon usage txt files to pandas-compatible CSV format.

This module provides utilities to parse Pokemon usage statistics from
txt files with pipe-delimited columns and extract Pokemon names and Usage %.
"""

import pandas as pd
from decimal import Decimal
from pathlib import Path


def parse_pokemon_usage_txt(input_file, output_file=None):
    """
    Parse a Pokemon usage txt file and extract Pokemon name and Usage %.
    
    The txt file is expected to have a specific structure with:
    - Metadata header lines (Total battles, Avg. weight/team, etc.)
    - Separator rows with +----+ pattern
    - Pipe-delimited data rows with columns including Pokemon and Usage %
    
    Args:
        input_file (str or Path): Path to the input txt file
        output_file (str or Path, optional): Path for output CSV file. 
                                             If None, uses input_file with .csv extension
    
    Returns:
        pd.DataFrame: DataFrame with columns ['Pokemon', 'Usage %']
    """
    
    input_path = Path(input_file)
    
    # Determine output file path
    if output_file is None:
        output_path = input_path.with_suffix('.csv')
    else:
        output_path = Path(output_file)
    
    # Read the file and extract data rows
    pokemon_data = []
    
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line in lines:
        # Skip separator rows (contain +----+)
        if line.startswith('+') or line.startswith('-'):
            continue
        
        # Skip metadata header lines (contain ':' but not pipes)
        if ':' in line and '|' not in line:
            continue
        
        # Process data rows (contain pipes)
        if '|' in line:
            # Split by pipe and strip whitespace
            columns = [col.strip() for col in line.split('|')]
            
            # Filter out empty strings from leading/trailing pipes
            columns = [col for col in columns if col]
            
            # Expected format: Rank | Pokemon | Usage % | Raw | % | Real | %
            # We need columns[1] (Pokemon) and columns[2] (Usage %)
            if len(columns) >= 3:
                pokemon_name = columns[1]
                usage_percent = columns[2]
                
                # Skip header row
                if pokemon_name.lower() != 'pokemon':
                    # Convert usage percent string (e.g., "32.87335%") to float (e.g., 0.3287335)
                    # Use Decimal for precise conversion to avoid floating point rounding errors
                    usage_float = float(Decimal(usage_percent.replace('%', '')) / 100)
                    
                    pokemon_data.append({
                        'Pokemon': pokemon_name,
                        'Usage %': usage_float
                    })
    
    # Create DataFrame
    df = pd.DataFrame(pokemon_data)
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    
    print(f"Successfully converted {input_file} to {output_path}")
    print(f"Total Pokemon records: {len(df)}")
    
    return df


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python convert_pokemon_usage.py <input_file> [output_file]")
        print("\nExample:")
        print("  python convert_pokemon_usage.py pkmnusage.txt")
        print("  python convert_pokemon_usage.py pkmnusage.txt output.csv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    df = parse_pokemon_usage_txt(input_file, output_file)
    print("\nFirst few rows:")
    print(df.head())
