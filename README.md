# StockMe

A comprehensive AI-powered stock analysis platform that generates in-depth reports by analyzing multiple data sources including stock data, news articles, social media sentiment, and more. The platform leverages advanced AI models like Google's Gemini AI to provide actionable insights and detailed analysis.

## Features

- Real-time stock data analysis
- News sentiment analysis from multiple sources
- YouTube content analysis
- Technical and fundamental analysis
- Interactive data visualizations using Weights & Biases Weave
- Comprehensive report generation
- Intelligent caching with ApertureDB

## Environment Setup

1. Create and activate a Conda environment:
```bash
conda create -n stock-me python=3.11
conda activate stock-me
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with required API keys:
```
GOOGLE_API_KEY=your_gemini_ai_key
AGENTQL_API_KEY=your_agentql_key
WANDB_API_KEY=your_wandb_api_key
```

## Getting Started

1. Start the backend server:
```bash
uvicorn backend.app.main:app --reload
```

2. Access the API at `http://localhost:8000`

3. View interactive visualizations at: https://wandb.ai/[your-username]/stock-analysis/weave

## Project Structure

- `backend/`: FastAPI backend service
  - `app/`: Core application code
  - `agents/`: AI agents for different analysis tasks
  - `tests/`: Test suite

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT
