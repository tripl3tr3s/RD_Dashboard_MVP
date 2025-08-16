# Project Structure Documentation
## Overview

This document outlines the architecture and organization of the RetailDAO Analytics MVP Dashboard.

### Directory Structure

retailDAO-Analytics-MVP/
├── 📁 .streamlit/                 # Streamlit configuration files
│   ├── config.toml               # App configuration
│   └── secrets.toml              # Secrets (not tracked in git)
│
├── 📁 components/                # Modular UI components
│   ├── __init__.py              # Package initialization
│   ├── btc_analysis.py          # Bitcoin price & MA ribbon chart
│   ├── dxy_analysis.py          # DXY index analysis & charts
│   ├── etf_flows.py             # ETF flow visualization components
│   └── funding_rates.py         # Perpetual funding rates display
│    
│
├── 📁 data/                      # Data fetching and processing
│   ├── __init__.py              # Package initialization  
│   ├── cache_utils.py           # Caching utilities and rate limiting
│   ├── crypto_data.py           # Cryptocurrency data from APIs
│   └── traditional_data.py      # Traditional market data (DXY, etc.)
│
├── 📁 utils/                     # Utility functions and helpers
│   ├── __init__.py              # Package initialization
│   ├── constants.py             # Application constants
│   ├── formatters.py            # Data formatting utilities
│   └── validators.py            # Input validation functions
│
├── 📁 MVPenv/                    # Python virtual environment (not tracked)
│
├── 📁 tests/                     # Unit tests (recommended addition)
│   ├── __init__.py
│   ├── test_data_fetching.py
│   └── test_components.py
│
├── 📁 docs/                      # Documentation (recommended addition)
│   ├── api_documentation.md
│   ├── deployment_guide.md
│   └── user_guide.md
│
├── 📄 .env                       # Environment variables (not tracked)
├── 📄 .env.example              # Template for environment variables
├── 📄 .gitignore                # Git ignore rules
├── 📄 main.py                   # Main Streamlit application entry point
├── 📄 requirements.txt          # Python dependencies
├── 📄 README.md                 # Project documentation
└── 📄 project_structure.md      # This file

## Component Architecture

🎨 Components (/components/)
Reusable Streamlit components that handle specific dashboard sections:

- btc_analysis.py: Bitcoin price charts with moving average ribbons
- funding_rates.py: Perpetual funding rate displays with explanations
- etf_flows.py: ETF flow visualizations and trend analysis
- dxy_analysis.py: DXY charts with risk asset correlation context

📊 Data Layer (/data/)
Handles all data fetching, processing, and caching:

- crypto_data.py: CoinGecko and Binance API interactions
- traditional_data.py: Alpha Vantage and other traditional market APIs
- cache_utils.py: Intelligent caching system with rate limiting

🛠 Utilities (/utils/)
Shared helper functions and configurations:

- constants.py: Application-wide constants and configurations
- formatters.py: Data formatting for display (percentages, currency, etc.)
- validators.py: Input validation and error handling

## Data Flow

APIs → data/ modules → cache_utils → components/ → main.py → Streamlit UI

API Calls: Data modules fetch from external APIs
Caching: cache_utils manages rate limiting and data freshness
Processing: Components process and format data for display
Rendering: main.py orchestrates component rendering
Display: Streamlit renders the final dashboard

Configuration Management

Environment Variables: Stored in .env (use .env.example as template)
Streamlit Config: App secrets in .streamlit/secrets.toml
Constants: Application constants in utils/constants.py

Security Considerations

1. All API keys stored in environment variables
2. .env file excluded from version control
3. Input validation on all user inputs
4. Rate limiting to prevent API abuse
5. Error handling prevents sensitive data exposure

Performance Optimizations

Intelligent caching reduces API calls
Component-based architecture enables selective updates
Data processing optimized for Streamlit's rerun behavior
Lazy loading of heavy computations

Recommended Additions

Testing: Add unit tests in /tests/ directory
Documentation: Expand /docs/ with API docs and guides
Logging: Add structured logging for monitoring
CI/CD: GitHub Actions for automated testing and deployment
Docker: Containerization for consistent deployment