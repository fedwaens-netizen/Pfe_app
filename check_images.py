"""Quick script to check destination image status in the database."""
from db.database import SessionLocal, Destination, DestinationImage, Place

db = SessionLocal()

dests = db.query(Destination).all()
print(f"Total destinations: {len(dests)}")

imgs = db.query(DestinationImage).count()
print(f"Total images in DB: {imgs}")

places = db.query(Place).count()
print(f"Total places in DB: {places}")

no_images = []
broken_images = []

print("\n--- All destinations with image status ---")
for d in dests:
    ic = len(d.images)
    pc = len(d.places)
    img_urls = [i.url for i in d.images[:3]]
    
    if ic == 0:
        no_images.append(d.name)
    else:
        for i in d.images:
            if not i.url or i.url.strip() == "" or "placehold" in i.url.lower():
                broken_images.append((d.name, i.url))
    
    print(f"  {d.name}: {ic} imgs, {pc} places")
    for url in img_urls:
        print(f"    -> {url[:100]}")

print(f"\n--- DESTINATIONS WITHOUT IMAGES ({len(no_images)}) ---")
for n in no_images:
    print(f"  ❌ {n}")

print(f"\n--- BROKEN/PLACEHOLDER IMAGES ({len(broken_images)}) ---")
for name, url in broken_images:
    print(f"  ⚠️  {name}: {url[:80]}")

# Check places with missing images
places_no_img = db.query(Place).filter((Place.image_url == None) | (Place.image_url == "")).all()
print(f"\n--- PLACES WITHOUT IMAGES ({len(places_no_img)}) ---")
for p in places_no_img[:20]:
    print(f"  ❌ {p.name} (destination_id={p.destination_id})")

db.close()
