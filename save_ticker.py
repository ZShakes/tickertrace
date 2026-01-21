"""Simple helpers to fetch ticker data (yfinance) and save to a .txt file.

This is a lighter, more readable version with short, one-line comments.
Requires: pip install yfinance pandas
"""

import os
from datetime import datetime

try:
    import yfinance as yf
    import pandas as pd
except Exception:
    yf = None
    pd = None


def get_ticker_summary(symbol, period="1mo", interval="1d"):
    """Fetch summary for `symbol` and return a simple dict.

    Returned dict contains:
    - symbol: string ticker
    - company: shortName or longName if available
    - last_price: most recent price (float) or None
    - previous_close: previous close price or None
    - change: last_price - previous_close (float) or None
    - change_pct: percent change (float) or None
    - direction: one of "up", "down", "flat", or None
    - history: list of {timestamp_iso: str, close: float} ordered oldest -> newest

    Raises ImportError if `yfinance` is not installed.
    """
    # require yfinance/pandas
    if yf is None or pd is None:
        raise ImportError("yfinance and pandas are required: pip install yfinance pandas")

    # create ticker object
    ticker = yf.Ticker(symbol)

    # read fast_info and fallback to info
    try:
        fast = getattr(ticker, "fast_info", {}) or {}
    except Exception:
        fast = {}
    try:
        info = getattr(ticker, "info", {}) or {}
    except Exception:
        info = {}

    # company display name
    company = info.get("shortName") or info.get("longName") or symbol

    # try lightweight sources for prices
    last_price = fast.get("last_price") or info.get("currentPrice")
    previous_close = fast.get("previous_close") or info.get("previousClose")

    # fetch history for plotting and fallback prices
    try:
        hist = ticker.history(period=period, interval=interval)
    except Exception:
        hist = pd.DataFrame()

    # If history present use it to derive prices when missing
    if (last_price is None or previous_close is None) and not hist.empty:
        # Ensure 'Close' column exists
        if "Close" in hist.columns:
            closes = hist["Close"].dropna()
            if not closes.empty:
                if last_price is None:
                    last_price = float(closes.iloc[-1])
                if previous_close is None and len(closes) >= 2:
                    previous_close = float(closes.iloc[-2])

    # compute change and direction
    change = None
    change_pct = None
    direction = None
    try:
        if last_price is not None and previous_close is not None:
            change = float(last_price) - float(previous_close)
            change_pct = (change / float(previous_close)) * 100 if previous_close != 0 else None
            direction = "up" if change > 0 else ("down" if change < 0 else "flat")
    except Exception:
        change = None
        change_pct = None
        direction = None

    # Prepare history points for frontend plotting (ISO timestamp + close price)
    # build simple history list for frontend: [{timestamp, close}, ...]
    history_points = []
    if not hist.empty and "Close" in hist.columns:
        df = hist.reset_index()
        # determine which column holds the datetime
        date_col = None
        for possible in ("Date", "Datetime"):
            if possible in df.columns:
                date_col = possible
                break
        if date_col is None and not df.empty:
            date_col = df.columns[0]

        for _, row in df.iterrows():
            try:
                dt = row[date_col]
                ts_iso = pd.Timestamp(dt).isoformat()
                close = row.get("Close")
                if pd.isna(close):
                    continue
                history_points.append({"timestamp": ts_iso, "close": float(close)})
            except Exception:
                continue

    # return plain dict values
    return {
        "symbol": symbol,
        "company": company,
        "last_price": float(last_price) if last_price is not None else None,
        "previous_close": float(previous_close) if previous_close is not None else None,
        "change": float(change) if change is not None else None,
        "change_pct": float(change_pct) if change_pct is not None else None,
        "direction": direction,
        "history": history_points,
    }


def save_ticker_to_txt(symbol, filepath=None, period="1mo", interval="1d"):
    """Fetch summary and write a readable .txt; returns absolute path written."""
    # get the structured summary
    summary = get_ticker_summary(symbol, period=period, interval=interval)

    # default filename in cwd when no path provided
    if filepath is None:
        now = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        filename = "%s_%s.txt" % (symbol.upper(), now)
        filepath = os.path.join(os.getcwd(), filename)

    # assemble text content lines
    lines = []
    lines.append("Symbol: %s" % summary.get("symbol"))
    lines.append("Company: %s" % summary.get("company"))
    lp = summary.get("last_price")
    pc = summary.get("previous_close")
    lines.append("Last price: %s" % (lp if lp is not None else "N/A"))
    lines.append("Previous close: %s" % (pc if pc is not None else "N/A"))

    # show change and percent
    ch = summary.get("change")
    chp = summary.get("change_pct")
    if ch is not None and chp is not None:
        sign = "+" if ch > 0 else ("-" if ch < 0 else "")
        lines.append("Change: %s%.4f (%s%.2f%%)" % (sign, abs(ch), sign, abs(chp)))
    else:
        lines.append("Change: N/A")

    # direction arrow text
    direction = summary.get("direction") or "N/A"
    lines.append("Direction: %s" % direction)

    lines.append("")
    lines.append("History (ISO timestamp, close):")
    for point in summary.get("history", []):
        lines.append("%s, %s" % (point["timestamp"], point["close"]))

    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return os.path.abspath(filepath)


if __name__ == "__main__":
    # Simple CLI: python save_ticker.py AAPL
    import sys

    if len(sys.argv) < 2:
        print("Usage: python save_ticker.py <TICKER> [output_filepath]")
        sys.exit(2)

    sym = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None
    try:
        path = save_ticker_to_txt(sym, filepath=out)
        print(f"Saved ticker summary to: {path}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
