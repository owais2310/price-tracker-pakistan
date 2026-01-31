import requests

# Common hiding spots for sitemaps
possible_maps = [
    "https://pk.khaadi.com/sitemap.xml",
    "https://pk.khaadi.com/sitemap_index.xml",
    "https://pk.khaadi.com/media/sitemap/sitemap.xml",
    "https://pk.khaadi.com/robots.txt"
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

print("Searching for the Master Map...")

found = False
for url in possible_maps:
    try:
        print(f"Checking: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f" -> SUCCESS! Found something at: {url}")
            print(f" -> content start: {response.text[:200]}") # Show first 200 chars
            found = True
        else:
            print(f" -> Failed ({response.status_code})")
            
    except Exception as e:
        print(f" -> Error: {e}")

if not found:
    print("\nCould not find a standard sitemap. We might need to inspect the Network Tab.")
