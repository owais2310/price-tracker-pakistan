import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime
import time

# --- CONFIGURATION ---
input_file = "links.txt"
csv_filename = "prices.csv"
BATCH_SAVE_SIZE = 10  # Save to CSV every 10 items (Safety net)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Use a Session for 2x Speed
session = requests.Session()
session.headers.update(headers)

print(f"ENTERPRISE TRACKER: Initializing Batch Job at {datetime.now()}...")

# 1. Read Links
if not os.path.exists(input_file):
    print("Error: links.txt not found!")
    exit()

with open(input_file, 'r') as f:
    urls = [line.strip() for line in f.readlines() if line.strip()]

total_links = len(urls)
print(f" -> Queue Size: {total_links} products.")

# 2. Check if CSV exists to write headers
file_exists = os.path.isfile(csv_filename)
if not file_exists:
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Name", "SKU", "Price", "Link"])

# 3. Processing Loop
current_batch = []
success_count = 0
error_count = 0

for i, url in enumerate(urls):
    # Print Progress every item
    print(f"[{i+1}/{total_links}] Scanning...", end="\r")
    
    try:
        # Retry Logic (Try 3 times if fails)
        response = None
        for attempt in range(3):
            try:
                response = session.get(url, timeout=10)
                if response.status_code == 200:
                    break
            except:
                time.sleep(2) # Wait before retry
        
        if response and response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract Data (Robust checks)
            price_tag = soup.find('span', class_='cc-price')
            price = price_tag.get('content') if price_tag else "0"
            
            # Cleanup Price (Remove 'PKR' or commas if present)
            price = price.replace(',', '').replace('PKR', '').strip()
            
            sku_tag = soup.find('span', class_='product-id')
            sku = sku_tag.text.strip() if sku_tag else "Unknown"
            
            name_tag = soup.find('div', class_='product-brand')
            # If standard tag fails, try fallback (Title)
            if not name_tag:
                 name_tag = soup.find('h1', class_='pdp-product-name')
            name = name_tag.text.strip() if name_tag else "Unknown"

            # Add to batch
            today = datetime.now().strftime("%Y-%m-%d")
            # Only save if price is valid
            if price != "0":
                data_row = [today, name, sku, price, url]
                current_batch.append(data_row)
                success_count += 1
            else:
                # 0 Price usually means Out of Stock or Error
                error_count += 1
                
        else:
            error_count += 1

    except Exception as e:
        error_count += 1

    # 4. SAVE BATCH (The Safety Net)
    if len(current_batch) >= BATCH_SAVE_SIZE or (i == total_links - 1):
        if current_batch:
            with open(csv_filename, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(current_batch)
            print(f"[{i+1}/{total_links}] Saved {len(current_batch)} items. (Total Success: {success_count})")
            current_batch = [] # Clear memory
    
    # Speed Control (0.5s is fast but safe with Session)
    time.sleep(0.5)

print(f"\nJOB COMPLETE.")
print(f" -> Success: {success_count}")
print(f" -> Errors/Stockouts: {error_count}")
