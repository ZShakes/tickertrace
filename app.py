from flask import Flask, render_template, request, jsonify
import yfinance as yf
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    """Search for stock or ETF information"""
    ticker_symbol = request.form.get('ticker', '').upper().strip()
    
    if not ticker_symbol:
        return render_template('index.html', error='Please enter a ticker symbol')
    
    try:
        # Fetch stock data using yfinance
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        
        # Get historical data for the last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        hist = ticker.history(start=start_date, end=end_date)
        
        # Check if ticker is valid
        if not info or 'symbol' not in info:
            return render_template('index.html', error=f'Invalid ticker symbol: {ticker_symbol}')
        
        # Prepare stock data
        stock_data = {
            'symbol': info.get('symbol', ticker_symbol),
            'name': info.get('longName', info.get('shortName', 'N/A')),
            'current_price': info.get('currentPrice', info.get('regularMarketPrice', 'N/A')),
            'previous_close': info.get('previousClose', 'N/A'),
            'open': info.get('open', info.get('regularMarketOpen', 'N/A')),
            'day_high': info.get('dayHigh', info.get('regularMarketDayHigh', 'N/A')),
            'day_low': info.get('dayLow', info.get('regularMarketDayLow', 'N/A')),
            'volume': info.get('volume', info.get('regularMarketVolume', 'N/A')),
            'market_cap': info.get('marketCap', 'N/A'),
            'pe_ratio': info.get('trailingPE', 'N/A'),
            'dividend_yield': info.get('dividendYield', 'N/A'),
            'week_52_high': info.get('fiftyTwoWeekHigh', 'N/A'),
            'week_52_low': info.get('fiftyTwoWeekLow', 'N/A'),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'type': info.get('quoteType', 'EQUITY')
        }
        
        # Calculate change
        if stock_data['current_price'] != 'N/A' and stock_data['previous_close'] != 'N/A':
            change = stock_data['current_price'] - stock_data['previous_close']
            change_percent = (change / stock_data['previous_close']) * 100
            stock_data['change'] = change
            stock_data['change_percent'] = change_percent
        else:
            stock_data['change'] = 'N/A'
            stock_data['change_percent'] = 'N/A'
        
        # Prepare historical data for chart
        historical_data = []
        if not hist.empty:
            for date, row in hist.iterrows():
                historical_data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'close': round(row['Close'], 2)
                })
        
        return render_template('result.html', 
                             stock=stock_data, 
                             historical_data=historical_data)
    
    except Exception as e:
        return render_template('index.html', 
                             error=f'Error fetching data for {ticker_symbol}: {str(e)}')

@app.route('/api/quote/<ticker>')
def api_quote(ticker):
    """API endpoint for getting real-time quote"""
    try:
        ticker_obj = yf.Ticker(ticker.upper())
        info = ticker_obj.info
        
        if not info or 'symbol' not in info:
            return jsonify({'error': 'Invalid ticker symbol'}), 404
        
        return jsonify({
            'symbol': info.get('symbol', ticker.upper()),
            'name': info.get('longName', info.get('shortName', 'N/A')),
            'price': info.get('currentPrice', info.get('regularMarketPrice', 'N/A')),
            'change': info.get('regularMarketChange', 'N/A'),
            'changePercent': info.get('regularMarketChangePercent', 'N/A')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', '5000'))
    app.run(debug=debug_mode, host=host, port=port)