# app.py
from src.utils.pdf_exporter import generate_portfolio_pdf
from src.models.vector_store import build_vector_store_from_docs
from src.models.llm_chain import get_llm_chain
from langchain_community.vectorstores import FAISS
import streamlit as st
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import time
import random
from langchain.chains import LLMChain
from langchain_community.embeddings import OpenAIEmbeddings  # ✅ (only if used elsewhere)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Crypto Investment Advisor",
    page_icon="💰",
    layout="wide"
)

# Initialize session state
if 'crypto_data' not in st.session_state:
    st.session_state.crypto_data = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

# Header
st.title("Crypto Investment Advisor 💰")
st.markdown("""
This application helps you make data-driven cryptocurrency investment decisions.
Enter your investment amount, and we'll analyze the market to suggest optimal coins.
""")

# Sidebar for user input
with st.sidebar:
    st.header("Investment Parameters")
    investment_amount = st.number_input("Investment Amount ($)", min_value=10, value=1000)
    risk_tolerance = st.select_slider(
        "Risk Tolerance",
        options=["Very Low", "Low", "Medium", "High", "Very High"],
        value="Medium"
    )
    investment_horizon = st.selectbox(
        "Investment Horizon",
        ["Short-term (0-3 months)", "Medium-term (3-12 months)", "Long-term (1+ years)"],
        index=1
    )
    
    st.divider()
    
    st.subheader("Data Sources")
    sources = st.multiselect(
        "Select data sources to analyze",
        ["CoinMarketCap", "CoinGecko", "CryptoCompare", "Binance Blog", "Kraken Blog"],
        default=["CoinMarketCap", "CoinGecko"]
    )

    data_refresh = st.button("Refresh Market Data")


# Function to scrape crypto data from websites
def scrape_crypto_data(sources):
    combined_data = []
    
    st.info("Collecting crypto market data... This may take a moment.")
    progress_bar = st.progress(0)
    
    # Add a placeholder for scraped data
    data_placeholder = st.empty()
    
    for i, source in enumerate(sources):
        # Update progress bar
        progress = (i + 1) / len(sources)
        progress_bar.progress(progress)
        
        # In a real app, we would scrape actual websites
        # For demo purposes, we're using simulated data
        if source == "CoinMarketCap":
            data = simulate_coinmarketcap_data()
        elif source == "CoinGecko":
            data = simulate_coingecko_data()
        elif source == "CryptoCompare":
            data = simulate_cryptocompare_data()
        elif source == "Binance Blog":
            data = simulate_binance_blog_data()
        elif source == "Kraken Blog":
            data = simulate_kraken_blog_data()
        
        combined_data.extend(data)
        
        # Show currently scraped data
        df = pd.DataFrame(combined_data)
        data_placeholder.dataframe(df, use_container_width=True)
        
        # Simulate scraping delay
        time.sleep(0.5)
    
    progress_bar.empty()
    data_placeholder.empty()
    
    return pd.DataFrame(combined_data)

# Simulate data from various sources for demo purposes
def simulate_coinmarketcap_data():
    coins = [
        {"name": "Bitcoin", "symbol": "BTC", "price": 61245.32, "market_cap": 1203450000000, "volume_24h": 32450000000, "change_24h": 2.3, "source": "CoinMarketCap"},
        {"name": "Ethereum", "symbol": "ETH", "price": 3214.54, "market_cap": 398760000000, "volume_24h": 12380000000, "change_24h": 1.8, "source": "CoinMarketCap"},
        {"name": "Binance Coin", "symbol": "BNB", "price": 542.65, "market_cap": 87650000000, "volume_24h": 2134000000, "change_24h": -0.7, "source": "CoinMarketCap"},
        {"name": "Solana", "symbol": "SOL", "price": 143.21, "market_cap": 62340000000, "volume_24h": 3218000000, "change_24h": 5.4, "source": "CoinMarketCap"},
        {"name": "Cardano", "symbol": "ADA", "price": 0.58, "market_cap": 23450000000, "volume_24h": 987000000, "change_24h": -1.2, "source": "CoinMarketCap"}
    ]
    return coins

