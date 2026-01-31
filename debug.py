import requests
from bs4 import BeautifulSoup

# We will test ONLY the Unstitched category
base_url = "https://pk.khaadi.com/unstitched.html"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def check_page(offset):
    url = f"{base_url}?start={offset}&sz=24" # I added '&sz=24' to force the size
    print(f"\n--- Checking Offset {offset} ---")
    print(f"URL: {url}")
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the first product title
    # Note: We use the 'pdp-link-heading' class you found earlier
    first_product = soup.find('h2', class_='pdp-link-heading')
    
    if first_product:
        print(f"FIRST PRODUCT NAME: {first_product.text.strip()}")
    else:
        print("ERROR: No products found on this page.")

# Check Page 1 (Offset 0)
check_page(0)

# Check Page 2 (Offset 24)
check_page(24)
