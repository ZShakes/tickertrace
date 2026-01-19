from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

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
