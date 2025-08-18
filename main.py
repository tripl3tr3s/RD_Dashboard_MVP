import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
from data.crypto_data import CryptoDataFetcher
from data.traditional_data import TraditionalDataFetcher
from components.etf_flows import render_etf_flows
from utils.formatters import apply_custom_css, format_currency, format_percentage, get_color_for_change

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
    percentage = min(max(rsi_value, 0), 100)
    total_height = 150
    fill_height = (percentage / 100) * total_height

    if percentage <= 30:
        gradient_color = '#A9FF33'
        fill_style = f"background-color: {gradient_color}; height: {fill_height}px;"
    elif 30 < percentage <= 70:
        mid_point = 50
        range_progress = (percentage - 30) / 40
        r = int(255 * range_progress + 169 * (1 - range_progress))
        g = int(255 * range_progress + 255 * (1 - range_progress))
        b = int(51 * range_progress + 0 * (1 - range_progress))
        gradient_color = f'rgb({r}, {g}, {b})'
        fill_style = f"background-color: {gradient_color}; height: {fill_height}px;"
    else:
        range_progress = (percentage - 70) / 30
        r = int(255)
        g = int(255 * (1 - range_progress))
        b = int(0)
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

def main():
    apply_custom_css()
    
    st.markdown("""
    <div class="header-title">RetailDAO Analytics Dashboard - MVP</div>
    <div class="header-subtitle">Real-time crypto market insights and analysis</div>
    """, unsafe_allow_html=True)
    
    with st.spinner("Loading data..."):
        crypto_fetcher = CryptoDataFetcher()
        traditional_fetcher = TraditionalDataFetcher()
        
        btc_df = crypto_fetcher.get_btc_price_data()
        rsi_7d = crypto_fetcher.get_btc_rsi(period=7)
        rsi_14d = crypto_fetcher.get_btc_rsi(period=14)
        rsi_30d = crypto_fetcher.get_btc_rsi(period=30)
        funding_rates = crypto_fetcher.get_funding_rates_7d_avg()
        current_prices = crypto_fetcher.get_current_prices()
        dxy_data = traditional_fetcher.get_dxy_data(days=30)
        dxy_analysis = traditional_fetcher.get_dxy_analysis()

    # Row 1: BTC Chart (2 columns) and DXY Chart (1 column)
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
            st.subheader("DXY Index")
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
            st.markdown('<div class="widget-subtext" style="text-align: center;">Real data from Alpha Vantage.</div>', unsafe_allow_html=True)

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
            st.markdown('<div class="widget-subtext" style="text-align: center;">Mock data, API key required for real data.</div>', unsafe_allow_html=True)
        
        with col3:
            st.subheader("RSI Indicators (BTC)")
            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                st.markdown(render_rsi_gauge(rsi_7d, 7), unsafe_allow_html=True)
            with col_r2:
                st.markdown(render_rsi_gauge(rsi_14d, 14), unsafe_allow_html=True)
            with col_r3:
                st.markdown(render_rsi_gauge(rsi_30d, 30), unsafe_allow_html=True)
            st.markdown('<div class="widget-subtext" style="text-align: center;">Real data from CoinGecko.</div>', unsafe_allow_html=True)

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