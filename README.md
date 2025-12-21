# FinGPT Analyst - Financial Data & AI Analyst

FinGPT Analyst is a comprehensive financial analysis platform that combines real-time market data with AI-powered insights.

## Features

- Real-time market data via yfinance
- Interactive financial charts and technical indicators
- AI-powered analysis using Google Gemini
- Price prediction using machine learning
- Financial news aggregation with multiple fallback sources
- Local and Cloud AI analysis with Ollama integration
- Alternative AI models via OpenRouter

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Google API Key for Gemini integration
- (Optional) Serper API Key for enhanced search
- (Optional) Exa API Key for specialized search
- (Optional) Ollama for local AI models

## Installation

1. Clone or download this repository
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
   
   Or use the deployment script:
   ```bash
   python deploy.py install
   ```

## Environment Variables

Create a `.env` file in the project root with the following variables:

```env
GOOGLE_API_KEY=your_google_api_key_here
SERPER_API_KEY=your_serper_api_key_here  # Optional
EXA_API_KEY=your_exa_api_key_here        # Optional
OPENROUTER_API_KEY=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
OPENROUTER_MODEL=cognitivecomputations/dolphin-mistral-24b-venice-edition:free
OLLAMA_CLOUD_API_KEY=c19ccb9b777445bab37c141adbe77a23.7Jpa8Fun4MfB9AqNfeawnMgy
OLLAMA_CLOUD_BASE_URL=https://ollama.com
OLLAMA_CLOUD_MODELS=gpt-oss:120b-cloud,gpt-oss:20b-cloud,deepseek-v3.1:671b-cloud,qwen3-coder:480b-cloud
```

## Running the Application

After installation and environment setup:

```bash
streamlit run app.py
```

Or use the deployment script:
```bash
python deploy.py
```

## API Keys

To use all features of the application, you'll need to obtain API keys:

1. **Google API Key**: Required for AI analysis features
   - Visit [Google AI Studio](https://aistudio.google.com/)
   - Create an API key

2. **Serper API Key**: Optional, for enhanced web search
   - Visit [Serper.dev](https://serper.dev/) 
   - Sign up and get an API key

3. **Exa API Key**: Optional, for specialized financial search
   - Visit [Exa.ai](https://exa.ai/)
   - Sign up and get an API key

4. **OpenRouter API Key**: Alternative AI models
   - Included by default in the .env.example file
   - Visit [OpenRouter](https://openrouter.ai/) for more information

5. **Ollama Cloud API Key**: Cloud-based Ollama models
   - Included by default in the .env.example file
   - Visit [Ollama](https://ollama.com/) for more information

## Ollama Integration (Optional)

To use AI models locally or via cloud:

### Local Mode:
1. Install [Ollama](https://ollama.ai/)
2. Pull a model (e.g., qwen2.5-coder):
   ```bash
   ollama pull qwen2.5-coder:7b
   ```
3. Start the Ollama service

### Cloud Mode:
1. The Ollama Cloud API key is already included in the .env.example file
2. Select a cloud model from the dropdown in the application UI
3. No local installation required

## Usage

1. Enter a stock ticker symbol (e.g., NVDA, AAPL, TSLA)
2. Select your preferred date range
3. Click "Fetch Market Data"
4. Explore the different analysis tabs:
   - Basic Charts
   - Advanced Analytics
   - AI Analyst
   - Price Prediction
   - News & Insights

## Dependencies

All required packages are listed in `requirements.txt`:
- streamlit
- pandas
- numpy
- yfinance
- langchain-google-genai
- scikit-learn
- requests
- python-dotenv
- exa-py
- nest-asyncio
- seaborn
- matplotlib
- plotly
- sentence-transformers

## License

This project is for educational and demonstration purposes.