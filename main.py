import streamlit as st
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import pandas as pd
import plotly.graph_objects as go
from data.crypto_data import CryptoDataFetcher
from data.traditional_data import TraditionalDataFetcher
from utils.formatters import apply_custom_css, format_currency, format_percentage, get_color_for_change

load_dotenv()

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
    color = get_color_for_change(rsi_value - 50)
    label = "Extremely Overbought" if rsi_value > 80 else \
            "Overbought" if rsi_value > 70 else \
            "Normal" if 30 <= rsi_value <= 70 else \
            "Oversold" if rsi_value > 20 else "Extremely Oversold"
    return f"""
    <div class="rsi-gauge">
        <div style="background-color: #161B22; width: 40px; height: 150px; border-radius: 20px; overflow: hidden; position: relative; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
            <div style="background: linear-gradient(to top, #8B00FF, #FFFF00); position: absolute; bottom: 0; width: 100%; height: {percentage}%;"></div>
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
        etf_flows = traditional_fetcher.get_etf_flows()
        dxy_data = traditional_fetcher.get_dxy_data(days=30)
        dxy_analysis = traditional_fetcher.get_dxy_analysis()

    # Row 1: BTC Chart and Price Display
    with st.container():
        # BTC Chart
        st.subheader("BTC Price with Ribbon MAs")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=btc_df['date'], y=btc_df['price'], mode='lines', name='Price', line=dict(color='#FFA500')))
        fig.add_trace(go.Scatter(x=btc_df['date'], y=btc_df['MA_20'], name='20d MA', line=dict(color='#00FFFF')))
        fig.add_trace(go.Scatter(x=btc_df['date'], y=btc_df['MA_50'], name='50d MA', line=dict(color='#00FFAA')))
        fig.add_trace(go.Scatter(x=btc_df['date'], y=btc_df['MA_100'], name='100d MA', line=dict(color='#00AAFF')))
        fig.add_trace(go.Scatter(x=btc_df['date'], y=btc_df['MA_200'], name='200d MA', line=dict(color='#AA00FF')))
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='#252a3a',  # Approximate lighter tone
            plot_bgcolor='#252a3a',   # Approximate lighter tone
            font_color='#FAFAFA',
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('<div class="widget-subtext" style="text-align: center;">Real data from CoinGecko.</div>', unsafe_allow_html=True)

        # Display current BTC price
        current_price = current_prices['BTC']['price']
        price_change = current_prices['BTC']['change_24h']
        change_color = "positive" if price_change >= 0 else "negative"
        change_symbol = "+" if price_change >= 0 else ""
        st.markdown(f"""
        <div class="metric-card" style="margin-top: 20px;">
            <div class="metric-title">Current BTC Price</div>
            <div class="metric-value" style="font-size: 36px;">{format_currency(current_price)}</div>
            <div class="metric-change {change_color}">
                {change_symbol}{format_currency(price_change)} ({change_symbol}{format_percentage(price_change)} 24h)
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Row 2: 3 columns for Funding, ETF, RSI
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Perp Funding Rate (7-Day Avg)")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            fig_btc_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=funding_rates['BTC'],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "BTC"},
                gauge={'axis': {'range': [-100, 100]},
                       'bar': {'color': "darkblue"},
                       'steps': [{'range': [-100, 0], 'color': "red"},
                                 {'range': [0, 100], 'color': "green"}]}
            ))
            fig_btc_gauge.update_layout(
                height=200,
                margin=dict(l=40, r=40, t=40, b=40),
                paper_bgcolor='#252a3a',  # Approximate lighter tone
                plot_bgcolor='#252a3a'    # Approximate lighter tone
            )
            st.plotly_chart(fig_btc_gauge, use_container_width=True)
        with col_f2:
            fig_eth_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=funding_rates['ETH'],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "ETH"},
                gauge={'axis': {'range': [-100, 100]},
                       'bar': {'color': "darkblue"},
                       'steps': [{'range': [-100, 0], 'color': "red"},
                                 {'range': [0, 100], 'color': "green"}]}
            ))
            fig_eth_gauge.update_layout(
                height=200,
                margin=dict(l=40, r=40, t=40, b=40),
                paper_bgcolor='#252a3a',  # Approximate lighter tone
                plot_bgcolor='#252a3a'    # Approximate lighter tone
            )
            st.plotly_chart(fig_eth_gauge, use_container_width=True)
        st.markdown('<div class="widget-subtext" style="text-align: center;">Real data from Binance.</div>', unsafe_allow_html=True)
        st.markdown('<div class="widget-subtext" style="text-align: center;">Funding rates are payments between long and short positions in perpetual futures. Positive (bullish): Longs pay shorts. Negative (bearish): Shorts pay longs. 7-day average smooths short-term noise.</div>', unsafe_allow_html=True)
    
    with col2:
        st.subheader("Spot ETF Net Flows (BTC & ETH)")
        fig_etf = go.Figure()
        x_values = ['BTC Daily', 'BTC 7d', 'ETH Daily', 'ETH 7d']
        y_values = [etf_flows['BTC']['net_flow_1d'], etf_flows['BTC']['net_flow_7d'], etf_flows['ETH']['net_flow_1d'], etf_flows['ETH']['net_flow_7d']]
        colors = ['#00d4aa' if v > 0 else '#ff5757' for v in y_values]  # Green for positive, red for negative
        fig_etf.add_trace(go.Bar(
            y=x_values,  # Horizontal for better readability
            x=y_values,
            orientation='h',
            marker_color=colors,
            text=[format_currency(v, 0) for v in y_values],  # Text labels
            textposition='auto'
        ))
        fig_etf.update_layout(
            template='plotly_dark',
            paper_bgcolor='#252a3a',  # Approximate lighter tone
            plot_bgcolor='#252a3a',   # Approximate lighter tone
            font_color='#FAFAFA',
            height=300,
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig_etf, use_container_width=True)
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
    
    # Row 3: DXY Chart spanning full width
    with st.container():
        st.subheader("U.S. Dollar Index (DXY)")
        if not dxy_data.empty:
            fig_dxy = go.Figure(go.Scatter(x=dxy_data['date'], y=dxy_data['dxy'], mode='lines', line=dict(color='#FFFF00')))
            fig_dxy.update_layout(
                template='plotly_dark',
                paper_bgcolor='#252a3a',  # Approximate lighter tone
                plot_bgcolor='#252a3a',   # Approximate lighter tone
                font_color='#FAFAFA',
                margin=dict(l=40, r=40, t=40, b=40)
            )
            st.plotly_chart(fig_dxy, use_container_width=True)
        else:
            st.write("No DXY data available.")
        st.markdown('<div class="widget-subtext" style="text-align: center;">Real data from Alpha Vantage.</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="widget-subtext" style="text-align: center;">Current: {dxy_analysis.get("current_value", "N/A")} | Trend: <span style="color: {dxy_analysis.get("color", "#a0a0a0")};">{dxy_analysis.get("trend", "N/A")}</span> | Impact: {dxy_analysis.get("impact", "N/A")}. The U.S. Dollar Index (DXY) measures the dollar\'s strength against major currencies. When DXY drops, it often benefits risk assets like crypto by making them more attractive to global investors.</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: #666; font-size: 14px;">
        RetailDAO Analytics Dashboard | Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M")} UTC
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()