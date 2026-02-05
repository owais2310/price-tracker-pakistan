# Script to remove any non-Pakistan links
filename = "links.txt"
try:
    with open(filename, "r") as f:
        lines = f.readlines()

    pk_links = [line for line in lines if "pk.khaadi.com" in line]

    with open(filename, "w") as f:
        f.writelines(pk_links)

    print(f"Done! Cleaned links.txt. Kept {len(pk_links)} Pakistan links.")
    print(f"Removed {len(lines) - len(pk_links)} foreign/junk links.")

except FileNotFoundError:
    print("links.txt not found.")
