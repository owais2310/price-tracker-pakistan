import requests
from bs4 import BeautifulSoup
import json

# The link that failed (from your log)
URL = "https://pk.khaadi.com/tailored-3-piece/T-A22-26-119FG1-VG_MULTI.html"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://pk.khaadi.com/"
}
cookies = {"store": "pk", "context": "b2c_pk_store_view"}

print(f"🕵️‍♂️ Scanning: {URL}")
response = requests.get(URL, headers=headers, cookies=cookies)
soup = BeautifulSoup(response.text, 'html.parser')

print("\n--- 1. META TAG PRICES (Robot Data) ---")
for tag in soup.find_all("meta"):
    if "price" in str(tag).lower():
        print(tag)

print("\n--- 2. JSON DATA (Hidden Data) ---")
# Look for Schema.org data
scripts = soup.find_all('script', type='application/ld+json')
for s in scripts:
    print(s.string[:500]) # Print first 500 chars

print("\n--- 3. VISIBLE PRICE ELEMENTS ---")
# Print anything that looks like a price
for p in soup.find_all(class_=lambda x: x and 'price' in x):
    text = p.get_text(strip=True)
    if any(char.isdigit() for char in text):
        print(f"Class: {p.get('class')} | Text: {text}")

print("\n--- TEST COMPLETE ---")
