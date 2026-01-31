import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime
import time

# --- CONFIGURATION ---
input_file = "links.txt"   # The list of products to track
csv_filename = "prices.csv" # The database

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

print(f"Starting Batch Job: {datetime.now()}")

# 1. Read the list of links
with open(input_file, 'r') as f:
    urls = f.read().splitlines()

# 2. Loop through each link
for url in urls:
    if not url.strip(): continue # Skip empty lines
    
    print(f"Checking: {url[:50]}...") # Print first 50 chars of link
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract Data
            price_tag = soup.find('span', class_='cc-price')
            price = price_tag.get('content') if price_tag else "0"
            
            sku_tag = soup.find('span', class_='product-id')
            sku = sku_tag.text.strip() if sku_tag else "Unknown"
            
            name_tag = soup.find('div', class_='product-brand')
            name = name_tag.text.strip() if name_tag else "Unknown"

            # Prepare Data
            today = datetime.now().strftime("%Y-%m-%d")
            data_row = [today, name, sku, price, url]

            # Save Data
            file_exists = os.path.isfile(csv_filename)
            with open(csv_filename, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                if not file_exists:
                    writer.writerow(["Date", "Name", "SKU", "Price", "Link"])
                writer.writerow(data_row)
            
            print(f" -> Saved: {name} | PKR {price}")
            
        else:
            print(" -> Blocked or Error.")

    except Exception as e:
        print(f" -> Error: {e}")

    # CRITICAL: Wait 2 seconds between requests so Khaadi doesn't ban us
    time.sleep(2)

print("Batch Job Complete.")
