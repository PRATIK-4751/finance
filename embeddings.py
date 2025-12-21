import streamlit as st
from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd

@st.cache_resource
def load_embedding_model():
    """Load and cache the sentence transformer model"""
    return SentenceTransformer('all-MiniLM-L6-v2')

def generate_embeddings(texts):
    """Generate embeddings for a list of texts"""
    model = load_embedding_model()
    embeddings = model.encode(texts)
    return embeddings

def find_similar_texts(query, texts, top_k=5):
    """Find the most similar texts to a query"""
    model = load_embedding_model()
    
    # Generate embeddings
    query_embedding = model.encode([query])
    text_embeddings = model.encode(texts)
    
    # Calculate cosine similarities
    similarities = np.dot(text_embeddings, query_embedding.T).flatten()
    
    # Get top-k most similar texts
    top_indices = np.argsort(similarities)[::-1][:top_k]
    
    return [(texts[i], similarities[i]) for i in top_indices]

def embed_financial_data(df):
    """Create embeddings for financial data"""
    # Convert financial data to text representations
    text_representations = []
    for _, row in df.iterrows():
        text = f"Date: {row['Date']}, Open: {row['Open']}, High: {row['High']}, Low: {row['Low']}, Close: {row['Close']}, Volume: {row['Volume']}"
        text_representations.append(text)
    
    # Generate embeddings
    embeddings = generate_embeddings(text_representations)
    
    return text_representations, embeddings