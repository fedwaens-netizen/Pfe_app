import json

def compare_lists():
    json_path = r"c:\App\touristes\morocco_data.json"
    names_path = r"c:\App\touristes\names.txt"
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    current_names = {d['name'].lower() for d in data}
    
    try:
        with open(names_path, 'r', encoding='utf-8') as f:
            provided_names = [line.strip() for line in f if line.strip() and line.strip() != '.']
    except UnicodeDecodeError:
        with open(names_path, 'r', encoding='latin-1') as f:
            provided_names = [line.strip() for line in f if line.strip() and line.strip() != '.']
    
    missing = [name for name in provided_names if name.lower() not in current_names]
    
    print(f"Current unique count: {len(current_names)}")
    print(f"Provided in names.txt: {len(provided_names)}")
    print(f"Missing from names.txt in dataset: {len(missing)}")
    if missing:
        print("Missing destinations:")
        for m in missing:
            print(f"- {m}")

if __name__ == "__main__":
    compare_lists()
