from playwright.sync_api import sync_playwright
import time
import os

# --- CONFIGURATION ---
# The main aisles of the store. Add more if you want (Kids, Home, etc.)
categories = [
    "https://pk.khaadi.com/new-in.html",
    "https://pk.khaadi.com/unstitched.html",
    "https://pk.khaadi.com/ready-to-wear.html",
    "https://pk.khaadi.com/west.html",
    "https://pk.khaadi.com/sale.html"
]

link_file = "links.txt"

def harvest_category(page, url):
    print(f"\n--- Navigating to: {url} ---")
    page.goto(url, timeout=60000) # Give it 60 seconds to load
    
    # 1. Handle "Accept Cookies" or Popups (optional, but good practice)
    try:
        page.locator("button:has-text('Accept')").click(timeout=2000)
    except:
        pass

    # 2. THE INFINITE SCROLL HACK
    # We scroll down, wait for new items, and repeat until no new items appear.
    last_height = page.evaluate("document.body.scrollHeight")
    scroll_attempts = 0
    max_scrolls = 50  # Safety limit (50 scrolls * 24 items = 1200 items per category)
    
    print("   -> Starting Infinite Scroll...")
    
    while scroll_attempts < max_scrolls:
        # Scroll to bottom
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        print(f"      Scroll {scroll_attempts+1}/{max_scrolls}...")
        
        # Wait for potential load (4 seconds)
        time.sleep(4)
        
        # Calculate new height
        new_height = page.evaluate("document.body.scrollHeight")
        
        # If height didn't change, we reached the bottom!
        if new_height == last_height:
            print("      -> Reached the bottom of the page!")
            break
            
        last_height = new_height
        scroll_attempts += 1

    # 3. Extract Links
    print("   -> Extracting product links...")
    # This finds all 'a' tags that look like products
    links = page.locator("div.pdp-link a").evaluate_all("list => list.map(element => element.href)")
    
    return links

def main():
    print("ULTIMATE HARVESTER: Initializing Browser Engine...")
    
    unique_links = set()
    
    # Load existing database
    if os.path.exists(link_file):
        with open(link_file, 'r') as f:
            unique_links = set(line.strip() for line in f.readlines() if line.strip())
    
    print(f" -> Current Database Size: {len(unique_links)}")

    with sync_playwright() as p:
        # --- SMART MODE ---
        # If "GITHUB_ACTIONS" exists, we are on the cloud -> Use Headless (Invisible)
        # If not, we are on your laptop -> Use Headaded (Visible)
        is_cloud = os.getenv("GITHUB_ACTIONS") == "true"
        
        if is_cloud:
            print(" -> Detected Cloud Environment. Running in INVISIBLE Mode.")
        else:
            print(" -> Detected Laptop. Running in VISIBLE Mode.")

        # Launch Browser with the smart flag
        browser = p.chromium.launch(headless=is_cloud)
        
        # Create a new page
        page = browser.new_page()
        
        for url in categories:
            try:
                found_links = harvest_category(page, url)
                
                # Filter and Add
                new_count = 0
                for link in found_links:
                    if '?' in link:
                        clean_link = link.split('?')[0]
                    else:
                        clean_link = link
                        
                    if clean_link not in unique_links:
                        unique_links.add(clean_link)
                        new_count += 1
                
                print(f"   -> Found {len(found_links)} total items. {new_count} were NEW.")
                
            except Exception as e:
                print(f"   -> Error on {url}: {e}")

        browser.close()

    # Save to file
    print(f"\nSaving Master Database...")
    with open(link_file, 'w') as f:
        for link in sorted(unique_links):
            f.write(link + "\n")
            
    print(f"SUCCESS: Total Genuine Database: {len(unique_links)} products.")

if __name__ == "__main__":
    main()
