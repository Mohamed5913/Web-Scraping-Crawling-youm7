import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import aiofiles

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

base_section_url = "https://www.youm7.com/Section/%D8%AA%D9%82%D8%A7%D8%B1%D9%8A%D8%B1-%D9%85%D8%B5%D8%B1%D9%8A%D8%A9/97"

sem = asyncio.Semaphore(10)  # عدد الاتصالات المتوازية (تحكم في السرعة)


async def fetch(session, url):
    async with sem:
        try:
            async with session.get(url, headers=headers) as response:
                return await response.text()
        except Exception as e:
            print(f"Request failed for {url}: {e}")
            return None


async def get_article_links(session, base_url, max_links):
    links = []
    page = 1

    while len(links) < max_links:
        if page == 1:
            current_url = f"{base_section_url}/1"
        else:
            current_url = f"{base_section_url}/{page}"

        print(f"Scraping page {page}: {current_url}")
        html = await fetch(session, current_url)
        if not html:
            break

        soup = BeautifulSoup(html, "html.parser")
        article_containers = soup.find_all("div", class_=["bigOneSec", "smallOneSec"])

        page_links = []
        for container in article_containers:
            link_tag = container.find("a", href=True)
            if link_tag and "/story/" in link_tag["href"]:
                full_url = urljoin(base_url, link_tag["href"])
                if full_url not in links and full_url not in page_links:
                    page_links.append(full_url)

        if not page_links:
            print("No more articles found")
            break

        links.extend(page_links)
        print(f"Found {len(page_links)} articles on this page (Total: {len(links)})")

        if len(links) >= max_links:
            links = links[:max_links]
            break

        page += 1

    return links


async def scrape_and_save(session, url, f):
    html = await fetch(session, url)
    if not html:
        return

    try:
        soup = BeautifulSoup(html, "html.parser")
        title = soup.find("h1").text.strip() if soup.find("h1") else "No title found"
        article_body = soup.find("div", {"id": "articleBody"}) or soup.find(
            "div", class_="articleCont"
        )
        paragraphs = article_body.find_all("p") if article_body else []
        text = "\n".join([p.text.strip() for p in paragraphs if p.text.strip()])

        article_data = {"title": title, "text": text, "url": url}

        await f.write(json.dumps(article_data, ensure_ascii=False) + "\n")
        print(f"Scraped and saved: {title}")

    except Exception as e:
        print(f"Failed to scrape {url}: {e}")


async def main():
    base_url = "https://www.youm7.com/"
    max_links = 100000

    async with aiohttp.ClientSession() as session:
        article_links = await get_article_links(session, base_url, max_links)
        print(f"\nTotal articles found: {len(article_links)}")

        async with aiofiles.open("clean_articles2.jsonl", "w", encoding="utf-8") as f:
            tasks = [scrape_and_save(session, link, f) for link in article_links]
            await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
