# src/scrapers/coingecko.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class CoinGeckoScraper:
    """
    Scraper for CoinGecko website.
    
    This class handles the extraction of cryptocurrency data from CoinGecko,
    including prices, market caps, volumes, and other metrics.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the CoinGecko scraper.
        
        Args:
            api_key: Optional API key for CoinGecko Pro API access
        """
        self.base_url = "https://www.coingecko.com"
        self.api_base_url = "https://api.coingecko.com/api/v3"
        self.pro_api_base_url = "https://pro-api.coingecko.com/api/v3"
        self.api_key = api_key
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        if api_key:
            self.headers['x_cg_pro_api_key'] = api_key
    
    def scrape_top_coins(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Scrape data for top cryptocurrencies from CoinGecko.
        
        Args:
            limit: Number of top coins to retrieve
            
        Returns:
            List of dictionaries containing coin data
        """
        try:
            # Use the API for data retrieval (free API has limits)
            endpoint = f"{self.api_base_url}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': limit,
                'page': 1,
                'sparkline': False,
                'price_change_percentage': '24h'
            }
            
            if self.api_key:
                # Use Pro API if key is available
                endpoint = f"{self.pro_api_base_url}/coins/markets"
            
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            coin_data = []
            for item in data:
                coin = {
                    'name': item['name'],
                    'symbol': item['symbol'].upper(),
                    'price': item['current_price'],
                    'market_cap': item['market_cap'],
                    'volume_24h': item['total_volume'],
                    'change_24h': item['price_change_percentage_24h'],
                    'source': 'CoinGecko'
                }
                coin_data.append(coin)
            
            return coin_data
            
        except Exception as e:
            logger.error(f"Error using CoinGecko API: {e}")
            
            # Fallback to web scraping if API fails
            return self._scrape_from_web(limit)
    
    def _scrape_from_web(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Fallback method to scrape from web if API fails."""
        try:
            url = f"{self.base_url}/en/coins"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract data from the table - structure may change, requiring updates
            coin_data = []
            
            # This is a simplified example - actual implementation would need to adapt to 
            # CoinGecko's current HTML structure
            rows = soup.select('table.sort tbody tr')
            
            for row in rows[:limit]:
                try:
                    name_elem = row.select_one('td:nth-child(3) .tw-hidden')
                    symbol_elem = row.select_one('td:nth-child(3) .d-lg-inline')
                    price_elem = row.select_one('td:nth-child(4) span')
                    change_elem = row.select_one('td:nth-child(6) span')
                    market_cap_elem = row.select_one('td:nth-child(7) span')
                    volume_elem = row.select_one('td:nth-child(8) span')
                    
                    # Skip if any essential element is missing
                    if not all([name_elem, symbol_elem, price_elem]):
                        continue
                    
                    coin = {
                        'name': name_elem.text.strip(),
                        'symbol': symbol_elem.text.strip().upper(),
                        'price': self._parse_price(price_elem.text.strip()),
                        'change_24h': self._parse_percentage(change_elem.text.strip()) if change_elem else None,
                        'market_cap': self._parse_market_cap(market_cap_elem.text.strip()) if market_cap_elem else None,
                        'volume_24h': self._parse_volume(volume_elem.text.strip()) if volume_elem else None,
                        'source': 'CoinGecko'
                    }
                    
                    coin_data.append(coin)
                    
                except Exception as e:
                    logger.warning(f"Error parsing coin row: {e}")
                    continue
            
            return coin_data
            
        except Exception as e:
            logger.error(f"Error scraping CoinGecko website: {e}")
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
    
    def get_coin_details(self, coin_id: str) -> Dict[str, Any]:
        """
        Get detailed information for a specific coin.
        
        Args:
            coin_id: CoinGecko ID for the coin (e.g., 'bitcoin')
            
        Returns:
            Dictionary containing detailed coin data
        """
        try:
            endpoint = f"{self.api_base_url}/coins/{coin_id}"
            params = {
                'localization': False,
                'tickers': False,
                'market_data': True,
                'community_data': True,
                'developer_data': True
            }
            
            if self.api_key:
                endpoint = f"{self.pro_api_base_url}/coins/{coin_id}"
            
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Extract relevant data
            details = {
                'name': data['name'],
                'symbol': data['symbol'].upper(),
                'source': 'CoinGecko',
                'description': data['description']['en'],
                'homepage': data['links']['homepage'][0] if data['links']['homepage'] else None,
                'github': data['links']['repos_url']['github'][0] if data['links']['repos_url']['github'] else None,
                'reddit': data['links']['subreddit_url'],
                'twitter_followers': data['community_data']['twitter_followers'],
                'reddit_subscribers': data['community_data']['reddit_subscribers'],
                'github_stars': data['developer_data']['stars'],
                'github_commits_4_weeks': data['developer_data']['commit_count_4_weeks'],
                'sentiment_votes_up_percentage': data['sentiment_votes_up_percentage'],
                'sentiment_votes_down_percentage': data['sentiment_votes_down_percentage']
            }
            
            # Add market data if available
            if 'market_data' in data:
                market_data = {
                    'current_price': data['market_data']['current_price']['usd'],
                    'market_cap': data['market_data']['market_cap']['usd'],
                    'market_cap_rank': data['market_data']['market_cap_rank'],
                    'total_volume': data['market_data']['total_volume']['usd'],
                    'high_24h': data['market_data']['high_24h']['usd'],
                    'low_24h': data['market_data']['low_24h']['usd'],
                    'price_change_24h': data['market_data']['price_change_24h'],
                    'price_change_percentage_24h': data['market_data']['price_change_percentage_24h'],
                    'price_change_percentage_7d': data['market_data']['price_change_percentage_7d'],
                    'price_change_percentage_30d': data['market_data']['price_change_percentage_30d'],
                    'price_change_percentage_1y': data['market_data']['price_change_percentage_1y'],
                    'ath': data['market_data']['ath']['usd'],
                    'ath_change_percentage': data['market_data']['ath_change_percentage']['usd'],
                    'ath_date': data['market_data']['ath_date']['usd'],
                    'atl': data['market_data']['atl']['usd'],
                    'atl_change_percentage': data['market_data']['atl_change_percentage']['usd'],
                    'atl_date': data['market_data']['atl_date']['usd'],
                    'roi': data['market_data']['roi'],
                    'fully_diluted_valuation': data['market_data'].get('fully_diluted_valuation', {}).get('usd'),
                    'total_supply': data['market_data']['total_supply'],
                    'max_supply': data['market_data']['max_supply'],
                    'circulating_supply': data['market_data']['circulating_supply']
                }
                details.update(market_data)
            
            return details
            
        except Exception as e:
            logger.error(f"Error getting coin details for {coin_id}: {e}")
            return {'name': coin_id.capitalize(), 'source': 'CoinGecko', 'details_available': False}