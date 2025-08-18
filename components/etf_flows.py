# etf_flows.py
import streamlit as st
from utils.formatters import format_currency, format_percentage
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import plotly.graph_objects as go

def get_flow_interpretation(flow_7d: float, asset: str) -> tuple:
    """
    Interpret ETF flows and return description with color
    
    Args:
        flow_7d: 7-day net flow in millions
        asset: Asset name (BTC or ETH)
        
    Returns:
        Tuple of (interpretation, color)
    """
    thresholds = [
        (500, "Very Strong Inflows", "#00d4aa"),
        (200, "Strong Inflows", "#4ecdc4"),
        (50, "Moderate Inflows", "#45b7d1"),
        (0, "Light Inflows", "#a0c4d4"),
        (-50, "Light Outflows", "#ffb84d"),
        (-200, "Moderate Outflows", "#ff8c42"),
        (-500, "Strong Outflows", "#ff6b47"),
    ]
    flow_7d_m = flow_7d / 1000000  # Convert to millions
    for threshold, desc, color in thresholds:
        if flow_7d_m >= threshold:
            return desc, color
    return "Very Strong Outflows", "#ff5757"

def mock_etf_flows():
    """Mock ETF flows data with realistic patterns"""
    random.seed(42)  # For reproducible results, remove for true randomness
    np.random.seed(42)
    
    two_months_ago = datetime.now() - timedelta(days=60)
    history = []
    
    # Base price trend (slight upward trend over 2 months)
    base_price = 116800
    price_trend = np.linspace(0, 2000, 60)  # +$2k over 60 days
    price_volatility = np.random.normal(0, 500, 60)  # Daily volatility
    
    # Create more realistic flow patterns
    for i in range(60):
        # Create periods of sustained inflows/outflows
        period_length = 7  # Weekly cycles
        period_index = i // period_length
        
        # Base flow bias (some periods favor inflows, others outflows)
        period_biases = [1, 0.5, -0.3, 1.2, 0.8, -0.5, 0.9, 1.1, 0.2]  # 9 periods for 60 days
        bias = period_biases[period_index % len(period_biases)]
        
        # Random component with varying magnitude
        base_magnitude = random.uniform(20, 800)  # 20M to 800M range
        random_factor = random.uniform(-1, 1)
        
        # Occasional large flows (simulate big institutional moves)
        if random.random() < 0.15:  # 15% chance of large flow
            base_magnitude *= random.uniform(1.5, 2.5)
        
        # Apply bias and randomness
        flow = base_magnitude * bias * random_factor
        
        # Add some momentum (flows tend to continue in same direction)
        if i > 0:
            prev_flow = history[i-1]['flow_usd']
            momentum = 0.3 if prev_flow > 0 else -0.3
            if abs(prev_flow) > 100000000:  # If previous flow was large
                flow += momentum * abs(flow) * 0.5
        
        # Ensure some variation in magnitude
        flow *= random.uniform(0.7, 1.3)
        
        # Convert to integer (millions)
        flow = int(flow * 1000000)
        
        # Calculate price with trend and volatility
        price = base_price + price_trend[i] + price_volatility[i]
        
        history.append({
            'timestamp': int((two_months_ago + timedelta(days=i)).timestamp() * 1000),
            'flow_usd': flow,
            'price_usd': max(price, 100000)  # Ensure price doesn't go below 100k
        })
    
    # Calculate recent summary stats from the generated data
    recent_flows = [h['flow_usd'] for h in history[-7:]]  # Last 7 days
    net_flow_7d = sum(recent_flows)
    net_flow_1d = history[-1]['flow_usd']
    
    # Calculate change percentage (comparing last day to previous day)
    change_pct = ((history[-1]['flow_usd'] - history[-2]['flow_usd']) / 
                  abs(history[-2]['flow_usd']) * 100) if history[-2]['flow_usd'] != 0 else 0
    
    return {
        'BTC': {
            'summary': {
                'net_flow_7d': net_flow_7d,
                'net_flow_1d': net_flow_1d,
                'change_pct': change_pct,
                'total_aum': 152000000000,  # $152B
            },
            'history': history
        },
        'ETH': {
            'summary': {
                'net_flow_7d': int(net_flow_7d * 0.05),  # ETH flows are typically much smaller
                'net_flow_1d': int(net_flow_1d * 0.05),
                'change_pct': change_pct * 0.8,  # Slightly different change
                'total_aum': 20000000000,  # $20B
            },
            'history': []  # No history needed for ETH in mock
        }
    }

