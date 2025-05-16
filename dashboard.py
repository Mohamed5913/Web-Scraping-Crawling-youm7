import streamlit as st
import json
import requests
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Cache data loading for performance
@st.cache_data
def load_data_from_gdrive(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to load data from Google Drive: {e}")
        return []

DATA_URL = "https://drive.google.com/uc?export=download&id=1MqnDpn3EN8MTKrmXB3aLezXsdeZ-koyl"

data = load_data_from_gdrive(DATA_URL)

if not data:
    st.error("❌ No data loaded. Please check your data URL or file sharing settings.")
    st.stop()

def calculate_crawlability_score(data):
    valid_articles = [item for item in data if item.get("text") and len(item["text"]) > 500]
    structured_articles = [item for item in valid_articles if item.get("title") and " " in item["title"]]

    if not data:
        return 0

    structure_ratio = len(structured_articles) / len(data)
    avg_length = sum(len(item["text"]) for item in valid_articles) / len(valid_articles)

    score = (structure_ratio * 60) + min(40, avg_length / 100)
    return int(score)



def get_top_articles(data, n=5):
    return sorted(data, key=lambda x: len(x["text"]), reverse=True)[:n]

def generate_sitemap(data):
    G = nx.DiGraph()
    base = "https://www.youm7.com/"
    for item in data:
        G.add_edge(base, item["url"])
    return G

# App Layout
st.title("🕷️ Web Crawl Dashboard")
st.markdown("Visual insights from scraping [youm7.com](https://www.youm7.com/)")

data = load_data_from_gdrive("clean_articles2.json")

if not data:
    st.error("❌ No data loaded. Please make sure 'clean_articles2.json' is not empty and properly formatted.")
    st.stop()


# Crawlability Score
st.subheader("📊 Crawlability Score")
score = calculate_crawlability_score(data)
st.metric("Score (out of 100)", score)

# Top Extracted Data
st.subheader("📰 Top Extracted Articles")
top_articles = get_top_articles(data)
for article in top_articles:
    st.markdown(f"**{article['title']}**")
    st.text_area("Preview", article["text"][:300] + "...", height=100)
    st.markdown(f"[Read more]({article['url']})\n")

# Recommendations
st.subheader("🧠 Recommendations for Crawling")
st.markdown("""
- Use `aiohttp` + `BeautifulSoup` for scalable async scraping.
- Add delay or random User-Agents to avoid blocking.
- Consider Scrapy or Selenium for dynamic pages.
- Use `robots.txt` parsing for responsible crawling.
""")

st.subheader("📏 Article Length Distribution")
lengths = [len(item["text"]) for item in data if item.get("text")]
st.bar_chart(lengths)


# Sitemap
st.subheader("🗺️ Visual Sitemap")
G = generate_sitemap(data[:50])  # limit for visualization clarity
plt.figure(figsize=(10, 6))
nx.draw(G, with_labels=False, node_size=20, arrows=True)
st.pyplot(plt)
