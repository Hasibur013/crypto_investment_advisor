# tests/test_scrapers.py
import unittest
from src.scrapers.coinmarketcap import CoinMarketCapScraper
from src.scrapers.coingecko import CoinGeckoScraper
from src.scrapers.cryptocompare import CryptoCompareScraper
import os

class TestScrapers(unittest.TestCase):
    def test_coinmarketcap_scraper(self):
        scraper = CoinMarketCapScraper(api_key=os.getenv("COINMARKETCAP_API_KEY"))
        data = scraper.scrape_top_coins(limit=5)
        self.assertTrue(isinstance(data, list))
        self.assertGreater(len(data), 0)
        self.assertIn("name", data[0])

    def test_coingecko_scraper(self):
        scraper = CoinGeckoScraper()
        data = scraper.scrape_top_coins(limit=5)
        self.assertTrue(isinstance(data, list))
        self.assertGreater(len(data), 0)
        self.assertIn("price", data[0])

    def test_cryptocompare_scraper(self):
        scraper = CryptoCompareScraper(api_key=os.getenv("CRYPTOCOMPARE_API_KEY"))
        data = scraper.get_top_coins(limit=5)
        self.assertTrue(isinstance(data, list))
        self.assertGreater(len(data), 0)
        self.assertIn("symbol", data[0])

if __name__ == "__main__":
    unittest.main()