def render_etf_flows():
    """Render ETF flows component"""
    # Use mock data instead of API
    etf_flows = mock_etf_flows()
    
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    
    if etf_flows and isinstance(etf_flows, dict):
        # Render BTC flow chart first
        btc_data = etf_flows.get('BTC', {})
        btc_history = btc_data.get('history', [])
        if btc_history:
            df = pd.DataFrame(btc_history)
            df['date'] = pd.to_datetime(df['timestamp'] / 1000, unit='s')
            df = df.sort_values('date')  # Oldest to newest
            # Filter to last 2 months (already in mock)
            
            if not df.empty:
                fig = go.Figure()
                # Bar for flows (green for inflow, red for outflow)
                colors = ['#00d4aa' if f >= 0 else '#ff5757' for f in df['flow_usd']]
                fig.add_trace(go.Bar(
                    x=df['date'],
                    y=df['flow_usd'],
                    marker_color=colors,
                    name='Net Flow'
                ))
                # Line for BTC price
                if 'price_usd' in df.columns and not df['price_usd'].empty:
                    fig.add_trace(go.Scatter(
                        x=df['date'],
                        y=df['price_usd'],
                        mode='lines',
                        name='BTC Price',
                        yaxis='y2',
                        line=dict(color='white', width=2)
                    ))
                # Layout
                fig.update_layout(
                    title=dict(text='Total Bitcoin Spot ETF Net Inflow (USD)', font=dict(color='white', size=16)),
                    xaxis=dict(title='Date', titlefont=dict(color='white'), tickfont=dict(color='white')),
                    yaxis=dict(title='Flows (USD)', titlefont=dict(color='white'), tickfont=dict(color='white'), side='left', showgrid=False),
                    yaxis2=dict(title='BTC Price', titlefont=dict(color='white'), tickfont=dict(color='white'), side='right', overlaying='y', showgrid=False, range=[100000, 125000]),
                    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1, font=dict(color='white')),
                    plot_bgcolor='black',
                    paper_bgcolor='black',
                    height=300,  # Smaller height to fit layout
                    margin=dict(l=40, r=40, t=40, b=40),
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Render BTC and ETH metric cards below the chart
        for asset, data in etf_flows.items():
            summary = data.get('summary', {})
            flow_7d = summary.get('net_flow_7d', 0)
            flow_1d = summary.get('net_flow_1d', 0)
            change_pct = summary.get('change_pct', 0)
            total_aum = summary.get('total_aum', 0)
            
            interpretation, flow_color = get_flow_interpretation(flow_7d, asset)
            change_color = "positive" if change_pct > 0 else "negative" if change_pct < 0 else "neutral"
            
            html_content = f"""
                <div style="margin: 20px 0; padding: 15px; background: rgba(255,255,255,0.05); border-radius: 10px; border-left: 4px solid {flow_color};">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <div style="color: white; font-weight: 700; font-size: 18px;">{asset} ETF</div>
                        <div style="text-align: right;">
                            <div style="color: {flow_color}; font-weight: 700; font-size: 20px;">
                                ${flow_7d:+,.0f}M
                            </div>
                            <div style="color: #a0a0a0; font-size: 12px;">7-day net</div>
                        </div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="color: #a0a0a0;">Daily Flow:</span>
                        <span style="color: white; font-weight: 600;">${flow_1d:+,.0f}M</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="color: #a0a0a0;">Daily Change %:</span>
                        <span class="{change_color}" style="font-weight: 600;">{format_percentage(change_pct)}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span style="color: #a0a0a0;">Total AUM:</span>
                        <span style="color: white; font-weight: 600;">${total_aum / 1000000000:,.1f}B</span>
                    </div>
                    <div style="color: {flow_color}; font-size: 14px; font-weight: 600; text-align: center; margin-top: 10px; padding: 8px; background: rgba(0,0,0,0.3); border-radius: 6px;">
                        {interpretation}
                    </div>
                </div>
            """
            st.markdown(html_content, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="color: #ff5757; text-align: center; padding: 20px;">
                Unable to fetch ETF flow data
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Market context (with safe access to avoid KeyError)
    total_flows = sum(data.get('summary', {}).get('net_flow_7d', 0) for data in etf_flows.values())
    flow_color = "positive" if total_flows > 0 else "negative" if total_flows < 0 else "neutral"
    
    st.markdown(f"""
    <div style="background: #2a2a3a; padding: 15px; border-radius: 8px; margin-top: 15px; border: 1px solid #3d3d4d;">
        <div style="text-align: center;">
            <div style="color: #a0a0a0; font-size: 14px; margin-bottom: 5px;">Combined 7-Day Net Flow</div>
            <div class="{flow_color}" style="font-size: 24px; font-weight: 700;">
                ${total_flows:+,.0f}M
            </div>
            <div style="color: #a0a0a0; font-size: 12px; margin-top: 5px;">
                {"Institutional buying pressure" if total_flows > 0 else "Institutional selling pressure" if total_flows < 0 else "Neutral institutional sentiment"}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)