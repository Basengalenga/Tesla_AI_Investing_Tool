import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from pymongo import MongoClient, DESCENDING
import logging
import numpy as np
from datetime import datetime, timedelta
import json
import html

# Page configuration with professional dark theme
st.set_page_config(
    page_title="TESLA | Investment Intelligence Platform", 
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="⚡"
)

# Custom CSS for professional look
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .ai-analysis-card {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
        border-left: 5px solid #ffd700;
    }
    
    .news-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        transition: transform 0.3s ease;
    }
    
    .news-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
    }
    
    .sidebar-logo {
        text-align: center;
        padding: 2rem 0;
        font-size: 2.5rem;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }
    
    .stMetric {
        background: rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #4ecdc4;
    }
    
    .raw-data-container {
        background: #1a1a1a;
        border: 1px solid #333;
        border-radius: 10px;
        padding: 1rem;
        font-family: 'Courier New', monospace;
        font-size: 12px;
        color: #00ff00;
        max-height: 600px;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar with branding
with st.sidebar:
    st.markdown('<div class="sidebar-logo">⚡ TESLA AI</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 🎯 **Investment Intelligence**")
    st.markdown("*Weekly Analysis - 7 days*")
    
    # Display settings
    st.markdown("### ⚙️ **Settings**")
    show_volume = st.checkbox("📊 Show volume", value=True)
    show_indicators = st.checkbox("📈 Technical indicators", value=True)
    
    st.markdown("---")
    st.markdown("### 📱 **Contact**")
    st.markdown("*Dashboard v2.0*  \n*Weekly analysis updated*")

# MongoDB connection with improved error handling
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data():
    try:
        client = MongoClient("mongodb://host.docker.internal:27017/")
        db = client["projectUnit2"]
        collection = db["AggregatedData"]
        record = collection.find_one(sort=[("loaded_at", DESCENDING)])
        return record
    except Exception as e:
        logging.error(f"Error connecting to MongoDB: {e}")
        return None

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_raw_data():
    try:
        client = MongoClient("mongodb://host.docker.internal:27017/")
        db = client["projectUnit2"]
        collection = db["RawData"]
        record = collection.find_one()
        return record
    except Exception as e:
        logging.error(f"Error connecting to MongoDB for raw data: {e}")
        return None

# Tab configuration
tab1, tab2 = st.tabs(["📊 **DASHBOARD**", "🔧 **RAW DATA**"])

with tab1:
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>⚡ TESLA INVESTMENT INTELLIGENCE PLATFORM</h1>
        <p>Advanced AI-driven analysis • Batch data • Professional insights</p>
    </div>
    """, unsafe_allow_html=True)

    # Load data
    record = load_data()
    if not record:
        st.error("🚨 **Critical error**: Could not connect to database. Please verify connection.")
        st.stop()

    # Extract data
    tesla = record["tesla_data"]
    tesla_values = tesla["values"]
    news_articles = record["news_data"]["first_20_articles"]
    reddit_posts = record["reddit_data"]["posts"]
    news_analysis = record["gemini_news_analysis"]["gemini_response"]
    reddit_analysis = record["gemini_reddit_analysis"]["gemini_response"]
    reddit_average_score = record['reddit_data']['score_average']

    # Preprocess historical data (only use pre-processed data)
    df = pd.DataFrame(tesla_values).T
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    df = df.astype(float)

    # Data already comes processed from MongoDB - no additional calculations

    # Main metrics with improved design
    st.markdown("## 📊 **KEY METRICS - WEEKLY ANALYSIS**")
    col1, col2, col3 = st.columns(3)

    with col1:
        current_price = df['close'].iloc[-1]
        price_change = df['close'].iloc[-1] - df['close'].iloc[-2]
        st.metric(
            "💰 Current Price", 
            f"${current_price:.2f}", 
            delta=f"{price_change:+.2f}",
            delta_color="normal"
        )

    with col2:
        volatility = round(tesla["volatility"], 4)
        st.metric("⚡ Weekly Volatility", f"{volatility:.4f}")

    with col3:
        average_close = round(tesla['average_close'], 4)
        st.metric('📈 Average Close', f'{average_close:.4f}')

    st.markdown("---")

    # Enhanced interactive main chart
    st.markdown("## 📈 **WEEKLY TECHNICAL ANALYSIS**")

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=('TSLA Price - Last Week', 'Trading Volume'),
        row_heights=[0.7, 0.3]
    )

    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name="TSLA",
            increasing_line_color='#00ff88',
            decreasing_line_color='#ff4757'
        ),
        row=1, col=1
    )

    # Volume
    if show_volume and 'volume' in df.columns:
        colors = ['#00ff88' if df['close'].iloc[i] >= df['open'].iloc[i] else '#ff4757' 
                  for i in range(len(df))]
        
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['volume'],
                name='Volume',
                marker_color=colors,
                opacity=0.7
            ),
            row=2, col=1
        )

    # Chart customization
    fig.update_layout(
        title="Tesla (TSLA) - Weekly Analysis",
        height=700,
        template="plotly_dark",
        showlegend=True,
        xaxis_rangeslider_visible=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0.1)',
        font=dict(color='white', size=12)
    )

    fig.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
    fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.1)')

    st.plotly_chart(fig, use_container_width=True)

    # Enhanced AI analysis
    st.markdown("## 🧠 **ADVANCED ARTIFICIAL INTELLIGENCE**")
    st.markdown("*Analysis generated by latest-generation models with natural language processing*")

    # News analysis with impactful design
    st.markdown("""
    <div class="ai-analysis-card">
        <h3>🔍 COMPREHENSIVE NEWS ANALYSIS</h3>
        <p><strong>Sentiment processing • Pattern detection • Impact assessment</strong></p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### 📰 **Market Sentiment Evaluation**")
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); 
                    padding: 2rem; border-radius: 15px; border-left: 5px solid #3498db;">
            <h4 style="color: #3498db;">🎯 Computational Analysis</h4>
            <p style="font-size: 1.1em; line-height: 1.6;">{news_analysis}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # Reemplaza la función extract_sentiment_from_analysis con esta nueva función
        def extract_sentiment_from_labeled_news(labeled_news_data):
            """
            Extrae el sentiment basado en los datos reales de labeled_news
            """
            if not labeled_news_data:
                return {'Positive': 0, 'Neutral': 100, 'Negative': 0}  # 100% neutral if no data
            
            # Contar cada tipo de sentimiento
            sentiment_counts = {
                'Positive': 0,
                'Negative': 0,
                'Neutral': 0,
                'Other': 0
            }
            
            for item in labeled_news_data:
                feeling = item.get('feeling', 'Other')
                if feeling in sentiment_counts:
                    sentiment_counts[feeling] += 1
                else:
                    sentiment_counts['Other'] += 1
            
            # Calcular total para obtener porcentajes
            total = sum(sentiment_counts.values())
            if total == 0:
                return {'Positive': 0, 'Neutral': 100, 'Negative': 0}
            
            # Combinar 'Other' con 'Neutral' para simplicidad del gráfico
            final_counts = {
                'Positive': sentiment_counts['Positive'],
                'Neutral': sentiment_counts['Neutral'] + sentiment_counts['Other'],
                'Negative': sentiment_counts['Negative']
            }
            
            # Convertir a porcentajes
            sentiment_percentages = {
                key: round((count / total) * 100, 1) 
                for key, count in final_counts.items()
            }
            
            return sentiment_percentages

        # También actualiza la sección donde se crea el gráfico de dona:
        # Reemplaza estas líneas:
        # sentiment_data = extract_sentiment_from_analysis(news_analysis)

        # Por estas:
        labeled_news_data = record.get("labeled_news", [])
        sentiment_data = extract_sentiment_from_labeled_news(labeled_news_data)

        # El resto del código del gráfico de dona permanece igual:
        fig_donut = go.Figure(data=[go.Pie(
            labels=list(sentiment_data.keys()),
            values=list(sentiment_data.values()),
            hole=0.5,
            marker_colors=['#00ff88', '#ffd700', '#ff4757']
        )])

        fig_donut.update_layout(
            title="Market Sentiment",
            height=300,
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=True,
            font=dict(color='white', size=10)
        )

        fig_donut.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            textfont_size=12
        )

        st.plotly_chart(fig_donut, use_container_width=True)

    # Reddit analysis with sentiment chart
    st.markdown("""
    <div class="ai-analysis-card">
        <h3>📢 SOCIAL SENTIMENT ANALYSIS (REDDIT)</h3>
        <p><strong>Community monitoring • Behavior analysis • Trend prediction</strong></p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #8e44ad 0%, #9b59b6 100%); 
                    padding: 2rem; border-radius: 15px; border-left: 5px solid #e74c3c;">
            <h4 style="color: #e74c3c;">🔬 Social Media Analysis</h4>
            <p style="font-size: 1.1em; line-height: 1.6;">{reddit_analysis}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        average_close = round(reddit_average_score, 1)
        st.metric('📈 Average score on reddit posts', f'{average_close:.1f}')

    st.markdown("---")

    # Redesigned news section
    st.markdown("## 📰 **FINANCIAL NEWS CENTER**")
    st.markdown("*Verified sources • Weekly analysis • Market impact*")

    # Show news in elegant cards
    news_container = st.container()
    with news_container:
        for i, article in enumerate(news_articles[:8]):  # Limit to top 8 most important
            if i % 2 == 0:
                cols = st.columns(2)
            
            col = cols[i % 2]
            with col:
                st.markdown(f"""
                <div class="news-card">
                    <h4 style="color: #3498db; margin-bottom: 1rem;">📈 {article.get('source', 'N/A')}</h4>
                    <p style="font-weight: bold; margin-bottom: 0.5rem;">✍️ {article.get('author', 'Author not available')}</p>
                    <p style="line-height: 1.5; margin-bottom: 1rem;">{article.get('description', 'Description not available')}</p>
                    <div style="border-top: 1px solid rgba(255,255,255,0.1); padding-top: 1rem;">
                        <small style="color: #7f8c8d;">🕐 Recently updated</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")

    # Enhanced Reddit posts section
    st.markdown("## 📱 **COMMUNITY PULSE**")
    st.markdown("*Retail sentiment analysis • Emerging trends • Public opinion*")

    reddit_cols = st.columns(3)
    for i, post in enumerate(reddit_posts[:9]):  # Top 9 posts
        col = reddit_cols[i % 3]
        with col:
            score_color = "#00ff88" if post['score'] > 0 else "#ff4757"
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.05); padding: 1.5rem; border-radius: 10px; 
                        border-left: 3px solid {score_color}; margin-bottom: 1rem;">
                <p style="font-size: 0.9em; line-height: 1.4; margin-bottom: 1rem;">
                    {post['selftext'][:150]}{'...' if len(post['selftext']) > 150 else ''}
                </p>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: {score_color}; font-weight: bold;">▲ {post['score']}</span>
                    <span style="color: #7f8c8d; font-size: 0.8em;">Reddit</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Professional footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: rgba(0,0,0,0.1); border-radius: 10px;">
        <h4>⚡ TESLA INVESTMENT INTELLIGENCE PLATFORM</h4>
        <p>Developed with cutting-edge technology • Batch data • Advanced AI</p>
        <small>© 2025 - Dashboard updated every 5 minutes</small>
    </div>
    """, unsafe_allow_html=True)

with tab2:
    st.markdown("""
    <div class="main-header">
        <h1>🔧 RAW DATA EXPLORER</h1>
        <p>Direct access to unprocessed database information</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load raw data
    raw_record = load_raw_data()
    
    if raw_record:
        st.markdown("## 📊 **Raw Database Content**")
        st.markdown("*Direct view of unprocessed data from MongoDB collection 'RawData'*")
        
        # Convert to formatted JSON string
        raw_data_json = json.dumps(raw_record, indent=2, default=str)
        
        # Escapar caracteres HTML peligrosos
        safe_raw_data_json = html.escape(raw_data_json)

        # Mostrar en HTML seguro
        st.markdown(f"""
            <div class="raw-data-container">
                <pre>{safe_raw_data_json}</pre>
            </div>
        """, unsafe_allow_html=True)

        # Additional info
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("📄 Document Size", f"{len(raw_data_json)} chars")
        
        with col2:
            st.metric("🔑 Root Keys", f"{len(raw_record.keys()) if isinstance(raw_record, dict) else 'N/A'}")
            
    else:
        st.error("🚨 **Error**: Could not load raw data from database.")
        st.markdown("Please verify that the 'RawData' collection exists and contains data.")