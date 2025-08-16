# RetailDAO Analytics MVP Dashboard

A comprehensive cryptocurrency and traditional market analytics dashboard providing real-time insights for retail investors and DAO participants.

## 🚀 Live Demo
[RetailDAO-Dashboard-MVP](https://mvpdashboardretaildao.streamlit.app/)

## 📊 Features

### Bitcoin Analysis
- **BTC Price Chart with Ribbon MAs**: Interactive chart displaying 20d, 50d, 100d, and 200d moving averages
- **14-Day RSI Indicator**: Visual gauge showing market sentiment (Extremely Overbought, Overbought, Normal, Oversold, Extremely Oversold)

### Derivatives Market Intelligence  
- **Perpetual Funding Rates**: 7-day average funding rates for BTC and ETH with contextual explanations
- **Market Sentiment Analysis**: Clear interpretation of funding rate implications for price direction

### Institutional Flow Tracking
- **Spot ETF Net Flows**: Daily and average net flows for BTC and ETH ETFs with rate of change metrics
- **Flow Impact Analysis**: Visual indicators showing institutional adoption trends

### Macro Economic Context
- **U.S. Dollar Index (DXY)**: Real-time DXY chart with educational context on risk asset correlation
- **Market Regime Identification**: Clear explanations of how DXY movements affect crypto markets

## 🛠 Technology Stack

- **Frontend**: Streamlit
- **Backend**: Python 3.9+
- **Data Sources**: 
  - CoinGecko API (BTC pricing & calculations)
  - Binance API (Perpetual funding rates)
  - Alpha Vantage API (DXY data)
  - *ETF Flow Data: Currently simulated (CoinGlass API requires paid tier)*
- **Caching**: Intelligent rate limit management and data caching
- **Deployment**: [Platform to be specified]

## 📁 Project Structure

```
retailDAO-Analytics-MVP/
├── .streamlit/              # Streamlit configuration
├── components/              # Reusable UI components
│   ├── __pycache__/
│   ├── __init__.py
│   ├── btc_analysis.py      # BTC chart and RSI components
│   ├── dxy_analysis.py      # DXY analysis component
│   ├── etf_flows.py         # ETF flows visualization
│   ├── funding_rates.py     # Perp funding rates component
│   
├── data/                    # Data processing modules
│   ├── __pycache__/
│   ├── __init__.py
│   ├── cache_utils.py       # Caching utilities
│   ├── crypto_data.py       # Crypto data fetching
│   └── traditional_data.py  # Traditional market data
├── utils/                   # Utility functions
├── MVPenv/                  # Virtual environment
├── .env                     # Environment variables (not tracked)
├── .gitignore              # Git ignore rules
├── main.py                 # Main Streamlit application
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🚦 Getting Started

### Prerequisites
- Python 3.9 or higher
- API keys for:
  - CoinGecko (free tier available)
  - Binance (for funding rates)
  - Alpha Vantage (free tier available)

### Installation

1. **Clone the repository**
   ```bash
   git clone [repository-url]
   cd retailDAO-Analytics-MVP
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv MVPenv
   source MVPenv/bin/activate  # On Windows: MVPenv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run the application**
   ```bash
   streamlit run main.py
   ```

## 🔧 Configuration

Create a `.env` file with the following variables:

```env
# API Keys
COINGECKO_API_KEY=your_coingecko_api_key
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET_KEY=your_binance_secret_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key

# Cache Settings
CACHE_DURATION_MINUTES=15
MAX_RETRIES=3

# App Settings
DEBUG_MODE=False
```

## 📈 Data Sources & Limitations

### Real-Time Data
- ✅ **BTC Price & Technical Indicators**: CoinGecko API (15-minute cache)
- ✅ **Perpetual Funding Rates**: Binance API (real-time)
- ✅ **DXY Index**: Alpha Vantage API (daily updates)

### Simulated Data
- ⚠️ **ETF Flow Data**: Currently using simulated data as CoinGlass API requires paid subscription
  - Mock data follows realistic patterns and ranges
  - Will be replaced with real data in production version

## 🎯 MVP Scope & Future Enhancements

### Current MVP Features
- [x] BTC price visualization with moving averages
- [x] RSI sentiment gauge
- [x] Funding rates with explanatory context
- [x] DXY correlation analysis
- [x] Responsive design for mobile/desktop
- [x] Intelligent caching system

### Planned Enhancements
- [ ] Real ETF flow data integration
- [ ] Additional altcoin coverage
- [ ] Historical backtesting features
- [ ] User customization options
- [ ] Alert system for key thresholds
- [ ] Export functionality for reports

## 🔒 Security & Performance

- **Rate Limiting**: Intelligent API request management to stay within limits
- **Error Handling**: Graceful degradation when APIs are unavailable
- **Data Validation**: Input sanitization and data integrity checks
- **Caching Strategy**: Optimized cache timing to balance freshness and performance
- **No Sensitive Data**: All API keys stored securely in environment variables

## 📱 Responsive Design

The dashboard is optimized for:
- Desktop browsers (primary experience)
- Tablet viewing
- High-resolution displays

## 🤝 Contributing

This is an MVP for RetailDAO. For feature requests or bug reports, please contact the development team.

## 📄 License

[License type to be specified]


---

**Note**: This is a Minimum Viable Product (MVP) designed to demonstrate core functionality. ETF flow data is currently simulated pending integration with premium data sources.

**Last Updated**: August 2025