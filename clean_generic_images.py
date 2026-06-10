import os
import sys

# Ensure the root directory is in the python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.database import SessionLocal, DestinationImage
from collections import Counter

def clean_duplicate_images():
    db = SessionLocal()
    print("Fetching all destination images...")
    all_images = db.query(DestinationImage).all()
    
    # Count occurrences of each URL
    url_counts = Counter([img.url for img in all_images])
    
    # Identify generic/duplicate URLs (appear more than 3 times)
    generic_urls = {url for url, count in url_counts.items() if count > 3}
    
    if not generic_urls:
        print("No duplicate generic images found.")
        db.close()
        return
        
    print(f"Found {len(generic_urls)} generic image URLs that are repeated.")
    
    deleted_count = 0
    for img in all_images:
        if img.url in generic_urls:
            db.delete(img)
            deleted_count += 1
            
    db.commit()
    print(f"Successfully deleted {deleted_count} generic image entries from the database.")
    db.close()

if __name__ == "__main__":
    clean_duplicate_images()