def simulate_coingecko_data():
    coins = [
        {"name": "Bitcoin", "symbol": "BTC", "price": 61278.12, "market_cap": 1204120000000, "volume_24h": 32520000000, "change_24h": 2.4, "source": "CoinGecko"},
        {"name": "Ethereum", "symbol": "ETH", "price": 3210.87, "market_cap": 398230000000, "volume_24h": 12410000000, "change_24h": 1.7, "source": "CoinGecko"},
        {"name": "Ripple", "symbol": "XRP", "price": 0.58, "market_cap": 31250000000, "volume_24h": 1342000000, "change_24h": 3.2, "source": "CoinGecko"},
        {"name": "Polkadot", "symbol": "DOT", "price": 7.32, "market_cap": 9870000000, "volume_24h": 432000000, "change_24h": -0.8, "source": "CoinGecko"},
        {"name": "Avalanche", "symbol": "AVAX", "price": 36.24, "market_cap": 13450000000, "volume_24h": 765000000, "change_24h": 4.3, "source": "CoinGecko"}
    ]
    return coins

def simulate_cryptocompare_data():
    coins = [
        {"name": "Bitcoin", "symbol": "BTC", "price": 61190.45, "market_cap": 1202980000000, "volume_24h": 32380000000, "change_24h": 2.2, "source": "CryptoCompare"},
        {"name": "Ethereum", "symbol": "ETH", "price": 3216.21, "market_cap": 399120000000, "volume_24h": 12350000000, "change_24h": 1.9, "source": "CryptoCompare"},
        {"name": "Chainlink", "symbol": "LINK", "price": 14.87, "market_cap": 8760000000, "volume_24h": 543000000, "change_24h": 6.2, "source": "CryptoCompare"},
        {"name": "Uniswap", "symbol": "UNI", "price": 8.43, "market_cap": 6540000000, "volume_24h": 321000000, "change_24h": 3.1, "source": "CryptoCompare"}
    ]
    return coins

def simulate_binance_blog_data():
    # Simulate blog data with news and market insights
    articles = [
        {"name": "Bitcoin", "symbol": "BTC", "sentiment": 0.8, "trend": "bullish", "source": "Binance Blog"},
        {"name": "Ethereum", "symbol": "ETH", "sentiment": 0.7, "trend": "bullish", "source": "Binance Blog"},
        {"name": "Binance Coin", "symbol": "BNB", "sentiment": 0.85, "trend": "very bullish", "source": "Binance Blog"},
        {"name": "Arbitrum", "symbol": "ARB", "sentiment": 0.6, "trend": "neutral", "source": "Binance Blog"}
    ]
    return articles

def simulate_kraken_blog_data():
    # Simulate blog data with news and market insights
    articles = [
        {"name": "Bitcoin", "symbol": "BTC", "sentiment": 0.75, "trend": "bullish", "source": "Kraken Blog"},
        {"name": "Ethereum", "symbol": "ETH", "sentiment": 0.65, "trend": "neutral", "source": "Kraken Blog"},
        {"name": "Dogecoin", "symbol": "DOGE", "sentiment": 0.5, "trend": "neutral", "source": "Kraken Blog"},
        {"name": "Polygon", "symbol": "MATIC", "sentiment": 0.7, "trend": "bullish", "source": "Kraken Blog"}
    ]
    return articles

