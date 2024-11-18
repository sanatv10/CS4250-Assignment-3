import urllib.request
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import pymongo


client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["cs_crawler"]
pages_collection = db["pages"]


class Frontier:
    def __init__(self):
        self.urls = []
        self.visited = set()

    def addURL(self, url):
        if url not in self.visited:
            self.urls.append(url)

    def nextURL(self):
        if self.urls:
            return self.urls.pop(0)
        return None

    def done(self):
        return len(self.urls) == 0

    def markVisited(self, url):
        self.visited.add(url)


def retrieveHTML(url):
    try:
        with urllib.request.urlopen(url) as response:
            return response.read().decode("utf-8")
    except Exception as e:
        print(f"Failed to retrieve {url}: {e}")
        return None


def parseURLs(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a", href=True)
    urls = set()
    for link in links:
        href = link["href"]
        if not href.startswith("javascript:"):
            urls.add(urljoin(base_url, href))
    return urls


def isTargetPage(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.find("h1", string="Permanent Faculty") is not None


def storePage(url, html):
    pages_collection.insert_one({"url": url, "html": html})


def crawler(frontier):
    while not frontier.done():
        url = frontier.nextURL()
        if not url:
            break
        print(f"Crawling: {url}")
        html = retrieveHTML(url)
        if html:
            storePage(url, html)
            if isTargetPage(html):
                print(f"Target page found: {url}")
                return
            for link in parseURLs(html, url):
                frontier.addURL(link)
        frontier.markVisited(url)


if __name__ == "__main__":
    start_url = "https://www.cpp.edu/sci/computer-science/"
    target_url = "https://www.cpp.edu/sci/computer-science/faculty-and-staff/permanent-faculty.shtml"

    
    frontier = Frontier()
    frontier.addURL(start_url)

   
    crawler(frontier)


    stored_pages_count = pages_collection.count_documents({})
    print(f"Number of pages stored in MongoDB: {stored_pages_count}")

    print("Crawling complete. Check MongoDB for stored pages.")
