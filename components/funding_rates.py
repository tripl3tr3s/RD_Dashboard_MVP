import streamlit as st
from data.crypto_data import CryptoDataFetcher
from utils.formatters import format_percentage

def get_funding_interpretation(rate: float) -> tuple:
    """
    Interpret funding rate and return description with color
    
    Args:
        rate: Funding rate in annualized percentage
        
    Returns:
        Tuple of (interpretation, color)
    """
    if rate >= 100:
        return "Extremely Bullish (High Leverage)", "#ff5757"
    elif rate >= 50:
        return "Very Bullish", "#ff8c42"
    elif rate >= 20:
        return "Bullish", "#ffa500"
    elif rate > 0:
        return "Slightly Bullish", "#00d4aa"
    elif rate == 0:
        return "Neutral", "#a0a0a0"
    elif rate >= -20:
        return "Slightly Bearish", "#4dabf7"
    elif rate >= -50:
        return "Bearish", "#339af0"
    elif rate >= -100:
        return "Very Bearish", "#1c7ed6"
    else:
        return "Extremely Bearish (High Short Leverage)", "#0c4a6e"

def render_funding_rates(skip_render=False):
    """Render funding rates component and return data"""
    crypto_fetcher = CryptoDataFetcher()
    
    # Get RSI data
    with st.spinner("Calculating RSI..."):
        rsi_value = crypto_fetcher.get_btc_rsi()
    
    data = {'eth': None, 'btc': None}  # Default values
    if rsi_value is not None:
        from components.btc_analysis import get_rsi_interpretation
        rsi_text, rsi_color = get_rsi_interpretation(rsi_value)
        
        if not skip_render:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">14-Day RSI</div>
                <div class="metric-value" style="color: {rsi_color};">{rsi_value}</div>
                <div class="metric-change" style="color: {rsi_color};">
                    {rsi_text}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        if not skip_render:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-title">14-Day RSI</div>
                <div class="metric-value" style="color: #ff5757;">Error</div>
                <div class="metric-change" style="color: #ff5757;">
                    Unable to calculate
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Fetch funding rates
    with st.spinner("Loading funding rates..."):
        funding_rates = crypto_fetcher.get_funding_rates()
    
    if funding_rates:
        for asset, rate in funding_rates.items():
            interpretation, color = get_funding_interpretation(rate)
            
            if not skip_render:
                st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; align-items: center; margin: 15px 0; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 8px;">
                        <div>
                            <div style="color: white; font-weight: 600; font-size: 16px;">{asset}</div>
                            <div style="color: {color}; font-size: 12px;">{interpretation}</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="color: {color}; font-weight: 700; font-size: 18px;">{format_percentage(rate)}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            data[asset] = rate  # Store the rate
    else:
        if not skip_render:
            st.markdown("""
                <div style="color: #ff5757; text-align: center; padding: 20px;">
                    Unable to fetch funding rates
                </div>
            """, unsafe_allow_html=True)
    
    if not skip_render:
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Educational content about funding rates
        st.markdown("""
        <div class="funding-explanation">
            <strong>📚 Funding Rates Explained:</strong><br><br>
            <strong>Positive rates:</strong> Longs pay shorts → Bullish sentiment (more buyers)<br>
            <strong>Negative rates:</strong> Shorts pay longs → Bearish sentiment (more sellers)<br><br>
            <strong>⚠️ Extreme rates (>±50% annually):</strong> Indicate overleveraged positions and potential liquidation cascades<br><br>
            <strong>💡 Trading insight:</strong> Very high positive rates often precede corrections, while very negative rates may signal bottoms.
        </div>
        """, unsafe_allow_html=True)
        
        # Historical context (if available)
        st.markdown("""
        <div style="background: #2a2a3a; padding: 10px; border-radius: 8px; margin-top: 10px; font-size: 12px; color: #cccccc;">
            <strong>Recent Context:</strong> Funding rates above 100% annualized have historically preceded major corrections in crypto markets.
            Rates below -50% often coincide with market bottoms.
        </div>
        """, unsafe_allow_html=True)
    
    return data