# Function to perform LLM-based analysis on the crypto data
def analyze_crypto_data(data, investment_amount, risk_tolerance, investment_horizon):
    # Create a text summary of the data
    data_summary = data.to_string()
    
    # In a real application, we would:
    # 1. Split this data into chunks
    # 2. Create embeddings
    # 3. Store in a vector database
    # 4. Retrieve relevant information based on query
    
    # For demo purposes, we'll simulate the LLM chain
    
    # Create a prompt template
    prompt_template = """
    You are a professional cryptocurrency analyst. Based on the following market data and user preferences, 
    recommend the best cryptocurrency investments.
    
    MARKET DATA:
    {data_summary}
    
    USER PREFERENCES:
    - Investment Amount: ${investment_amount}
    - Risk Tolerance: {risk_tolerance}
    - Investment Horizon: {investment_horizon}
    
    Provide a detailed analysis with the following:
    1. Top 3 recommended cryptocurrencies with allocation percentages
    2. Rationale for each recommendation
    3. Suggested holding period for each coin
    4. Potential risks and considerations
    5. Market outlook
    
    FORMAT YOUR RESPONSE AS JSON with the following structure:
    {{
        "recommendations": [
            {{
                "coin": "Name (Symbol)",
                "allocation_percentage": number,
                "allocation_amount": number,
                "rationale": "string",
                "holding_period": "string",
                "risk_level": "string",
                "potential_return": "string"
            }}
        ],
        "market_outlook": "string",
        "risk_assessment": "string",
        "additional_advice": "string"
    }}
    """
    
    # In a real app, this would call the LLM API
    # For demo purposes, we'll simulate the LLM response
    
    # Create a simulated analysis based on the input parameters
    # analysis = simulate_llm_analysis(data, investment_amount, risk_tolerance, investment_horizon)
    
    # Save data as temp file to feed into vector store
    temp_path = "data/processed/temp_crypto_data.txt"
    with open(temp_path, "w") as f:
        f.write(data.to_string(index=False))

    # Build vector store from document
    vector_store = build_vector_store_from_docs([temp_path])
    qa_chain = get_llm_chain(vector_store)

    query = f"""
    User wants to invest ${investment_amount} with {risk_tolerance} risk tolerance and {investment_horizon} horizon.
    Based on this and the provided crypto data, suggest top coins, allocation, rationale, risk, returns.
    """

    response = qa_chain.run(query)

    # Optional: convert to JSON with eval or json.loads
    analysis = {
        "recommendations": [],
        "market_outlook": "Market sentiment analysis not available in demo.",
        "risk_assessment": f"Risk profile: {risk_tolerance}.",
        "additional_advice": response
    }

    
    return analysis

