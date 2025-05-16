# Web Crawler & Dashboard Project

## 🔍 Overview

This project scrapes articles from [Youm7.com](https://www.youm7.com), extracts their titles and text, and visualizes insights using a Streamlit dashboard.

---

## ⚙️ Technologies Used

- Python 3.10
- `aiohttp`, `aiofiles`, `BeautifulSoup`
- `Streamlit`, `Matplotlib`, `NetworkX`, `Pandas`
- JSON for data storage

---

## 🕸️ Scraper Workflow (`scrap3.py`)

1. Async fetch articles from a base section.
2. Extract links containing `/story/`.
3. Scrape title and paragraphs from each article.
4. Save data as a JSON array in `clean_articles2.json`.

---

## 📊 Dashboard Workflow (`dashboard.py`)

- **Crawlability Score**: Based on average article length and structure.
- **Top Articles**: Display longest entries.
- **Recommendations**: Static guidance on scraping.
- **Sitemap**: Visualized using NetworkX.

---

## 🧪 Testing

Tested with a sample of 100 articles. Validated structure, ensured titles and texts are properly parsed.

## Deployment


(https://web-scraping-crawling-youm7-5p6thdxnenju5jinepzj2e.streamlit.app/)
