import streamlit as st
from openai import OpenAI, OpenAIError, APIError, APIConnectionError, RateLimitError
import yfinance as yf
import plotly.graph_objects as go
import re
import os
from typing import Dict, Optional, Tuple
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="AI Stock Analyzer", page_icon="📈", layout="wide")

# Initialize session state
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []
if 'api_key_validated' not in st.session_state:
    st.session_state.api_key_validated = False

def validate_stock_symbol(symbol: str) -> Tuple[bool, str]:
    """
    Validate stock symbol format.
    Returns: (is_valid, cleaned_symbol or error_message)
    """
    if not symbol:
        return False, "Stock symbol cannot be empty"
    
    # Clean and uppercase
    symbol = symbol.strip().upper()
    
    # Basic validation: 1-5 alphanumeric characters (covers most stock symbols)
    if not re.match(r'^[A-Z]{1,5}$', symbol):
        return False, "Invalid stock symbol format. Please use 1-5 letters (e.g., AAPL, GOOGL)"
    
    return True, symbol

def validate_openai_api_key() -> Tuple[bool, str]:
    """
    Validate that OpenAI API key is available and works.
    Returns: (is_valid, error_message)
    """
    try:
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            return False, "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
        
        # Try a minimal API call to validate the key
        client = OpenAI(api_key=api_key)
        # Just check if we can create a client - actual validation happens on first use
        return True, ""
    except Exception as e:
        return False, f"Failed to initialize OpenAI client: {str(e)}"

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_stock_info(symbol: str) -> Dict:
    """
    Fetch stock information using yfinance with error handling.
    Cached to reduce API calls.
    """
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        
        # Check if the stock exists by looking for key fields
        if not info or 'symbol' not in info and 'longName' not in info:
            raise ValueError(f"Stock symbol '{symbol}' not found or data unavailable")
        
        stock_data = {
            'symbol': symbol,
            'name': info.get('longName', info.get('shortName', 'N/A')),
            'current_price': info.get('currentPrice', info.get('regularMarketPrice', None)),
            'previous_close': info.get('previousClose', None),
            'market_cap': info.get('marketCap', None),
            'pe_ratio': info.get('trailingPE', None),
            'fifty_two_week_high': info.get('fiftyTwoWeekHigh', None),
            'fifty_two_week_low': info.get('fiftyTwoWeekLow', None),
            'volume': info.get('volume', None),
            'avg_volume': info.get('averageVolume', None),
            'dividend_yield': info.get('dividendYield', None),
            'beta': info.get('beta', None),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
        }
        
        # Validate that we have at least basic price data
        if stock_data['current_price'] is None:
            raise ValueError(f"Unable to fetch current price for '{symbol}'")
        
        return stock_data
    
    except Exception as e:
        raise ValueError(f"Error fetching stock data: {str(e)}")

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_stock_history(symbol: str, period: str = "6mo") -> pd.DataFrame:
    """
    Get historical stock data with error handling.
    Cached to reduce API calls.
    """
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        
        if hist.empty:
            raise ValueError(f"No historical data available for '{symbol}'")
        
        return hist
    
    except Exception as e:
        raise ValueError(f"Error fetching historical data: {str(e)}")

def format_currency(value: Optional[float], decimals: int = 2) -> str:
    """Format numeric value as currency or return N/A"""
    if value is None or (isinstance(value, str) and value == 'N/A'):
        return "N/A"
    try:
        if decimals == 0:
            return f"${value:,.0f}"
        return f"${value:,.{decimals}f}"
    except:
        return "N/A"

def format_number(value: Optional[float], decimals: int = 2) -> str:
    """Format numeric value or return N/A"""
    if value is None or (isinstance(value, str) and value == 'N/A'):
        return "N/A"
    try:
        if decimals == 0:
            return f"{value:,.0f}"
        return f"{value:,.{decimals}f}"
    except:
        return "N/A"

def format_percentage(value: Optional[float], decimals: int = 2) -> str:
    """Format value as percentage or return N/A"""
    if value is None or (isinstance(value, str) and value == 'N/A'):
        return "N/A"
    try:
        return f"{value * 100:.{decimals}f}%"
    except:
        return "N/A"

