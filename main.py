import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from data.crypto_data import CryptoDataFetcher
from components.etf_flows import render_etf_flows  # Import the render_etf_flows function
from utils.formatters import apply_custom_css, format_currency, format_percentage, get_color_for_change

# No need for TraditionalDataFetcher since we're mocking DXY

st.set_page_config(
    page_title="RetailDAO Analytics Dashboard - MVP",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def render_rsi_gauge(rsi_value, period):
    """Pill-shaped vertical gauge with gradient for a specific RSI period"""
    if rsi_value is None:
        return '<div style="text-align: center; color: #a0a0a0;">N/A</div>'
    percentage = min(max(rsi_value, 0), 100)  # Clamp to 0-100
    total_height = 150  # Total height of the gauge in pixels
    fill_height = (percentage / 100) * total_height  # Calculate fill height in pixels

    # Determine color based on RSI range
    if percentage <= 30:
        # Greenish-yellow up to 30
        gradient_color = '#A9FF33'  # Blend of green (#00FF00) and yellow (#FFFF00)
        fill_style = f"background-color: {gradient_color}; height: {fill_height}px;"
    elif 30 < percentage <= 70:
        # Transition from greenish-yellow to yellow, proportional within 30-70 range
        mid_point = 50  # Target yellow at 50
        range_progress = (percentage - 30) / 40  # 0 to 1 from 30 to 70
        r = int(255 * range_progress + 169 * (1 - range_progress))  # Red component
        g = int(255 * range_progress + 255 * (1 - range_progress))  # Green component
        b = int(51 * range_progress + 0 * (1 - range_progress))     # Blue component
        gradient_color = f'rgb({r}, {g}, {b})'
        fill_style = f"background-color: {gradient_color}; height: {fill_height}px;"
    else:  # percentage > 70
        # Transition from yellow to red, proportional within 70-100 range
        range_progress = (percentage - 70) / 30  # 0 to 1 from 70 to 100
        r = int(255)  # Full red
        g = int(255 * (1 - range_progress))  # Fade green out
        b = int(0)    # No blue
        gradient_color = f'rgb({r}, {g}, {b})'
        fill_style = f"background-color: {gradient_color}; height: {fill_height}px;"

    label = "Extremely Overbought" if rsi_value > 80 else \
            "Overbought" if rsi_value > 70 else \
            "Normal" if 30 <= rsi_value <= 70 else \
            "Oversold" if rsi_value > 20 else "Extremely Oversold"
    color = get_color_for_change(rsi_value - 50)

    return f"""
    <div class="rsi-gauge" style="display: flex; flex-direction: column; align-items: center;">
        <div style="background-color: #161B22; width: 40px; height: 150px; border-radius: 20px; overflow: hidden; position: relative; box-shadow: 0 4px 6px rgba(0,0,0,0.3); margin: 0 auto;">
            <div style="{fill_style} width: 100%; position: absolute; bottom: 0; border-radius: 0 0 20px 20px;"></div>
        </div>
        <div style="text-align: center; color: #FAFAFA; font-size: 18px; font-weight: 700; margin-top: 10px;">{rsi_value:.2f} ({period}d)</div>
        <div style="text-align: center; color: {color}; font-size: 12px;">{label}</div>
    </div>
    """

def calculate_rsi(prices: pd.Series, period: int) -> float:
    """Calculate RSI from price series using EMA method"""
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period-1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period-1, min_periods=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def mock_dxy_data(days: int = 30) -> pd.DataFrame:
    """Mock DXY data (falling trend around current real value ~98)"""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    dxy_values = np.linspace(100, 98, days)  # Simulated falling from 100 to 98
    return pd.DataFrame({'date': dates, 'dxy': dxy_values})

def mock_dxy_analysis(dxy_data: pd.DataFrame) -> dict:
    """Mock DXY analysis based on data"""
    current_value = dxy_data['dxy'].iloc[-1]
    diff_mean = dxy_data['dxy'].diff().mean()
    trend = "Falling Strongly" if diff_mean < -0.1 else "Falling" if diff_mean < 0 else "Rising"
    color = "#FF0000" if "Falling" in trend else "#00FF00"  # Red for falling (positive for crypto)
    impact = "Positive for risk assets like crypto" if "Falling" in trend else "Negative for risk assets"
    return {
        "current_value": f"{current_value:.2f}",
        "trend": trend,
        "color": color,
        "impact": impact
    }

def main():
    apply_custom_css()
    
    st.markdown("""
    <div class="header-title">RetailDAO Analytics Dashboard - MVP</div>
    <div class="header-subtitle">Real-time crypto market insights and analysis</div>
    """, unsafe_allow_html=True)
    
    with st.spinner("Loading data..."):
        crypto_fetcher = CryptoDataFetcher()
        
        btc_df = crypto_fetcher.get_btc_price_data()
        # Compute RSIs from BTC price data (reuses the working CoinGecko call)
        rsi_7d = calculate_rsi(btc_df['price'], 7) if not btc_df.empty else None
        rsi_14d = calculate_rsi(btc_df['price'], 14) if not btc_df.empty else None
        rsi_30d = calculate_rsi(btc_df['price'], 30) if not btc_df.empty else None
        funding_rates = crypto_fetcher.get_funding_rates_7d_avg()  # Already mock
        current_prices = crypto_fetcher.get_current_prices()
        # Mock DXY (no API)
        dxy_data = mock_dxy_data(days=30)
        dxy_analysis = mock_dxy_analysis(dxy_data)

    # Row 1: BTC Chart (2 columns) and Mini DXY Chart (1 column)
    with st.container():
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("BTC Price with Ribbon MAs")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=btc_df['date'], y=btc_df['price'], mode='lines', name='Price', line=dict(color='#FFA500')))
            fig.add_trace(go.Scatter(x=btc_df['date'], y=btc_df['MA_20'], name='20d MA', line=dict(color='#00FFFF')))
            fig.add_trace(go.Scatter(x=btc_df['date'], y=btc_df['MA_50'], name='50d MA', line=dict(color='#00FFAA')))
            fig.add_trace(go.Scatter(x=btc_df['date'], y=btc_df['MA_100'], name='100d MA', line=dict(color='#00AAFF')))
            fig.add_trace(go.Scatter(x=btc_df['date'], y=btc_df['MA_200'], name='200d MA', line=dict(color='#AA00FF')))
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='#252a3a',
                plot_bgcolor='#252a3a',
                font_color='#FAFAFA',
                margin=dict(l=20, r=20, t=40, b=20),
                height=300,
                width=600  # Adjusted width to fill the two-column space better
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('<div class="widget-subtext" style="text-align: center;">Real data from CoinGecko.</div>', unsafe_allow_html=True)
        
        with col2:
            st.subheader("DXY (Mini)")
            if not dxy_data.empty:
                latest_dxy = dxy_data['dxy'].iloc[-1] if not dxy_data.empty else "N/A"
                fig_dxy = go.Figure(go.Scatter(x=dxy_data['date'], y=dxy_data['dxy'], mode='lines', line=dict(color='#FFFF00', width=2)))
                fig_dxy.add_annotation(
                    x=dxy_data['date'].iloc[-1],
                    y=latest_dxy,
                    text=f"{latest_dxy:.2f}",
                    showarrow=True,
                    arrowhead=2,
                    ax=0,
                    ay=-40,
                    font=dict(size=14, color="#FAFAFA"),
                    bgcolor="rgba(0, 0, 0, 0.7)"
                )
                fig_dxy.update_layout(
                    template='plotly_dark',
                    paper_bgcolor='#252a3a',
                    plot_bgcolor='#252a3a',
                    font_color='#FAFAFA',
                    margin=dict(l=20, r=20, t=40, b=20),
                    height=300,
                    showlegend=False,
                    xaxis=dict(showticklabels=False),
                    yaxis=dict(showticklabels=True, title=None)
                )
                st.plotly_chart(fig_dxy, use_container_width=True)
                st.markdown(f'<div class="widget-subtext" style="text-align: center;">Current: {dxy_analysis.get("current_value", "N/A")} | Trend: <span style="color: {dxy_analysis.get("color", "#a0a0a0")};">{dxy_analysis.get("trend", "N/A")}</span></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="text-align: center; color: #a0a0a0;">No DXY data available.</div>', unsafe_allow_html=True)
            st.markdown('<div class="widget-subtext" style="text-align: center;">Mock data (realistic simulation).</div>', unsafe_allow_html=True)

    # Row 2: Funding, ETF, RSI
    with st.container():
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("Perp Funding Rate (7-Day Avg)")
            from components.funding_rates import render_funding_rates
            render_funding_rates()
            st.markdown('<div class="widget-subtext" style="text-align: center;">Mock data used.</div>', unsafe_allow_html=True)
        
        with col2:
            st.subheader("Spot ETF Net Flows (BTC & ETH)")
            render_etf_flows()
            st.markdown('<div class="widget-subtext" style="text-align: center;">Mock data used.</div>', unsafe_allow_html=True)
        
        with col3:
            st.subheader("RSI Indicators (BTC)")
            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                st.markdown(render_rsi_gauge(rsi_7d, 7), unsafe_allow_html=True)
            with col_r2:
                st.markdown(render_rsi_gauge(rsi_14d, 14), unsafe_allow_html=True)
            with col_r3:
                st.markdown(render_rsi_gauge(rsi_30d, 30), unsafe_allow_html=True)
            st.markdown('<div class="widget-subtext" style="text-align: center;">Calculated from CoinGecko price data.</div>', unsafe_allow_html=True)

    # Row 3: Prices
    with st.container():
        price_col1, price_col2, price_col3 = st.columns(3)
        for col, asset in zip([price_col1, price_col2, price_col3], ['BTC', 'ETH', 'SOL']):
            with col:
                if asset in current_prices:
                    current_price = current_prices[asset]['price']
                    price_change = current_prices[asset]['change_24h']
                    change_color = "positive" if price_change >= 0 else "negative"
                    change_symbol = "+" if price_change >= 0 else ""
                    st.markdown(f"""
                    <div class="metric-card" style="margin-top: 20px;">
                        <div class="metric-title">Current {asset} Price</div>
                        <div class="metric-value" style="font-size: 36px;">{format_currency(current_price)}</div>
                        <div class="metric-change {change_color}">
                            {change_symbol}{format_currency(price_change)} ({change_symbol}{format_percentage(price_change)} 24h)
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="metric-card" style="margin-top: 20px;">
                        <div class="metric-title">Current {asset} Price</div>
                        <div class="metric-value" style="font-size: 36px;">N/A</div>
                        <div class="metric-change neutral">
                            N/A (N/A 24h)
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: #666; font-size: 14px;">
        RetailDAO Analytics Dashboard | Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M")} UTC
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()