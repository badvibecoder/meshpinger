import json
import glob
import os
from datetime import datetime

def deep_merge(source, destination):
    """
    Recursively merges source dict into destination dict.
    """
    for key, value in source.items():
        if isinstance(value, dict):
            node = destination.setdefault(key, {})
            deep_merge(value, node)
        else:
            destination[key] = value
    return destination

def is_valid_modern_format(data, test_type):
    """
    Checks if the JSON data contains the 'status' key 
    within the expected test structure.
    """
    try:
        # Data structure: { "hostname": { "tests": { "test_type": { "timestamp": { "status": "pass" } } } } }
        for hostname in data:
            test_entry = data[hostname].get("tests", {}).get(test_type, {})
            for timestamp in test_entry:
                if "status" in test_entry[timestamp]:
                    return True
    except Exception:
        return False
    return False

def get_latest_files(found_files):
    """
    Groups files by Node and Test Type, returning only the newest 
    VALID file (containing a status key) for each.
    """
    latest_map = {}

    for filepath in found_files:
        if "aggregator-" in filepath:
            continue

        filename = os.path.basename(filepath)
        
        # Identify Test Type
        if "pingtest" in filename:
            test_type = "backendpingtest"
            category = "pingtest"
        elif "eterrors" in filename:
            test_type = "ethtool_errors"
            category = "eterrors"
        else:
            continue

        # Reconstruct node name
        node_name = filename.split(f"-{category}")[0]
        
        # --- NEW VALIDATION STEP ---
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                if not is_valid_modern_format(data, test_type):
                    # Skip files that don't have the "status" key
                    continue
        except (json.JSONDecodeError, IOError):
            continue
        # ---------------------------

        mtime = os.path.getmtime(filepath)
        group_key = (node_name, category)

        if group_key not in latest_map or mtime > latest_map[group_key]['mtime']:
            latest_map[group_key] = {
                'path': filepath,
                'mtime': mtime
            }
    
    return [info['path'] for info in latest_map.values()]

def aggregate_jsons():
    output_dir = "/var/tmp/aggregator"
    timestamp_str = datetime.now().strftime("%Y-%m-%d-%H-%M")
    output_file = os.path.join(output_dir, f"aggregator-{timestamp_str}.json")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    search_pattern = "*/files/logs/*.json" 
    all_files = glob.glob(search_pattern)

    # Filter to only the newest files that pass the "status" key check
    files_to_process = get_latest_files(all_files)

    print(f"DEBUG: Found {len(all_files)} total files.")
    print(f"DEBUG: Processing {len(files_to_process)} modern files (with status key).")

    if not files_to_process:
        print("WARNING: No modern JSON files (containing 'status') were found.")
        return

    final_data = {}

    for filename in files_to_process:
        with open(filename, 'r') as f:
            try:
                data = json.load(f)
                deep_merge(data, final_data)
            except json.JSONDecodeError:
                continue

    with open(output_file, 'w') as f:
        json.dump(final_data, f, indent=4)

    print(f"Successfully aggregated {len(final_data)} unique nodes into {output_file}")

if __name__ == "__main__":
    aggregate_jsons()
