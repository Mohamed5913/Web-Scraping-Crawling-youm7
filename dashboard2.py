# run it with streamlit run dashboard2.py
import streamlit as st
import pandas as pd
import json
import seaborn as sns
import matplotlib.pyplot as plt
import networkx as nx
import requests
from io import StringIO

# Set page config
st.set_page_config(page_title="Youm7 Scraper Dashboard", layout="wide")

st.title("📰 Youm7 Scraper Dashboard")

# ✅ Correct Dropbox direct download link
dropbox_url = "https://www.dropbox.com/scl/fi/uulrjbxjpbastuh92f9zu/youm7_articles.json?rlkey=eltkmj7ry9nr4j0rz5oa7kafp&st=liq8ocfj&dl=1"

# Download and load JSON
try:
    response = requests.get(dropbox_url)
    response.raise_for_status()
    data = json.load(StringIO(response.text))
    df = pd.DataFrame(data)
except Exception as e:
    st.error(f"❌ Failed to download or load JSON file.\n\n{e}")
    st.stop()

# Convert scrape_time to datetime
if "scrape_time" in df.columns:
    df['scrape_time'] = pd.to_datetime(df['scrape_time'], errors='coerce')

# Sidebar filters
st.sidebar.header("🔎 Filters")
section_filter = st.sidebar.multiselect("Select Sections", df["section"].unique(), default=df["section"].unique())
writer_filter = st.sidebar.multiselect("Select Writers", df["writer"].dropna().unique())

# Apply filters
filtered_df = df[df["section"].isin(section_filter)]
if writer_filter:
    filtered_df = filtered_df[filtered_df["writer"].isin(writer_filter)]

# SECTION-WISE ARTICLE COUNT
st.subheader("📌 Articles per Section")
section_counts = filtered_df["section"].value_counts()
st.bar_chart(section_counts)

# TOP WRITERS
st.subheader("✍️ Top Writers")
top_writers = filtered_df["writer"].value_counts().head(10)
st.bar_chart(top_writers)

# WORD COUNT DISTRIBUTION BY SECTION
st.subheader("📝 Word Count Distribution by Section")
fig_wc, ax_wc = plt.subplots(figsize=(12, 6))
sns.boxplot(data=filtered_df, x="word_count", y="section", ax=ax_wc)
ax_wc.set_title("Word Count Distribution")
st.pyplot(fig_wc)

# IMAGE COUNT PER SECTION
st.subheader("🖼️ Average Image Count per Section")
image_counts = filtered_df.groupby("section")["image_count"].mean().sort_values(ascending=False)
st.bar_chart(image_counts)

# RECENT ARTICLES
st.subheader("🆕 Recent Articles")
recent_articles = filtered_df.sort_values(by="scrape_time", ascending=False).head(5)
for _, row in recent_articles.iterrows():
    st.markdown(f"**{row['title']}**")
    st.write(f"🗂️ Section: {row['section']} | ✍️ Writer: {row['writer'] or 'Unknown'} | 📅 Date: {row['date']}")
    st.write(f"📝 Word Count: {row['word_count']} | 🖼️ Image Count: {row['image_count']}")
    st.write(row["text"][:300] + "...")
    st.markdown(f"[🔗 Read more]({row['url']})")
    st.write("---")

# VISUAL SITEMAP (First 50 URLs)
st.subheader("🗺️ Visual Sitemap")
G = nx.DiGraph()
base_url = "https://www.youm7.com/"
for url in filtered_df["url"].head(50):
    G.add_edge(base_url, url)

fig_map, ax_map = plt.subplots(figsize=(10, 6))
nx.draw(G, ax=ax_map, with_labels=False, node_size=20, arrows=True)
st.pyplot(fig_map)
