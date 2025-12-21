import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

def safe_extract_value(value):
    if isinstance(value, pd.Series):
        if len(value) > 0:
            return value.values[0]
        return 0
    elif isinstance(value, (list, tuple)):
        return value[0] if len(value) > 0 else 0
    return value

def display_candlestick_chart(df, title="Candlestick Chart"):
    try:
        if len(df) == 0:
            st.warning("No data available for candlestick chart")
            return
        
        fig = go.Figure(data=go.Candlestick(
            x=df['Date'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close']
        ))
        fig.update_layout(title=title, xaxis_title="Date", yaxis_title="Price", height=500)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error displaying candlestick chart: {str(e)}")

def display_volume_chart(df, title="Trading Volume"):
    try:
        if len(df) == 0:
            st.warning("No data available for volume chart")
            return
        
        fig = px.bar(df, x='Date', y='Volume', title=title)
        fig.update_layout(xaxis_title="Date", yaxis_title="Volume", height=400)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error displaying volume chart: {str(e)}")

def display_correlation_heatmap(df, title="Correlation Heatmap"):
    try:
        numerical_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        available_cols = [col for col in numerical_cols if col in df.columns]
        
        if len(available_cols) < 2:
            st.warning("Not enough data columns for correlation analysis")
            return
        
        corr_data = df[available_cols].corr()
        
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr_data, annot=True, cmap='coolwarm', center=0, ax=ax, fmt='.2f')
        ax.set_title(title)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    except Exception as e:
        st.error(f"Error displaying correlation heatmap: {str(e)}")

def display_moving_averages(df, title="Moving Averages"):
    try:
        if len(df) < 50:
            st.warning("Not enough data points for 50-day moving average. Showing available data.")
        
        df = df.copy()
        df['MA_20'] = df['Close'].rolling(window=min(20, len(df))).mean()
        if len(df) >= 50:
            df['MA_50'] = df['Close'].rolling(window=50).mean()
            y_cols = ['Close', 'MA_20', 'MA_50']
        else:
            y_cols = ['Close', 'MA_20']
        
        fig = px.line(df, x='Date', y=y_cols, title=title)
        fig.update_layout(xaxis_title="Date", yaxis_title="Price", height=500)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error displaying moving averages: {str(e)}")

def display_bollinger_bands(df, title="Bollinger Bands"):
    try:
        if len(df) < 20:
            st.warning("Not enough data points for Bollinger Bands (minimum 20 required)")
            return
        
        df = df.copy()
        window = min(20, len(df))
        df['MA_20'] = df['Close'].rolling(window=window).mean()
        df['STD_20'] = df['Close'].rolling(window=window).std()
        df['Upper_Band'] = df['MA_20'] + (df['STD_20'] * 2)
        df['Lower_Band'] = df['MA_20'] - (df['STD_20'] * 2)
        
        df_clean = df.dropna(subset=['MA_20', 'Upper_Band', 'Lower_Band'])
        
        if len(df_clean) == 0:
            st.warning("Not enough data for Bollinger Bands calculation")
            return
        
        fig = px.line(df_clean, x='Date', y=['Close', 'MA_20', 'Upper_Band', 'Lower_Band'], title=title)
        fig.update_layout(xaxis_title="Date", yaxis_title="Price", height=500)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error displaying Bollinger Bands: {str(e)}")

def display_rsi_indicator(df, title="RSI Indicator"):
    try:
        if len(df) < 14:
            st.warning("Not enough data points for RSI (minimum 14 required)")
            return
        
        df = df.copy()
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        
        loss = loss.replace(0, 0.0001)
        
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        df_clean = df.dropna(subset=['RSI'])
        
        if len(df_clean) == 0:
            st.warning("Not enough data for RSI calculation")
            return
        
        fig = px.line(df_clean, x='Date', y='RSI', title=title)
        fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
        fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")
        fig.update_layout(xaxis_title="Date", yaxis_title="RSI", height=400)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error displaying RSI: {str(e)}")

def display_price_distribution(df, title="Price Distribution"):
    try:
        if len(df) == 0:
            st.warning("No data available for price distribution")
            return
        
        fig = px.histogram(df, x='Close', nbins=min(50, len(df)//2 or 10), title=title)
        fig.update_layout(xaxis_title="Price", yaxis_title="Frequency", height=400)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error displaying price distribution: {str(e)}")

def display_all_charts(df, current_ticker):
    if df is None or len(df) == 0:
        st.error("No data available for analysis")
        return
    
    st.subheader(f"Advanced Analysis for {current_ticker}")
    
    m1, m2, m3 = st.columns(3)
    
    try:
        last_price = safe_extract_value(df['Close'].iloc[-1])
        max_price = safe_extract_value(df['High'].max())
        min_price = safe_extract_value(df['Low'].min())
        
        m1.metric("Last Price", f"${float(last_price):.2f}")
        m2.metric("Max Price", f"${float(max_price):.2f}")
        m3.metric("Min Price", f"${float(min_price):.2f}")
    except Exception as e:
        st.error(f"Error displaying metrics: {str(e)}")
    
    display_candlestick_chart(df, f"{current_ticker} Candlestick Chart")
    
    display_moving_averages(df, f"{current_ticker} Moving Averages")
    
    display_bollinger_bands(df, f"{current_ticker} Bollinger Bands")
    
    display_rsi_indicator(df, f"{current_ticker} RSI Indicator")
    
    display_volume_chart(df, f"{current_ticker} Trading Volume")
    
    display_correlation_heatmap(df, f"{current_ticker} Correlation Heatmap")
    
    display_price_distribution(df, f"{current_ticker} Price Distribution")