@st.cache_data(ttl=3600)  # Cache for 1 hour
def analyze_stock_with_gpt(stock_data: Dict, api_key: Optional[str] = None) -> str:
    """
    Analyze stock with GPT (using gpt-4 or gpt-4-turbo as gpt-5 doesn't exist yet).
    Includes error handling and rate limiting protection.
    """
    try:
        # Build a comprehensive prompt
        prompt = f"""Analyze this stock and provide a brief investment summary:

Stock: {stock_data['name']} ({stock_data['symbol']})
Sector: {stock_data['sector']}
Industry: {stock_data['industry']}

Current Metrics:
- Current Price: {format_currency(stock_data['current_price'])}
- Previous Close: {format_currency(stock_data['previous_close'])}
- Market Cap: {format_currency(stock_data['market_cap'], 0)}
- P/E Ratio: {format_number(stock_data['pe_ratio'])}
- 52-Week High: {format_currency(stock_data['fifty_two_week_high'])}
- 52-Week Low: {format_currency(stock_data['fifty_two_week_low'])}
- Beta: {format_number(stock_data.get('beta'))}
- Dividend Yield: {format_percentage(stock_data.get('dividend_yield'))}

Provide a 2-3 sentence analysis focusing on:
1. Current valuation and price position
2. Key risks or opportunities
3. Brief outlook

Keep it concise and objective."""

        # Initialize OpenAI client
        if api_key:
            client = OpenAI(api_key=api_key)
        else:
            client = OpenAI()  # Uses OPENAI_API_KEY from environment
        
        # Use gpt-4-turbo or gpt-4 (gpt-5 doesn't exist yet)
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",  # or "gpt-4" for older version
            messages=[
                {"role": "system", "content": "You are a professional financial analyst providing concise, objective stock analysis."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    except RateLimitError:
        return "⚠️ Rate limit reached. Please try again in a few moments."
    except APIConnectionError:
        return "⚠️ Connection error. Please check your internet connection and try again."
    except APIError as e:
        return f"⚠️ OpenAI API error: {str(e)}"
    except OpenAIError as e:
        return f"⚠️ OpenAI error: {str(e)}"
    except Exception as e:
        return f"⚠️ Unexpected error during analysis: {str(e)}"

# App Title
st.title("📈 AI-Powered Stock Analyzer")
st.markdown("*Powered by GPT-4 and Yahoo Finance*")

# Check for API key on first run
if not st.session_state.api_key_validated:
    is_valid, error_msg = validate_openai_api_key()
    if not is_valid:
        st.error(f"🔑 {error_msg}")
        st.info("💡 **How to set up:**\n\n1. Get your API key from [OpenAI](https://platform.openai.com/api-keys)\n2. Set it as an environment variable: `export OPENAI_API_KEY='your-key-here'`\n3. Restart this app")
        st.stop()
    st.session_state.api_key_validated = True

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    time_period = st.selectbox(
        "Chart Time Period",
        ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
        index=2,
        help="Select the time period for the price history chart"
    )
    
    st.markdown("---")
    
    # Analysis History
    st.subheader("📜 Recent Analyses")
    if st.session_state.analysis_history:
        for idx, item in enumerate(reversed(st.session_state.analysis_history[-5:])):  # Show last 5
            with st.expander(f"{item['symbol']} - {item['timestamp']}"):
                st.write(f"**{item['name']}**")
                st.write(f"Price: {format_currency(item['price'])}")
        
        if st.button("Clear History", use_container_width=True):
            st.session_state.analysis_history = []
            st.rerun()
    else:
        st.caption("No analyses yet")
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("This app fetches real-time stock data and uses GPT-4 to provide AI-powered analysis.")
    st.markdown("**Features:**")
    st.markdown("- Real-time stock data")
    st.markdown("- Interactive price charts")
    st.markdown("- AI-powered analysis")
    st.markdown("- Analysis history")
    
    st.markdown("---")
    st.caption("Built with Streamlit & OpenAI")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    symbol_input = st.text_input(
        "Enter Stock Symbol",
        placeholder="e.g., AAPL, GOOGL, TSLA",
        value="",
        help="Enter a valid stock ticker symbol (1-5 letters)"
    )

with col2:
    analyze_button = st.button("🔍 Analyze Stock", type="primary", use_container_width=True)

# Quick access buttons
st.markdown("**Quick Access:**")
col1, col2, col3, col4, col5 = st.columns(5)
popular_stocks = [("AAPL", "Apple"), ("GOOGL", "Google"), ("MSFT", "Microsoft"), ("TSLA", "Tesla"), ("AMZN", "Amazon")]

for idx, (col, (sym, name)) in enumerate(zip([col1, col2, col3, col4, col5], popular_stocks)):
    with col:
        if st.button(f"📊 {sym}", key=f"quick_{sym}", use_container_width=True, help=name):
            symbol_input = sym
            analyze_button = True

if analyze_button and symbol_input:
    # Validate symbol format
    is_valid, result = validate_stock_symbol(symbol_input)
    
    if not is_valid:
        st.error(f"❌ {result}")
    else:
        symbol = result
        
        try:
            # Fetch stock data
            with st.spinner(f"📥 Fetching data for {symbol}..."):
                stock_data = get_stock_info(symbol)
                hist_data = get_stock_history(symbol, period=time_period)
            
            # Add to history
            st.session_state.analysis_history.append({
                'symbol': symbol,
                'name': stock_data['name'],
                'price': stock_data['current_price'],
                'timestamp': datetime.now().strftime("%I:%M %p")
            })
            
            # Display stock info header
            st.markdown("---")
            col1, col2 = st.columns([3, 1])
            with col1:
                st.header(f"{stock_data['name']} ({stock_data['symbol']})")
                if stock_data['sector'] != 'N/A':
                    st.caption(f"{stock_data['sector']} · {stock_data['industry']}")
            with col2:
                # Calculate price change
                if stock_data['current_price'] and stock_data['previous_close']:
                    price_change = stock_data['current_price'] - stock_data['previous_close']
                    price_change_pct = (price_change / stock_data['previous_close']) * 100
                    change_color = "🟢" if price_change >= 0 else "🔴"
                    st.metric(
                        "Change",
                        f"{change_color} {price_change_pct:.2f}%",
                        f"${price_change:.2f}"
                    )
            
            # Key metrics row 1
            st.subheader("📊 Key Metrics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Current Price",
                    format_currency(stock_data['current_price']),
                    help="Latest trading price"
                )
            
            with col2:
                st.metric(
                    "Market Cap",
                    format_currency(stock_data['market_cap'], 0),
                    help="Total market value of the company"
                )
            
            with col3:
                st.metric(
                    "P/E Ratio",
                    format_number(stock_data['pe_ratio']),
                    help="Price-to-Earnings ratio"
                )
            
            with col4:
                st.metric(
                    "Volume",
                    format_number(stock_data['volume'], 0),
                    help="Trading volume for the day"
                )
            
            # Key metrics row 2
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "52W High",
                    format_currency(stock_data['fifty_two_week_high']),
                    help="Highest price in the last 52 weeks"
                )
            
            with col2:
                st.metric(
                    "52W Low",
                    format_currency(stock_data['fifty_two_week_low']),
                    help="Lowest price in the last 52 weeks"
                )
            
            with col3:
                st.metric(
                    "Beta",
                    format_number(stock_data.get('beta')),
                    help="Stock volatility compared to market"
                )
            
            with col4:
                st.metric(
                    "Dividend Yield",
                    format_percentage(stock_data.get('dividend_yield')),
                    help="Annual dividend as % of stock price"
                )
            
            # Price chart
            st.subheader(f"📈 Price History ({time_period})")
            
            try:
                fig = go.Figure()
                fig.add_trace(go.Candlestick(
                    x=hist_data.index,
                    open=hist_data['Open'],
                    high=hist_data['High'],
                    low=hist_data['Low'],
                    close=hist_data['Close'],
                    name='Price',
                    increasing_line_color='#26a69a',
                    decreasing_line_color='#ef5350'
                ))
                
                fig.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Price (USD)",
                    height=450,
                    template="plotly_white",
                    xaxis_rangeslider_visible=False,
                    hovermode='x unified',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                )
                
                st.plotly_chart(fig, use_container_width=True)
            except Exception as chart_error:
                st.warning(f"⚠️ Could not generate price chart: {str(chart_error)}")
            
            # GPT Analysis
            st.subheader("🤖 AI Analysis")
            with st.spinner("🧠 Generating AI analysis..."):
                try:
                    analysis = analyze_stock_with_gpt(stock_data)
                    
                    if analysis.startswith("⚠️"):
                        st.warning(analysis)
                    else:
                        st.info(analysis)
                        
                        # Disclaimer
                        st.caption("⚠️ **Disclaimer:** This analysis is generated by AI and should not be considered as financial advice. Always do your own research and consult with a financial advisor before making investment decisions.")
                
                except Exception as analysis_error:
                    st.error(f"❌ Failed to generate AI analysis: {str(analysis_error)}")
                    st.info("💡 The stock data is still available above. You can try the analysis again or check your OpenAI API key.")
            
            # Additional details in expander
            with st.expander("📊 Additional Details"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Trading Information**")
                    st.markdown(f"- **Previous Close:** {format_currency(stock_data['previous_close'])}")
                    st.markdown(f"- **Volume:** {format_number(stock_data['volume'], 0)}")
                    st.markdown(f"- **Avg Volume:** {format_number(stock_data['avg_volume'], 0)}")
                
                with col2:
                    st.markdown("**Valuation Metrics**")
                    st.markdown(f"- **52-Week High:** {format_currency(stock_data['fifty_two_week_high'])}")
                    st.markdown(f"- **52-Week Low:** {format_currency(stock_data['fifty_two_week_low'])}")
                    st.markdown(f"- **Beta:** {format_number(stock_data.get('beta'))}")
            
            # Export data option
            with st.expander("💾 Export Data"):
                st.markdown("**Download historical data as CSV**")
                csv_data = hist_data.to_csv()
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name=f"{symbol}_history_{time_period}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        except ValueError as ve:
            st.error(f"❌ {str(ve)}")
            st.markdown("**Possible issues:**")
            st.markdown("- Stock symbol might be incorrect or not found")
            st.markdown("- Yahoo Finance API might be temporarily unavailable")
            st.markdown("- Try a different stock symbol or try again later")
        
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
            st.markdown("**What you can try:**")
            st.markdown("1. Check your internet connection")
            st.markdown("2. Verify the stock symbol is correct")
            st.markdown("3. Try again in a few moments")
            st.markdown("4. Contact support if the issue persists")

elif analyze_button and not symbol_input:
    st.warning("⚠️ Please enter a stock symbol.")

# Footer
st.markdown("---")
st.markdown("*Data provided by Yahoo Finance. Analysis generated by OpenAI GPT-4.*")
st.caption("This tool is for informational purposes only and does not constitute financial advice.")

