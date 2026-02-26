import json
import os

file_path = "c:\\App\\touristes\\morocco_data.json"

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✅ JSON is valid.")
    print(f"Total destinations: {len(data)}")
    
    names = [d['name'] for d in data]
    unique_names = set(names)
    
    if len(names) != len(unique_names):
        print("❌ Duplicates found!")
        from collections import Counter
        duplicates = [item for item, count in Counter(names).items() if count > 1]
        print(f"Duplicate names: {duplicates}")
    else:
        print("✅ No duplicate names found.")

    # Check for duplicate images
    all_images = []
    for d in data:
        all_images.extend(d.get('images', []))
        for place in d.get('places', []):
            if 'image' in place:
                all_images.append(place['image'])
    
    unique_images = set(all_images)
    print(f"Total images used: {len(all_images)}")
    print(f"Unique images: {len(unique_images)}")
    if len(all_images) != len(unique_images):
        print(f"⚠️  {len(all_images) - len(unique_images)} duplicate image usages found (acceptable if minimal).")

except json.JSONDecodeError as e:
    print(f"❌ JSON Decode Error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")

# Find line numbers of duplicates
if 'duplicates' in locals() and duplicates:
    print("\n--- Finding Duplicate Locations ---")
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for dup in duplicates:
        print(f"Locations for '{dup}':")
        for i, line in enumerate(lines):
            if f'"{dup}"' in line:
                print(f"  Line {i+1}: {line.strip()}")
