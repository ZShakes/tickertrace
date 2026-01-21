# TickerTrace
TickerTrace is a dynamic stock and ETF tracking application buit with Python, Flask, and Jinja2. It uses the yfinance API to retrieve real time market data and present stock prices and portfolio information through a simple web interface.

# Problem the App solves
Many users want an easy way to track the value of multiple stocks they own without using complex financial paltforms. This applicaton helps users calculate their total portfolio value by allowing them to enter stock ticker symbols and the number of shares they own. The application then displays real time price data and portfolio brakdowns in a clear interface.  

# Features overview
- Supports input of up to five stock ticker symbols
- Allows users to enter the number of shares owned for each stock
- Displays current stock price and daily price change 
- Calculate total value per stock and overall portfolio value
- Retrieves real time market data using API
- Clean, card based user interface for easy readability

# Setup Instructions 
1. Clone the repository from GitHub
2. Ensure python3 is installed on your system 
3. Install the required dependencies using 'pip'

# Data source 
Market data is retrieved using the [yfinance API](https://pypi.org/project/yfinance/)
