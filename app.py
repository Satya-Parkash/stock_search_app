import matplotlib
matplotlib.use('Agg')  # Headless backend

from flask import Flask, render_template, request
import yfinance as yf
import mplfinance as mpf
from datetime import datetime

app = Flask(__name__)

# Companies grouped by region
COMPANIES = {
    "US": {
        "Apple": "AAPL",
        "Tesla": "TSLA",
        "Google": "GOOGL",
        "Amazon": "AMZN",
        "Microsoft": "MSFT",
        "Facebook / Meta": "META",
        "Netflix": "NFLX",
        "Nvidia": "NVDA",
        "Intel": "INTC",
        "Adobe": "ADBE",
        "Paypal": "PYPL",
        "Disney": "DIS",
        "Spotify": "SPOT",
        "Zoom": "ZM"
    },
    "India": {
        "Tata Consultancy Services": "TCS.NS",
        "Tata Motors": "TATAMOTORS.NS",
        "Reliance Industries": "RELIANCE.NS",
        "Infosys": "INFY.NS",
        "HDFC Bank": "HDFCBANK.NS",
        "ICICI Bank": "ICICIBANK.NS",
        "State Bank of India": "SBIN.NS",
        "Larsen & Toubro": "LT.NS",
        "Maruti Suzuki": "MARUTI.NS",
        "Mahindra & Mahindra": "M&M.NS"
    },
    "Global": {
        "Samsung Electronics": "005930.KS",
        "Toyota": "7203.T",
        "Sony": "6758.T",
        "Alibaba": "BABA",
        "Baidu": "BIDU"
    }
}

def get_symbol(name):
    for region in COMPANIES.values():
        if name in region:
            return region[name]
    return name.upper()

@app.route("/", methods=["GET", "POST"])
def index():
    stock_data = None
    error = None
    selected_company = None

    if request.method == "POST":
        selected_company = request.form.get("selected_company")
        search_trigger = request.form.get("search_trigger")

        if search_trigger and selected_company:
            symbol = get_symbol(selected_company)
            try:
                stock = yf.Ticker(symbol)
                info = stock.info
                current_price = info.get("currentPrice")
                previous_close = info.get("previousClose")
                day_high = info.get("dayHigh")
                day_low = info.get("dayLow")
                full_name = info.get("longName", symbol)

                # Calculate percentage change
                if current_price and previous_close:
                    percent_change = round((current_price - previous_close) / previous_close * 100, 2)
                else:
                    percent_change = None

                # Historical data
                hist = stock.history(period="1mo")
                if hist.empty:
                    error = "Historical data not available."
                else:
                    chart_path = "static/candle.png"
                    mpf.plot(
                        hist,
                        type='candle',
                        style='charles',
                        title=f"{full_name} Candlestick Chart",
                        ylabel='Price',
                        savefig=chart_path
                    )

                    stock_data = {
                        "name": full_name,
                        "symbol": symbol,
                        "price": current_price,
                        "high": day_high,
                        "low": day_low,
                        "percent_change": percent_change,
                        "chart": chart_path,
                        "last_updated": datetime.now().strftime("%d %b %Y %H:%M:%S")
                    }

            except Exception as e:
                print("Error:", e)
                error = "Stock not found or API error."

    return render_template(
        "index.html",
        stock_data=stock_data,
        error=error,
        companies=COMPANIES,
        selected_company=selected_company
    )

if __name__ == "__main__":
    app.run(debug=True)