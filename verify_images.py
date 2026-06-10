from db.database import SessionLocal
from db.crud import get_destination_by_name

db = SessionLocal()

# Imlili had a generic image that was likely deleted.
print("Fetching destination Imlili...")
dest = get_destination_by_name(db, "Imlili")
if dest and dest.images:
    for img in dest.images:
        print(f"Success! Image for {dest.name}: {img.url}")
else:
    print(f"No image found for {dest.name if dest else 'None'}")

# Ighzrane
print("Fetching destination Ighzrane...")
dest2 = get_destination_by_name(db, "Ighzrane")
if dest2 and dest2.images:
    for img in dest2.images:
        print(f"Success! Image for {dest2.name}: {img.url}")
else:
    print(f"No image found for {dest2.name if dest2 else 'None'}")

db.close()
