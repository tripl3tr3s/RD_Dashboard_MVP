import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from data.crypto_data import CryptoDataFetcher
from utils.formatters import format_currency, format_percentage

def create_btc_chart(df):
    """Create BTC price chart with moving averages"""
    fig = go.Figure()
    
    # Add price line
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['price'],
        mode='lines',
        name='BTC Price',
        line=dict(color='#ffffff', width=3),
        hovertemplate='<b>%{y:$,.0f}</b><br>%{x}<extra></extra>'
    ))
    
    # Add moving averages with ribbon effect
    colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#f9ca24']
    mas = ['MA_20', 'MA_50', 'MA_100', 'MA_200']
    names = ['20-day MA', '50-day MA', '100-day MA', '200-day MA']
    
    for ma, name, color in zip(mas, names, colors):
        # Filter out NaN values for moving averages
        ma_data = df[df[ma].notna()]
        if not ma_data.empty:
            fig.add_trace(go.Scatter(
                x=ma_data['date'],
                y=ma_data[ma],
                mode='lines',
                name=name,
                line=dict(color=color, width=2),
                hovertemplate=f'<b>{name}: %{{y:$,.0f}}</b><br>%{{x}}<extra></extra>'
            ))
    
    fig.update_layout(
        title=dict(
            text='Bitcoin Price with Moving Average Ribbon',
            font=dict(size=24, color='white', family="Arial Black"),
            x=0
        ),
        xaxis=dict(
            title='Date',
            gridcolor='#2d2d3d',
            color='white',
            showgrid=True,
            gridwidth=1
        ),
        yaxis=dict(
            title='Price (USD)',
            gridcolor='#2d2d3d',
            color='white',
            tickformat='$,.0f',
            showgrid=True,
            gridwidth=1
        ),
        plot_bgcolor='#1e1e2e',
        paper_bgcolor='#1e1e2e',
        font=dict(color='white'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(0,0,0,0.5)"
        ),
        hovermode='x unified',
        height=500
    )
    
    return fig

def get_ma_analysis(df):
    """Analyze current price relative to moving averages"""
    if df.empty:
        return {}
    
    current_price = df['price'].iloc[-1]
    analysis = {}
    
    mas = {
        'MA_20': '20-day',
        'MA_50': '50-day', 
        'MA_100': '100-day',
        'MA_200': '200-day'
    }
    
    for ma_col, ma_name in mas.items():
        ma_value = df[ma_col].iloc[-1]
        if pd.notna(ma_value):
            percentage_diff = ((current_price - ma_value) / ma_value) * 100
            analysis[ma_name] = {
                'value': ma_value,
                'diff_pct': percentage_diff,
                'above': current_price > ma_value
            }
    
    return analysis

def get_rsi_interpretation(rsi: float) -> tuple:
    """Return RSI interpretation and color"""
    if rsi >= 80:
        return "Extremely Overbought", "#ff5757"
    elif rsi >= 70:
        return "Overbought", "#ff8c42"
    elif rsi >= 60:
        return "Slightly Overbought", "#ffa500"
    elif rsi >= 40:
        return "Normal", "#00d4aa"
    elif rsi >= 30:
        return "Slightly Oversold", "#4dabf7"
    elif rsi >= 20:
        return "Oversold", "#339af0"
    else:
        return "Extremely Oversold", "#1c7ed6"

def render_btc_analysis(skip_render=False):
    """Render BTC analysis component and return data"""
    crypto_fetcher = CryptoDataFetcher()
    
    # Fetch BTC data
    with st.spinner("Loading BTC price data..."):
        btc_df = crypto_fetcher.get_btc_price_data()
        rsi_value = crypto_fetcher.get_btc_rsi()
    
    data = {}
    if not btc_df.empty:
        # Create and display chart
        fig_btc = create_btc_chart(btc_df)
        if not skip_render:
            st.plotly_chart(fig_btc, use_container_width=True)
        
        # Price metrics
        current_price = btc_df['price'].iloc[-1]
        prev_price = btc_df['price'].iloc[-2] if len(btc_df) > 1 else current_price
        price_change = current_price - prev_price
        price_change_pct = (price_change / prev_price) * 100 if prev_price != 0 else 0
        
        # Display current price card
        change_color = "positive" if price_change >= 0 else "negative"
        change_symbol = "+" if price_change >= 0 else ""
        
        if not skip_render:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Current BTC Price</div>
                <div class="metric-value">{format_currency(current_price)}</div>
                <div class="metric-change {change_color}">
                    {change_symbol}{format_currency(price_change)} ({change_symbol}{format_percentage(price_change_pct)}) 24h
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # RSI and MA analysis
        if rsi_value is not None:
            rsi_text, rsi_color = get_rsi_interpretation(rsi_value)
            if not skip_render:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-title">14-Day RSI</div>
                        <div class="metric-value" style="color: {rsi_color};">{rsi_value}</div>
                        <div class="metric-change" style="color: {rsi_color};">
                            {rsi_text}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    ma_analysis = get_ma_analysis(btc_df)
                    above_count = sum(1 for ma in ma_analysis.values() if ma['above'])
                    total_mas = len(ma_analysis)
                    
                    if total_mas > 0:
                        ma_strength = "Bullish" if above_count >= total_mas * 0.75 else "Bearish" if above_count <= total_mas * 0.25 else "Mixed"
                        ma_color = "#00d4aa" if ma_strength == "Bullish" else "#ff5757" if ma_strength == "Bearish" else "#ffa500"
                        
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-title">MA Ribbon Signal</div>
                            <div class="metric-value" style="color: {ma_color};">{ma_strength}</div>
                            <div class="metric-change" style="color: {ma_color};">
                                Above {above_count}/{total_mas} MAs
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
        
        # Store data for return
        data = {
            'price': current_price,
            'rsi': rsi_value,
            'change_24h': price_change,
            'change_pct_24h': price_change_pct,
            'ma_signal': ma_strength if 'ma_strength' in locals() else "Unknown"
        }
    else:
        if not skip_render:
            st.error("Unable to load BTC price data. Please check your internet connection.")
    
    return data