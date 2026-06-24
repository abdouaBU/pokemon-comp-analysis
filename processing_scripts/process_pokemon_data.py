#!/usr/bin/env python3
"""
Process Pokemon data from all.html and pokemon_list.txt to create a comprehensive CSV
with base stats, types, and competitive tiers.
"""

import re
import csv
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set

# Define all 18 types
ALL_TYPES = [
    'normal', 'fire', 'water', 'grass', 'electric', 'ice', 'fighting', 'poison',
    'ground', 'flying', 'psychic', 'bug', 'rock', 'ghost', 'dragon', 'dark', 'steel', 'fairy'
]

# Define all 12 tiers
ALL_TIERS = ['Ubers', 'OU', 'UUBL', 'UU', 'RUBL', 'RU', 'NUBL', 'NU', 'PUBL', 'PU', 'ZUBL', 'ZU']

def load_alternate_names(filepath: str) -> Dict[str, str]:
    """Load alternate names mapping from file."""
    alt_names = {}
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                parts = [p.strip() for p in line.split(',')]
                if len(parts) == 2:
                    alt_names[parts[0]] = parts[1]  # Map from full name to short name
    print(f"Loaded {len(alt_names)} alternate name mappings")
    return alt_names

def parse_pokemon_tiers(filepath: str) -> Dict[str, str]:
    """Parse pokemon_list.txt to extract tier information."""
    pokemon_tiers = {}
    current_tier = None
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            
            if not line:
                continue
            
            if ':' in line:  # Tier header like "Ubers:"
                current_tier = line.rstrip(':')
            elif line == '@':  # Delimiter
                current_tier = None
            elif current_tier:
                pokemon_tiers[line] = current_tier
    
    print(f"Loaded {len(pokemon_tiers)} Pokemon with tier information")
    return pokemon_tiers

def extract_pokemon_data_from_html(filepath: str, alt_names: Dict[str, str]) -> Dict[str, Dict]:
    """Extract Pokemon stats and types from HTML file."""
    pokemon_data = {}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match Pokemon entries in the HTML table
    # Looking for patterns like: name in href, types, and base stats
    
    # First, let's extract individual Pokemon blocks more carefully
    # Pattern: <a class="ent-name" ... >PokemonName</a> followed by types and stats
    
    pokemon_pattern = r'<a class="ent-name"[^>]*>([^<]+)</a>.*?<a class="type-icon[^>]*>([^<]+)</a>(?:.*?<br>.*?<a class="type-icon[^>]*>([^<]+)</a>)?'
    
    # Find all Pokemon entries with their names and types
    pattern = r'<span class="infocard-cell-data">(\d+)</span></td>\s*<td class="cell-name"><a[^>]*>([^<]+)</a>(?:<br>.*?)?</td>\s*<td class="cell-icon">(.*?)</td>'
    
    for match in re.finditer(pattern, content):
        pokedex_num = match.group(1)
        pokemon_name = match.group(2)
        types_html = match.group(3)
        
        # Extract types from HTML
        type_matches = re.findall(r'<a class="type-icon type-(\w+)"[^>]*>([^<]+)</a>', types_html)
        types = [t[1].lower() for t in type_matches]
        
        # Normalize name (remove variants like "Mega", "Alolan", etc. for base form matching)
        base_name = pokemon_name
        if '<br>' in pokemon_name or '<small' in pokemon_name:
            base_name = re.sub(r'<br>.*', '', pokemon_name)
            base_name = re.sub(r'<small.*</small>', '', base_name).strip()
        
        base_name = base_name.strip()
        
        # Skip variants (we only want base Pokemon)
        # Variants typically have additional info after the name
        if '<small' in pokemon_name or '<br>' in pokemon_name:
            continue
        
        if base_name not in pokemon_data:
            pokemon_data[base_name] = {'types': types}
    
    print(f"Extracted {len(pokemon_data)} unique Pokemon from HTML")
    
    # Now extract base stats
    # Pattern for base stats row: looking for stat values in table cells
    
    # More precise pattern: find Pokemon name followed by stats
    stats_pattern = r'<a class="ent-name"[^>]*>([^<]+?)</a>.*?(?:<br><small[^>]*>[^<]*</small>)?</td>.*?<td[^>]*>(\d+)</td>.*?<td[^>]*>(\d+)</td>.*?<td[^>]*>(\d+)</td>.*?<td[^>]*>(\d+)</td>.*?<td[^>]*>(\d+)</td>.*?<td[^>]*>(\d+)</td>.*?<td[^>]*>(\d+)</td>'
    
    # Try a different approach: parse the entire table structure
    # Look for HP, ATK, DEF, SPA, SPD, SPE values
    
    print("Attempting to extract base stats from HTML...")
    
    # This is complex; let me use a more systematic approach
    # Split by Pokemon entries and extract stats for each
    
    return pokemon_data

