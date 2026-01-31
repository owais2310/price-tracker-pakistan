import requests
import xml.etree.ElementTree as ET
import os

# --- CONFIGURATION ---
# We will guess these common names
possible_maps = [
    "https://pk.khaadi.com/sitemap_index.xml",
    "https://pk.khaadi.com/sitemap_0.xml",
    "https://pk.khaadi.com/sitemap_1.xml",
    "https://pk.khaadi.com/sitemap_2.xml",
    "https://pk.khaadi.com/sitemap_3.xml",
    "https://pk.khaadi.com/sitemap_products_1.xml"
]

link_file = "links.txt"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

print("DEEP HARVESTER: Hunting for hidden maps...")

# 1. Load existing links
existing_links = set()
if os.path.exists(link_file):
    with open(link_file, 'r') as f:
        existing_links = set(line.strip() for line in f.readlines() if line.strip())

print(f" -> Starting count: {len(existing_links)}")
new_links_found = 0

# 2. Check every possible map
for map_url in possible_maps:
    print(f"\nChecking: {map_url}...")
    
    try:
        response = requests.get(map_url, headers=headers)
        
        if response.status_code == 200:
            print("   -> FOUND! Parsing...")
            
            # Try to parse XML
            try:
                root = ET.fromstring(response.content)
                namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
                
                # Extract links
                urls = [elem.text for elem in root.findall('.//ns:loc', namespace)]
                print(f"   -> Contains {len(urls)} links.")
                
                # Filter for Products
                map_new_count = 0
                for url in urls:
                    clean_url = url.strip()
                    # Khaadi products usually end in .html
                    if clean_url.endswith('.html') and clean_url not in existing_links:
                        existing_links.add(clean_url)
                        map_new_count += 1
                        new_links_found += 1
                
                print(f"   -> Added {map_new_count} NEW products.")
                
            except ET.ParseError:
                print("   -> Error: File exists but is not valid XML.")
        else:
            print(f"   -> Not found (Status {response.status_code})")

    except Exception as e:
        print(f"   -> Error: {e}")

# 3. Save
if new_links_found > 0:
    print(f"\nSaving database...")
    with open(link_file, 'w') as f:
        for link in existing_links:
            f.write(link + "\n")
    print(f"SUCCESS: Total Database Size: {len(existing_links)} products.")
else:
    print(f"\nScan Complete. Total Database Size: {len(existing_links)}")
