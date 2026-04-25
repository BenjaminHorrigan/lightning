#!/usr/bin/env python3
"""
LIGHTNING Rule Bulk Loader — CSV to ASP Atoms
==========================================

Generates ASP atom files from CSV data sources for list-based regimes.
Handles ~70% of LIGHTNING rule volume (substance lists, entity lists, etc.).

Usage:
    python scripts/generate_substance_atoms.py --regime cwc --schedule 1
    python scripts/generate_substance_atoms.py --all
    python scripts/generate_substance_atoms.py --validate

Dependencies: csv, argparse, pathlib (stdlib only)
"""

import csv
import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import re


@dataclass
class RegimeConfig:
    """Configuration for a regime's CSV-to-atoms conversion."""
    csv_file: str
    output_file: str
    regime_name: str
    schedule_value: str
    description: str
    required_columns: List[str]
    optional_columns: List[str] = None
    
    def __post_init__(self):
        if self.optional_columns is None:
            self.optional_columns = []


# =============================================================================
# REGIME CONFIGURATIONS
# =============================================================================

REGIME_CONFIGS = {
    # CWC Chemical Weapons Convention
    "cwc_schedule_1": RegimeConfig(
        csv_file="data/sources/cwc_schedule_1.csv",
        output_file="src/lightning/reasoning/rules/cwc/schedule_1_generated.lp",
        regime_name="cwc",
        schedule_value="1",
        description="CWC Schedule 1 chemicals - no significant peaceful use",
        required_columns=["canonical_name"],
        optional_columns=["cas_number", "iupac_name", "common_names", "molecular_formula"]
    ),
    
    "cwc_schedule_2": RegimeConfig(
        csv_file="data/sources/cwc_schedule_2.csv", 
        output_file="src/lightning/reasoning/rules/cwc/schedule_2_generated.lp",
        regime_name="cwc",
        schedule_value="2",
        description="CWC Schedule 2 chemicals - dual-use precursors",
        required_columns=["canonical_name"],
        optional_columns=["cas_number", "iupac_name", "common_names", "molecular_formula", "threshold_kg"]
    ),
    
    "cwc_schedule_3": RegimeConfig(
        csv_file="data/sources/cwc_schedule_3.csv",
        output_file="src/lightning/reasoning/rules/cwc/schedule_3_generated.lp", 
        regime_name="cwc",
        schedule_value="3",
        description="CWC Schedule 3 chemicals - bulk industrial with weapons potential",
        required_columns=["canonical_name"],
        optional_columns=["cas_number", "iupac_name", "common_names", "molecular_formula", "threshold_kg"]
    ),
    
    # DEA Controlled Substances Act
    "dea_schedule_i": RegimeConfig(
        csv_file="data/sources/dea_schedule_i.csv",
        output_file="src/lightning/reasoning/rules/dea/schedule_i_generated.lp",
        regime_name="dea", 
        schedule_value="I",
        description="DEA Schedule I - no accepted medical use",
        required_columns=["canonical_name"],
        optional_columns=["cas_number", "common_names", "molecular_formula", "dea_number"]
    ),
    
    "dea_schedule_ii": RegimeConfig(
        csv_file="data/sources/dea_schedule_ii.csv",
        output_file="src/lightning/reasoning/rules/dea/schedule_ii_generated.lp",
        regime_name="dea",
        schedule_value="II", 
        description="DEA Schedule II - high potential for abuse, accepted medical use",
        required_columns=["canonical_name"],
        optional_columns=["cas_number", "common_names", "molecular_formula", "dea_number"]
    ),
    
    "dea_schedule_iii_v": RegimeConfig(
        csv_file="data/sources/dea_schedule_iii_v.csv",
        output_file="src/lightning/reasoning/rules/dea/schedule_iii_v_generated.lp",
        regime_name="dea",
        schedule_value="III_IV_V",
        description="DEA Schedules III, IV, V - lower-risk controlled substances",
        required_columns=["canonical_name", "dea_schedule"],
        optional_columns=["cas_number", "common_names", "molecular_formula", "dea_number"]
    ),
    
    # HHS Select Agents
    "hhs_select_agents": RegimeConfig(
        csv_file="data/sources/hhs_select_agents.csv",
        output_file="src/lightning/reasoning/rules/bwc_select_agents/hhs_select_agents_generated.lp",
        regime_name="hhs_select",
        schedule_value="agent",
        description="HHS Select Agents - 42 CFR 73",
        required_columns=["canonical_name"],
        optional_columns=["scientific_name", "pathogen_type", "biosafety_level", "tier_1"]
    ),
    
    # USDA Select Agents  
    "usda_select_agents": RegimeConfig(
        csv_file="data/sources/usda_select_agents.csv",
        output_file="src/lightning/reasoning/rules/bwc_select_agents/usda_select_agents_generated.lp", 
        regime_name="usda_select",
        schedule_value="agent",
        description="USDA Select Agents - 9 CFR 121",
        required_columns=["canonical_name"],
        optional_columns=["scientific_name", "pathogen_type", "host_species"]
    ),
    
    # Australia Group
    "australia_group_bio": RegimeConfig(
        csv_file="data/sources/australia_group_biological.csv",
        output_file="src/lightning/reasoning/rules/bwc_select_agents/australia_group_bio_generated.lp",
        regime_name="australia_group",
        schedule_value="biological",
        description="Australia Group biological agents list",
        required_columns=["canonical_name"],
        optional_columns=["scientific_name", "pathogen_type", "category"]
    ),
    
    # Entity Lists (different structure - organizations not substances)
    "bis_entity_list": RegimeConfig(
        csv_file="data/sources/bis_entity_list.csv",
        output_file="src/lightning/reasoning/rules/ear/bis_entity_list_generated.lp",
        regime_name="bis_entity_list", 
        schedule_value="restricted",
        description="BIS Entity List - entities subject to license requirements",
        required_columns=["entity_name", "country"],
        optional_columns=["addresses", "federal_register_date", "reasons"]
    )
}


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def normalize_name(name: str) -> str:
    """Convert substance name to ASP atom format (lowercase_underscore)."""
    # Remove common chemical prefixes/suffixes that don't affect identity
    name = re.sub(r'\s*\([^)]*\)', '', name)  # Remove parenthetical remarks
    name = re.sub(r'\s*,.*', '', name)         # Remove alternate names after comma
    
    # Convert to lowercase and replace spaces/punctuation with underscores
    name = re.sub(r'[^a-zA-Z0-9]', '_', name.lower())
    name = re.sub(r'_+', '_', name)            # Collapse multiple underscores
    name = name.strip('_')                     # Remove leading/trailing underscores
    
    return name


