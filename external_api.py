import yfinance as yf
from typing import Dict, Any, Optional
import time
import threading

_rate_lock = threading.Lock()
_last_call_ts = 0.0
_min_interval = 0.5  # seconds between outbound Yahoo calls


def _throttle():
    global _last_call_ts
    with _rate_lock:
        now = time.monotonic()
        wait_for = _min_interval - (now - _last_call_ts)
        if wait_for > 0:
            time.sleep(wait_for)
            now = time.monotonic()
        _last_call_ts = now

def _safe_float(x) -> Optional[float]:
	try:
		return float(x)
	except Exception:
		return None


def get_ticker_summary(symbol: str) -> Dict[str, Any]:
	"""Return a JSON-serializable summary for a ticker symbol.

	Returned fields:
	  - symbol: requested ticker
	  - name: company short or long name (best-effort)
	  - market_price: current/latest market price (float) or None
	  - previous_close: previous close price (float) or None
	  - change: market_price - previous_close (float) or None
	  - change_percent: percent change (float) or None
	  - direction: 'up' | 'down' | 'flat' | 'unknown'
	  - error: error message if API call failed (str) or None
	  - raw_info: small subset of ticker.info for debugging (can be empty)

	Notes:
	  - yfinance does not require an API key.
	  - Values can be None if data is missing from Yahoo.
	"""
	symbol = symbol.upper().strip()
	_throttle()
	
	try:
		t = yf.Ticker(symbol)
		fast = t.fast_info

		# company name
		name = symbol

		# Try multiple price sources - fast_info keys vary
		market_price = _safe_float(fast.get("last_price")) or \
		               _safe_float(fast.get("regularMarketPrice")) or \
		               _safe_float(fast.get("currentPrice"))
		
		previous_close = _safe_float(fast.get("previous_close")) or \
		                 _safe_float(fast.get("regularMarketPreviousClose")) or \
		                 _safe_float(fast.get("previousClose"))
		
		# Fallback to history if fast_info doesn't have the data
		if market_price is None or previous_close is None:
			hist = t.history(period="2d", interval="1d")
			if not hist.empty:
				if market_price is None and 'Close' in hist.columns:
					market_price = _safe_float(hist['Close'].iloc[-1])
				if previous_close is None and len(hist) > 1 and 'Close' in hist.columns:
					previous_close = _safe_float(hist['Close'].iloc[-2])
	except Exception as e:
		# Handle network errors, 429 rate limits, invalid tickers, etc.
		error_msg = str(e)
		if '429' in error_msg or 'Too Many Requests' in error_msg:
			error_msg = 'Rate limited by Yahoo Finance. Please wait and try again.'
		elif 'No data found' in error_msg or 'not found' in error_msg.lower():
			error_msg = f'Ticker "{symbol}" not found.'
		else:
			error_msg = f'Unable to fetch data: {error_msg[:100]}'
		
		return {
			'symbol': symbol,
			'name': symbol,
			'market_price': None,
			'previous_close': None,
			'change': None,
			'change_percent': None,
			'direction': 'unknown',
			'error': error_msg,
			'raw_info': {},
		}


	change = None
	change_percent = None
	direction = "unknown"

	if market_price is not None and previous_close is not None:
		try:
			change = market_price - previous_close
			if previous_close != 0:
				change_percent = (change / previous_close) * 100
			if change > 0:
				direction = "up"
			elif change < 0:
				direction = "down"
			else:
				direction = "flat"
		except Exception:
			pass

	# Provide a tiny slice of info for debugging without returning huge blobs
	raw_info = {}
	try:
		raw_info['exchange'] = fast.get('exchange')
		raw_info['currency'] = fast.get('currency')
	except Exception:
		# Accessing fast_info properties can fail if Yahoo response is missing keys
		pass

	return {
		'symbol': symbol,
		'name': name,
		'market_price': market_price,
		'previous_close': previous_close,
		'change': _safe_float(change) if change is not None else None,
		'change_percent': _safe_float(change_percent) if change_percent is not None else None,
		'direction': direction,
		'error': None,
		'raw_info': raw_info,
	}


def get_ticker_payload(symbol: str) -> Dict[str, Any]:
	"""Legacy helper retained for compatibility; returns only summary now."""
	return {'summary': get_ticker_summary(symbol)}


if __name__ == '__main__':
	# Quick local test when running the module directly
	import json

	examples = ['AAPL', 'DIS', 'NKE']
	for s in examples:
		print(f"--- {s} ---")
		summary = get_ticker_summary(s)
		print(json.dumps(summary, indent=2))