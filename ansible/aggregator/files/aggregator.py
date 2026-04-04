import json
import glob
import os
from datetime import datetime

def aggregate_jsons():
    # Set up paths
    output_dir = "/var/tmp/aggregator"
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%min")
    output_file = os.path.join(output_dir, f"aggregator-{timestamp}.json")
    
    # Ensure directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    final_data = {}
    # Recursive wildcard to find logs in all role folders
    search_pattern = "roles/*/files/logs/*.json"
    found_files = glob.glob(search_pattern)

    for filename in found_files:
        with open(filename, 'r') as f:
            try:
                data = json.load(f)
                final_data.update(data)
            except json.JSONDecodeError:
                continue
    
    with open(output_file, 'w') as f:
        json.dump(final_data, f, indent=4)
    
    print(f"Aggregated {len(found_files)} files into {output_file}")

if __name__ == "__main__":
    aggregate_jsons()