def normalize_variant_name(base_name: str, variant_label: str) -> str | None:
    """Convert HTML variant labels into normalized names that match pokemon_list.txt."""
    if not variant_label:
        return base_name

    label = variant_label.strip()
    lower = label.lower()
    base_lower = base_name.lower()

    # If the variant label repeats the base name, strip it off.
    if lower.startswith(base_lower + ' '):
        label = label[len(base_name):].strip()
        lower = label.lower()

    # Skip forms that are not in Gen 9 usage lists
    if 'mega' in lower or 'primal' in lower or 'gigantamax' in lower or 'gmax' in lower:
        return None

    # Urshifu forms
    if 'single strike' in lower:
        return f"{base_name}-Single"
    if 'rapid strike' in lower:
        return f"{base_name}-Rapid"

    # Standard regional forms
    if lower.startswith('alolan'):
        return f"{base_name}-Alola"
    if lower.startswith('galarian'):
        return f"{base_name}-Galar"
    if lower.startswith('hisuian'):
        return f"{base_name}-Hisui"
    if lower.startswith('paldean'):
        return f"{base_name}-Paldea"

    # Paldea breed forms and mask forms
    if 'aqua breed' in lower:
        return f"{base_name}-Paldea-Aqua"
    if 'blaze breed' in lower:
        return f"{base_name}-Paldea-Blaze"
    if 'combat breed' in lower:
        return f"{base_name}-Paldea-Combat"
    if lower.endswith(' mask'):
        prefix = label[:-5].strip()
        clean = prefix.replace(' ', '')
        return f"{base_name}-{clean}"

    # Named forms such as Midday Form, Midnight Form, Dusk Form
    if lower.endswith(' form'):
        form = label[:-5].strip().replace(' ', '')
        return f"{base_name}-{form}"

    # Fallback to a normalized hyphenated variant name
    return f"{base_name}-{label.replace(' ', '')}"


def extract_base_stats_from_html(filepath: str) -> Dict[str, Dict]:
    """
    Extract base stats from HTML by parsing table structure.
    Includes regular Pokemon and valid Gen 9 variant forms.
    """
    pokemon_stats = {}
    skipped = 0

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    row_pattern = re.compile(
        r'<span class="infocard-cell-data">(\d+)</span>.*?'
        r'<a class="ent-name"[^>]*>([^<]+)</a>'
        r'(?:<br>\s*<small class="text-muted">([^<]+)</small>)?</td>.*?'
        r'<td class="cell-icon">(.*?)</td>(.*?)</tr>',
        re.DOTALL
    )

    rows = row_pattern.findall(content)
    print(f"Found {len(rows)} Pokemon rows in HTML")

    for pokedex_num, display_name, variant_label, types_html, stats_html in rows:
        name_key = normalize_variant_name(display_name.strip(), variant_label or '')
        if name_key is None:
            skipped += 1
            continue

        type_matches = re.findall(r'type-(\w+)"[^>]*>([^<]+)</a>', types_html)
        types = [t[1].lower() for t in type_matches]

        stat_cells = re.findall(r'<td[^>]*>(\d+)</td>', stats_html)
        if len(stat_cells) < 7:
            continue

        total, hp, atk, df, spa, spd, spe = stat_cells[0:7]
        pokemon_stats[name_key] = {
            'types': types,
            'hp': int(hp),
            'atk': int(atk),
            'def': int(df),
            'spa': int(spa),
            'spd': int(spd),
            'spe': int(spe),
            'total': int(total)
        }

    print(f"Extracted stats for {len(pokemon_stats)} Pokemon")
    print(f"Skipped {skipped} Mega/Primal/Gigantamax rows")
    return pokemon_stats


