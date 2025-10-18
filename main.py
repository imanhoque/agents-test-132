from openai import OpenAI
import yfinance as yf

def get_stock_info(symbol):
    """Fetch stock information using yfinance"""
    stock = yf.Ticker(symbol)
    info = stock.info
    
    # Get relevant data
    stock_data = {
        'symbol': symbol,
        'name': info.get('longName', 'N/A'),
        'current_price': info.get('currentPrice', info.get('regularMarketPrice', 'N/A')),
        'previous_close': info.get('previousClose', 'N/A'),
        'market_cap': info.get('marketCap', 'N/A'),
        'pe_ratio': info.get('trailingPE', 'N/A'),
        'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 'N/A'),
        'fifty_two_week_low': info.get('fiftyTwoWeekLow', 'N/A'),
    }
    return stock_data

def analyze_stock_with_gpt(symbol):
    """Get stock info and analyze it with GPT-5"""
    # Fetch stock data
    stock_data = get_stock_info(symbol)
    
    # Create prompt for GPT-5
    prompt = f"""Analyze this stock and provide a brief summary:

Stock: {stock_data['name']} ({stock_data['symbol']})
Current Price: ${stock_data['current_price']}
Previous Close: ${stock_data['previous_close']}
Market Cap: ${stock_data['market_cap']:,} (if available)
P/E Ratio: {stock_data['pe_ratio']}
52-Week High: ${stock_data['fifty_two_week_high']}
52-Week Low: ${stock_data['fifty_two_week_low']}

Provide a 2-3 sentence analysis of this stock's current position."""

    # Call GPT-5
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-5",  # Use gpt-4 or gpt-4-turbo (gpt-5 may not be available yet)
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return {
        'stock_data': stock_data,
        'analysis': response.choices[0].message.content
    }

if __name__ == "__main__":
    # Example: Analyze Apple stock
    symbol = input("Enter stock symbol (e.g., AAPL, GOOGL, TSLA): ").upper()
    
    try:
        result = analyze_stock_with_gpt(symbol)
        
        print(f"\n{'='*60}")
        print(f"Stock Analysis: {result['stock_data']['name']}")
        print(f"{'='*60}")
        print(f"\nCurrent Price: ${result['stock_data']['current_price']}")
        print(f"Previous Close: ${result['stock_data']['previous_close']}")
        print(f"\nGPT-5 Analysis:")
        print(f"{result['analysis']}")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"Error: {e}")