def validate_cas_number(cas: str) -> bool:
    """Validate CAS number format (XXXXX-XX-X)."""
    if not cas or cas.upper() == 'N/A':
        return False
    
    pattern = re.compile(r'^\d{2,7}-\d{2}-\d$')
    return bool(pattern.match(cas.strip()))


def parse_common_names(names_str: str) -> List[str]:
    """Parse semicolon or comma-separated common names."""
    if not names_str or names_str.upper() == 'N/A':
        return []
    
    # Split on semicolon or comma
    names = re.split(r'[;,]', names_str)
    return [name.strip() for name in names if name.strip()]


def sanitize_string_for_asp(s: str) -> str:
    """Escape string for safe inclusion in ASP atom."""
    if not s:
        return ""
    
    # Escape quotes and backslashes
    s = s.replace('\\', '\\\\')
    s = s.replace('"', '\\"')
    return s


# =============================================================================
# ATOM GENERATION FUNCTIONS  
# =============================================================================

def generate_substance_atoms(config: RegimeConfig, csv_data: List[Dict[str, Any]]) -> List[str]:
    """Generate ASP atoms for substance-based regimes (CWC, DEA, Select Agents)."""
    atoms = []
    
    # Header comment
    atoms.extend([
        f"% {config.description}",
        f"% Generated from {config.csv_file}",
        f"% Total substances: {len(csv_data)}",
        "",
        '#include "_common/atom_vocabulary.lp".',
        ""
    ])
    
    for row in csv_data:
        canonical_name = normalize_name(row["canonical_name"])
        
        # KB metadata only — do NOT assert substance/1 here. The artifact
        # injects substance/1 facts; if we asserted them in the KB, every
        # rule that joins on substance(S) would fire for every loaded
        # substance regardless of input.
        atoms.append(f'schedule("{canonical_name}", "{config.regime_name}", "{config.schedule_value}").')
        
        # Optional CAS number
        if "cas_number" in row and row["cas_number"]:
            cas = row["cas_number"].strip()
            if validate_cas_number(cas):
                atoms.append(f'cas_number("{canonical_name}", "{cas}").')
        
        # Optional molecular formula
        if "molecular_formula" in row and row["molecular_formula"]:
            formula = sanitize_string_for_asp(row["molecular_formula"].strip())
            atoms.append(f'molecular_formula("{canonical_name}", "{formula}").')
            
        # Optional IUPAC name
        if "iupac_name" in row and row["iupac_name"]:
            iupac = sanitize_string_for_asp(row["iupac_name"].strip())
            atoms.append(f'iupac_name("{canonical_name}", "{iupac}").')
        
        # Common names as alternative identifiers
        if "common_names" in row:
            common_names = parse_common_names(row["common_names"])
            for alt_name in common_names:
                normalized_alt = normalize_name(alt_name)
                if normalized_alt != canonical_name:  # Avoid duplicates
                    atoms.append(f'alternative_name("{canonical_name}", "{normalized_alt}").')
        
        # Regime-specific attributes
        if config.regime_name == "dea" and "dea_number" in row and row["dea_number"]:
            dea_num = sanitize_string_for_asp(row["dea_number"].strip())
            atoms.append(f'dea_number("{canonical_name}", "{dea_num}").')
            
        if config.regime_name.endswith("_select") and "pathogen_type" in row and row["pathogen_type"]:
            pathogen_type = sanitize_string_for_asp(row["pathogen_type"].strip().lower())
            atoms.append(f'pathogen_type("{canonical_name}", "{pathogen_type}").')
            
        if "threshold_kg" in row and row["threshold_kg"]:
            try:
                # Clingo's standard ASP only handles integer arithmetic, so
                # quantize to int. Sub-kg thresholds round up to 1 kg.
                threshold = max(1, int(round(float(row["threshold_kg"]))))
                atoms.append(f'quantity_threshold("{canonical_name}", {threshold}, "kg").')
            except ValueError:
                pass  # Skip invalid threshold values
                
        atoms.append("")  # Blank line between substances
    
    return atoms


