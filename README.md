# TickerTrace 📈

A dynamic stock and ETF tracker built with Python, Flask, and Jinja2, utilizing the yfinance API for real-time market data.

![TickerTrace Homepage](https://github.com/user-attachments/assets/748140ab-adcb-404a-842d-4d265570dbff)

## Features

- **Real-time Stock Data**: Get up-to-date stock prices and market information powered by yfinance API
- **Historical Charts**: View 30-day price history and trends for any stock or ETF with interactive Chart.js visualizations
- **Comprehensive Information**: Access detailed information including:
  - Current price and price changes
  - Market cap, P/E ratio, and dividend yield
  - 52-week high/low prices
  - Sector and industry classification
  - Trading volume and daily price ranges
- **RESTful API**: JSON API endpoint for programmatic access to stock quotes
- **Responsive Design**: Beautiful gradient UI that works on desktop and mobile devices
- **Error Handling**: Graceful error handling for invalid tickers and API issues

## Technologies Used

- **Backend**: Python 3.x, Flask 3.0.0
- **Data Source**: yfinance 0.2.37 (Yahoo Finance API)
- **Frontend**: Jinja2 templates, HTML5, CSS3
- **Visualization**: Chart.js 4.4.0
- **Data Processing**: pandas 2.2.0

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Lenfried/tickertrace.git
cd tickertrace
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

1. Start the Flask development server:
```bash
python app.py
```

By default, the application runs on `http://127.0.0.1:5000` in production mode. 

2. For development with debug mode, set environment variables:
```bash
export FLASK_DEBUG=true
export FLASK_HOST=0.0.0.0
export FLASK_PORT=5000
python app.py
```

Or on Windows:
```cmd
set FLASK_DEBUG=true
set FLASK_HOST=0.0.0.0
set FLASK_PORT=5000
python app.py
```

3. Open your web browser and navigate to:
```
http://localhost:5000
```

4. Enter a stock ticker symbol (e.g., AAPL, GOOGL, TSLA) or ETF symbol (e.g., SPY, QQQ) in the search box and click "Search"

### API Usage

You can also access stock data programmatically via the REST API:

```bash
curl http://localhost:5000/api/quote/AAPL
```

Response format:
```json
{
  "symbol": "AAPL",
  "name": "Apple Inc.",
  "price": 150.25,
  "change": 2.35,
  "changePercent": 1.59
}
```

## Project Structure

```
tickertrace/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/            # Jinja2 HTML templates
│   ├── base.html        # Base template with common layout
│   ├── index.html       # Home page with search form
│   └── result.html      # Stock details page
└── static/              # Static assets (CSS, JS, images)
```

## Example Searches

Try searching for these popular tickers:

### Stocks
- **AAPL** - Apple Inc.
- **GOOGL** - Alphabet Inc. (Google)
- **MSFT** - Microsoft Corporation
- **TSLA** - Tesla Inc.
- **AMZN** - Amazon.com Inc.

### ETFs
- **SPY** - SPDR S&P 500 ETF Trust
- **QQQ** - Invesco QQQ Trust (Nasdaq-100)
- **VTI** - Vanguard Total Stock Market ETF
- **IWM** - iShares Russell 2000 ETF

## Development

### Environment Variables

The application supports the following environment variables for configuration:

- `FLASK_DEBUG`: Set to `true` to enable debug mode (default: `false`)
- `FLASK_HOST`: Host to bind the server to (default: `127.0.0.1`)
- `FLASK_PORT`: Port to run the server on (default: `5000`)

You can copy `.env.example` to `.env` and modify the values as needed. Note that `.env` files are gitignored for security.

```bash
cp .env.example .env
# Edit .env with your preferred settings
```

### Running in Debug Mode

For development, you can enable debug mode which provides:
- Auto-reloading when code changes
- Detailed error pages
- Debug toolbar

To enable debug mode:
```bash
export FLASK_DEBUG=true
python app.py
```

### Production Deployment

For production deployment:
- Keep `FLASK_DEBUG` unset or set to `false`
- Use a production WSGI server like Gunicorn or uWSGI
- Set appropriate host/port via environment variables
- Consider using a reverse proxy like Nginx

### Customization

You can customize the application by:
- Modifying the CSS in `templates/base.html`
- Adjusting the historical data range in `app.py` (default: 30 days)
- Adding more stock metrics in the `search()` function
- Extending the API with additional endpoints

## Troubleshooting

### Common Issues

**Issue**: "Error fetching data" when searching for a ticker
- **Solution**: Check your internet connection. The yfinance library requires internet access to fetch data from Yahoo Finance.

**Issue**: Invalid ticker symbol error
- **Solution**: Verify the ticker symbol is correct. Use the official symbol from stock exchanges (e.g., AAPL for Apple, not APPLE).

**Issue**: Port 5000 already in use
- **Solution**: Change the port in `app.py` or stop the process using port 5000:
```bash
# Find and kill process on port 5000
lsof -ti:5000 | xargs kill -9
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Data provided by [Yahoo Finance](https://finance.yahoo.com/) via the yfinance library
- Chart visualization powered by [Chart.js](https://www.chartjs.org/)
- Built with [Flask](https://flask.palletsprojects.com/)
