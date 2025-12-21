import streamlit as st
import requests
import json
import os

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_CLOUD_BASE_URL = os.getenv('OLLAMA_CLOUD_BASE_URL', 'https://ollama.com')
OLLAMA_CLOUD_API_KEY = os.getenv('OLLAMA_CLOUD_API_KEY')
OLLAMA_CLOUD_MODELS = os.getenv('OLLAMA_CLOUD_MODELS', '').split(',') if os.getenv('OLLAMA_CLOUD_MODELS') else []

def check_ollama_connection():
    """Check if Ollama is running"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags")
        return response.status_code == 200
    except:
        return False

def check_ollama_cloud_connection():
    """Check if Ollama Cloud is accessible"""
    try:
        if not OLLAMA_CLOUD_API_KEY:
            return False
        
        headers = {
            "Authorization": f"Bearer {OLLAMA_CLOUD_API_KEY}",
            "Content-Type": "application/json"
        }
        response = requests.get(f"{OLLAMA_CLOUD_BASE_URL}/api/tags", headers=headers)
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

def list_ollama_cloud_models():
    """List available Ollama Cloud models"""
    try:
        if not OLLAMA_CLOUD_API_KEY:
            st.warning("Ollama Cloud API key not found")
            return []
        
        headers = {
            "Authorization": f"Bearer {OLLAMA_CLOUD_API_KEY}",
            "Content-Type": "application/json"
        }
        response = requests.get(f"{OLLAMA_CLOUD_BASE_URL}/api/tags", headers=headers)
        if response.status_code == 200:
            models = response.json()
            return [model['name'] for model in models['models']]
        return []
    except Exception as e:
        st.error(f"Error listing Ollama Cloud models: {str(e)}")
        return []

def generate_ollama_response(prompt, model="qwen2.5-coder:7b", use_cloud=False):
    """Generate response using Ollama model (local or cloud)"""
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        if use_cloud:
            # Use Ollama Cloud
            if not OLLAMA_CLOUD_API_KEY:
                st.error("Ollama Cloud API key not found")
                return None
            
            headers = {
                "Authorization": f"Bearer {OLLAMA_CLOUD_API_KEY}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{OLLAMA_CLOUD_BASE_URL}/api/generate",
                json=payload,
                headers=headers
            )
        else:
            # Use local Ollama
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

def analyze_financial_data_with_ollama(df, query, model="qwen2.5-coder:7b", use_cloud=False):
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
    response = generate_ollama_response(prompt, model, use_cloud)
    return response

def hybrid_analysis(df, query, use_ollama=True, use_ollama_cloud=False):
    """Perform hybrid analysis using both Gemini and Ollama (local or cloud)"""
    results = {}
    
    # Ollama analysis (if enabled and available)
    if use_ollama and (check_ollama_connection() or check_ollama_cloud_connection()):
        ollama_response = analyze_financial_data_with_ollama(df, query, use_cloud=use_ollama_cloud)
        if ollama_response:
            results['ollama'] = ollama_response
    
    return results