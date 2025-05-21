import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import re

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

async def scrape_article(session, url, article_number):
    html = await fetch(session, url)
    if not html:
        return None
    try:
        soup = BeautifulSoup(html, "html.parser")
        
        # Extract title
        title = soup.find("h1").text.strip() if soup.find("h1") else "No title found"
        
        # Extract article body
        article_body = soup.find("div", {"id": "articleBody"}) or soup.find(
            "div", class_="articleCont"
        )
        paragraphs = article_body.find_all("p") if article_body else []
        text = "\n".join([p.text.strip() for p in paragraphs if p.text.strip()])
        
        # Extract date
        date_element = soup.find("span", class_="newsStoryDate")
        date = date_element.text.strip() if date_element else "No date found"
        
        # Extract writer/author
        writer_element = soup.find("span", class_="writeBy")
        writer = writer_element.text.strip() if writer_element else "No writer found"
        # Clean up writer text by removing "كتب" prefix if present
        if writer.startswith("كتب"):
            writer = re.sub(r'^كتب\s+', '', writer)
        
        # Extract images
        images = []
        # Main article image
        main_image = soup.find("div", class_="img-cont")
        if main_image and main_image.find("img"):
            img_element = main_image.find("img")
            img_url = img_element.get("src") or img_element.get("data-src")
            img_caption = ""
            caption_element = main_image.find("span", class_="img-cap")
            if caption_element:
                img_caption = caption_element.text.strip()
            
            if img_url:
                images.append({
                    "url": img_url,
                    "caption": img_caption
                })
        
        # Additional images in article body
        if article_body:
            body_images = article_body.find_all("img")
            for img in body_images:
                img_url = img.get("src") or img.get("data-src")
                if img_url and not any(img_url == existing_img["url"] for existing_img in images):
                    img_caption = ""
                    # Try to find caption near the image
                    caption_element = img.find_next("span", class_="img-cap")
                    if caption_element:
                        img_caption = caption_element.text.strip()
                    
                    images.append({
                        "url": img_url,
                        "caption": img_caption
                    })
        
        # Create article data with all fields including the article number
        article_data = {
            "id": article_number,
            "title": title,
            "text": text,
            "url": url,
            "date": date,
            "writer": writer,
            "images": images
        }
        
        print(f"Scraped article #{article_number}: {title}")
        return article_data
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        return None

async def main():
    base_url = "https://www.youm7.com/"
    max_links = 10
    async with aiohttp.ClientSession() as session:
        article_links = await get_article_links(session, base_url, max_links)
        print(f"\nTotal articles found: {len(article_links)}")
        
        # Scrape all articles with their sequential numbers
        tasks = []
        for idx, link in enumerate(article_links, start=1):
            tasks.append(scrape_article(session, link, idx))
        
        articles = await asyncio.gather(*tasks)
        
        # Filter out any None values (failed scrapes)
        articles = [article for article in articles if article is not None]
        
        # Save to a proper JSON file
        with open("articles.json", "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        
        print(f"\nSuccessfully saved {len(articles)} articles to articles.json")

if __name__ == "__main__":
    asyncio.run(main())