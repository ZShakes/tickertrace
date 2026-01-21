import yfinance as yf
import requests
from typing import Dict, List, Any, Optional
import datetime


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
	  - raw_info: small subset of ticker.info for debugging (can be empty)

	Notes:
	  - yfinance does not require an API key.
	  - Values can be None if data is missing from Yahoo.
	"""
	symbol = symbol.upper().strip()
	t = yf.Ticker(symbol)

	# Try the faster fast_info first, then fall back to info/history
	fast = getattr(t, "fast_info", {}) or {}
	info = getattr(t, "info", {}) or {}

	# company name
	name = info.get("shortName") or info.get("longName") or symbol

	market_price = _safe_float(fast.get("last_price") or info.get("currentPrice"))
	previous_close = _safe_float(fast.get("previous_close") or info.get("previousClose") or info.get("regularMarketPreviousClose"))

	# If market_price is still None, attempt to get last Close from history
	if market_price is None:
		try:
			hist = t.history(period="2d", interval="1d")
			if not hist.empty:
				market_price = _safe_float(hist['Close'].iloc[-1])
				if previous_close is None and len(hist['Close']) > 1:
					previous_close = _safe_float(hist['Close'].iloc[-2])
		except Exception:
			pass

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
	raw_info = {
		'exchange': info.get('exchange') or info.get('exchangeName'),
		'currency': info.get('currency') or fast.get('currency'),
	}

	return {
		'symbol': symbol,
		'name': name,
		'market_price': market_price,
		'previous_close': previous_close,
		'change': _safe_float(change) if change is not None else None,
		'change_percent': _safe_float(change_percent) if change_percent is not None else None,
		'direction': direction,
		'raw_info': raw_info,
	}


def get_historical_series(symbol: str, period: str = "1mo", interval: str = "1d") -> List[Dict[str, Any]]:
	"""Return historical data points for plotting.

	Each point is a dict: {"timestamp": ISO8601 string, "close": float}

	period examples: '1d','5d','1mo','3mo','1y','5y'
	interval examples: '1m','5m','1d','1wk','1mo'
	Note: intraday ('1m') may be limited to recent data.
	"""
	symbol = symbol.upper().strip()
	t = yf.Ticker(symbol)
	points: List[Dict[str, Any]] = []
	try:
		hist = t.history(period=period, interval=interval)
		if hist.empty:
			return points
		# hist.index may be DatetimeIndex
		for idx, row in hist.iterrows():
			# handle pandas Timestamp
			ts = None
			if hasattr(idx, 'to_pydatetime'):
				ts = idx.to_pydatetime()
			elif isinstance(idx, (int, float)):
				ts = datetime.datetime.fromtimestamp(idx)
			else:
				# fallback
				try:
					ts = datetime.datetime.fromisoformat(str(idx))
				except Exception:
					ts = None

			close = _safe_float(row.get('Close') if isinstance(row, dict) else row.Close)
			if ts is not None and close is not None:
				points.append({'timestamp': ts.isoformat(), 'close': close})
	except Exception:
		# on errors, return empty list (caller should handle)
		return []

	return points


def get_ticker_payload(symbol: str, period: str = "1mo", interval: str = "1d") -> Dict[str, Any]:
	"""Combined payload: summary + series for frontend consumption."""
	summary = get_ticker_summary(symbol)
	series = get_historical_series(symbol, period=period, interval=interval)
	return {
		'summary': summary,
		'series': series,
	}


if __name__ == '__main__':
	# Quick local test when running the module directly
	import json

	examples = ['AAPL', 'DIS', 'NKE']
	for s in examples:
		print(f"--- {s} ---")
		payload = get_ticker_payload(s, period='1mo', interval='1d')
		print(json.dumps(payload['summary'], indent=2))
		print(f"points: {len(payload['series'])}\n")