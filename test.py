import pandas as pd
import json
import sys
from pathlib import Path
from collections import OrderedDict

def process_csv(input_file):
    try:
        # Read the CSV file
        df = pd.read_csv(input_file)
        
        # Check if 'result' column exists
        if 'result' not in df.columns:
            print("Error: 'result' column not found in the CSV file")
            return
        
        # Function to safely parse JSON strings
        def parse_json(x):
            try:
                if pd.isna(x):
                    return {}
                return json.loads(x) if isinstance(x, str) else x
            except json.JSONDecodeError:
                print(f"Warning: Could not parse JSON for value: {x}")
                return {}
        
        # Parse JSON in the result column
        df['result'] = df['result'].apply(parse_json)
        
        # Get all unique keys while preserving order of first appearance
        ordered_keys = OrderedDict()
        for json_obj in df['result']:
            if isinstance(json_obj, dict):
                for key in json_obj:
                    ordered_keys[key] = None
        
        # Create new columns for each JSON key in order
        for key in ordered_keys:
            df[key] = df['result'].apply(lambda x: x.get(key) if isinstance(x, dict) else None)
        
        # Generate output filename
        input_path = Path(input_file)
        output_file = input_path.parent / f"{input_path.stem}new{input_path.suffix}"
        
        # Save the processed data
        df.to_csv(output_file, index=False)
        print(f"Successfully processed {input_file}")
        print(f"Output saved to: {output_file}")
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python test.py <input_csv_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    process_csv(input_file)

if __name__ == "__main__":
    main()
