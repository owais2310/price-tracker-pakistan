import requests
from bs4 import BeautifulSoup
from datetime import datetime
import random
import time
import re

# --- THE NEW REGEX ENGINE ---
class UltimateHarvester:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://pk.khaadi.com/"
        }
        self.cookies = {"store": "pk", "context": "b2c_pk_store_view"}

    def fetch_page(self, url):
        try:
            print(f"   Context: Fetching {url}...")
            response = requests.get(url, headers=self.headers, cookies=self.cookies, timeout=10)
            if response.status_code == 200:
                return response.text
            return None
        except Exception as e:
            print(f"   Error: {e}")
            return None

    def parse_product(self, url):
        html = self.fetch_page(url)
        if not html: return None

        # 1. GET NAME
        soup = BeautifulSoup(html, 'html.parser')
        name_element = soup.find('h1', class_='page-title')
        name = name_element.get_text(strip=True) if name_element else "Unknown Product"

        # 2. GET PRICE (REGEX VACUUM)
        # Looking for "price": 9500 OR "price": "9500.00"
        price_matches = re.findall(r'"price"\s*:\s*"?([\d,.]+)"?', html)
        
        found_price = None
        for p in price_matches:
            try:
                if "." in p: p = p.split(".")[0] # Remove decimals
                clean = ''.join(filter(str.isdigit, p)) # Remove commas
                
                if clean:
                    amount = int(clean)
                    if amount > 500: # THE FILTER
                        found_price = amount
                        break
            except:
                continue

        if not found_price:
            print(f"   ❌ FAILED: No price > 500 found.")
            return None

        return {"Name": name, "Price": found_price}

# --- THE TEST LAB (5 Problematic Links) ---
links_to_test = [
    "https://pk.khaadi.com/tailored-3-piece/T-A22-26-119FG1-VG_MULTI.html", # Failed before
    "https://pk.khaadi.com/tailored-3-piece/T-A22-26-119FH1-VG_MULTI.html", # Failed before
    "https://pk.khaadi.com/tailored-3-piece/T-A33-26-105FA-VG_MULTI.html", # Failed before
    "https://pk.khaadi.com/trousers/6-26-106-B-A-VG_MULTI.html",            # Failed before
    "https://pk.khaadi.com/tunic/6-26-106-A-A-VG_MULTI.html"                 # Failed before
]

print("🔍 STARTING LOCAL TEST (REGEX MODE)...\n")
bot = UltimateHarvester()

for i, link in enumerate(links_to_test):
    print(f"[{i+1}/5] Testing Link...")
    result = bot.parse_product(link)
    
    if result:
        print(f"   ✅ SUCCESS! Found: {result['Name']}")
        print(f"      Real Price: Rs. {result['Price']}")
        if result['Price'] == 40:
            print("      ⚠️ WARNING: IT IS STILL FINDING 40!")
    else:
        print("   ⚠️ SKIPPED (Blocked or Empty)")
    print("-" * 40)
