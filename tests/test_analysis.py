# tests/test_analysis.py
# python -m unittest discover tests
import unittest
import pandas as pd
from src.analysis.market_analyzer import MarketAnalyzer

class TestMarketAnalysis(unittest.TestCase):
    def setUp(self):
        self.analyzer = MarketAnalyzer()
        self.mock_data = pd.DataFrame([
            {"name": "Bitcoin", "symbol": "BTC", "price": 60000, "change_24h": 2.0, "market_cap": 1e12, "volume_24h": 4e10},
            {"name": "Ethereum", "symbol": "ETH", "price": 3000, "change_24h": -1.0, "market_cap": 5e11, "volume_24h": 2e10}
        ])

    def test_analyze_market_trends(self):
        result = self.analyzer.analyze_market_trends(self.mock_data)
        self.assertEqual(result["status"], "success")
        self.assertIn("market_sentiment", result)

    def test_recommend_investments(self):
        result = self.analyzer.recommend_investments(
            self.mock_data, 
            investment_amount=1000,
            risk_tolerance="Medium",
            investment_horizon="Medium-term (3-12 months)"
        )
        self.assertEqual(result["status"], "success")
        self.assertLessEqual(len(result["recommendations"]), 3)

if __name__ == "__main__":
    unittest.main()
