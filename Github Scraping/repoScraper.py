import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, urljoin
from pathlib import Path

BASE_URL = "https://github.com"
MAX_RESULTS = 10

search = input("What do you want to search on GitHub? ").strip()

if not search:
    print("Please enter a search term.")
    exit()

search_url = (
    f"{BASE_URL}/search"
    f"?q={quote(search)}"
    f"&type=repositories"
)

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

try:
    response = requests.get(
        search_url,
        headers=headers,
        timeout=50
    )

    if response.status_code == 429:
        print("GitHub is rate-limiting your request.")
        print("Please wait and try again later.")
        exit()

    response.raise_for_status()

except requests.RequestException as error:
    print("Failed to access GitHub.")
    print("Error:", error)
    exit()

soup = BeautifulSoup(response.text, "html.parser")

# Find repository links
repository_links = soup.select(
    "a[href*='/'][data-testid='results-list']"
)

# Fallback selector if the first selector finds nothing
if not repository_links:
    repository_links = soup.select(
        "a[href^='/'][data-hovercard-type='repository']"
    )

results = []

for link_tag in repository_links:

    href = link_tag.get("href", "").strip()

    if not href:
        continue

    link = urljoin(BASE_URL, href)

    # Make sure this is a repository URL
    if link.count("/") < 4:
        continue

    title = link_tag.get_text(" ", strip=True)

    if not title:
        continue

    results.append((title, link))

    if len(results) >= MAX_RESULTS:
        break


# Save results
output_file = Path(__file__).parent / "github.txt"

with open(output_file, "w", encoding="utf-8") as file:

    for title, link in results:
        file.write(f"{title} - {link}\n")


# Display results
print()
print(f"Found {len(results)} repositories.")

for title, link in results:
    print(f"{title} - {link}")

print()
print(f"Results saved to: {output_file}")