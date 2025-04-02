# src/scrapers/cryptocompare.py
import requests
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class CryptoCompareScraper:
    """
    Scraper for CryptoCompare data using the official API.
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://min-api.cryptocompare.com/data"
        self.headers = {
            "Authorization": f"Apikey {self.api_key}" if self.api_key else ""
        }

    def get_top_coins(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top cryptocurrencies by market cap.

        Args:
            limit: number of coins to fetch

        Returns:
            A list of coin data dictionaries
        """
        try:
            url = f"{self.base_url}/top/mktcapfull"
            params = {
                "limit": limit,
                "tsym": "USD"
            }
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()

            coin_list = []
            for item in data.get("Data", []):
                coin_info = item["CoinInfo"]
                raw = item.get("RAW", {}).get("USD", {})

                coin = {
                    "name": coin_info.get("FullName"),
                    "symbol": coin_info.get("Name"),
                    "price": raw.get("PRICE"),
                    "market_cap": raw.get("MKTCAP"),
                    "volume_24h": raw.get("TOTALVOLUME24H"),
                    "change_24h": raw.get("CHANGEPCT24HOUR"),
                    "source": "CryptoCompare"
                }

                coin_list.append(coin)

            return coin_list

        except Exception as e:
            logger.error(f"Failed to fetch data from CryptoCompare: {e}")
            return []
