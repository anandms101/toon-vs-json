#!/usr/bin/env python3
"""
Convert JSON files to Toon format.

This script reads JSON files from the datasets directory and converts them
to Toon (Token-Oriented Object Notation) format, which is more compact
and token-efficient for LLM applications. The converted files are saved
to the outputs directory with a .toon extension.

Usage:
    python convert_to_toon.py [datasets_dir] [output_dir]
    
If no directories are specified, defaults to datasets/ and outputs/.
"""

import json
import os
import sys
from pathlib import Path

# Import the toon library for encoding JSON data to Toon format
try:
    from toon import encode
except ImportError:
    print("Error: toon package not installed. Install with: pip install toon-llm")
    sys.exit(1)


def convert_json_to_toon(json_data):
    """
    Convert JSON data structure to Toon format string.
    
    Args:
        json_data: Python data structure (dict, list, etc.) loaded from JSON
        
    Returns:
        String representation in Toon format, or None if conversion fails
    """
    try:
        # The encode function from toon library converts Python data to Toon format
        toon_data = encode(json_data)
        return toon_data
    except Exception as e:
        print(f"Error converting to Toon: {e}")
        return None


def convert_file(input_path, output_dir):
    """
    Convert a single JSON file to Toon format.
    
    Args:
        input_path: Path to the input JSON file
        output_dir: Directory where the output .toon file should be saved
        
    Returns:
        True if conversion succeeded, False otherwise
    """
    try:
        # Read and parse the JSON file
        with open(input_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Convert the parsed JSON data to Toon format
        toon_data = convert_json_to_toon(json_data)
        
        if toon_data is None:
            return False
        
        # Generate output filename by replacing .json extension with .toon
        input_filename = Path(input_path).stem
        output_path = Path(output_dir) / f"{input_filename}.toon"
        
        # Write the Toon-formatted data to the output file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(toon_data)
        
        print(f"Converted {input_path.name} -> {output_path.name}")
        return True
        
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON in {input_path}: {e}")
        return False
    except Exception as e:
        print(f"Error processing {input_path}: {e}")
        return False


def batch_convert(datasets_dir, output_dir):
    """
    Convert all JSON files in the datasets directory to Toon format.
    
    This function finds all .json files in the specified directory,
    converts each one to Toon format, and saves them to the output directory.
    
    Args:
        datasets_dir: Directory containing JSON files to convert
        output_dir: Directory where converted .toon files will be saved
    """
    datasets_path = Path(datasets_dir)
    output_path = Path(output_dir)
    
    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all JSON files in the datasets directory
    json_files = list(datasets_path.glob("*.json"))
    
    if not json_files:
        print(f"No JSON files found in {datasets_dir}")
        return
    
    print(f"Found {len(json_files)} JSON file(s) to convert...")
    print()
    
    # Convert each JSON file
    success_count = 0
    for json_file in json_files:
        if convert_file(json_file, output_path):
            success_count += 1
    
    print()
    print(f"Conversion complete: {success_count}/{len(json_files)} files converted successfully")


def main():
    """
    Main entry point for the script.
    
    Sets up default directories (datasets/ and outputs/) but allows
    custom directories to be specified via command line arguments.
    """
    # Get project root directory (parent of scripts directory)
    project_root = Path(__file__).parent.parent
    datasets_dir = project_root / "datasets"
    output_dir = project_root / "outputs"
    
    # Allow custom directories to be specified via command line arguments
    if len(sys.argv) > 1:
        datasets_dir = Path(sys.argv[1])
    if len(sys.argv) > 2:
        output_dir = Path(sys.argv[2])
    
    batch_convert(datasets_dir, output_dir)


if __name__ == "__main__":
    main()

