import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path

BASE_URL = "https://www.onlinejobs.ph"
SEARCH_URL = f"{BASE_URL}/jobseekers/jobsearch"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# Ask the user what job they want
job_search = input("What job are you looking for? ").strip()

if not job_search:
    print("Please enter a job title.")
    exit()

try:
    response = requests.get(
        SEARCH_URL,
        headers=headers,
        timeout=10
    )

    response.raise_for_status()

except requests.RequestException as error:
    print("Failed to access OnlineJobs.ph")
    print("Error:", error)
    exit()

soup = BeautifulSoup(response.text, "html.parser")

# Find all job titles
jobs = soup.select(".jobseeker-search .results h4")

matching_jobs = []

for job in jobs:

    title = job.get_text(" ", strip=True)

    # Case-insensitive search
    if job_search.lower() not in title.lower():
        continue

    # Find the job link
    link_tag = job.find("a", href=True)

    if link_tag is None:
        parent = job.parent

        while parent is not None:
            links = parent.find_all(
                "a",
                href=lambda href: (
                    href and "/jobseekers/job/" in href
                )
            )

            if links:
                link_tag = links[0]
                break

            parent = parent.parent

    if link_tag:
        link = urljoin(
            BASE_URL,
            link_tag["href"]
        )
    else:
        link = "No link found"

    matching_jobs.append((title, link))


# Save results
output_file = Path(__file__).parent / "jobs.txt"

with open(output_file, "w", encoding="utf-8") as file:

    for title, link in matching_jobs:
        file.write(f"{title} - {link}\n")


# Display results
print()
print(f"Found {len(matching_jobs)} matching jobs.")

for title, link in matching_jobs:
    print(f"{title} - {link}")

print()
print(f"Results saved to: {output_file}")