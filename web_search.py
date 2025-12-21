import streamlit as st
import http.client
import json
import requests
import os
from dotenv import load_dotenv
from exa_py import Exa

# Load environment variables
load_dotenv()

def search_serper(query):
    """Search using Serper API"""
    try:
        api_key = os.getenv('SERPER_API_KEY')
        if not api_key:
            st.warning("Serper API key not found")
            return None
            
        conn = http.client.HTTPSConnection("google.serper.dev")
        payload = json.dumps({
            "q": query
        })
        headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
        conn.request("POST", "/search", payload, headers)
        res = conn.getresponse()
        data = res.read()
        return json.loads(data.decode("utf-8"))
    except Exception as e:
        st.error(f"Serper search error: {str(e)}")
        return None

def search_searchapi(query):
    """Search using SearchAPI"""
    try:
        url = "https://www.searchapi.io/api/v1/search"
        params = {
            "engine": "google",
            "q": query
        }
        response = requests.get(url, params=params)
        return response.json()
    except Exception as e:
        st.error(f"SearchAPI error: {str(e)}")
        return None

def search_exa(query):
    """Search using Exa API"""
    try:
        api_key = os.getenv('EXA_API_KEY')
        if not api_key:
            st.warning("Exa API key not found")
            return None
        
        exa = Exa(api_key)
        result = exa.search_and_contents(
            query,
            type="auto",
            text=True,
        )
        return result
    except Exception as e:
        st.error(f"Exa search error: {str(e)}")
        return None

def search_openrouter(query):
    """Search using OpenRouter API"""
    try:
        api_key = os.getenv('OPENROUTER_API_KEY')
        model = os.getenv('OPENROUTER_MODEL', 'cognitivecomputations/dolphin-mistral-24b-venice-edition:free')
        
        if not api_key:
            st.warning("OpenRouter API key not found")
            return None
        
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": f"Provide a list of recent financial news articles about {query}. Include titles, brief summaries, and URLs if available."}
            ]
        }
        
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"OpenRouter API error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"OpenRouter search error: {str(e)}")
        return None

def search_financial_news(company_name):
    """Search for financial news about a company"""
    query = f"{company_name} financial news"
    
    # Try Exa first (most reliable for financial content)
    result = search_exa(query)
    if result:
        return result
    
    # Fallback to Serper
    result = search_serper(query)
    if result:
        return result
    
    # Fallback to OpenRouter
    result = search_openrouter(query)
    if result:
        return result
    
    # Final fallback to SearchAPI
    result = search_searchapi(query)
    return result

def extract_key_info(search_results):
    """Extract key information from search results"""
    if not search_results:
        return []
    
    key_info = []
    
    # Handle different API response formats
    if hasattr(search_results, 'results'):  # Exa format
        for item in search_results.results:
            if hasattr(item, 'text'):
                key_info.append({
                    'title': getattr(item, 'title', 'N/A'),
                    'url': getattr(item, 'url', 'N/A'),
                    'snippet': item.text[:200] + '...' if len(item.text) > 200 else item.text
                })
    elif 'organic' in search_results:  # Serper format
        for item in search_results['organic'][:5]:  # Top 5 results
            key_info.append({
                'title': item.get('title', 'N/A'),
                'url': item.get('link', 'N/A'),
                'snippet': item.get('snippet', 'N/A')
            })
    elif 'answerBox' in search_results:  # SearchAPI format
        key_info.append({
            'title': 'Featured Result',
            'url': search_results.get('answerBox', {}).get('link', 'N/A'),
            'snippet': search_results.get('answerBox', {}).get('snippet', 'N/A')
        })
    
    return key_info