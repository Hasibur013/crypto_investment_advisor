# src/analysis/market_analyzer.py
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class MarketAnalyzer:
    """
    Analyzes cryptocurrency market data to identify investment opportunities.
    """
    
    def __init__(self):
        """Initialize the market analyzer."""
        pass
    
    def analyze_market_trends(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze overall market trends from the provided data.
        
        Args:
            data: DataFrame containing cryptocurrency market data
            
        Returns:
            Dictionary with market trend analysis
        """
        try:
            # Ensure data is not empty
            if data.empty:
                return {"status": "error", "message": "No data available for analysis"}
            
            # Calculate average market metrics
            avg_change_24h = data['change_24h'].mean() if 'change_24h' in data.columns else None
            median_change_24h = data['change_24h'].median() if 'change_24h' in data.columns else None
            
            # Count positive vs negative performers
            if 'change_24h' in data.columns:
                positive_performers = (data['change_24h'] > 0).sum()
                negative_performers = (data['change_24h'] < 0).sum()
                neutral_performers = (data['change_24h'] == 0).sum()
                
                # Calculate the ratio
                positive_ratio = positive_performers / len(data) if len(data) > 0 else 0
            else:
                positive_performers = None
                negative_performers = None
                neutral_performers = None
                positive_ratio = None
            
            # Determine market sentiment
            if avg_change_24h is not None:
                if avg_change_24h > 3:
                    sentiment = "strongly bullish"
                elif avg_change_24h > 0:
                    sentiment = "mildly bullish"
                elif avg_change_24h > -3:
                    sentiment = "mildly bearish"
                else:
                    sentiment = "strongly bearish"
            else:
                sentiment = "neutral"
            
            # Identify top gainers and losers
            if 'change_24h' in data.columns:
                top_gainers = data.nlargest(5, 'change_24h')[['name', 'symbol', 'change_24h']]
                top_losers = data.nsmallest(5, 'change_24h')[['name', 'symbol', 'change_24h']]
            else:
                top_gainers = pd.DataFrame()
                top_losers = pd.DataFrame()
            
            # Construct the analysis result
            analysis = {
                "status": "success",
                "avg_change_24h": avg_change_24h,
                "median_change_24h": median_change_24h,
                "positive_performers": positive_performers,
                "negative_performers": negative_performers,
                "neutral_performers": neutral_performers,
                "positive_ratio": positive_ratio,
                "market_sentiment": sentiment,
                "top_gainers": top_gainers.to_dict('records') if not top_gainers.empty else [],
                "top_losers": top_losers.to_dict('records') if not top_losers.empty else []
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing market trends: {e}")
            return {"status": "error", "message": str(e)}
    
    def recommend_investments(
        self, 
        data: pd.DataFrame, 
        investment_amount: float,
        risk_tolerance: str,
        investment_horizon: str,
        sentiment_data: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """
        Generate investment recommendations based on market data and user preferences.
        
        Args:
            data: DataFrame containing cryptocurrency market data
            investment_amount: Amount to invest in USD
            risk_tolerance: User's risk tolerance (Very Low, Low, Medium, High, Very High)
            investment_horizon: Investment time frame (Short-term, Medium-term, Long-term)
            sentiment_data: Optional DataFrame with sentiment data
            
        Returns:
            Dictionary with investment recommendations
        """
        try:
            # Ensure data is not empty
            if data.empty:
                return {"status": "error", "message": "No data available for recommendations"}
            
            # Remove duplicates by taking the mean of metrics for each coin
            if 'name' in data.columns:
                # Group by coin name and aggregate
                grouped_data = data.groupby('name').agg({
                    'symbol': 'first',
                    'price': 'mean',
                    'market_cap': 'mean',
                    'volume_24h': 'mean',
                    'change_24h': 'mean'
                }).reset_index()
            else:
                grouped_data = data.copy()
            
            # Score coins based on risk tolerance and investment horizon
            scored_coins = self._score_coins(grouped_data, risk_tolerance, investment_horizon)
            
            # Incorporate sentiment data if available
            if sentiment_data is not None and not sentiment_data.empty:
                scored_coins = self._incorporate_sentiment(scored_coins, sentiment_data)
            
            # Select top performing coins based on score
            top_coins = scored_coins.nlargest(10, 'score')
            
            # Determine allocation percentages
            allocations = self._calculate_allocations(top_coins, investment_amount, risk_tolerance)
            
            # Generate recommendations
            recommendations = []
            for _, row in allocations.iterrows():
                coin_name = row['name']
                symbol = row['symbol']
                allocation_percentage = row['allocation_percentage']
                allocation_amount = row['allocation_amount']
                
                # Generate rationale based on coin attributes
                rationale = self._generate_rationale(
                    coin_name, 
                    row['score'], 
                    row['market_cap'] if 'market_cap' in row else None,
                    row['change_24h'] if 'change_24h' in row else None
                )
                
                # Determine holding period based on investment horizon and risk
                holding_period = self._recommend_holding_period(coin_name, investment_horizon, risk_tolerance)
                
                # Determine risk level for this specific coin
                risk_level = self._determine_coin_risk_level(coin_name, risk_tolerance)
                
                # Calculate potential return range
                potential_return = self._estimate_potential_return(coin_name, risk_level, investment_horizon)
                
                recommendation = {
                    "coin": f"{coin_name} ({symbol})",
                    "allocation_percentage": allocation_percentage,
                    "allocation_amount": allocation_amount,
                    "rationale": rationale,
                    "holding_period": holding_period,
                    "risk_level": risk_level,
                    "potential_return": potential_return
                }
                
                recommendations.append(recommendation)
            
            # Generate market outlook based on data
            market_outlook = self._generate_market_outlook(grouped_data)
            
            # Generate risk assessment based on risk tolerance
            risk_assessment = self._generate_risk_assessment(risk_tolerance)
            
            # Generate additional advice
            additional_advice = (
                "Remember to practice proper risk management by not investing more than you can afford to lose. "
                "Consider dollar-cost averaging instead of lump-sum investing to reduce timing risk. "
                "Regularly review your portfolio and adjust allocations as market conditions change."
            )
            
            # Construct the recommendation result
            result = {
                "status": "success",
                "recommendations": recommendations[:3],  # Limit to top 3
                "market_outlook": market_outlook,
                "risk_assessment": risk_assessment,
                "additional_advice": additional_advice
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating investment recommendations: {e}")
            return {"status": "error", "message": str(e)}
    
    def _score_coins(
        self, 
        data: pd.DataFrame, 
        risk_tolerance: str,
        investment_horizon: str
    ) -> pd.DataFrame:
        """Score coins based on various metrics."""
        if data is None or data.empty:
            return pd.DataFrame()

        # Create a copy to avoid modifying the original data
        scored_data = data.copy()
        scored_data['score'] = 0.0

        # Score based on market cap
        if 'market_cap' in scored_data.columns:
            max_market_cap = scored_data['market_cap'].max()
            scored_data['market_cap_score'] = np.log1p(scored_data['market_cap']) / np.log1p(max_market_cap)
            risk_weights = {
                "Very Low": 3.0,
                "Low": 2.0,
                "Medium": 1.0,
                "High": 0.5,
                "Very High": 0.2
            }
            scored_data['score'] += scored_data['market_cap_score'] * risk_weights.get(risk_tolerance, 1.0)

        # Score based on 24h change
        if 'change_24h' in scored_data.columns:
            scored_data['change_score'] = ((scored_data['change_24h'] + 10) / 20).clip(0, 1)
            horizon_weights = {
                "Short-term (0-3 months)": 2.0,
                "Medium-term (3-12 months)": 1.0,
                "Long-term (1+ years)": 0.5
            }
            scored_data['score'] += scored_data['change_score'] * horizon_weights.get(investment_horizon, 1.0)

        # Score based on volume
        if 'volume_24h' in scored_data.columns and 'market_cap' in scored_data.columns:
            scored_data['volume_to_cap'] = scored_data['volume_24h'] / scored_data['market_cap']
            max_ratio = scored_data['volume_to_cap'].quantile(0.95)
            scored_data['volume_score'] = (scored_data['volume_to_cap'] / max_ratio).clip(0, 1)
            scored_data['score'] += scored_data['volume_score'] * 0.5

        # Add custom bias for BTC / ETH (optional)
        def btc_eth_bias(row):
            if row['name'] == 'Bitcoin':
                return 1.5 if risk_tolerance in ['Very Low', 'Low'] else 0.8
            if row['name'] == 'Ethereum':
                return 1.3 if risk_tolerance in ['Low', 'Medium'] else 0.9
            return 1.0

        scored_data['score'] *= scored_data.apply(btc_eth_bias, axis=1)

        return scored_data

    def _calculate_allocations(
        self,
        top_coins: pd.DataFrame,
        investment_amount: float,
        risk_tolerance: str
    ) -> pd.DataFrame:
        """
        Allocate investment across top coins based on score proportionally.

        Args:
            top_coins: DataFrame with scored coins
            investment_amount: Total investment in USD
            risk_tolerance: User risk level (affects weighting logic if needed)

        Returns:
            DataFrame with allocation percentages and USD values
        """
        if top_coins.empty or "score" not in top_coins.columns:
            return pd.DataFrame()

        total_score = top_coins["score"].sum()
        if total_score == 0:
            return pd.DataFrame()

        top_coins["allocation_percentage"] = (top_coins["score"] / total_score * 100).round(2)
        top_coins["allocation_amount"] = (top_coins["allocation_percentage"] / 100 * investment_amount).round(2)
        
        return top_coins

    def _generate_rationale(
        self,
        coin_name: str,
        score: float,
        market_cap: Optional[float],
        change_24h: Optional[float]
    ) -> str:
        """
        Generate a human-readable rationale for why a coin is recommended.

        Args:
            coin_name: Name of the cryptocurrency
            score: The score it received during analysis
            market_cap: Market cap in USD
            change_24h: 24h change percentage

        Returns:
            A string explanation
        """
        rationale_parts = [f"{coin_name} was selected due to its strong performance indicators."]

        if market_cap:
            if market_cap > 1e11:
                rationale_parts.append("It has a very large market capitalization, indicating stability and broad adoption.")
            elif market_cap > 1e10:
                rationale_parts.append("It has a solid market cap, making it relatively stable in the market.")
            else:
                rationale_parts.append("It is a mid-cap coin, which may offer growth potential but with more volatility.")

        if change_24h:
            if change_24h > 5:
                rationale_parts.append("The asset showed strong recent gains in the last 24 hours.")
            elif change_24h < -5:
                rationale_parts.append("The asset had a recent dip, which could present a buying opportunity.")
            else:
                rationale_parts.append("The asset had modest price movement recently, suggesting relative stability.")

        if score > 2:
            rationale_parts.append("Its overall analysis score suggests a favorable investment outlook.")

        return " ".join(rationale_parts)

    def _recommend_holding_period(
        self,
        coin_name: str,
        investment_horizon: str,
        risk_tolerance: str
    ) -> str:
        """
        Recommend how long to hold the coin based on risk and horizon.

        Args:
            coin_name: Name of the cryptocurrency
            investment_horizon: User's horizon (Short-term, Medium-term, Long-term)
            risk_tolerance: User's risk tolerance level

        Returns:
            Suggested holding period as a string
        """
        if investment_horizon == "Short-term (0-3 months)":
            return "1-3 months" if risk_tolerance in ["Low", "Medium"] else "2-6 weeks"

        elif investment_horizon == "Medium-term (3-12 months)":
            if risk_tolerance in ["Very Low", "Low"]:
                return "6-9 months"
            elif risk_tolerance == "Medium":
                return "4-6 months"
            else:
                return "3-5 months"

        elif investment_horizon == "Long-term (1+ years)":
            if coin_name in ["Bitcoin", "Ethereum"]:
                return "2+ years"
            else:
                return "1-2 years" if risk_tolerance in ["Medium", "High"] else "2-3 years"

        return "6 months (default)"

    def _determine_coin_risk_level(
        self,
        coin_name: str,
        user_risk_tolerance: str
    ) -> str:
        """
        Determine risk level of a coin adjusted by user's tolerance.

        Args:
            coin_name: Name of the cryptocurrency
            user_risk_tolerance: User-defined risk tolerance

        Returns:
            Risk level label as a string
        """
        # Base risk category by coin
        conservative = ["Bitcoin", "Ethereum"]
        aggressive = ["Dogecoin", "Shiba Inu", "Pepe"]

        if coin_name in conservative:
            base_risk = 1
        elif coin_name in aggressive:
            base_risk = 4
        else:
            base_risk = 2  # mid-cap, new projects

        # Adjust based on user risk tolerance
        risk_map = {
            "Very Low": -1,
            "Low": 0,
            "Medium": 1,
            "High": 2,
            "Very High": 3
        }

        risk_index = max(1, min(5, base_risk + risk_map.get(user_risk_tolerance, 1)))

        label_map = {
            1: "Very Low",
            2: "Low",
            3: "Medium",
            4: "High",
            5: "Very High"
        }

        return label_map[risk_index]

    def _estimate_potential_return(
        self,
        coin_name: str,
        risk_level: str,
        investment_horizon: str
    ) -> str:
        """
        Estimate potential return range for a coin based on risk and horizon.

        Args:
            coin_name: Name of the coin
            risk_level: Computed risk level for the coin
            investment_horizon: User's investment horizon

        Returns:
            A string representing expected return range
        """
        return_table = {
            "Very Low": {
                "Short-term (0-3 months)": "2-5%",
                "Medium-term (3-12 months)": "5-10%",
                "Long-term (1+ years)": "10-20%"
            },
            "Low": {
                "Short-term (0-3 months)": "3-7%",
                "Medium-term (3-12 months)": "7-15%",
                "Long-term (1+ years)": "15-30%"
            },
            "Medium": {
                "Short-term (0-3 months)": "5-15%",
                "Medium-term (3-12 months)": "10-25%",
                "Long-term (1+ years)": "25-50%"
            },
            "High": {
                "Short-term (0-3 months)": "10-25%",
                "Medium-term (3-12 months)": "20-50%",
                "Long-term (1+ years)": "40-80%"
            },
            "Very High": {
                "Short-term (0-3 months)": "15-40%",
                "Medium-term (3-12 months)": "30-70%",
                "Long-term (1+ years)": "60-150%"
            }
        }

        return return_table.get(risk_level, {}).get(investment_horizon, "10-30%")


    def _generate_market_outlook(self, data: pd.DataFrame) -> str:
        """
        Generate a market outlook summary based on average 24h change.

        Args:
            data: Aggregated or grouped market DataFrame

        Returns:
            A summary string
        """
        if "change_24h" not in data.columns or data.empty:
            return "Market sentiment could not be determined due to lack of recent change data."

        avg_change = data["change_24h"].mean()

        if avg_change > 3:
            return "The market is showing strong bullish momentum with several coins trending upward."
        elif avg_change > 0:
            return "The market is mildly bullish, indicating growing investor confidence."
        elif avg_change > -3:
            return "The market is showing mild bearish behavior. Some coins are stabilizing while others decline."
        else:
            return "The market is in a bearish trend, and caution is advised for short-term investors."


    def _generate_risk_assessment(self, risk_tolerance: str) -> str:
        """
        Generate a risk profile description based on user's risk tolerance.

        Args:
            risk_tolerance: User's selected risk level

        Returns:
            A summary string explaining risk profile
        """
        profiles = {
            "Very Low": (
                "You prefer minimal risk and capital preservation. "
                "The portfolio emphasizes large-cap, stable assets like Bitcoin and Ethereum."
            ),
            "Low": (
                "You are cautious but open to moderate growth. "
                "The portfolio contains a balance of stability and carefully selected growth assets."
            ),
            "Medium": (
                "You have a balanced risk appetite. "
                "This portfolio mixes well-established coins with mid-cap options for better upside."
            ),
            "High": (
                "You're comfortable with volatility and seeking higher returns. "
                "This portfolio includes emerging coins with strong potential."
            ),
            "Very High": (
                "You are aggressive and aiming for maximum returns. "
                "The portfolio leans into high-risk, high-reward assets with growth upside."
            )
        }

        return profiles.get(risk_tolerance, "Custom risk profile not recognized.")
