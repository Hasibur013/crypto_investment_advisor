# src/scrapers/blog_scrapers.py
import requests
from bs4 import BeautifulSoup

def scrape_binance_blog():
    # Dummy return for now
    return [
        {"name": "Bitcoin", "sentiment": 0.8, "trend": "bullish", "source": "Binance Blog"},
        {"name": "Ethereum", "sentiment": 0.75, "trend": "bullish", "source": "Binance Blog"},
    ]

def scrape_kraken_blog():
    return [
        {"name": "Solana", "sentiment": 0.65, "trend": "neutral", "source": "Kraken Blog"},
        {"name": "Polygon", "sentiment": 0.72, "trend": "bullish", "source": "Kraken Blog"},
    ]
