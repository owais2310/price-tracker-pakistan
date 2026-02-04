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
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def fetch_page(self, url):
        """Downloads the HTML of the page nicely."""
        try:
            time.sleep(random.uniform(1, 3)) # Sleep to act human
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.text
            return None
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")
            return None

    def parse_product(self, url):
        """Extracts the Real Name and Real Price (ignoring discounts)."""
        html = self.fetch_page(url)
        if not html:
            return None

        soup = BeautifulSoup(html, 'html.parser')
        
        try:
            # --- 1. SMART NAME EXTRACTOR ---
            # Try to find the specific H1 title first (Class usually 'page-title')
            name_element = soup.find('h1', class_='page-title')
            
            if name_element:
                # Found the specific title
                name = name_element.get_text(strip=True)
            else:
                # Fallback: Try any H1 if specific class is missing
                h1_tag = soup.find('h1')
                if h1_tag:
                    name = h1_tag.get_text(strip=True)
                else:
                    name = "Unknown Product"

            # --- 2. SMART PRICE EXTRACTOR ---
            # Find all potential price numbers on the page
            price_elements = soup.find_all(class_='price')
            
            found_price = None
            
            for p in price_elements:
                text = p.get_text(strip=True)
                # Clean the text: remove 'PKR', 'Rs', commas, etc.
                digits = ''.join(filter(str.isdigit, text))
                
                if digits:
                    amount = int(digits)
                    
                    # THE SAFETY FILTER: 
                    # If price is < 500, it is likely a "30% OFF" label or a glitch.
                    # Khaadi suits are rarely Rs. 40.
                    if amount > 500:
                        found_price = amount
                        break # Stop as soon as we find a realistic price
            
            if not found_price:
                print(f"⚠️ Skipped: No valid price > Rs. 500 found for {url}")
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
        """Main loop: Reads links, gets prices, saves to CSV."""
        if not os.path.exists(self.links_file):
            print("Error: links.txt not found!")
            return

        # Read all links
        with open(self.links_file, "r") as f:
            links = [line.strip() for line in f if line.strip()]

        print(f"🚀 Starting harvest on {len(links)} products...")
        
        new_data = []
        for index, link in enumerate(links):
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
            
        print(f"\n✅ Harvest Complete! Added {len(new_data)} prices to database.")

if __name__ == "__main__":
    bot = UltimateHarvester()
    bot.harvest()