def generate_entity_atoms(config: RegimeConfig, csv_data: List[Dict[str, Any]]) -> List[str]:
    """Generate ASP atoms for entity-based regimes (BIS Entity List, SDN, etc.)."""
    atoms = []
    
    # Header comment
    atoms.extend([
        f"% {config.description}",
        f"% Generated from {config.csv_file}",
        f"% Total entities: {len(csv_data)}",
        "",
        '#include "_common/atom_vocabulary.lp".',
        ""
    ])
    
    for row in csv_data:
        entity_name = sanitize_string_for_asp(row["entity_name"])
        normalized_name = normalize_name(entity_name)
        country = row.get("country", "").strip().upper()
        
        # Core entity facts
        atoms.append(f'restricted_entity("{normalized_name}").')
        atoms.append(f'entity_regime("{normalized_name}", "{config.regime_name}").')
        
        if country:
            atoms.append(f'entity_country("{normalized_name}", "{country}").')
            
        # Original name for display/matching
        if entity_name != normalized_name:
            atoms.append(f'entity_display_name("{normalized_name}", "{entity_name}").')
            
        # Addresses if provided
        if "addresses" in row and row["addresses"]:
            addresses = parse_common_names(row["addresses"])  # Reuse parser
            for addr in addresses[:3]:  # Limit to 3 addresses max
                clean_addr = sanitize_string_for_asp(addr)
                atoms.append(f'entity_address("{normalized_name}", "{clean_addr}").')
        
        atoms.append("")
    
    return atoms


# =============================================================================
# MAIN GENERATION LOGIC
# =============================================================================

def generate_atoms_for_regime(regime_key: str, force: bool = False) -> bool:
    """Generate atoms for a single regime configuration."""
    config = REGIME_CONFIGS[regime_key]
    
    # Check if CSV file exists
    csv_path = Path(config.csv_file)
    if not csv_path.exists():
        print(f"⚠️  CSV file not found: {config.csv_file}")
        print(f"   Create this file with columns: {', '.join(config.required_columns)}")
        return False
    
    # Check if output file exists and is newer than CSV
    output_path = Path(config.output_file)
    if not force and output_path.exists():
        csv_mtime = csv_path.stat().st_mtime
        output_mtime = output_path.stat().st_mtime
        if output_mtime > csv_mtime:
            print(f"✓  {regime_key}: output is up to date")
            return True
    
    try:
        # Read CSV data
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            csv_data = list(reader)
        
        # Validate required columns
        if not csv_data:
            print(f"⚠️  Empty CSV file: {config.csv_file}")
            return False
            
        missing_cols = set(config.required_columns) - set(csv_data[0].keys())
        if missing_cols:
            print(f"❌ Missing required columns in {config.csv_file}: {missing_cols}")
            return False
        
        # Generate atoms
        if regime_key.endswith("_entity_list"):
            atoms = generate_entity_atoms(config, csv_data)
        else:
            atoms = generate_substance_atoms(config, csv_data)
        
        # Write output file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(atoms))
        
        print(f"✓  {regime_key}: generated {len(csv_data)} items → {config.output_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error generating {regime_key}: {e}")
        return False


