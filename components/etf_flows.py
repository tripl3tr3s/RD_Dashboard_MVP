import streamlit as st
from data.traditional_data import TraditionalDataFetcher
from utils.formatters import format_currency, format_percentage
import pandas as pd
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

def render_etf_flows():
    """Render ETF flows component"""
    traditional_fetcher = TraditionalDataFetcher()
    
    # Fetch ETF flow data
    with st.spinner("Loading ETF flow data..."):
        etf_flows = traditional_fetcher.get_etf_flows()
    
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    
    if etf_flows and isinstance(etf_flows, dict):
        # Render BTC flow chart first
        btc_data = etf_flows.get('BTC', {})
        btc_history = btc_data.get('history', [])
        if btc_history:
            df = pd.DataFrame(btc_history)
            df['date'] = pd.to_datetime(df['timestamp'] / 1000, unit='s')
            df = df.sort_values('date')  # Oldest to newest
            # Filter to last 2 months
            two_months_ago = datetime.now() - timedelta(days=60)
            df = df[df['date'] >= two_months_ago]
            
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
                    # Ensure price_usd is within a reasonable range, default to 116800 if invalid
                    df['price_usd'] = df['price_usd'].apply(lambda x: max(100000, min(125000, x)) if pd.notna(x) else 116800)
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
                    height=300,
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
    
    # Market context
    total_flows = sum(data['summary'].get('net_flow_7d', 0) for data in etf_flows.values() if etf_flows)
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