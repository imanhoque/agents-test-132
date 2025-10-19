# AI-Powered Stock Analyzer 📈

An interactive, production-ready stock analysis tool powered by GPT-4 and real-time market data with comprehensive error handling and caching.

## Features

### Core Functionality
- 📊 **Real-time Stock Data**: Fetches live stock information using Yahoo Finance API
- 🤖 **AI Analysis**: Leverages GPT-4 Turbo to provide intelligent stock insights
- 📈 **Interactive Charts**: Beautiful candlestick charts with customizable time periods
- 💹 **Comprehensive Metrics**: Price, market cap, P/E ratio, volume, beta, dividend yield, and more
- 🎨 **Modern UI**: Clean, responsive Streamlit interface with sidebar navigation

### Robust Features
- ✅ **Input Validation**: Stock symbol format validation and sanitization
- 🔄 **Smart Caching**: Reduces API calls with 5-minute cache for stock data, 1-hour for AI analysis
- 🛡️ **Error Handling**: Comprehensive error handling for network issues, invalid symbols, API rate limits
- 📜 **Analysis History**: Track your recent stock analyses with timestamps
- 💾 **Data Export**: Download historical stock data as CSV
- ⚡ **Quick Access**: Pre-configured buttons for popular stocks (AAPL, GOOGL, MSFT, TSLA, AMZN)
- 🔐 **API Key Validation**: Checks for OpenAI API key on startup with helpful setup instructions
- ⚠️ **User Guidance**: Detailed error messages and troubleshooting tips

## Installation

### Prerequisites
- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- Internet connection for real-time data

### Setup Steps

1. **Clone or download this repository:**
```bash
cd /path/to/your/directory
```

2. **Install required packages:**
```bash
pip install -r requirements.txt
```

3. **Set up your OpenAI API key:**

**On macOS/Linux:**
```bash
export OPENAI_API_KEY='your-api-key-here'
```

**On Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY='your-api-key-here'
```

**Or create a `.env` file:**
```bash
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

## Usage

### Streamlit Web App (Recommended)

Run the interactive web interface:
```bash
streamlit run streamlit_app.py
```

The app will open in your default browser at `http://localhost:8501`

**Features:**
- Enter any stock symbol (e.g., AAPL, GOOGL, TSLA)
- Or use quick access buttons for popular stocks
- Adjust time period for historical charts (1mo to 5y)
- View comprehensive metrics and AI analysis
- Download historical data as CSV
- Track analysis history in the sidebar

### Command Line Script

Run the CLI version:
```bash
python main.py
```

Enter a stock symbol when prompted to get instant analysis.

## Architecture & Robustness

### Error Handling
- **Invalid Symbols**: Validates format before API calls
- **Network Issues**: Graceful handling of connection errors
- **Rate Limits**: Catches and reports OpenAI rate limit errors
- **Missing Data**: Safely handles missing or incomplete stock data
- **API Failures**: Fallback messages when APIs are unavailable

### Performance Optimizations
- **Data Caching**: 
  - Stock data cached for 5 minutes (reduces Yahoo Finance calls)
  - AI analysis cached for 1 hour (reduces OpenAI API costs)
- **Lazy Loading**: Only fetches data when needed
- **Efficient Rendering**: Uses Streamlit's native caching mechanisms

### Data Validation
- Stock symbol format validation (1-5 letter symbols)
- Type checking for all numeric values
- Safe formatting functions that handle None/missing values
- Validates API responses before processing

### User Experience
- Clear loading indicators during API calls
- Informative error messages with actionable solutions
- Help tooltips for all metrics
- Analysis history tracking
- Export functionality for further analysis

## Technologies Used

- **OpenAI GPT-4 Turbo**: AI-powered stock analysis with fallback handling
- **yfinance**: Real-time stock data from Yahoo Finance
- **Streamlit**: Modern web interface with caching
- **Plotly**: Interactive candlestick charts
- **Pandas**: Data processing and CSV export

## API Rate Limits & Costs

### Yahoo Finance (yfinance)
- Free, no API key required
- Rate limits are generous for personal use
- Caching reduces API calls significantly

### OpenAI API
- Requires API key with billing
- GPT-4 Turbo costs approximately:
  - Input: $0.01 per 1K tokens
  - Output: $0.03 per 1K tokens
- Each analysis uses ~300-500 tokens
- Caching reduces repeated analysis costs

## Troubleshooting

### "OpenAI API key not found"
1. Make sure you've set the `OPENAI_API_KEY` environment variable
2. Restart your terminal/IDE after setting the variable
3. Verify the key is valid on [OpenAI Platform](https://platform.openai.com)

### "Stock symbol not found"
1. Verify the symbol is correct (e.g., AAPL not Apple)
2. Check if it's a valid ticker on major exchanges
3. Try searching on [Yahoo Finance](https://finance.yahoo.com) first

### "Rate limit reached"
1. Wait a few minutes before trying again
2. Check your OpenAI usage limits
3. Consider upgrading your OpenAI plan

### Charts not displaying
1. Ensure Plotly is installed: `pip install plotly --upgrade`
2. Clear your browser cache
3. Try a different browser

## Development

### Project Structure
```
agents-test/
├── streamlit_app.py    # Main Streamlit web application
├── main.py             # CLI version
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

### Key Functions
- `validate_stock_symbol()`: Input validation
- `validate_openai_api_key()`: API key verification
- `get_stock_info()`: Fetch stock data (cached)
- `get_stock_history()`: Fetch historical data (cached)
- `analyze_stock_with_gpt()`: AI analysis (cached)
- `format_currency()`, `format_number()`, `format_percentage()`: Safe formatters

## License

MIT License - feel free to use, modify, and distribute as needed.

## Disclaimer

⚠️ **Important**: This tool is for informational and educational purposes only. It does not constitute financial advice. The AI analysis should not be the sole basis for investment decisions. Always do your own research and consult with a qualified financial advisor before making any investment decisions.

Stock market investments carry risk, including the potential loss of principal.

## Support

For issues, questions, or contributions, please open an issue or submit a pull request.

---

Built with ❤️ using Streamlit and OpenAI


