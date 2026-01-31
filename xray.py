import requests

# The URL that was failing in your screenshot
url = "https://pk.khaadi.com/unstitched.html?start=24&sz=24"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

print(f"Connecting to: {url}")
response = requests.get(url, headers=headers)

print(f"Status Code: {response.status_code}")

# We save exactly what the website sent us into a file
filename = "robot_view.html"
with open(filename, "w", encoding="utf-8") as f:
    f.write(response.text)

print(f"SUCCESS: Saved the website content to '{filename}'")
print(f" -> Go to your folder and open '{filename}' in your browser.")
