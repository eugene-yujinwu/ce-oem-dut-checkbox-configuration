import json
import sys

def update_json(file1_path, file2_path):
    # Read the first JSON file
    try:
        with open(file1_path, 'r') as f1:
            data1 = json.load(f1)
    except FileNotFoundError:
        print(f"Error: File {file1_path} does not exist")
        return
    except json.JSONDecodeError:
        print(f"Error: File {file1_path} is not a valid JSON file")
        return

    # Read the second JSON file
    try:
        with open(file2_path, 'r') as f2:
            data2 = json.load(f2)
    except FileNotFoundError:
        print(f"Error: File {file2_path} does not exist")
        return
    except json.JSONDecodeError:
        print(f"Error: File {file2_path} is not a valid JSON file")
        return

    # Verify both data structures are dictionaries
    if not isinstance(data1, dict) or not isinstance(data2, dict):
        print("Error: Both JSON files must contain dictionary objects")
        return

    # Compare keys and add missing ones
    added_keys = []
    for key in data1:
        if key not in data2:
            data2[key] = True
            added_keys.append(key)

    # If no keys were added
    if not added_keys:
        print(f"File {file2_path} already contains all keys from {file1_path}")
        return

    # Write updated data back to the second file
    try:
        with open(file2_path, 'w') as f2:
            json.dump(data2, f2, indent=4, sort_keys=True)
            # Add trailing newline for Unix compatibility
            f2.write('\n')
    except IOError:
        print(f"Error: Could not write to file {file2_path}")
        return

    # Print results
    print(f"Added {len(added_keys)} keys to {file2_path}:")
    for key in added_keys:
        print(f"  - {key}")

if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) != 3:
        print("Usage: python update_json.py <source_JSON> <target_JSON>")
        print("Example: python update_json.py features1.json features2.json")
        sys.exit(1)
    
    # Get file paths
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    
    # Execute update
    update_json(file1, file2)