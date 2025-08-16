import streamlit as st
import requests
import pandas as pd
import numpy as np
from typing import Dict, Optional, Any
from .cache_utils import cache_data

class CryptoDataFetcher:
    """Handles cryptocurrency data fetching from various APIs"""
    
    def __init__(self):
        self.coingecko_api_key = st.secrets["general"]["COINGECKO_API_KEY"]
        self.binance_api_key = st.secrets["general"]["BINANCE_API_KEY"]
        self.session = requests.Session()
        
        # Set headers if API keys are available
        if self.coingecko_api_key:
            self.session.headers.update({
                'x-cg-demo-api-key': self.coingecko_api_key
            })
    
    @cache_data(ttl=3600)
    def get_btc_price_data(self, days: int = 365) -> pd.DataFrame:  # Increased to 365 days for 12 months
        """Fetch BTC price data from CoinGecko"""
        try:
            url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': 'daily'
            }
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            prices = data['prices']
            df = pd.DataFrame(prices, columns=['timestamp', 'price'])
            df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
            df = df.sort_values('date').reset_index(drop=True)
            df['MA_20'] = df['price'].rolling(window=20, min_periods=1).mean()  # min_periods=1 to handle shorter data
            df['MA_50'] = df['price'].rolling(window=50, min_periods=1).mean()
            df['MA_100'] = df['price'].rolling(window=100, min_periods=1).mean()
            df['MA_200'] = df['price'].rolling(window=200, min_periods=1).mean()
            return df
        except requests.exceptions.RequestException as e:
            print(f"Network error fetching BTC price data: {e}")
            return pd.DataFrame()
        except Exception as e:
            print(f"Error fetching BTC price data: {e}")
            return pd.DataFrame()
    
    def calculate_rsi(self, prices: np.ndarray, period: int = 14) -> float:
        """Calculate RSI for given price array"""
        if len(prices) < period + 1:
            return None
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        if avg_loss == 0:
            return 100
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return round(rsi, 2)
    
    @cache_data(ttl=300)
    def get_btc_rsi(self, period: int = 14) -> Optional[float]:
        """Get current RSI for BTC with specified period"""
        try:
            df = self.get_btc_price_data(days=period + 10)  # Fetch enough data for the period
            if df.empty or len(df) < period + 1:
                return None
            prices = df['price'].tail(period + 1).values
            return self.calculate_rsi(prices, period=period)
        except Exception as e:
            print(f"Error calculating {period}-day RSI: {e}")
            return None
    
    @cache_data(ttl=600)
    def get_funding_rates_7d_avg(self) -> Dict[str, float]:
        """Fetch 7-day average funding rates from Binance"""
        try:
            url = "https://fapi.binance.com/fapi/v1/fundingRate"
            params = {
                'symbol': 'BTCUSDT',
                'limit': 168  # Approx 7 days with 8h intervals
            }
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            btc_rates = [float(item['fundingRate']) for item in response.json()]
            btc_avg = sum(btc_rates) / len(btc_rates) if btc_rates else 0
            
            params['symbol'] = 'ETHUSDT'
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            eth_rates = [float(item['fundingRate']) for item in response.json()]
            eth_avg = sum(eth_rates) / len(eth_rates) if eth_rates else 0
            
            return {'BTC': btc_avg * 100 * 24 * 365, 'ETH': eth_avg * 100 * 24 * 365}  # Annualized %
        except requests.exceptions.RequestException as e:
            print(f"Network error fetching funding rates: {e}")
            return {'BTC': 0, 'ETH': 0}
        except Exception as e:
            print(f"Error fetching funding rates: {e}")
            return {'BTC': 0, 'ETH': 0}
    
    @cache_data(ttl=300)
    def get_current_prices(self) -> Dict[str, Dict[str, float]]:
        """Get current prices for BTC and ETH"""
        try:
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': 'bitcoin,ethereum',
                'vs_currencies': 'usd',
                'include_24hr_change': 'true'
            }
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return {
                'BTC': {
                    'price': data['bitcoin']['usd'],
                    'change_24h': data['bitcoin']['usd_24h_change']
                },
                'ETH': {
                    'price': data['ethereum']['usd'],
                    'change_24h': data['ethereum']['usd_24h_change']
                }
            }
        except Exception as e:
            print(f"Error fetching current prices: {e}")
            return {
                'BTC': {'price': 0, 'change_24h': 0},
                'ETH': {'price': 0, 'change_24h': 0}
            }