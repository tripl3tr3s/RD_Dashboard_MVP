import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from .cache_utils import cache_data
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TraditionalDataFetcher:
    """Handles traditional market data fetching (DXY, ETF flows, etc.)"""
    
    def __init__(self):
        self.session = requests.Session()
    
    @cache_data(ttl=3600)  # Cache for 1 hour
    def get_etf_flows(self) -> Dict[str, Dict[str, Any]]:
        """Get real ETF flow data for BTC and ETH from CoinGlass v4, with mock fallback"""
        try:
            coinglass_api_key = st.secrets["general"]["COINGLASS_API_KEY"]
            # Fetch BTC ETF flow history
            btc_url = "https://open-api-v4.coinglass.com/api/etf/bitcoin/flow-history"
            btc_headers = {"CG-API-KEY": coinglass_api_key}
            btc_response = self.session.get(btc_url, headers=btc_headers, timeout=10)
            btc_response.raise_for_status()
            btc_data = btc_response.json()
            logger.info(f"BTC CoinGlass response: {btc_data}")
            
            # Fetch ETH ETF flow history
            eth_url = "https://open-api-v4.coinglass.com/api/etf/ethereum/flow-history"
            eth_headers = {"CG-API-KEY": coinglass_api_key}
            eth_response = self.session.get(eth_url, headers=eth_headers, timeout=10)
            eth_response.raise_for_status()
            eth_data = eth_response.json()
            logger.info(f"ETH CoinGlass response: {eth_data}")
            
            # Check for upgrade plan error
            if btc_data.get('code') == '400' and btc_data.get('msg') == 'Upgrade plan':
                logger.warning("CoinGlass requires plan upgrade; falling back to mock data")
                return self._get_mock_etf_flows()
            
            # Parse BTC data (adjust keys based on actual response structure)
            btc_flow = btc_data.get('data', [{}])[0] if btc_data.get('data') else {}
            eth_flow = eth_data.get('data', [{}])[0] if eth_data.get('data') else {}
            
            return {
                'BTC': {
                    'net_flow_1d': btc_flow.get('daily_flow', 0),  # Adjust key if differs
                    'net_flow_7d': btc_flow.get('weekly_flow', 0),
                    'change_pct': btc_flow.get('change', 0),
                    'total_aum': btc_flow.get('aum', 0)
                },
                'ETH': {
                    'net_flow_1d': eth_flow.get('daily_flow', 0),
                    'net_flow_7d': eth_flow.get('weekly_flow', 0),
                    'change_pct': eth_flow.get('change', 0),
                    'total_aum': eth_flow.get('aum', 0)
                }
            }
        except requests.RequestException as e:
            logger.error(f"ETF flow error: {e}, response text: {btc_response.text if 'btc_response' in locals() else eth_response.text if 'eth_response' in locals() else 'No response'}")
            # Fallback to mock data on network error
            return self._get_mock_etf_flows()
    
    def _get_mock_etf_flows(self) -> Dict[str, Dict[str, Any]]:
        """Generate mock ETF flow data for BTC and ETH"""
        np.random.seed(int(datetime.now().timestamp()) // 3600)  # Change hourly
        return {
            'BTC': {
                'net_flow_1d': np.random.randint(-200, 300) * 1000000,  # Daily in USD
                'net_flow_7d': np.random.randint(-800, 1200) * 1000000,  # 7-day in USD
                'change_pct': np.random.uniform(-25, 35),  # Percentage change
                'total_aum': np.random.randint(50000, 80000) * 1000000  # Total AUM in USD
            },
            'ETH': {
                'net_flow_1d': np.random.randint(-100, 150) * 1000000,
                'net_flow_7d': np.random.randint(-400, 600) * 1000000,
                'change_pct': np.random.uniform(-30, 40),
                'total_aum': np.random.randint(8000, 12000) * 1000000
            }
        }
    
    @cache_data(ttl=3600)
    def get_dxy_data(self, days: int = 90) -> pd.DataFrame:
        """Get real DXY data from Alpha Vantage (approximation via USD/EUR)"""
        try:
            api_key = st.secrets["general"]["ALPHA_VANTAGE_API_KEY"]
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=USDEUR&apikey={api_key}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json().get("Time Series (Daily)", {})
            dates = []
            prices = []
            for date_str, values in data.items():
                date = pd.to_datetime(date_str)
                if (datetime.now() - timedelta(days=days)).date() <= date.date():
                    dates.append(date)
                    eur_usd = float(values["4. close"])
                    usd_eur = 1 / eur_usd if eur_usd != 0 else 0
                    prices.append(usd_eur * 100)  # Scale to approximate DXY base
            df = pd.DataFrame({'date': dates, 'dxy': prices}).sort_values('date').reset_index(drop=True)
            print(f"DXY data fetched: {len(df)} rows from {df['date'].min()} to {df['date'].max()}")
            return df
        except requests.RequestException as e:
            print(f"Error fetching DXY data from Alpha Vantage: {e}")
            return pd.DataFrame({'date': [], 'dxy': []})
    
    def get_dxy_analysis(self) -> Dict[str, Any]:
        """Get DXY analysis and interpretation based on real data"""
        try:
            df = self.get_dxy_data(days=30)
            if df.empty:
                return {}
            current_dxy = df['dxy'].iloc[-1]
            prev_dxy = df['dxy'].iloc[-2] if len(df) > 1 else current_dxy
            week_ago_dxy = df['dxy'].iloc[-7] if len(df) > 7 else current_dxy
            daily_change = current_dxy - prev_dxy
            weekly_change = current_dxy - week_ago_dxy
            if daily_change > 0.1:
                trend, impact, color = "Rising Strongly", "Risk-Off (Bearish for Crypto)", "#ff5757"
            elif daily_change > 0:
                trend, impact, color = "Rising", "Slight Risk-Off", "#ff8c42"
            elif daily_change < -0.1:
                trend, impact, color = "Falling Strongly", "Risk-On (Bullish for Crypto)", "#00d4aa"
            elif daily_change < 0:
                trend, impact, color = "Falling", "Slight Risk-On", "#4ecdc4"
            else:
                trend, impact, color = "Stable", "Neutral", "#a0a0a0"
            return {
                'current_value': current_dxy,
                'daily_change': daily_change,
                'weekly_change': weekly_change,
                'trend': trend,
                'impact': impact,
                'color': color,
                'dataframe': df
            }
        except Exception as e:
            print(f"Error analyzing DXY data: {e}")
            return {}