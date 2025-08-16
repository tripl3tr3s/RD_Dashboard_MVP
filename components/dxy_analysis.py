import streamlit as st
import plotly.graph_objects as go
from data.traditional_data import TraditionalDataFetcher
from utils.formatters import format_percentage

def create_dxy_chart(df):
    """Create DXY chart with area fill"""
    fig = go.Figure()
    
    # Add DXY line with gradient fill
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['dxy'],
        mode='lines',
        name='DXY',
        line=dict(color='#ffa500', width=3),
        fill='tonexty',
        fillcolor='rgba(255, 165, 0, 0.1)',
        hovertemplate='<b>DXY: %{y:.2f}</b><br>%{x}<extra></extra>'
    ))
    
    # Add horizontal reference lines
    current_value = df['dxy'].iloc[-1]
    
    # Add support/resistance levels
    fig.add_hline(
        y=105, 
        line_dash="dash", 
        line_color="#ff5757", 
        annotation_text="Strong Resistance (105)",
        annotation_position="top right"
    )
    
    fig.add_hline(
        y=100, 
        line_dash="dash", 
        line_color="#00d4aa", 
        annotation_text="Key Support (100)",
        annotation_position="bottom right"
    )
    
    fig.update_layout(
        title=dict(
            text='U.S. Dollar Index (DXY) - 90 Days',
            font=dict(size=20, color='white', family="Arial Black"),
            x=0
        ),
        xaxis=dict(
            title='Date',
            gridcolor='#2d2d3d',
            color='white',
            showgrid=True
        ),
        yaxis=dict(
            title='Index Value',
            gridcolor='#2d2d3d',
            color='white',
            showgrid=True,
            range=[df['dxy'].min() * 0.98, df['dxy'].max() * 1.02]
        ),
        plot_bgcolor='#1e1e2e',
        paper_bgcolor='#1e1e2e',
        font=dict(color='white'),
        showlegend=False,
        height=400,
        hovermode='x unified'
    )
    
    return fig

def get_dxy_market_impact(current_dxy: float, daily_change: float, weekly_change: float) -> dict:
    """
    Analyze DXY impact on crypto markets
    
    Args:
        current_dxy: Current DXY value
        daily_change: Daily change
        weekly_change: Weekly change
        
    Returns:
        Dictionary with impact analysis
    """
    impact_data = {
        'level_analysis': '',
        'trend_analysis': '',
        'crypto_impact': '',
        'color': '#a0a0a0'
    }
    
    # Level analysis
    if current_dxy >= 106:
        impact_data['level_analysis'] = "Very High (Strong Dollar)"
        impact_data['crypto_impact'] = "Very Bearish for Crypto"
        impact_data['color'] = "#ff5757"
    elif current_dxy >= 104:
        impact_data['level_analysis'] = "High (Strong Dollar)"
        impact_data['crypto_impact'] = "Bearish for Crypto"
        impact_data['color'] = "#ff8c42"
    elif current_dxy >= 102:
        impact_data['level_analysis'] = "Elevated (Firm Dollar)"
        impact_data['crypto_impact'] = "Slightly Bearish for Crypto"
        impact_data['color'] = "#ffa500"
    elif current_dxy >= 100:
        impact_data['level_analysis'] = "Normal Range"
        impact_data['crypto_impact'] = "Neutral for Crypto"
        impact_data['color'] = "#a0a0a0"
    else:
        impact_data['level_analysis'] = "Low (Weak Dollar)"
        impact_data['crypto_impact'] = "Bullish for Crypto"
        impact_data['color'] = "#00d4aa"
    
    # Trend analysis
    if daily_change > 0.15:
        impact_data['trend_analysis'] = "Rising Strongly"
    elif daily_change > 0.05:
        impact_data['trend_analysis'] = "Rising"
    elif daily_change < -0.15:
        impact_data['trend_analysis'] = "Falling Strongly"
    elif daily_change < -0.05:
        impact_data['trend_analysis'] = "Falling"
    else:
        impact_data['trend_analysis'] = "Stable"
    
    return impact_data

