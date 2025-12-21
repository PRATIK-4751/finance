import streamlit as st
import yfinance as yf
import pandas as pd

def validate_and_clean_data(df):
    if df is None or df.empty:
        return None
    
    df = df.copy()
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
    
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in required_columns:
        if col not in df.columns:
            st.error(f"Missing required column: {col}")
            return None
    
    if 'Date' not in df.columns and df.index.name == 'Date':
        df = df.reset_index()
    elif 'Date' not in df.columns:
        df['Date'] = df.index
        df = df.reset_index(drop=True)
    
    df = df.dropna(subset=['Close'])
    
    df = df[df['Close'] > 0]
    df = df[df['Volume'] >= 0]
    
    return df

def fetch_market_data(ticker, start_date, end_date):
    try:
        ticker = ticker.strip().upper()
        
        with st.spinner("Fetching data..."):
            df_raw = yf.download(ticker, start=start_date, end=end_date, progress=False)
            
            if df_raw.empty:
                st.error(f"❌ No data found for ticker '{ticker}'. Please check the ticker symbol.")
                return
            
            df_clean = validate_and_clean_data(df_raw)
            
            if df_clean is None or len(df_clean) == 0:
                st.error(f"❌ Invalid data for ticker '{ticker}'. Please try a different ticker.")
                return
            
            if len(df_clean) < 2:
                st.error(f"⚠ Not enough data points. Please select a longer date range.")
                return
            
            st.session_state['df'] = df_clean
            st.session_state['ticker'] = ticker
            st.success(f"✓ Data loaded successfully! {len(df_clean)} data points retrieved.")
            
    except Exception as e:
        st.error(f"❌ Error fetching data: {str(e)}")
        st.info("💡 Try using a valid US stock ticker (e.g., AAPL, MSFT, GOOGL, TSLA, NVDA)")

def get_financial_metrics(df):
    try:
        last_price = df['Close'].iloc[-1]
        if isinstance(last_price, pd.Series):
            last_price = last_price.values[0]
        
        max_price = df['High'].max()
        if isinstance(max_price, pd.Series):
            max_price = max_price.values[0]
        
        min_price = df['Low'].min()
        if isinstance(min_price, pd.Series):
            min_price = min_price.values[0]
        
        return {
            'last_price': float(last_price),
            'max_price': float(max_price),
            'min_price': float(min_price)
        }
    except Exception as e:
        st.error(f"Error calculating metrics: {str(e)}")
        return None