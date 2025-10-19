#!/usr/bin/env python3
"""
CLI Stock Analyzer - Command-line interface for stock analysis
"""

from openai import OpenAI, OpenAIError, APIError, APIConnectionError, RateLimitError
import yfinance as yf
import sys
import os
import re
from typing import Dict, Tuple, Optional

def validate_stock_symbol(symbol: str) -> Tuple[bool, str]:
    """
    Validate stock symbol format.
    Returns: (is_valid, cleaned_symbol or error_message)
    """
    if not symbol:
        return False, "Stock symbol cannot be empty"
    
    # Clean and uppercase
    symbol = symbol.strip().upper()
    
    # Basic validation: 1-5 alphanumeric characters
    if not re.match(r'^[A-Z]{1,5}$', symbol):
        return False, "Invalid stock symbol format. Please use 1-5 letters (e.g., AAPL, GOOGL)"
    
    return True, symbol

def validate_openai_api_key() -> Tuple[bool, str]:
    """
    Validate that OpenAI API key is available.
    Returns: (is_valid, error_message)
    """
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        return False, "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
    return True, ""

def get_stock_info(symbol: str) -> Dict:
    """Fetch stock information using yfinance with error handling"""
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        
        # Check if the stock exists
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

def format_value(value: Optional[float], prefix: str = "", suffix: str = "", decimals: int = 2) -> str:
    """Format numeric value or return N/A"""
    if value is None or (isinstance(value, str) and value == 'N/A'):
        return "N/A"
    try:
        if decimals == 0:
            return f"{prefix}{value:,.0f}{suffix}"
        return f"{prefix}{value:,.{decimals}f}{suffix}"
    except:
        return "N/A"

