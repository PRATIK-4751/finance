import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

def safe_extract_value(value):
    if isinstance(value, pd.Series):
        if len(value) > 0:
            return value.values[0]
        return 0
    elif isinstance(value, (list, tuple)):
        return value[0] if len(value) > 0 else 0
    return value

def display_financial_charts(df, current_ticker):
    if df is None or len(df) == 0:
        st.error("No data available to display")
        return
    
    st.subheader(f"Analysis for {current_ticker}")
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
        return

    try:
        fig, ax = plt.subplots(figsize=(10, 4))
        
        if 'Date' in df.columns:
            df_plot = df[['Date', 'Close']].copy()
            df_plot = df_plot.dropna()
            
            if len(df_plot) > 0:
                sns.lineplot(data=df_plot, x='Date', y='Close', ax=ax, color='blue')
                plt.xticks(rotation=45)
                ax.set_title(f"{current_ticker} Price Movement")
                ax.set_xlabel("Date")
                ax.set_ylabel("Close Price ($)")
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.warning("No valid data to plot")
        else:
            st.error("Date column not found in data")
    except Exception as e:
        st.error(f"Error creating chart: {str(e)}")
    finally:
        plt.close()

def display_prediction_chart(df, prediction):
    try:
        prediction_value = safe_extract_value(prediction)
        
        st.metric("Predicted Price for Tomorrow", f"${float(prediction_value):.2f}")
        st.write("This uses a trend-line algorithm (Linear Regression).")
        
        fig, ax = plt.subplots(figsize=(10, 4))
        
        if 'Date' in df.columns:
            recent_df = df.tail(30)[['Date', 'Close']].copy()
            recent_df = recent_df.dropna()
            
            if len(recent_df) > 0:
                sns.lineplot(data=recent_df, x='Date', y='Close', ax=ax, color='blue', label='Historical')
                
                last_date = pd.to_datetime(recent_df['Date'].iloc[-1])
                next_date = last_date + pd.Timedelta(days=1)
                
                ax.scatter(next_date, prediction_value, color='red', s=100, zorder=5, label='Prediction')
                ax.legend()
                plt.xticks(rotation=45)
                ax.set_title("Price Prediction")
                ax.set_xlabel("Date")
                ax.set_ylabel("Price ($)")
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.warning("Not enough data for prediction visualization")
        else:
            st.warning("Date information not available for prediction chart")
    except Exception as e:
        st.error(f"Error displaying prediction: {str(e)}")
    finally:
        plt.close()