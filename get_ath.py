import requests
from dotenv import load_dotenv
import os
import argparse

def valid_date(date_string: str):
    if not date_string:
        return "none"
    try:
        # Split the date string
        year, month, day = map(int, date_string.split('-'))
        
        # Basic validation
        if not (1900 <= year <= 2100):
            raise ValueError("Year must be between 1900 and 2100")
        if not (1 <= month <= 12):
            raise ValueError("Month must be between 1 and 12")
        if not (1 <= day <= 31):
            raise ValueError("Day must be between 1 and 31")
            
        # Format the date back to string
        return f"{year:04d}-{month:02d}-{day:02d}"
    except (ValueError, TypeError):
        msg = f"'{date_string}' is not a valid date in YYYY-MM-DD format"
        raise argparse.ArgumentTypeError(msg)

parser = argparse.ArgumentParser()

parser.add_argument('symbol', type=str, help='Stock symbol (e.g., AAPL)')
parser.add_argument('--eod', type=valid_date, help='End of date (e.g., 2025-02-14)', default="")

load_dotenv()

ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_KEY')
if not ALPHA_VANTAGE_KEY:
    raise ValueError("ALPHA_VANTAGE_KEY not found in environment variables")

def main():
    args: argparse.Namespace = parser.parse_args()
    symbol = args.symbol
    eod = args.eod
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={ALPHA_VANTAGE_KEY}"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()

        time_series_daily: dict = data["Time Series (Daily)"]
        high_prices = []
        for date, daily_data in time_series_daily.items():
            high_price = float(daily_data['2. high'])
            high_prices.append((date, high_price))
        high_prices = high_prices[::-1]

        curr_ath = 0
        total_ath = 0
        for date, high_price in high_prices:
            if eod != "none" and date > eod:
                break
            if high_price > curr_ath:
                curr_ath = high_price
                total_ath += 1
                print(f"Date: {date}, All-time high: {curr_ath}")
        if eod == "none":
            print(f"All-time highs for {symbol} from {high_prices[0][0]} to {high_prices[-1][0]}")
        else:
            print(f"All-time highs for {symbol} from {high_prices[0][0]} to {eod}")
        print(f"Total number of all-time highs: {total_ath}")
    else:
        print(f"Error: {response.status_code}")

if __name__ == "__main__":
    main()