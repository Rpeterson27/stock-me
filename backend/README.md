# Stock Analysis AI Backend

This is the backend service for the Stock Analysis AI Report Generator. It provides AI-powered stock analysis by integrating multiple data sources and leveraging generative AI.

## Architecture

The backend is built with FastAPI and consists of several key components:

### Core Components

- `app/main.py`: FastAPI application entry point and API routes
- `app/services.py`: Core business logic and service layer

### AI Agents

- `agents/report_generator.py`: Generates comprehensive stock analysis using Gemini AI
- `agents/news_lookup_agent.py`: Fetches and processes stock-related news articles
- `agents/news_article_scraping_agent.py`: Scrapes full article content with paywall detection
- `agents/browser_context.py`: Manages browser automation for web scraping
- `agents/youtube_agent.py`: Retrieves relevant YouTube content

## Data Sources

1. **Stock Data**: Yahoo Finance API
   - Real-time and historical price data
   - Company information and metrics

2. **News Articles**: 
   - Yahoo Finance news feed
   - Full article content from various sources
   - Paywall detection and handling

3. **Social Media**: 
   - YouTube videos and analysis
   - Channel and content metadata

4. **AI Analysis**:
   - Google's Gemini AI for report generation
   - AgentQL for structured data extraction

5. **Data Visualization**:
   - Weights & Biases Weave for interactive visualizations
   - Real-time tracking of analysis metrics
   - Historical data comparison
   - View traces at: https://wandb.ai/[your-username]/stock-analysis/weave

## API Endpoints

### Generate Stock Report
```http
POST /report/{ticker}
```
Generates a comprehensive stock analysis report including:
- Technical Analysis
- News Sentiment
- Social Media Analysis
- Fundamental Analysis
- Actionable Summary
- Potential Risks/Opportunities

## Environment Variables

Required environment variables in `.env`:
```
GOOGLE_API_KEY=your_gemini_ai_key
AGENTQL_API_KEY=your_agentql_key
WANDB_API_KEY=your_wandb_api_key  # For Weights & Biases integration
```

## Getting Started

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with required API keys:
```
GOOGLE_API_KEY=your_gemini_ai_key
AGENTQL_API_KEY=your_agentql_key
WANDB_API_KEY=your_wandb_api_key  # For Weights & Biases integration
```

3. Run the server:
```bash
uvicorn backend.app.main:app --reload
```

## Future Improvements

1. **Caching Layer**:
   - Implement ApertureDB for data caching
   - Cache frequently accessed stock data
   - Store historical analysis reports

2. **Enhanced Analysis**:
   - More sophisticated AI prompt engineering
   - Additional data source integrations
   - Real-time market sentiment analysis

3. **Performance**:
   - Implement parallel processing for data fetching
   - Optimize browser automation
   - Add request rate limiting

4. **Monitoring & Analytics**:
   - Enhanced Weave integration for more metrics
   - Custom dashboards for analysis quality
   - A/B testing different prompt strategies

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
