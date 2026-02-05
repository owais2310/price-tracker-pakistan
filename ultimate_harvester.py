import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime
import random
import time

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
            "context": "b2c_pk_store_view" # This tells Khaadi "I am in Pakistan"
        }

    def fetch_page(self, url):
        """Downloads the HTML using Pakistan Cookies."""
        try:
            time.sleep(random.uniform(1, 3)) # Sleep to act human
            
            # We send the cookies with the request to force PK version
            response = requests.get(url, headers=self.headers, cookies=self.cookies, timeout=10)
            
            if response.status_code == 200:
                return response.text
            return None
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")
            return None

    def parse_product(self, url):
        """Extracts Real Name and Price (PKR Only)."""
        
        # --- PATRIOT FILTER ---
        # If the link is for USA or UK, ignore it immediately.
        if "pk.khaadi.com" not in url:
            print(f"🚫 Ignoring Foreign Link: {url}")
            return None

        html = self.fetch_page(url)
        if not html:
            return None

        soup = BeautifulSoup(html, 'html.parser')
        
        try:
            # --- 1. SMART NAME EXTRACTOR ---
            name_element = soup.find('h1', class_='page-title')
            if name_element:
                name = name_element.get_text(strip=True)
            else:
                h1_tag = soup.find('h1')
                name = h1_tag.get_text(strip=True) if h1_tag else "Unknown Product"

            # --- 2. SMART PRICE EXTRACTOR ---
            price_elements = soup.find_all(class_='price')
            
            found_price = None
            
            for p in price_elements:
                text = p.get_text(strip=True)
                
                # Check for currency symbols to ensure it's not USD
                if "$" in text or "USD" in text or "£" in text:
                    print(f"⚠️ Warning: Found foreign currency in {url}. Skipping.")
                    continue

                # Clean digits
                digits = ''.join(filter(str.isdigit, text))
                
                if digits:
                    amount = int(digits)
                    
                    # LOGIC: Khaadi PK prices are usually > 500
                    if amount > 500:
                        found_price = amount
                        break 
            
            if not found_price:
                print(f"⚠️ Skipped: No valid PKR price > 500 found for {url}")
                return None

            return {
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Name": name,
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
            # Only load valid lines
            links = [line.strip() for line in f if line.strip()]

        print(f"🚀 Starting harvest on {len(links)} products...")
        
        new_data = []
        for index, link in enumerate(links):
            # Double check link before processing
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
