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
