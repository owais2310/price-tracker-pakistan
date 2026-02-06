import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime
import random
import time
import re  # <--- The Regex Tool

class UltimateHarvester:
    def __init__(self):
        self.prices_file = "prices.csv"
        self.links_file = "links.txt"
        
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://pk.khaadi.com/"
        }
        
        self.cookies = {
            "store": "pk",
            "context": "b2c_pk_store_view"
        }

    def fetch_page(self, url):
        try:
            time.sleep(random.uniform(1, 3)) 
            response = requests.get(url, headers=self.headers, cookies=self.cookies, timeout=10)
            if response.status_code == 200:
                return response.text
            return None
        except Exception:
            return None

    def parse_product(self, url):
        """REGEX MODE: Scans raw text for 'price': 9500 pattern."""
        if "pk.khaadi.com" not in url:
            return None

        html = self.fetch_page(url)
        if not html:
            return None

        # 1. GET NAME (Standard method)
        soup = BeautifulSoup(html, 'html.parser')
        name_element = soup.find('h1', class_='page-title')
        if name_element:
            name = name_element.get_text(strip=True)
        else:
            name = "Unknown Product"

        # 2. GET PRICE (The Vacuum Method)
        # This regex looks for "price": "1234" OR "price": 1234 anywhere in the file
        # It catches the dataLayer, JSON-LD, and GA4 tags.
        price_matches = re.findall(r'"price"\s*:\s*"?([\d,.]+)"?', html)
        
        found_price = None
        
        for p in price_matches:
            try:
                # Clean the number (remove dots and commas)
                # "9500.00" -> "9500"
                if "." in p:
                    p = p.split(".")[0]
                
                clean_digits = ''.join(filter(str.isdigit, p))
                
                if clean_digits:
                    amount = int(clean_digits)
                    # THE FILTER: Must be real price (> 500)
                    if amount > 500:
                        found_price = amount
                        break
            except:
                continue

        if not found_price:
            print(f"⚠️ Skipped: No valid price > 500 found for {url}")
            return None

        return {
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Name": name,
            "Price": found_price,
            "Link": url
        }

    def harvest(self):
        if not os.path.exists(self.links_file):
            return

        with open(self.links_file, "r") as f:
            links = [line.strip() for line in f if line.strip()]

        print(f"🚀 Starting Regex Harvest on {len(links)} products...")
        
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
