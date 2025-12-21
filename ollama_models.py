import streamlit as st
import requests
import json

OLLAMA_BASE_URL = "http://localhost:11434"

def check_ollama_connection():
    """Check if Ollama is running"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags")
        return response.status_code == 200
    except:
        return False

def list_ollama_models():
    """List available Ollama models"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags")
        if response.status_code == 200:
            models = response.json()
            return [model['name'] for model in models['models']]
        return []
    except Exception as e:
        st.error(f"Error listing Ollama models: {str(e)}")
        return []

def generate_ollama_response(prompt, model="qwen2.5-coder:7b"):
    """Generate response using Ollama model"""
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', '')
        else:
            st.error(f"Ollama API error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error generating Ollama response: {str(e)}")
        return None

def analyze_financial_data_with_ollama(df, query, model="qwen2.5-coder:7b"):
    """Analyze financial data using Ollama model"""
    # Prepare data context
    recent_data = df.tail(10).to_string()
    summary_stats = df.describe().to_string()
    
    # Create prompt
    prompt = f"""You are a financial analyst. Based on this data:
{recent_data}

And these stats:
{summary_stats}

Answer the user: {query}"""
    
    # Generate response
    response = generate_ollama_response(prompt, model)
    return response

def hybrid_analysis(df, query, use_ollama=True):
    """Perform hybrid analysis using both Gemini and Ollama"""
    results = {}
    
    # Ollama analysis (if enabled and available)
    if use_ollama and check_ollama_connection():
        ollama_response = analyze_financial_data_with_ollama(df, query)
        if ollama_response:
            results['ollama'] = ollama_response
    
    return results