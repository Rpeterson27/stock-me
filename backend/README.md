# StockMe Backend Developer Documentation

This document provides technical details about the backend service architecture and implementation. For general project information and setup instructions, please refer to the main README in the root directory.

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
