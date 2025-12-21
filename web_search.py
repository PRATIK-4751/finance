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
        conn = http.client.HTTPSConnection("google.serper.dev")
        payload = json.dumps({
            "q": query
        })
        headers = {
            'X-API-KEY': os.getenv('SERPER_API_KEY'),
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
        exa = Exa(os.getenv('EXA_API_KEY'))
        result = exa.search_and_contents(
            query,
            type="auto",
            text=True,
        )
        return result
    except Exception as e:
        st.error(f"Exa search error: {str(e)}")
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