def render_dxy_analysis():
    """Render DXY analysis component"""
    traditional_fetcher = TraditionalDataFetcher()
    
    # Fetch DXY data and analysis
    with st.spinner("Loading DXY data..."):
        dxy_analysis = traditional_fetcher.get_dxy_analysis()
    
    if dxy_analysis and 'dataframe' in dxy_analysis:
        df = dxy_analysis['dataframe']
        
        # Create and display chart
        fig_dxy = create_dxy_chart(df)
        st.plotly_chart(fig_dxy, use_container_width=True)
        
        # Get detailed impact analysis
        current_dxy = dxy_analysis['current_value']
        daily_change = dxy_analysis['daily_change']
        weekly_change = dxy_analysis['weekly_change']
        
        impact_analysis = get_dxy_market_impact(current_dxy, daily_change, weekly_change)
        
        # Display metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Current DXY</div>
                <div class="metric-value">{current_dxy:.2f}</div>
                <div class="metric-change" style="color: {impact_analysis['color']};">
                    {impact_analysis['level_analysis']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            change_color = "positive" if daily_change > 0 else "negative" if daily_change < 0 else "neutral"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Daily Change</div>
                <div class="metric-value" style="color: {change_color};">{daily_change:+.2f}</div>
                <div class="metric-change" style="color: {change_color};">
                    {impact_analysis['trend_analysis']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Crypto market impact explanation
        st.markdown(f"""
        <div class="dxy-explanation">
            <strong>💱 DXY Impact on Crypto:</strong><br><br>
            <div style="display: flex; justify-content: space-between; align-items: center; margin: 10px 0; padding: 10px; background: rgba(0,0,0,0.3); border-radius: 6px;">
                <span><strong>Current Impact:</strong></span>
                <span style="color: {impact_analysis['color']}; font-weight: 700;">{impact_analysis['crypto_impact']}</span>
            </div>
            
            <strong>📈 How it works:</strong><br>
            • <strong>Rising DXY:</strong> Stronger dollar → Risk-off sentiment → Crypto sells off<br>
            • <strong>Falling DXY:</strong> Weaker dollar → Risk-on sentiment → Crypto rallies<br><br>
            
            <strong>🎯 Key Levels:</strong><br>
            • Above 105: Major headwinds for risk assets<br>
            • Below 100: Tailwinds for crypto and risk assets<br>
            • 102-104: Normal range, trend direction matters more
        </div>
        """, unsafe_allow_html=True)
        
        # Weekly change context
        weekly_color = "negative" if weekly_change > 0 else "positive" if weekly_change < 0 else "neutral"
        weekly_impact = "Increasing headwinds" if weekly_change > 0 else "Decreasing headwinds" if weekly_change < 0 else "No change"
        
        st.markdown(f"""
        <div style="background: #2a2a3a; padding: 15px; border-radius: 8px; margin-top: 15px; border: 1px solid #3d3d4d;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="color: #a0a0a0; font-size: 14px;">Weekly Change</div>
                    <div class="{weekly_color}" style="font-size: 18px; font-weight: 700;">
                        {weekly_change:+.2f} ({format_percentage(weekly_change/current_dxy*100)})
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="color: #a0a0a0; font-size: 14px;">For Crypto</div>
                    <div class="{weekly_color}" style="font-size: 14px; font-weight: 600;">
                        {weekly_impact}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Historical context
        st.markdown("""
        <div style="background: #1a1a2e; padding: 10px; border-radius: 8px; margin-top: 10px; font-size: 12px; color: #cccccc; border-left: 4px solid #ffa500;">
            <strong>📊 Historical Context:</strong> Major crypto rallies often coincide with DXY falling below 102. 
            DXY spikes above 105 have historically marked significant crypto corrections.
        </div>
        """, unsafe_allow_html=True)
        
    else:
        st.error("Unable to load DXY data. Please check your internet connection.")