import json

def deduplicate():
    target_file = r"c:\App\touristes\morocco_data.json"
    print(f"Reading from {target_file}")
    with open(target_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    unique_map = {}
    duplicates_count = 0
    
    cleaned_data = []
    for entry in data:
        name = entry.get("name")
        if name in unique_map:
            print(f"Duplicate found: {name}")
            duplicates_count += 1
            continue
        unique_map[name] = True
        cleaned_data.append(entry)
        
    print(f"Total entries before: {len(data)}")
    print(f"Total entries after: {len(cleaned_data)}")
    print(f"Duplicates removed: {duplicates_count}")
    
    with open(target_file, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, indent=4, ensure_ascii=False)
    print("Deduplication complete.")

if __name__ == "__main__":
    deduplicate()
