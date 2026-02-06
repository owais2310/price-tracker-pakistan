import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime
import random
import time
import json  # <--- CRITICAL NEW IMPORT

class UltimateHarvester:
    def __init__(self):
        self.prices_file = "prices.csv"
        self.links_file = "links.txt"
        
        # HEADERS: Act like a real Chrome browser
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://pk.khaadi.com/"
        }
        
        # COOKIES: FORCE the server to show Pakistan Store (PKR)
        self.cookies = {
            "store": "pk",
            "context": "b2c_pk_store_view"
        }

    def fetch_page(self, url):
        """Downloads the HTML using Pakistan Cookies."""
        try:
            time.sleep(random.uniform(1, 3)) 
            response = requests.get(url, headers=self.headers, cookies=self.cookies, timeout=10)
            if response.status_code == 200:
                return response.text
            return None
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")
            return None

    def parse_product(self, url):
        """Extracts Data from JSON-LD (Google Data) to avoid HTML errors."""
        if "pk.khaadi.com" not in url:
            return None

        html = self.fetch_page(url)
        if not html:
            return None

        soup = BeautifulSoup(html, 'html.parser')
        
        try:
            found_price = None
            found_name = "Unknown Product"

            # --- STRATEGY 1: JSON-LD (The "Gold Mine") ---
            # We look for the special script tag that contains trusted product data
            json_tags = soup.find_all('script', type='application/ld+json')
            
            for tag in json_tags:
                try:
                    if not tag.string: continue
                    
                    data = json.loads(tag.string)
                    
                    # Search inside the JSON structure
                    # 1. Check if it's a Product
                    if data.get('@type') == 'Product':
                        found_name = data.get('name', found_name)
                        
                        # 2. Extract Price from 'offers'
                        offers = data.get('offers')
                        price_raw = None
                        
                        if isinstance(offers, dict):
                            price_raw = offers.get('price')
                        elif isinstance(offers, list) and len(offers) > 0:
                            price_raw = offers[0].get('price')
                            
                        # 3. Clean and Validate Price
                        if price_raw:
                            # Remove decimals "9500.00" -> "9500"
                            price_str = str(price_raw).split('.')[0] 
                            clean_price = int(''.join(filter(str.isdigit, price_str)))
                            
                            if clean_price > 500:
                                found_price = clean_price
                                break # Stop searching, we found it!
                                
                except Exception as json_error:
                    continue

            # --- STRATEGY 2: FALLBACK HTML (Backup Plan) ---
            # If JSON failed, try the old HTML method but with STRICT checks
            if not found_price:
                price_elements = soup.find_all(class_='price')
                for p in price_elements:
                    text = p.get_text(strip=True)
                    
                    # CRITICAL FIX: Stop reading at the dot!
                    if "." in text: 
                        text = text.split(".")[0]
                        
                    digits = ''.join(filter(str.isdigit, text))
                    
                    if digits:
                        amount = int(digits)
                        if amount > 500:
                            found_price = amount
                            break

            # --- FINAL VALIDATION ---
            if not found_price:
                print(f"⚠️ Skipped: No valid price > 500 found for {url}")
                return None

            return {
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Name": found_name,
                "Price": found_price,
                "Link": url
            }

        except Exception as e:
            print(f"Error parsing {url}: {e}")
            return None

    def harvest(self):
        """Main loop."""
        if not os.path.exists(self.links_file):
            print("Error: links.txt not found!")
            return

        with open(self.links_file, "r") as f:
            links = [line.strip() for line in f if line.strip()]

        print(f"🚀 Starting harvest on {len(links)} products...")
        
        new_data = []
        for index, link in enumerate(links):
            if "pk.khaadi.com" not in link:
                continue

            print(f"[{index+1}/{len(links)}] Scanning: {link[:50]}...")
            product = self.parse_product(link)
            
            if product:
                new_data.append(product)
                print(f"   ✅ Found: {product['Name']} - Rs. {product['Price']}")

        # Save to CSV
        file_exists = os.path.exists(self.prices_file)
        
        with open(self.prices_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["Date", "Name", "Price", "Link"])
            if not file_exists:
                writer.writeheader()
            writer.writerows(new_data)
            
        print(f"\n✅ Harvest Complete! Added {len(new_data)} prices.")

if __name__ == "__main__":
    bot = UltimateHarvester()
    bot.harvest()