def create_sample_csv_files():
    """Create sample CSV files with correct structure for testing."""
    samples = {
        "data/sources/cwc_schedule_1.csv": {
            "headers": ["canonical_name", "cas_number", "iupac_name", "molecular_formula"],
            "rows": [
                ["Sarin", "107-44-8", "Methylphosphonofluoridic acid", "C4H10FO2P"],
                ["VX", "50782-69-9", "Ethyl N-[2-(diisopropylamino)ethyl] methylphosphonothioate", "C11H26NO2PS"],
                ["Mustard gas", "505-60-2", "Bis(2-chloroethyl) sulfide", "C4H8Cl2S"]
            ]
        },
        
        "data/sources/dea_schedule_i.csv": {
            "headers": ["canonical_name", "cas_number", "dea_number", "molecular_formula"],
            "rows": [
                ["Heroin", "561-27-3", "9200", "C21H23NO5"],
                ["LSD", "50-37-3", "7315", "C20H25N3O"],
                ["MDMA", "42542-10-9", "7405", "C11H15NO2"]
            ]
        },
        
        "data/sources/hhs_select_agents.csv": {
            "headers": ["canonical_name", "scientific_name", "pathogen_type", "biosafety_level"],
            "rows": [
                ["Anthrax", "Bacillus anthracis", "bacteria", "BSL-3"],
                ["Ebola virus", "Ebolavirus", "virus", "BSL-4"], 
                ["Smallpox virus", "Variola major", "virus", "BSL-4"]
            ]
        }
    }
    
    print("Creating sample CSV files...")
    for filepath, data in samples.items():
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(data["headers"])
            writer.writerows(data["rows"])
        
        print(f"  Created: {filepath}")


def validate_all_configs() -> bool:
    """Validate all regime configurations for completeness."""
    print("Validating regime configurations...")
    
    all_valid = True
    for key, config in REGIME_CONFIGS.items():
        print(f"\n{key}:")
        print(f"  CSV: {config.csv_file}")
        print(f"  Output: {config.output_file}")
        print(f"  Required columns: {config.required_columns}")
        
        # Check CSV exists
        if not Path(config.csv_file).exists():
            print(f"  ❌ CSV file missing")
            all_valid = False
        else:
            print(f"  ✓  CSV file exists")
            
        # Check output directory can be created
        try:
            Path(config.output_file).parent.mkdir(parents=True, exist_ok=True)
            print(f"  ✓  Output directory accessible")
        except Exception as e:
            print(f"  ❌ Cannot create output directory: {e}")
            all_valid = False
    
    return all_valid


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate ASP atoms from CSV regime data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Available regimes:
{chr(10).join('  ' + key for key in REGIME_CONFIGS.keys())}

Examples:
  # Generate CWC Schedule 1 atoms
  python {Path(__file__).name} --regime cwc_schedule_1

  # Generate all regimes
  python {Path(__file__).name} --all

  # Create sample CSV files for testing  
  python {Path(__file__).name} --create-samples
        """
    )
    
    parser.add_argument("--regime", choices=list(REGIME_CONFIGS.keys()),
                       help="Generate atoms for specific regime")
    parser.add_argument("--all", action="store_true", 
                       help="Generate atoms for all configured regimes")
    parser.add_argument("--force", action="store_true",
                       help="Regenerate even if output is newer than CSV")
    parser.add_argument("--validate", action="store_true",
                       help="Validate all configurations without generating")
    parser.add_argument("--create-samples", action="store_true",
                       help="Create sample CSV files for testing")
    
    args = parser.parse_args()
    
    # Handle special actions
    if args.create_samples:
        create_sample_csv_files()
        return
        
    if args.validate:
        if validate_all_configs():
            print("\n✓  All configurations valid")
        else:
            print("\n❌ Some configurations have issues")
        return
    
    # Main generation logic
    if args.all:
        print("Generating atoms for all regimes...")
        success_count = 0
        for regime_key in REGIME_CONFIGS.keys():
            if generate_atoms_for_regime(regime_key, args.force):
                success_count += 1
        
        print(f"\nCompleted: {success_count}/{len(REGIME_CONFIGS)} regimes successful")
        
    elif args.regime:
        generate_atoms_for_regime(args.regime, args.force)
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
