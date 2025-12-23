import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

from utils import fetch_market_data, get_financial_metrics, validate_and_clean_data
from models import initialize_gemini_model, create_analysis_prompt, perform_price_prediction
from charts import display_financial_charts, display_prediction_chart
from advanced_charts import display_all_charts
from web_search import search_financial_news, extract_key_info
from ollama_models import check_ollama_connection, list_ollama_models, analyze_financial_data_with_ollama
from embeddings import find_similar_texts, embed_financial_data

st.set_page_config(
    page_title="FinGPT Analyst",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #fafafa;
    }
    .stApp {
        background-color: #0e1117;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #1e2130;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #262730;
        color: #fafafa;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ff4b4b;
        color: white;
    }
    pre {
        background-color: transparent !important;
        color: #00ff00 !important;
        font-family: 'Courier New', monospace;
        line-height: 1.2;
    }
    code {
        color: #00ff00 !important;
    }
    .sidebar .sidebar-content {
        background-color: #262730;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
```
 _____ _       ____ ____ _____   
|  ___(_)_ __ / ___|  _ \_   _|  
| |_  | | '_ \| |  _| |_) || |    
|  _| | | | | | |_| |  __/ | |    
|_|   |_|_| |_|\____|_|    |_|    
                                   
Financial Data & AI Analyst
================================
```
""")

st.sidebar.markdown("### ⚙ Configuration Panel")

with st.sidebar:
    st.markdown("**Market Data Settings**")
    ticker = st.text_input("Ticker Symbol", value="NVDA", placeholder="e.g., AAPL, GOOGL")
    
    col_start, col_end = st.columns(2)
    with col_start:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=365))
    with col_end:
        end_date = st.date_input("End Date", datetime.now())
    
    st.markdown("---")
    fetch_btn = st.button("⚡ Fetch Market Data", use_container_width=True)
    
    if fetch_btn:
        with st.spinner("Loading market data..."):
            fetch_market_data(ticker, start_date, end_date)
            if 'df' in st.session_state:
                st.success("✓ Data loaded successfully")

if 'df' in st.session_state:
    df = st.session_state['df']
    current_ticker = st.session_state['ticker']
    
    df = validate_and_clean_data(df)
    
    if df is None or len(df) == 0:
        st.error("❌ Invalid or empty data. Please try a different ticker or date range.")
        st.stop()
    
    if len(df) < 2:
        st.warning("⚠ Not enough data points. Please select a longer date range.")
        st.stop()
    
    st.markdown("---")
    
    st.markdown(f"### 📊 Market Summary: {current_ticker}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        latest_price = df['Close'].iloc[-1]
        if isinstance(latest_price, pd.Series):
            latest_price = latest_price.values[0]
        st.metric("💵 Current Price", f"${float(latest_price):.2f}")
    
    with col2:
        current_close = df['Close'].iloc[-1]
        prev_close = df['Close'].iloc[-2]
        if isinstance(current_close, pd.Series):
            current_close = current_close.values[0]
        if isinstance(prev_close, pd.Series):
            prev_close = prev_close.values[0]
        price_change = float(current_close) - float(prev_close)
        pct_change = (price_change / float(prev_close)) * 100
        st.metric("📈 Daily Change", f"${price_change:.2f}", f"{pct_change:.2f}%")
    
    with col3:
        avg_volume = df['Volume'].mean()
        if isinstance(avg_volume, pd.Series):
            avg_volume = avg_volume.values[0]
        st.metric("📊 Avg Volume", f"{float(avg_volume):,.0f}")
    
    with col4:
        high_52w = df['High'].tail(252).max()
        if isinstance(high_52w, pd.Series):
            high_52w = high_52w.values[0]
        st.metric("🎯 52-Week High", f"${float(high_52w):.2f}")
    
    st.markdown("---")
    
    tab_viz, tab_adv_viz, tab_ai, tab_ml, tab_news = st.tabs([
        "📊 Basic Charts",
        "📈 Advanced Analytics",
        "🤖 AI Analyst",
        "🔮 Price Prediction",
        "📰 News & Insights"
    ])
    
    with tab_viz:
        st.markdown("### Basic Market Visualization")
        try:
            display_financial_charts(df, current_ticker)
        except Exception as e:
            st.error(f"Error displaying charts: {str(e)}")
    
    with tab_adv_viz:
        st.markdown("### Advanced Technical Analysis")
        try:
            display_all_charts(df, current_ticker)
        except Exception as e:
            st.error(f"Error displaying advanced charts: {str(e)}")
    
    with tab_ai:
        st.markdown("""
```
   ___    ___   ___              _           _   
  / _ \  |_ _| / _ \  _ _   __ _| |_  _ ___ | |_ 
 | | | |  | | | | | || ' \ / _` | | || (_-< |  _|
 |_| |_| |___||_| |_||_||_|\__,_|_|\_, /__/  \__|
                                   |__/           
```
""")
        st.caption("Ask questions about trends, patterns, and insights")
        
        llm = initialize_gemini_model()
        if llm:
            recent_data = df.tail(10).to_string()
            summary_stats = df.describe().to_string()
            prompt = create_analysis_prompt()
            chain = prompt | llm
            
            user_query = st.text_area("💬 Enter your question:", placeholder="What are the key trends in this data?", height=100)
            
            if st.button("▶ Run Analysis", use_container_width=True, key="ai_analyst_button"):
                if user_query:
                    col_left, col_mid, col_right = st.columns([1, 3, 1])
                    
                    with col_mid:
                        with st.spinner("🔄 Analyzing..."):
                            try:
                                response = chain.invoke({
                                    "question": user_query,
                                    "data": recent_data,
                                    "stats": summary_stats
                                })
                                
                                st.markdown("### 📊 Analysis Results")
                                st.markdown("---")
                                st.write(response.content)
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("⚠ Please enter a question first")
        else:
            st.warning("⚠ AI model not initialized. Check API configuration.")
    
    with tab_ml:
        st.markdown("""
```
  ___              _ _      _   _          
 | _ \_ _ ___ _ __| (_)_ __| |_(_)___ _ _  
 |  _/ '_/ -_) / _` | | / _|  _| / _ \ ' \ 
 |_| |_| \___\_\__,_|_|_\__|\__|_\___/_||_|
```
""")
        st.caption("Next-day prediction using Linear Regression")
        
        try:
            prediction = perform_price_prediction(df)
            display_prediction_chart(df, prediction)
        except Exception as e:
            st.error(f"❌ Prediction error: {str(e)}")
    
    with tab_news:
        st.markdown(f"### 📰 Latest Financial News: {current_ticker}")
        
        try:
            with st.spinner("🔍 Fetching news..."):
                search_results = search_financial_news(current_ticker)
            
            if search_results:
                key_info = extract_key_info(search_results)
                
                if key_info:
                    for i, article in enumerate(key_info):
                        with st.expander(f"📄 [{i+1}] {article['title']}", expanded=i==0):
                            st.markdown(f"**🔗 Source:** {article['url']}")
                            st.markdown(article['snippet'])
                else:
                    st.info("ℹ No news articles found.")
            else:
                st.info("ℹ No recent news available.")
        except Exception as e:
            st.error(f"❌ News fetch error: {str(e)}")
        
        st.markdown("---")
        
        col_left_space, col_patterns, col_right_space = st.columns([1, 2, 1])
        
        with col_patterns:
            st.markdown("### 🔍 Historical Patterns")
            
            if len(df) > 5:
                try:
                    text_repr, embeddings = embed_financial_data(df)
                    
                    if text_repr:
                        query = "significant market movement"
                        similar_periods = find_similar_texts(query, text_repr, top_k=3)
                        
                        for period, similarity in similar_periods:
                            st.write(f"**📅 {period}**")
                            st.progress(similarity)
                            st.caption(f"Similarity: {similarity:.1%}")
                except Exception as e:
                    st.warning(f"⚠ Pattern analysis unavailable")
        
        st.markdown("---")
        
        col_l, col_ollama, col_r = st.columns([1, 2, 1])
        
        with col_ollama:
            st.markdown("### 🖥 Offline AI Analysis")
            
            if check_ollama_connection():
                st.success("✓ Ollama Connected")
                
                models = list_ollama_models()
                if models:
                    selected_model = st.selectbox("🤖 Model", models, index=0)
                    ollama_query = st.text_area(
                        "💬 Query",
                        "What are the key trends?",
                        height=100
                    )
                    
                    if st.button("▶ Run Analysis", use_container_width=True, key="ollama_analysis_button"):
                        if ollama_query:
                            with st.spinner("⏳ Processing..."):
                                ollama_response = analyze_financial_data_with_ollama(
                                    df, ollama_query, selected_model
                                )
                                if ollama_response:
                                    st.markdown("### 🤖 Ollama Analysis Results")
                                    st.markdown("---")
                                    st.write(ollama_response)
                                else:
                                    st.error("❌ Failed to get response")
                        else:
                            st.warning("⚠ Please enter a query first")
                else:
                    st.warning("⚠ No Ollama models found. Please pull a model first.")
            else:
                st.warning("✗ Ollama not running. Please start Ollama service.")
                st.info("💡 Install Ollama from: https://ollama.ai")

else:
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
```
 _    _      _                          
| |  | |    | |                         
| |  | | ___| | ___ ___  _ __ ___   ___ 
| |/\| |/ _ \ |/ __/ _ \| '_ ` _ \ / _ \
\  /\  /  __/ | (_| (_) | | | | | |  __/
 \/  \/ \___|_|\___\___/|_| |_| |_|\___|
                                         
     to FinGPT Analyst Platform
=====================================
```
""")
        
        st.info("👈 Enter a ticker symbol in the sidebar and click 'Fetch Market Data' to begin")
        
        st.markdown("### 🚀 Quick Start Guide")
        st.markdown("""
**Step 1:** Enter a ticker symbol (e.g., NVDA, AAPL, TSLA)  
**Step 2:** Select your preferred date range  
**Step 3:** Click 'Fetch Market Data' to load data  
**Step 4:** Explore the tabs for different analyses
""")
        
        st.markdown("---")
        
        st.markdown("### 🎯 Platform Features")
        
        st.markdown("""
**📊 Basic Charts**  
View price movements, volume, and candlestick patterns

**📈 Advanced Analytics**  
Technical indicators: RSI, Bollinger Bands, Moving Averages

**🤖 AI Analyst**  
Natural language queries for data insights

**🔮 Price Prediction**  
Machine learning forecasting for next-day prices

**📰 News & Insights**  
Real-time news with historical pattern matching
""")
        
        st.markdown("---")
        
        st.markdown("""
```
 ___        _               
|_ _|_ _  _| |_ ___  
 | || ' \| |  _/ _ \ 
|___|_||_|_|\__\___/ 
                      
• Python-based financial analysis
• AI-powered insights via Gemini
• Real-time market data via yfinance
• Technical analysis indicators
• News aggregation from multiple sources
```
""")