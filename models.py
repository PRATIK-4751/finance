import streamlit as st
import asyncio
import nest_asyncio
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from sklearn.linear_model import LinearRegression
import numpy as np

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

def initialize_gemini_model():
    """Initialize and return the Gemini model"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("Google API key not found in environment variables.")
        return None
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    except RuntimeError:
        pass
    
    return ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key)

def create_analysis_prompt():
    """Create and return the analysis prompt template"""
    return PromptTemplate(
        input_variables=["question", "data", "stats"],
        template="You are a financial analyst. Based on this data:\n{data}\n\nAnd these stats:\n{stats}\n\nAnswer the user: {question}"
    )

def perform_price_prediction(df):
    """Perform price prediction using linear regression"""
    df['Day_Num'] = np.arange(len(df))
    X = df[['Day_Num']]
    y = df['Close']
    
    model = LinearRegression()
    model.fit(X, y)
    
    next_index = np.array([[len(df)]])
    prediction = model.predict(next_index)[0]
    
    return prediction