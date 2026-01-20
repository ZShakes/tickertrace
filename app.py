from flask import Flask, render_template, request, jsonify
import external_api

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


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


if __name__ == "__main__":
    app.run(debug=True)