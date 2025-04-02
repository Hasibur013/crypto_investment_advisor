# src/scrapers/coinmarketcap.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class CoinMarketCapScraper:
    """
    Scraper for CoinMarketCap website.
    
    This class handles the extraction of cryptocurrency data from CoinMarketCap,
    including prices, market caps, volumes, and other metrics.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the CoinMarketCap scraper.
        
        Args:
            api_key: Optional API key for CoinMarketCap API access
        """
        self.base_url = "https://coinmarketcap.com"
        self.api_base_url = "https://pro-api.coinmarketcap.com/v1"
        self.api_key = api_key
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        if api_key:
            self.headers['X-CMC_PRO_API_KEY'] = api_key
    
    def scrape_top_coins(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Scrape data for top cryptocurrencies from CoinMarketCap.
        
        Args:
            limit: Number of top coins to retrieve
            
        Returns:
            List of dictionaries containing coin data
        """
        try:
            # If API key is available, use the API instead of web scraping
            if self.api_key:
                return self._get_data_from_api(limit)
            
            # Otherwise, fall back to web scraping (note: may be against ToS)
            url = f"{self.base_url}/en/"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract data from the table - structure may change, requiring updates
            coin_data = []
            
            # This is a simplified example - actual implementation would need to adapt to 
            # CoinMarketCap's current HTML structure
            rows = soup.select('table tbody tr')
            
            for row in rows[:limit]:
                try:
                    name_elem = row.select_one('.cmc-link')
                    symbol_elem = row.select_one('.coin-item-symbol')
                    price_elem = row.select_one('td:nth-child(4)')
                    change_elem = row.select_one('td:nth-child(5)')
                    market_cap_elem = row.select_one('td:nth-child(7)')
                    volume_elem = row.select_one('td:nth-child(8)')
                    
                    # Skip if any essential element is missing
                    if not all([name_elem, symbol_elem, price_elem]):
                        continue
                    
                    coin = {
                        'name': name_elem.text.strip(),
                        'symbol': symbol_elem.text.strip(),
                        'price': self._parse_price(price_elem.text.strip()),
                        'change_24h': self._parse_percentage(change_elem.text.strip()) if change_elem else None,
                        'market_cap': self._parse_market_cap(market_cap_elem.text.strip()) if market_cap_elem else None,
                        'volume_24h': self._parse_volume(volume_elem.text.strip()) if volume_elem else None,
                        'source': 'CoinMarketCap'
                    }
                    
                    coin_data.append(coin)
                    
                except Exception as e:
                    logger.warning(f"Error parsing coin row: {e}")
                    continue
            
            return coin_data
            
        except Exception as e:
            logger.error(f"Error scraping CoinMarketCap: {e}")
            return []
    
    def _get_data_from_api(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get data from CoinMarketCap API instead of scraping."""
        url = f"{self.api_base_url}/cryptocurrency/listings/latest"
        parameters = {
            'start': '1',
            'limit': str(limit),
            'convert': 'USD'
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=parameters)
            response.raise_for_status()
            data = response.json()
            
            coin_data = []
            for item in data['data']:
                coin = {
                    'name': item['name'],
                    'symbol': item['symbol'],
                    'price': item['quote']['USD']['price'],
                    'market_cap': item['quote']['USD']['market_cap'],
                    'volume_24h': item['quote']['USD']['volume_24h'],
                    'change_24h': item['quote']['USD']['percent_change_24h'],
                    'source': 'CoinMarketCap'
                }
                coin_data.append(coin)
            
            return coin_data
                
        except Exception as e:
            logger.error(f"Error fetching data from CoinMarketCap API: {e}")
            return []
    
    def _parse_price(self, price_str: str) -> float:
        """Parse price string to float."""
        try:
            # Remove currency symbols and commas
            price_str = price_str.replace('$', '').replace(',', '')
            return float(price_str)
        except (ValueError, TypeError):
            return None
    
    def _parse_percentage(self, percentage_str: str) -> float:
        """Parse percentage string to float."""
        try:
            # Remove % symbol
            percentage_str = percentage_str.replace('%', '')
            return float(percentage_str)
        except (ValueError, TypeError):
            return None
    
    def _parse_market_cap(self, market_cap_str: str) -> float:
        """Parse market cap string to float."""
        try:
            # Handle abbreviations like $1.2B or $900M
            market_cap_str = market_cap_str.replace('$', '').replace(',', '')
            
            if 'B' in market_cap_str:
                return float(market_cap_str.replace('B', '')) * 1_000_000_000
            elif 'M' in market_cap_str:
                return float(market_cap_str.replace('M', '')) * 1_000_000
            elif 'K' in market_cap_str:
                return float(market_cap_str.replace('K', '')) * 1_000
            else:
                return float(market_cap_str)
        except (ValueError, TypeError):
            return None
    
    def _parse_volume(self, volume_str: str) -> float:
        """Parse volume string to float."""
        # Same logic as market cap parsing
        return self._parse_market_cap(volume_str)
    
    def scrape_coin_details(self, coin_slug: str) -> Dict[str, Any]:
        """
        Scrape detailed information for a specific coin.
        
        Args:
            coin_slug: URL slug for the coin (e.g., 'bitcoin')
            
        Returns:
            Dictionary containing detailed coin data
        """
        try:
            url = f"{self.base_url}/currencies/{coin_slug}/"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Implementation would parse the specific coin page
            # This is just a placeholder for the actual implementation
            
            return {
                'name': coin_slug.capitalize(),
                'source': 'CoinMarketCap',
                'details_available': True
            }
            
        except Exception as e:
            logger.error(f"Error scraping coin details for {coin_slug}: {e}")
            return {'name': coin_slug.capitalize(), 'source': 'CoinMarketCap', 'details_available': False}