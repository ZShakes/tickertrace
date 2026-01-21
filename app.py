from flask import Flask, render_template, request
import external_api

app = Flask(__name__)

@app.route('/')
def index():
    # Render the main index page with the stock input form.
    return render_template('index.html')

@app.route('/track', methods=['POST'])
def track():
    """Handle submitted tickers, fetch data server-side and render results.

    For each form row we expect `tickerN` and `sharesN` where N in 1..5.
    We call external_api.get_ticker_summary(symbol) for each provided ticker
    and compute total values and portfolio percentages.
    """
    stocks = []

    # Read up to 5 entries from the submitted form
    for i in range(1, 6):
        ticker = request.form.get(f'ticker{i}', '').strip().upper()
        shares_raw = request.form.get(f'shares{i}', '').strip()

        if not ticker or not shares_raw:
            continue

        try:
            shares = float(shares_raw)
        except ValueError:
            # invalid shares entry — skip this row
            continue

        # Fetch ticker summary from external_api (synchronous, server-side)
        summary = external_api.get_ticker_summary(ticker)

         #Data level validation
        is_valid = summary.get('market_price') is not None

        if not is_valid:
            continue

        company_name = summary.get('name') or ticker
        current_price = summary.get('market_price') or 0.0
        price_change_usd = summary.get('change') or 0.0
        percentage_change = summary.get('change_percent') or 0.0

        total_value = shares * current_price if is_valid else 0.0

        stocks.append({
            'ticker': ticker,
            'shares': shares,
            'company_name': company_name,
            'current_price': current_price,
            'percentage_change': percentage_change,
            'price_change_usd': price_change_usd,
            'total_value': total_value,
            'portfolio_percentage': 0.0,  # computed after total
            'is_valid': is_valid
        })

    # Compute portfolio totals and percentages
    total_portfolio_value = sum(s['total_value'] for s in stocks if s['is_valid'])
    if total_portfolio_value > 0:
        for s in stocks:
            if s['is_valid']:
                s['portfolio_percentage'] = (s['total_value'] / total_portfolio_value) * 100

    # Render server-side only results page (no JS)
    return render_template('results.html', stocks=stocks, total_portfolio_value=total_portfolio_value)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
from flask import Flask, render_template, request, jsonify
import external_api

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('home_page.html')


@app.route('/tracker')
def tracker():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/api/ticker')
def api_ticker():
    """API endpoint for frontend to get ticker summary + series.

    Query params:
      - symbol (required): ticker symbol, e.g. AAPL
      - period (optional): yfinance period, default '1mo'
      - interval (optional): yfinance interval, default '1d'
    """
    symbol = request.args.get('symbol', '').strip()
    if not symbol:
        return jsonify({'error': 'missing symbol parameter'}), 400

    period = request.args.get('period', '1mo')
    interval = request.args.get('interval', '1d')

    payload = external_api.get_ticker_payload(symbol, period=period, interval=interval)
    return jsonify(payload)


@app.route('/track', methods=['POST'])
def track():
    # Get ticker and shares data from form
    stocks = []
    
    for i in range(1, 6):
        ticker = request.form.get(f'ticker{i}', '').strip().upper()
        shares = request.form.get(f'shares{i}', '')
        
        if ticker and shares:
            try:
                shares = float(shares)
                stocks.append({
                    'ticker': ticker,
                    'shares': shares,
                    'company_name': 'Company Name',  # Get from API
                    'current_price': 0.00,  # Get from API
                    'percentage_change': 0.00,  # Get from API
                    'price_change_usd': 0.00,  # Get from API
                    'total_value': shares * 0.00,  # Calculate
                    'portfolio_percentage': 0.00  # Calculate
                })
            except ValueError:
                pass
    
    total_portfolio_value = sum(stock['total_value'] for stock in stocks)
    
    # Calculate portfolio percentages
    if total_portfolio_value > 0:
        for stock in stocks:
            stock['portfolio_percentage'] = (stock['total_value'] / total_portfolio_value) * 100
    
    return render_template('results.html', stocks=stocks, total_portfolio_value=total_portfolio_value)


if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)