# Simulate LLM response based on input parameters
def simulate_llm_analysis(data, investment_amount, risk_tolerance, investment_horizon):
    # Aggregate data by coin
    coin_data = {}
    for _, row in data.iterrows():
        if 'name' in row and 'symbol' in row:
            coin = row['name']
            if coin not in coin_data:
                coin_data[coin] = {
                    'symbol': row['symbol'],
                    'price_points': [],
                    'change_points': [],
                    'sentiment_points': [],
                    'sources': set()
                }
            
            if 'price' in row:
                coin_data[coin]['price_points'].append(row['price'])
            if 'change_24h' in row:
                coin_data[coin]['change_points'].append(row['change_24h'])
            if 'sentiment' in row:
                coin_data[coin]['sentiment_points'].append(row['sentiment'])
            if 'source' in row:
                coin_data[coin]['sources'].add(row['source'])
    
    # Calculate average metrics and source counts
    for coin in coin_data:
        if coin_data[coin]['price_points']:
            coin_data[coin]['avg_price'] = sum(coin_data[coin]['price_points']) / len(coin_data[coin]['price_points'])
        if coin_data[coin]['change_points']:
            coin_data[coin]['avg_change'] = sum(coin_data[coin]['change_points']) / len(coin_data[coin]['change_points'])
        if coin_data[coin]['sentiment_points']:
            coin_data[coin]['avg_sentiment'] = sum(coin_data[coin]['sentiment_points']) / len(coin_data[coin]['sentiment_points'])
        coin_data[coin]['source_count'] = len(coin_data[coin]['sources'])
    
    # Score coins based on risk tolerance and investment horizon
    coin_scores = {}
    for coin, data in coin_data.items():
        # Base score from data points
        base_score = 0
        
        # Add points for data availability
        base_score += data['source_count'] * 2
        
        # Add points for positive sentiment if available
        if 'avg_sentiment' in data:
            base_score += data['avg_sentiment'] * 10
        
        # Add points for positive price change if available
        if 'avg_change' in data:
            base_score += data['avg_change']
        
        # Apply risk tolerance modifier
        risk_modifier = {
            "Very Low": lambda c: 2 if c == "Bitcoin" or c == "Ethereum" else 0.5,
            "Low": lambda c: 1.5 if c == "Bitcoin" or c == "Ethereum" else 0.7,
            "Medium": lambda c: 1,
            "High": lambda c: 0.7 if c == "Bitcoin" or c == "Ethereum" else 1.3,
            "Very High": lambda c: 0.5 if c == "Bitcoin" or c == "Ethereum" else 1.5
        }
        
        # Apply investment horizon modifier
        horizon_modifier = {
            "Short-term (0-3 months)": lambda c: 1.2 if 'avg_change' in data and data['avg_change'] > 2 else 0.8,
            "Medium-term (3-12 months)": lambda c: 1,
            "Long-term (1+ years)": lambda c: 1.2 if c == "Bitcoin" or c == "Ethereum" else 0.9
        }
        
        # Calculate final score
        coin_scores[coin] = base_score * risk_modifier[risk_tolerance](coin) * horizon_modifier[investment_horizon](coin)
    
    # Sort coins by score
    sorted_coins = sorted(coin_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Select top 3 coins
    top_coins = sorted_coins[:3]
    
    # Calculate allocation percentages based on scores
    total_score = sum(score for _, score in top_coins)
    allocations = [(coin, score / total_score) for coin, score in top_coins]
    
    # Generate holding periods based on investment horizon
    holding_periods = {
        "Short-term (0-3 months)": ["1-4 weeks", "4-8 weeks", "2-3 months"],
        "Medium-term (3-12 months)": ["3-6 months", "6-9 months", "9-12 months"],
        "Long-term (1+ years)": ["1-2 years", "2-3 years", "3+ years"]
    }
    
    # Generate risk levels based on risk tolerance and coin
    def get_risk_level(coin, risk_tolerance):
        if coin == "Bitcoin":
            base_risk = 2
        elif coin == "Ethereum":
            base_risk = 3
        else:
            base_risk = 4
            
        risk_modifier = {
            "Very Low": -1,
            "Low": 0,
            "Medium": 1,
            "High": 2,
            "Very High": 3
        }
        
        risk_level = base_risk + risk_modifier[risk_tolerance]
        risk_mapping = {
            1: "Very Low",
            2: "Low",
            3: "Medium",
            4: "High",
            5: "Very High"
        }
        
        return risk_mapping.get(min(max(risk_level, 1), 5))
    
    # Create recommendations
    recommendations = []
    for i, (coin, allocation) in enumerate(allocations):
        symbol = coin_data[coin]['symbol']
        allocation_percentage = round(allocation * 100, 1)
        allocation_amount = round(investment_amount * allocation, 2)
        
        # Generate rationale
        if coin == "Bitcoin":
            rationale = "Bitcoin remains the most established cryptocurrency with strong institutional adoption and a proven track record. It serves as an excellent store of value and inflation hedge."
        elif coin == "Ethereum":
            rationale = "Ethereum continues to dominate the smart contract platform space with ongoing development and a strong ecosystem. The transition to Proof of Stake has improved scalability and environmental concerns."
        elif coin == "Solana":
            rationale = "Solana offers high throughput and low transaction costs, making it attractive for DeFi and NFT applications. The ecosystem has shown resilience and continued growth despite market challenges."
        elif coin == "Binance Coin":
            rationale = "As the native token of the world's largest crypto exchange, BNB benefits from Binance's extensive ecosystem and regular token burns which reduce supply over time."
        elif coin == "Avalanche":
            rationale = "Avalanche provides a highly scalable platform for decentralized applications with strong interoperability features and subnets that allow for customizable blockchains."
        else:
            rationale = f"{coin} shows promising technical indicators and development activity with potential for growth in the current market conditions."
        
        # Assign holding period from options based on index
        period_index = min(i, len(holding_periods[investment_horizon]) - 1)
        holding_period = holding_periods[investment_horizon][period_index]
        
        # Get risk level
        risk_level = get_risk_level(coin, risk_tolerance)
        
        # Generate potential return based on risk level and investment horizon
        potential_return_mapping = {
            "Very Low": {"Short-term (0-3 months)": "5-10%", "Medium-term (3-12 months)": "10-20%", "Long-term (1+ years)": "15-30%"},
            "Low": {"Short-term (0-3 months)": "10-15%", "Medium-term (3-12 months)": "15-25%", "Long-term (1+ years)": "20-40%"},
            "Medium": {"Short-term (0-3 months)": "15-25%", "Medium-term (3-12 months)": "20-35%", "Long-term (1+ years)": "30-60%"},
            "High": {"Short-term (0-3 months)": "20-40%", "Medium-term (3-12 months)": "30-60%", "Long-term (1+ years)": "50-100%"},
            "Very High": {"Short-term (0-3 months)": "30-60%", "Medium-term (3-12 months)": "50-100%", "Long-term (1+ years)": "80-150%"}
        }
        potential_return = potential_return_mapping[risk_level][investment_horizon]
        
        recommendations.append({
            "coin": f"{coin} ({symbol})",
            "allocation_percentage": allocation_percentage,
            "allocation_amount": allocation_amount,
            "rationale": rationale,
            "holding_period": holding_period,
            "risk_level": risk_level,
            "potential_return": potential_return
        })
    
    # Generate market outlook based on data
    avg_change = 0
    change_count = 0
    for coin, data in coin_data.items():
        if 'avg_change' in data:
            avg_change += data['avg_change']
            change_count += 1
    
    if change_count > 0:
        avg_market_change = avg_change / change_count
    else:
        avg_market_change = 0
        
    if avg_market_change > 3:
        market_outlook = "The cryptocurrency market shows strong bullish momentum with most assets trending upward. Institutional adoption continues to grow, and regulatory clarity is improving in major markets."
    elif avg_market_change > 0:
        market_outlook = "The market demonstrates cautious optimism with modest gains across various cryptocurrencies. Market sentiment appears to be gradually improving after the recent consolidation phase."
    elif avg_market_change > -3:
        market_outlook = "Market conditions remain mixed with some assets showing stability while others experience downward pressure. Investors should remain cautious and focus on projects with strong fundamentals."
    else:
        market_outlook = "The market is currently in a bearish trend with most assets experiencing significant downward pressure. This may present buying opportunities for long-term investors, but short-term volatility is expected."
    
    # Generate risk assessment based on risk tolerance
    risk_assessment_mapping = {
        "Very Low": "Your conservative risk profile suggests focusing on established cryptocurrencies with proven track records. While this approach may limit potential returns compared to higher-risk alternatives, it also provides better protection against market downturns.",
        "Low": "Your cautious risk profile balances safety with moderate growth potential. The recommended portfolio focuses primarily on established cryptocurrencies with some limited exposure to promising mid-cap projects.",
        "Medium": "Your balanced risk profile seeks to optimize the risk-reward ratio. The recommended portfolio includes a mix of established cryptocurrencies and promising projects with strong fundamentals.",
        "High": "Your growth-oriented risk profile seeks significant returns while accepting higher volatility. The recommended portfolio includes exposure to emerging projects with strong upside potential alongside established cryptocurrencies.",
        "Very High": "Your aggressive risk profile prioritizes maximum growth potential. The recommended portfolio includes significant exposure to promising emerging projects that offer the potential for substantial returns, though with corresponding increased risk."
    }
    risk_assessment = risk_assessment_mapping[risk_tolerance]
    
    # Generate additional advice
    additional_advice = "Remember to practice proper risk management by not investing more than you can afford to lose. Consider dollar-cost averaging instead of lump-sum investing to reduce timing risk. Regularly review your portfolio and adjust allocations as market conditions change."
    
    # Construct the analysis result
    analysis = {
        "recommendations": recommendations,
        "market_outlook": market_outlook,
        "risk_assessment": risk_assessment,
        "additional_advice": additional_advice
    }
    
    return analysis

# Main application flow
if data_refresh or st.session_state.crypto_data is None:
    if sources:
        crypto_data = scrape_crypto_data(sources)
        st.session_state.crypto_data = crypto_data
    else:
        st.warning("Please select at least one data source.")

# Display the data if available
if st.session_state.crypto_data is not None:
    st.subheader("Market Data")
    # Create tabs for different data views
    tab1, tab2 = st.tabs(["Price Data", "News & Sentiment"])
    
    with tab1:
        price_data = st.session_state.crypto_data[st.session_state.crypto_data.columns.intersection(['name', 'symbol', 'price', 'market_cap', 'volume_24h', 'change_24h', 'source'])]
        price_data = price_data.dropna(subset=['price'], how='all')
        if not price_data.empty:
            st.dataframe(price_data, use_container_width=True)
        else:
            st.info("No price data available from selected sources.")
    
    with tab2:
        columns = st.session_state.crypto_data.columns

        if 'sentiment' in columns or 'trend' in columns:
            sentiment_data = st.session_state.crypto_data[columns.intersection(['name', 'symbol', 'sentiment', 'trend', 'source'])]

            if 'sentiment' in sentiment_data.columns or 'trend' in sentiment_data.columns:
                sentiment_data = sentiment_data.dropna(
                    subset=list(set(['sentiment', 'trend']) & set(sentiment_data.columns)),
                    how='all'
                )

            if not sentiment_data.empty:
                st.dataframe(sentiment_data, use_container_width=True)
            else:
                st.info("No sentiment data available from selected sources.")
        else:
            st.info("No sentiment data columns present in current dataset.")

    
    # Analysis button
    if st.button("Analyze Investment Options"):
        with st.spinner("Analyzing crypto market data..."):
            # Simulate processing time
            time.sleep(2)
            analysis_results = analyze_crypto_data(
                st.session_state.crypto_data,
                investment_amount,
                risk_tolerance,
                investment_horizon
            )
            st.session_state.analysis_results = analysis_results
            st.success("Analysis complete!")

# Display analysis results if available
if st.session_state.analysis_results is not None:
    st.header("Investment Recommendations")
    
    results = st.session_state.analysis_results
    
    # Display recommendations in an attractive format
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Recommended Portfolio")
        
        # Create a pie chart of allocations
        labels = [rec["coin"] for rec in results["recommendations"]]
        sizes = [rec["allocation_percentage"] for rec in results["recommendations"]]
        
        fig = {
            "data": [
                {
                    "values": sizes,
                    "labels": labels,
                    "type": "pie",
                    "hole": 0.4,
                    "marker": {"colors": ["#1f77b4", "#ff7f0e", "#2ca02c"]}
                }
            ],
            "layout": {
                "title": f"Allocation for ${investment_amount} Investment"
            }
        }
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Market Outlook")
        st.write(results["market_outlook"])
        
        st.subheader("Risk Assessment")
        st.write(results["risk_assessment"])
    
    # Display detailed recommendations
    st.subheader("Detailed Coin Recommendations")
    
    for i, rec in enumerate(results["recommendations"]):
        with st.expander(f"{i+1}. {rec['coin']} - {rec['allocation_percentage']}% (${rec['allocation_amount']})"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Rationale:**")
                st.write(rec["rationale"])
                
                st.markdown("**Recommended Holding Period:**")
                st.write(rec["holding_period"])
            
            with col2:
                st.markdown("**Risk Level:**")
                risk_colors = {
                    "Very Low": "blue",
                    "Low": "green",
                    "Medium": "orange",
                    "High": "red",
                    "Very High": "purple"
                }
                st.markdown(f"<span style='color:{risk_colors.get(rec['risk_level'], 'black')}'>{rec['risk_level']}</span>", unsafe_allow_html=True)
                
                st.markdown("**Potential Return:**")
                st.write(rec["potential_return"])
    # Add download button for PDF report
    user_inputs = {
        "Investment Amount": f"${investment_amount}",
        "Risk Tolerance": risk_tolerance,
        "Investment Horizon": investment_horizon
    }

    pdf_buffer = generate_portfolio_pdf(
        recommendations=results["recommendations"],
        market_outlook=results["market_outlook"],
        risk_assessment=results["risk_assessment"],
        advice=results["additional_advice"],
        user_inputs=user_inputs
    )

    st.download_button(
        label="📄 Download PDF Report",
        data=pdf_buffer,
        file_name="crypto_investment_report.pdf",
        mime="application/pdf"
    )

    st.subheader("Additional Advice")
    st.info(results["additional_advice"])

# Add documentation section
with st.expander("How This Application Works"):
    st.markdown("""
    ## How the Crypto Investment Advisor Works
    
    1. **Data Collection:** The application scrapes real-time data from multiple cryptocurrency websites and news sources.
    
    2. **Data Processing:** The collected data is cleaned, normalized, and structured for analysis.
    
    3. **RAG (Retrieval-Augmented Generation):** The system uses a vector database to store and retrieve relevant cryptocurrency information based on your investment parameters.
    
    4. **LLM Analysis:** A large language model analyzes the retrieved data along with your risk tolerance and investment horizon to generate personalized recommendations.
    
    5. **Recommendation Generation:** The system creates a diversified portfolio recommendation with detailed rationales and holding periods.
    
    ## Best Practices for Crypto Investing
    
    - **Diversify:** Don't put all your investment into a single cryptocurrency.
    - **Research:** Always conduct your own research beyond algorithmic recommendations.
    - **Dollar-Cost Average:** Consider investing smaller amounts regularly rather than one large sum.
    - **Security:** Use hardware wallets for long-term storage of significant investments.
    - **Tax Considerations:** Be aware of the tax implications of cryptocurrency trading in your jurisdiction.
    
    *Note: This application provides information for educational purposes only. It does not constitute financial advice.*
    """)

# Footer
st.markdown("""
---
*Disclaimer: This application is for informational purposes only and does not constitute financial advice. 
Cryptocurrency investments are volatile and risky. Always conduct your own research before investing.*
""")