import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from data.crypto_data import CryptoDataFetcher
from data.traditional_data import TraditionalDataFetcher  # Import the enhanced class
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

def render_enhanced_dxy_chart(dxy_analysis):
    """Render enhanced DXY chart with better visualization"""
    if not dxy_analysis or 'dataframe' not in dxy_analysis:
        st.markdown('<div style="text-align: center; color: #a0a0a0;">No DXY data available.</div>', unsafe_allow_html=True)
        return
    
    dxy_data = dxy_analysis['dataframe']
    
    if dxy_data.empty:
        st.markdown('<div style="text-align: center; color: #a0a0a0;">No DXY data available.</div>', unsafe_allow_html=True)
        return
    
    # Create enhanced plotly chart
    fig_dxy = go.Figure()
    
    def hex_to_rgba(hex_color, alpha=0.1):
        """Convert hex color to rgba string"""
        if hex_color.startswith('#'):
            hex_color = hex_color[1:]
        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return f"rgba({r}, {g}, {b}, {alpha})"
        except:
            return f"rgba(255, 255, 0, {alpha})"  # Fallback yellow
    
    # Add main DXY line with gradient effect
    fig_dxy.add_trace(go.Scatter(
        x=dxy_data['date'], 
        y=dxy_data['dxy'], 
        mode='lines',
        name='DXY',
        line=dict(
            color=dxy_analysis.get('color', '#FFFF00'), 
            width=3,
            shape='spline'  # Smooth line
        ),
        fill='tozeroy',
        fillcolor=hex_to_rgba(dxy_analysis.get('color', '#FFFF00'), 0.1)  # Semi-transparent fill
    ))
    
    # Add trend indicators
    current_value = dxy_analysis.get('current_value', 0)
    daily_change = dxy_analysis.get('daily_change', 0)
    
    # Add current value annotation
    fig_dxy.add_annotation(
        x=dxy_data['date'].iloc[-1],
        y=current_value,
        text=f"<b>{current_value:.2f}</b><br><span style='font-size:10px'>{daily_change:+.2f}</span>",
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=-50,
        font=dict(size=14, color="#FAFAFA"),
        bgcolor="rgba(0, 0, 0, 0.8)",
        bordercolor=dxy_analysis.get('color', '#FFFF00'),
        borderwidth=2,
        arrowcolor=dxy_analysis.get('color', '#FFFF00')
    )
    
    # Add horizontal reference lines
    min_val, max_val = dxy_data['dxy'].min(), dxy_data['dxy'].max()
    mid_val = (min_val + max_val) / 2
    
    # Support/Resistance levels
    fig_dxy.add_hline(
        y=min_val, 
        line_dash="dot", 
        line_color="rgba(255,255,255,0.3)",
        annotation_text=f"Low: {min_val:.2f}",
        annotation_position="top right"
    )
    fig_dxy.add_hline(
        y=max_val, 
        line_dash="dot", 
        line_color="rgba(255,255,255,0.3)",
        annotation_text=f"High: {max_val:.2f}",
        annotation_position="bottom right"
    )
    
    # Chart layout with enhanced styling
    fig_dxy.update_layout(
        template='plotly_dark',
        paper_bgcolor='#1e2329',
        plot_bgcolor='#1e2329',
        font_color='#FAFAFA',
        margin=dict(l=20, r=20, t=20, b=20),
        height=320,
        showlegend=False,
        xaxis=dict(
            showticklabels=True,
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            title=None
        ),
        yaxis=dict(
            showticklabels=True, 
            title=None,
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            range=[min_val - 0.5, max_val + 0.5]
        )
    )
    
    st.plotly_chart(fig_dxy, use_container_width=True)
    
    # Enhanced status display
    trend = dxy_analysis.get('trend', 'N/A')
    impact = dxy_analysis.get('impact', 'N/A')
    color = dxy_analysis.get('color', '#a0a0a0')
    strength = dxy_analysis.get('strength_level', 'N/A')
    weekly_change = dxy_analysis.get('weekly_change', 0)
    weekly_pct = dxy_analysis.get('weekly_change_pct', 0)
    
    # Create status card
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02)); 
                padding: 15px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1);
                margin-top: 10px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="color: #a0a0a0; font-size: 12px;">Current Value</span>
            <span style="color: white; font-weight: 700; font-size: 16px;">{current_value:.2f}</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="color: #a0a0a0; font-size: 12px;">Daily Change</span>
            <span style="color: {color}; font-weight: 600; font-size: 14px;">{daily_change:+.3f} ({dxy_analysis.get('daily_change_pct', 0):+.2f}%)</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="color: #a0a0a0; font-size: 12px;">Weekly Change</span>
            <span style="color: {color}; font-weight: 600; font-size: 14px;">{weekly_change:+.3f} ({weekly_pct:+.2f}%)</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <span style="color: #a0a0a0; font-size: 12px;">Trend Strength</span>
            <span style="color: white; font-weight: 600; font-size: 14px;">{strength}</span>
        </div>
        <div style="text-align: center; margin-top: 10px; padding: 8px; 
                    background: rgba(0,0,0,0.3); border-radius: 6px; border-left: 3px solid {color};">
            <div style="color: {color}; font-weight: 700; font-size: 13px; margin-bottom: 3px;">{trend}</div>
            <div style="color: #a0a0a0; font-size: 11px;">{impact}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    apply_custom_css()
    
    st.markdown("""
    <div class="header-title">RetailDAO Analytics Dashboard - MVP</div>
    <div class="header-subtitle">Real-time crypto market insights and analysis</div>
    """, unsafe_allow_html=True)
    
    with st.spinner("Loading data..."):
        crypto_fetcher = CryptoDataFetcher()
        traditional_fetcher = TraditionalDataFetcher()  # Use the enhanced fetcher
        
        btc_df = crypto_fetcher.get_btc_price_data()
        # Compute RSIs from BTC price data (reuses the working CoinGecko call)
        rsi_7d = calculate_rsi(btc_df['price'], 7) if not btc_df.empty else None
        rsi_14d = calculate_rsi(btc_df['price'], 14) if not btc_df.empty else None
        rsi_30d = calculate_rsi(btc_df['price'], 30) if not btc_df.empty else None
        funding_rates = crypto_fetcher.get_funding_rates_7d_avg()  # Already mock
        current_prices = crypto_fetcher.get_current_prices()
        # Enhanced DXY with natural randomness
        dxy_analysis = traditional_fetcher.get_dxy_analysis()

    # Row 1: BTC Chart (2 columns) and Enhanced DXY Chart (1 column)
    with st.container():
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("BTC Price with Ribbon MAs")
            fig = go.Figure()
            
            # Add MA traces first (so they appear behind the price)
            fig.add_trace(go.Scatter(
                x=btc_df['date'], 
                y=btc_df['MA_200'], 
                name='200d MA', 
                line=dict(color='#AA00FF', width=2),
                opacity=0.8
            ))
            fig.add_trace(go.Scatter(
                x=btc_df['date'], 
                y=btc_df['MA_100'], 
                name='100d MA', 
                line=dict(color='#00AAFF', width=2),
                opacity=0.8
            ))
            fig.add_trace(go.Scatter(
                x=btc_df['date'], 
                y=btc_df['MA_50'], 
                name='50d MA', 
                line=dict(color='#00FFAA', width=2),
                opacity=0.8
            ))
            fig.add_trace(go.Scatter(
                x=btc_df['date'], 
                y=btc_df['MA_20'], 
                name='20d MA', 
                line=dict(color='#00FFFF', width=2),
                opacity=0.8
            ))
            
            # Add BTC price line with fill
            fig.add_trace(go.Scatter(
                x=btc_df['date'], 
                y=btc_df['price'], 
                mode='lines', 
                name='BTC Price', 
                line=dict(color='#FFA500', width=3),
                fill='tozeroy',
                fillcolor='rgba(255, 165, 0, 0.1)'  # Orange with transparency
            ))
            
            # Get price range for better y-axis scaling
            price_min = btc_df['price'].min()
            price_max = btc_df['price'].max()
            price_range = price_max - price_min
            y_min = price_min - (price_range * 0.05)  # 5% padding below
            y_max = price_max + (price_range * 0.05)  # 5% padding above
            
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='#1e2329',
                plot_bgcolor='#1e2329',
                font_color='#FAFAFA',
                margin=dict(l=20, r=20, t=20, b=20),
                height=555,  # Match DXY total height (chart + status card)
                showlegend=True,
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='right',
                    x=1,
                    font=dict(size=10)
                ),
                xaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(255,255,255,0.1)',
                    title=None
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(255,255,255,0.1)',
                    title='Price (USD)',
                    range=[y_min, y_max],
                    tickformat='$,.0f'
                )
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('<div class="widget-subtext" style="text-align: center;">Real data from CoinGecko.</div>', unsafe_allow_html=True)
        
        with col2:
            st.subheader("US Dollar Index (DXY)")
            render_enhanced_dxy_chart(dxy_analysis)
            st.markdown('<div class="widget-subtext" style="text-align: center;">Mock data used.</div>', unsafe_allow_html=True)

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