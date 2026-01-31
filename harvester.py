import requests
from bs4 import BeautifulSoup
import os
import time

# --- CONFIGURATION ---
category_urls = [
    "https://pk.khaadi.com/new-in.html",
    "https://pk.khaadi.com/ready-to-wear.html",
    "https://pk.khaadi.com/unstitched.html",
    "https://pk.khaadi.com/west.html", 
    "https://pk.khaadi.com/sale.html"
]

link_file = "links.txt"
base_url = "https://pk.khaadi.com"
PAGE_SIZE = 24 
MAX_LOOPS = 5 # Reduced to 5 to be safe and faster

# We use a Session to keep cookies (Like a real browser)
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5'
})

print("HARVESTER: Starting Session Scan...")

# 1. Load existing links
existing_links = set()
if os.path.exists(link_file):
    with open(link_file, 'r') as f:
        existing_links = set(line.strip() for line in f.readlines() if line.strip())

print(f" -> Database start count: {len(existing_links)}")
total_new_found = 0

for category_url in category_urls:
    print(f"\n--- Scanning Category: {category_url} ---")
    
    for loop_count in range(MAX_LOOPS):
        offset = loop_count * PAGE_SIZE
        
        # LOGIC: If Offset is 0, use the clean URL. 
        # If Offset > 0, ONLY add 'start=XX' (No 'sz' parameter)
        if offset == 0:
            target_url = category_url
        else:
            separator = '&' if '?' in category_url else '?'
            target_url = f"{category_url}{separator}start={offset}"
            
        print(f"   Reading Offset {offset}...")
        
        try:
            response = session.get(target_url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Check if we hit the "Oops" page or error page
                page_title = soup.find('title')
                if page_title and "Oops" in page_title.text:
                    print("   -> Hit 'Oops' Page. The website didn't like this Offset. Stopping category.")
                    break

                product_divs = soup.find_all('div', class_='pdp-link')
                
                if not product_divs:
                    print("   -> No products found (End of List). Stopping category.")
                    break
                
                page_new_count = 0
                for div in product_divs:
                    link_tag = div.find('a')
                    if link_tag and link_tag.get('href'):
                        raw_link = link_tag.get('href')
                        full_link = base_url + raw_link if not raw_link.startswith('http') else raw_link
                        
                        if '?' in full_link:
                            full_link = full_link.split('?')[0]

                        if full_link not in existing_links:
                            existing_links.add(full_link)
                            page_new_count += 1
                            total_new_found += 1
                
                print(f"      -> Found {page_new_count} NEW items.")
                
                # If we found 0 items on a page that SHOULD have items, the pagination might be repeating.
                # We stop to prevent infinite loops.
                if page_new_count == 0 and len(product_divs) > 0:
                     print("      -> Saw products but they are all old. Stopping category.")
                     break

            else:
                print(f"   -> Error Status: {response.status_code}")
                break 
                
        except Exception as e:
            print(f"   -> Error: {e}")
            
        time.sleep(2) # Be polite

# Save
if total_new_found > 0:
    with open(link_file, 'w') as f:
        for link in existing_links:
            f.write(link + "\n")
    print(f"\nSUCCESS: Added {total_new_found} NEW products.")
else:
    print("\nScan Complete. No new products found.")
