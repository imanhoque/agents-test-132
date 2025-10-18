import streamlit as st
from openai import OpenAI
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(page_title="AI Stock Analyzer", page_icon="📈", layout="wide")

def get_stock_info(symbol):
    """Fetch stock information using yfinance!"""
    stock = yf.Ticker(symbol)
    info = stock.info
    
    stock_data = {
        'symbol': symbol,
        'name': info.get('longName', 'N/A'),
        'current_price': info.get('currentPrice', info.get('regularMarketPrice', 'N/A')),
        'previous_close': info.get('previousClose', 'N/A'),
        'market_cap': info.get('marketCap', 'N/A'),
        'pe_ratio': info.get('trailingPE', 'N/A'),
        'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 'N/A'),
        'fifty_two_week_low': info.get('fiftyTwoWeekLow', 'N/A'),
        'volume': info.get('volume', 'N/A'),
        'avg_volume': info.get('averageVolume', 'N/A'),
    }
    return stock_data

def get_stock_history(symbol, period="6mo"):
    """Get historical stock data"""
    stock = yf.Ticker(symbol)
    hist = stock.history(period=period)
    return hist

def analyze_stock_with_gpt(stock_data):
    """Analyze stock with GPT-5"""
    prompt = f"""Analyze this stock and provide a brief summary:

Stock: {stock_data['name']} ({stock_data['symbol']})
Current Price: ${stock_data['current_price']}
Previous Close: ${stock_data['previous_close']}
Market Cap: ${stock_data['market_cap']:,} (if available)
P/E Ratio: {stock_data['pe_ratio']}
52-Week High: ${stock_data['fifty_two_week_high']}
52-Week Low: ${stock_data['fifty_two_week_low']}

Provide a 2-3 sentence analysis of this stock's current position."""

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-5",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content

# App Title
st.title("📈 AI-Powered Stock Analyzer")
st.markdown("*Powered by GPT-5 and Yahoo Finance*")

# Sidebar
with st.sidebar:
    st.header("Settings")
    time_period = st.selectbox(
        "Chart Time Period",
        ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
        index=2
    )
    st.markdown("---")
    st.markdown("### About")
    st.markdown("This app fetches real-time stock data and uses GPT-5 to provide AI-powered analysis.")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    symbol = st.text_input("Enter Stock Symbol", placeholder="e.g., AAPL, GOOGL, TSLA", value="AAPL")

with col2:
    analyze_button = st.button("🔍 Analyze Stock", type="primary", use_container_width=True)

if analyze_button and symbol:
    try:
        with st.spinner(f"Fetching data for {symbol.upper()}..."):
            # Get stock data
            stock_data = get_stock_info(symbol.upper())
            hist_data = get_stock_history(symbol.upper(), period=time_period)
            
        # Display stock info
        st.header(f"{stock_data['name']} ({stock_data['symbol']})")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Current Price",
                f"${stock_data['current_price']:.2f}" if isinstance(stock_data['current_price'], (int, float)) else "N/A",
                delta=f"{((stock_data['current_price'] - stock_data['previous_close']) / stock_data['previous_close'] * 100):.2f}%" if isinstance(stock_data['current_price'], (int, float)) and isinstance(stock_data['previous_close'], (int, float)) else None
            )
        
        with col2:
            st.metric("Market Cap", f"${stock_data['market_cap']:,.0f}" if isinstance(stock_data['market_cap'], (int, float)) else "N/A")
        
        with col3:
            st.metric("P/E Ratio", f"{stock_data['pe_ratio']:.2f}" if isinstance(stock_data['pe_ratio'], (int, float)) else "N/A")
        
        with col4:
            st.metric("Volume", f"{stock_data['volume']:,}" if isinstance(stock_data['volume'], (int, float)) else "N/A")
        
        # Price chart
        st.subheader("Price History")
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=hist_data.index,
            open=hist_data['Open'],
            high=hist_data['High'],
            low=hist_data['Low'],
            close=hist_data['Close'],
            name='Price'
        ))
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            height=400,
            template="plotly_dark",
            xaxis_rangeslider_visible=False
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # GPT-5 Analysis
        st.subheader("🤖 AI Analysis")
        with st.spinner("Generating AI analysis..."):
            analysis = analyze_stock_with_gpt(stock_data)
        
        st.info(analysis)
        
        # Additional details in expander
        with st.expander("📊 Detailed Metrics"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**52-Week High:** ${stock_data['fifty_two_week_high']}")
                st.markdown(f"**52-Week Low:** ${stock_data['fifty_two_week_low']}")
            with col2:
                st.markdown(f"**Average Volume:** {stock_data['avg_volume']:,}" if isinstance(stock_data['avg_volume'], (int, float)) else "**Average Volume:** N/A")
                st.markdown(f"**Previous Close:** ${stock_data['previous_close']}")
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.markdown("Please check if the stock symbol is correct and try again.")

elif not symbol and analyze_button:
    st.warning("⚠️ Please enter a stock symbol.")

# Footer
st.markdown("---")
st.markdown("*Data provided by Yahoo Finance. Analysis generated by OpenAI GPT-5.*")

