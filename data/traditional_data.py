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
            btc_flow_url = "https://open-api-v4.coinglass.com/api/etf/bitcoin/flow-history"
            headers = {"CG-API-KEY": coinglass_api_key}
            btc_flow_response = self.session.get(btc_flow_url, headers=headers, timeout=10)
            btc_flow_response.raise_for_status()
            btc_flow_data = btc_flow_response.json()
            logger.info(f"BTC CoinGlass flow response: {btc_flow_data}")
            
            # Fetch ETH ETF flow history
            eth_flow_url = "https://open-api-v4.coinglass.com/api/etf/ethereum/flow-history"
            eth_flow_response = self.session.get(eth_flow_url, headers=headers, timeout=10)
            eth_flow_response.raise_for_status()
            eth_flow_data = eth_flow_response.json()
            logger.info(f"ETH CoinGlass flow response: {eth_flow_data}")
            
            # Check for upgrade plan error
            if btc_flow_data.get('code') == '400' and btc_flow_data.get('msg') == 'Upgrade plan':
                logger.warning("CoinGlass requires plan upgrade; falling back to mock data")
                return self._get_mock_etf_flows()
            
            # Fetch BTC ETF list for AUM
            btc_list_url = "https://open-api-v4.coinglass.com/api/etf/bitcoin/list"
            btc_list_response = self.session.get(btc_list_url, headers=headers, timeout=10)
            btc_list_response.raise_for_status()
            btc_list_data = btc_list_response.json()
            
            # Fetch ETH ETF list for AUM
            eth_list_url = "https://open-api-v4.coinglass.com/api/etf/ethereum/list"
            eth_list_response = self.session.get(eth_list_url, headers=headers, timeout=10)
            eth_list_response.raise_for_status()
            eth_list_data = eth_list_response.json()
            
            # Compute total AUM
            btc_total_aum = sum(float(d.get('aum_usd', 0)) for d in btc_list_data.get('data', [])) if btc_list_data.get('code') == '0' else 0
            eth_total_aum = sum(float(d.get('aum_usd', 0)) for d in eth_list_data.get('data', [])) if eth_list_data.get('code') == '0' else 0
            
            # Parse history (sort by timestamp descending, latest first)
            btc_history = sorted(btc_flow_data.get('data', []), key=lambda x: x['timestamp'], reverse=True)
            eth_history = sorted(eth_flow_data.get('data', []), key=lambda x: x['timestamp'], reverse=True)
            
            # Compute summaries for BTC
            btc_summary = self._compute_etf_summary(btc_history, btc_total_aum)
            eth_summary = self._compute_etf_summary(eth_history, eth_total_aum)
            
            return {
                'BTC': {
                    'summary': btc_summary,
                    'history': btc_history
                },
                'ETH': {
                    'summary': eth_summary,
                    'history': eth_history
                }
            }
        except requests.RequestException as e:
            logger.error(f"ETF flow error: {str(e)}")
            return self._get_mock_etf_flows()
    
    def _compute_etf_summary(self, history: list, total_aum: float) -> Dict[str, Any]:
        if not history:
            return {
                'net_flow_1d': 0,
                'net_flow_7d': 0,
                'change_pct': 0,
                'total_aum': total_aum
            }
        net_flow_1d = history[0].get('flow_usd', 0)
        net_flow_7d = sum(d.get('flow_usd', 0) for d in history[:7])
        prev_flow = history[1].get('flow_usd', 0) if len(history) > 1 else 0
        change_pct = ((net_flow_1d - prev_flow) / abs(prev_flow) * 100) if prev_flow != 0 else 0
        return {
            'net_flow_1d': net_flow_1d,
            'net_flow_7d': net_flow_7d,
            'change_pct': change_pct,
            'total_aum': total_aum
        }
    
    def _get_mock_etf_flows(self) -> Dict[str, Dict[str, Any]]:
        """Generate mock ETF flow data for BTC and ETH"""
        np.random.seed(int(datetime.now().timestamp()) // 3600)  # Change hourly
        days = 60  # Approximately 2 months
        end_date = datetime.now()
        dates = pd.date_range(end=end_date, periods=days, freq='B')  # Business days
        
        # Mock for BTC
        btc_daily_flows = np.random.randint(-500, 1500, size=days) * 1000000
        btc_prices = 60000 + np.cumsum(np.random.normal(0, 500, days))
        btc_history = [
            {
                'timestamp': int(date.timestamp() * 1000),
                'flow_usd': float(btc_daily_flows[i]),
                'price_usd': float(btc_prices[i])
            } for i, date in enumerate(dates)
        ][::-1]  # Newest first
        
        # Mock for ETH
        eth_daily_flows = np.random.randint(-200, 600, size=days) * 1000000
        eth_prices = 3000 + np.cumsum(np.random.normal(0, 50, days))
        eth_history = [
            {
                'timestamp': int(date.timestamp() * 1000),
                'flow_usd': float(eth_daily_flows[i]),
                'price_usd': float(eth_prices[i])
            } for i, date in enumerate(dates)
        ][::-1]  # Newest first
        
        # Summaries
        btc_summary = self._compute_etf_summary(btc_history, np.random.randint(100000, 120000) * 1000000)
        eth_summary = self._compute_etf_summary(eth_history, np.random.randint(8000, 12000) * 1000000)
        
        return {
            'BTC': {'summary': btc_summary, 'history': btc_history},
            'ETH': {'summary': eth_summary, 'history': eth_history}
        }
    
    @cache_data(ttl=3600)
    def get_dxy_data(self, days: int = 90) -> pd.DataFrame:
        """Get real DXY data from Alpha Vantage (approximation via USD/EUR), with mock fallback"""
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
            logger.info(f"DXY data fetched: {len(df)} rows from {df['date'].min()} to {df['date'].max()}")
            if df.empty:
                logger.warning("No DXY data fetched; falling back to mock data")
                return self._get_mock_dxy_data(days)
            return df
        except requests.RequestException as e:
            logger.error(f"Error fetching DXY data from Alpha Vantage: {e}")
            return self._get_mock_dxy_data(days)
    
    def _get_mock_dxy_data(self, days: int = 90) -> pd.DataFrame:
        """Generate mock DXY data"""
        np.random.seed(int(datetime.now().timestamp()) // 3600)  # Change hourly
        end_date = datetime.now()
        dates = pd.date_range(end=end_date, periods=days, freq='B')  # Business days
        # Generate realistic DXY values with a random walk around 100
        dxy_values = 100 + np.cumsum(np.random.normal(0, 0.2, days))
        df = pd.DataFrame({
            'date': dates,
            'dxy': dxy_values
        }).sort_values('date').reset_index(drop=True)
        logger.info(f"Generated mock DXY data: {len(df)} rows from {df['date'].min()} to {df['date'].max()}")
        return df
    
    def get_dxy_analysis(self) -> Dict[str, Any]:
        """Get DXY analysis and interpretation based on real or mock data"""
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
            logger.error(f"Error analyzing DXY data: {e}")
            return {}