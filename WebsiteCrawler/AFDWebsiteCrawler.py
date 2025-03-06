import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Base URL (Change if needed)
BASE_URL = "https://web.archive.org/web/20250224090619/https://www.afd.de/"

# Set up storage folder
FOLDER_PATH = os.path.join("Data", "AFD Website Texts")
os.makedirs(FOLDER_PATH, exist_ok=True)

# Track visited links to avoid duplicate crawling
visited_links = set()


def get_internal_links(soup, base_url):
    """Extract all internal links from a BeautifulSoup object."""
    internal_links = set()
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        full_url = urljoin(base_url, href)

        # Ensure it's an internal link (same domain)
        if "afd.de" in urlparse(full_url).netloc:
            full_url_webarchive = full_url.replace("https://www.afd.de/", "")
            internal_links.add(base_url + full_url_webarchive)

    return internal_links


def clean_filename(url):
    """Generate a safe filename based on the URL."""
    parsed_url = urlparse(url)
    filename = parsed_url.path.strip("/").replace("/", "_")
    filename = filename.replace("web_20250224090619_https:__www.afd.de", "")
    if filename == "":
        filename = "AFD Main Page"
    return f"{filename}.txt"


def save_text(url, text):
    """Save extracted text to a file."""
    filename = os.path.join(FOLDER_PATH, clean_filename(url))
    with open(filename, "w", encoding="utf-8") as file:
        file.write(text)
    print(f"Saved: {filename}")


def crawl_page(url):
    """Crawl a single page and extract text from #content."""
    if url in visited_links:
        return
    print(f"Crawling: {url}")

    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch {url} (Status: {response.status_code})")
        return

    soup = BeautifulSoup(response.content, "html.parser")

    # Extract the main content
    content_section = soup.find(id="content")
    if content_section:
        text_content = content_section.get_text(separator="\n", strip=True)
        save_text(url, text_content)
    else:
        print(f"No content section found in {url}")

    visited_links.add(url)

    # Find and crawl internal links
    internal_links = get_internal_links(soup, url)
    for link in internal_links:
        if link not in visited_links:
            crawl_page(link)


# Start crawling from the main page
crawl_page(BASE_URL)