def create_csv_output(pokemon_stats: Dict, pokemon_tiers: Dict, alt_names: Dict, output_dir: str):
    """Create the final CSV output with all required columns."""
    
    output_path = Path(output_dir) / "pokemon_competitive_stats.csv"
    output_path.parent.mkdir(exist_ok=True)
    
    # Prepare CSV headers
    headers = ['pokemon_name', 'bst', 'hp', 'atk', 'def', 'spa', 'spd', 'spe']
    headers += [f'type_{t}' for t in ALL_TYPES]
    headers += [f'tier_{t}' for t in ALL_TIERS]
    
    # Process each Pokemon in pokemon_list.txt order
    rows = []
    
    for pokemon_name in sorted(pokemon_tiers.keys()):
        # Try to find the Pokemon in our stats data
        stats_key = None
        
        # First try exact match
        if pokemon_name in pokemon_stats:
            stats_key = pokemon_name
        # Then try alternate name mapping
        elif pokemon_name in alt_names:
            alt_name = alt_names[pokemon_name]
            if alt_name in pokemon_stats:
                stats_key = alt_name
        
        # Also try finding by checking if the name appears in our stats
        if not stats_key:
            for key in pokemon_stats:
                if pokemon_name.lower() in key.lower() or key.lower() in pokemon_name.lower():
                    stats_key = key
                    break
        
        if not stats_key:
            print(f"Warning: Could not find stats for {pokemon_name}")
            continue
        
        stats = pokemon_stats[stats_key]
        tier = pokemon_tiers[pokemon_name]
        
        # Build row
        row = {
            'pokemon_name': pokemon_name,
            'bst': stats['total'],
            'hp': stats['hp'],
            'atk': stats['atk'],
            'def': stats['def'],
            'spa': stats['spa'],
            'spd': stats['spd'],
            'spe': stats['spe']
        }
        
        # Add type columns (binary)
        for type_name in ALL_TYPES:
            row[f'type_{type_name}'] = 1 if type_name in stats['types'] else 0
        
        # Add tier columns (binary)
        for tier_name in ALL_TIERS:
            row[f'tier_{tier_name}'] = 1 if tier_name == tier else 0
        
        rows.append(row)
    
    print(f"Writing {len(rows)} Pokemon to CSV...")
    
    # Write CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"CSV written to {output_path}")
    return len(rows)

def main():
    """Main function to orchestrate the data processing."""
    base_dir = Path("c:/Users/papi2/github_general/pokemon-comp-analysis")
    
    print("="*60)
    print("Pokemon Competitive Data Processor")
    print("="*60)
    
    # Load alternate names
    print("\n1. Loading alternate names...")
    alt_names = load_alternate_names(str(base_dir / "alternate_names.txt"))
    
    # Parse tiers
    print("\n2. Parsing Pokemon tiers...")
    pokemon_tiers = parse_pokemon_tiers(str(base_dir / "pokemon_list.txt"))
    
    # Extract Pokemon data from HTML
    print("\n3. Extracting Pokemon data from HTML...")
    pokemon_stats = extract_base_stats_from_html(str(base_dir / "all.html"))
    
    if not pokemon_stats:
        print("ERROR: Could not extract any Pokemon data from HTML!")
        return
    
    # Create CSV output
    print("\n4. Creating CSV output...")
    num_written = create_csv_output(pokemon_stats, pokemon_tiers, alt_names, str(base_dir / "bst_typing"))
    
    print("\n" + "="*60)
    print(f"SUCCESS: Processed {num_written} Pokemon")
    print("="*60)

if __name__ == "__main__":
    main()