def analyze_stock_with_gpt(symbol: str) -> Dict:
    """Get stock info and analyze it with GPT-4"""
    
    # Validate API key first
    is_valid, error_msg = validate_openai_api_key()
    if not is_valid:
        raise ValueError(error_msg)
    
    # Fetch stock data
    stock_data = get_stock_info(symbol)
    
    # Create comprehensive prompt for GPT-4
    prompt = f"""Analyze this stock and provide a brief investment summary:

Stock: {stock_data['name']} ({stock_data['symbol']})
Sector: {stock_data['sector']}
Industry: {stock_data['industry']}

Current Metrics:
- Current Price: {format_value(stock_data['current_price'], '$')}
- Previous Close: {format_value(stock_data['previous_close'], '$')}
- Market Cap: {format_value(stock_data['market_cap'], '$', '', 0)}
- P/E Ratio: {format_value(stock_data['pe_ratio'])}
- 52-Week High: {format_value(stock_data['fifty_two_week_high'], '$')}
- 52-Week Low: {format_value(stock_data['fifty_two_week_low'], '$')}
- Beta: {format_value(stock_data.get('beta'))}
- Dividend Yield: {format_value(stock_data.get('dividend_yield') * 100 if stock_data.get('dividend_yield') else None, '', '%')}

Provide a 2-3 sentence analysis focusing on:
1. Current valuation and price position
2. Key risks or opportunities
3. Brief outlook

Keep it concise and objective."""

    try:
        # Call GPT-4
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",  # Using gpt-4-turbo as gpt-5 doesn't exist
            messages=[
                {"role": "system", "content": "You are a professional financial analyst providing concise, objective stock analysis."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        analysis = response.choices[0].message.content
        
    except RateLimitError:
        analysis = "Rate limit reached. Please try again in a few moments."
    except APIConnectionError:
        analysis = "Connection error. Please check your internet connection."
    except APIError as e:
        analysis = f"OpenAI API error: {str(e)}"
    except OpenAIError as e:
        analysis = f"OpenAI error: {str(e)}"
    except Exception as e:
        analysis = f"Unexpected error during analysis: {str(e)}"
    
    return {
        'stock_data': stock_data,
        'analysis': analysis
    }

def print_banner():
    """Print application banner"""
    print("\n" + "="*70)
    print("📈 AI-Powered Stock Analyzer (CLI)")
    print("="*70)
    print("Powered by GPT-4 and Yahoo Finance")
    print("="*70 + "\n")

def print_stock_analysis(result: Dict):
    """Pretty print stock analysis results"""
    stock_data = result['stock_data']
    analysis = result['analysis']
    
    print(f"\n{'='*70}")
    print(f"📊 Stock Analysis: {stock_data['name']} ({stock_data['symbol']})")
    print(f"{'='*70}")
    
    if stock_data['sector'] != 'N/A':
        print(f"Sector: {stock_data['sector']} | Industry: {stock_data['industry']}")
        print(f"{'-'*70}")
    
    # Price information
    print("\n💰 Price Information:")
    print(f"  Current Price:    {format_value(stock_data['current_price'], '$')}")
    print(f"  Previous Close:   {format_value(stock_data['previous_close'], '$')}")
    
    if stock_data['current_price'] and stock_data['previous_close']:
        change = stock_data['current_price'] - stock_data['previous_close']
        change_pct = (change / stock_data['previous_close']) * 100
        emoji = "🟢" if change >= 0 else "🔴"
        print(f"  Change:           {emoji} {format_value(change, '$')} ({change_pct:+.2f}%)")
    
    # Valuation metrics
    print("\n📈 Valuation Metrics:")
    print(f"  Market Cap:       {format_value(stock_data['market_cap'], '$', '', 0)}")
    print(f"  P/E Ratio:        {format_value(stock_data['pe_ratio'])}")
    print(f"  Beta:             {format_value(stock_data['beta'])}")
    print(f"  Dividend Yield:   {format_value(stock_data.get('dividend_yield') * 100 if stock_data.get('dividend_yield') else None, '', '%')}")
    
    # 52-week range
    print("\n📊 52-Week Range:")
    print(f"  High:             {format_value(stock_data['fifty_two_week_high'], '$')}")
    print(f"  Low:              {format_value(stock_data['fifty_two_week_low'], '$')}")
    
    # Trading info
    print("\n📦 Trading Information:")
    print(f"  Volume:           {format_value(stock_data['volume'], '', '', 0)}")
    
    # AI Analysis
    print(f"\n🤖 AI Analysis:")
    print(f"{'-'*70}")
    print(f"{analysis}")
    print(f"{'-'*70}")
    
    # Disclaimer
    print("\n⚠️  DISCLAIMER: This analysis is for informational purposes only and")
    print("   does not constitute financial advice. Always do your own research")
    print("   and consult with a financial advisor before making investment decisions.")
    print(f"{'='*70}\n")

def main():
    """Main CLI application"""
    print_banner()
    
    # Check for API key
    is_valid, error_msg = validate_openai_api_key()
    if not is_valid:
        print(f"❌ Error: {error_msg}\n")
        print("To fix this:")
        print("1. Get your API key from: https://platform.openai.com/api-keys")
        print("2. Set it as an environment variable:")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        print("3. Run this script again\n")
        sys.exit(1)
    
    # Main loop
    while True:
        try:
            # Get user input
            symbol_input = input("Enter stock symbol (or 'quit' to exit): ").strip()
            
            if symbol_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Thank you for using AI-Powered Stock Analyzer!\n")
                break
            
            # Validate symbol
            is_valid, result = validate_stock_symbol(symbol_input)
            if not is_valid:
                print(f"\n❌ Error: {result}\n")
                continue
            
            symbol = result
            
            # Fetch and analyze
            print(f"\n⏳ Fetching data for {symbol}...")
            analysis_result = analyze_stock_with_gpt(symbol)
            
            # Display results
            print_stock_analysis(analysis_result)
            
            # Ask if user wants to continue
            continue_choice = input("Analyze another stock? (y/n): ").strip().lower()
            if continue_choice not in ['y', 'yes', '']:
                print("\n👋 Thank you for using AI-Powered Stock Analyzer!\n")
                break
        
        except ValueError as ve:
            print(f"\n❌ Error: {str(ve)}")
            print("Please try again with a different stock symbol.\n")
        
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user. Goodbye!\n")
            break
        
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
            print("Please try again or contact support if the issue persists.\n")

if __name__ == "__main__":
    main()
