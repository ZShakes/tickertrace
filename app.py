from flask import Flask, render_template, request, jsonify, send_file
import external_api
import csv
import io
from datetime import datetime

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
    """API endpoint for frontend to get ticker summary only."""
    symbol = request.args.get('symbol', '').strip()
    if not symbol:
        return jsonify({'error': 'missing symbol parameter'}), 400

    summary = external_api.get_ticker_summary(symbol)
    return jsonify({'summary': summary})


@app.route('/track', methods=['POST'])
def track():
    """Handle submitted tickers, fetch summary data, and render results."""
    stocks = []
    errors = []

    # Read up to 5 entries from the submitted form
    for i in range(1, 6):
        ticker = request.form.get(f'ticker{i}', '').strip().upper()
        shares_raw = request.form.get(f'shares{i}', '').strip()

        if not ticker or not shares_raw:
            continue

        try:
            shares = float(shares_raw)
        except ValueError:
            errors.append(f'{ticker}: Invalid share quantity')
            continue

        summary = external_api.get_ticker_summary(ticker)
        
        # Check for API errors
        if summary.get('error'):
            errors.append(f'{ticker}: {summary.get("error")}')
            continue
        
        is_valid = summary.get('market_price') is not None
        if not is_valid:
            errors.append(f'{ticker}: No price data available')
            continue

        company_name = summary.get('name') or ticker
        current_price = summary.get('market_price') or 0.0
        price_change_usd = summary.get('change') or 0.0
        percentage_change = summary.get('change_percent') or 0.0

        total_value = shares * current_price

        stocks.append({
            'ticker': ticker,
            'shares': shares,
            'company_name': company_name,
            'current_price': current_price,
            'percentage_change': percentage_change,
            'price_change_usd': price_change_usd,
            'total_value': total_value,
            'portfolio_percentage': 0.0,
            'is_valid': True
        })

    total_portfolio_value = sum(s['total_value'] for s in stocks)
    if total_portfolio_value > 0:
        for s in stocks:
            s['portfolio_percentage'] = (s['total_value'] / total_portfolio_value) * 100

    return render_template('results.html', stocks=stocks, total_portfolio_value=total_portfolio_value, errors=errors)


@app.route('/download-csv', methods=['POST'])
def download_csv():
    """Generate and download portfolio results as CSV."""
    data = request.get_json()
    stocks = data.get('stocks', [])
    total_value = data.get('total_portfolio_value', 0)
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Ticker', 'Company Name', 'Shares', 'Current Price', 'Daily Change %', 'Daily Change $', 'Total Value', 'Portfolio %'])
    
    # Write stock data
    for stock in stocks:
        writer.writerow([
            stock['ticker'],
            stock['company_name'],
            f"{stock['shares']:.2f}",
            f"${stock['current_price']:.2f}",
            f"{stock['percentage_change']:.2f}%",
            f"${stock['price_change_usd']:.2f}",
            f"${stock['total_value']:.2f}",
            f"{stock['portfolio_percentage']:.2f}%"
        ])
    
    # Add total row
    writer.writerow([])
    writer.writerow(['TOTAL', '', '', '', '', '', f"${total_value:.2f}", '100.00%'])
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'portfolio_{timestamp}.csv'
    
    # Convert to bytes
    output.seek(0)
    csv_bytes = io.BytesIO(output.getvalue().encode('utf-8'))
    
    return send_file(
        csv_bytes,
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )


if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)

