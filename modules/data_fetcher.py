import os
import pandas as pd
from twelvedata import TDClient

# Force column order
forced_columns = ['Date', 'Close', 'High', 'Low', 'Open', 'Volume', 'RSI', '20DMA', '50DMA']

# Your Twelve Data API key
API_KEY = ""  # 🔁 Replace this with your actual API key

# Initialize Twelve Data client
td = TDClient(apikey=API_KEY)

# Ensure data folder exists
os.makedirs("data", exist_ok=True)

def compute_indicators(df):
    df = df.copy()

    # Convert Date to datetime if not already
    df['Date'] = pd.to_datetime(df['Date'])

    # RSI (14)
    delta = df['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # 20-day and 50-day moving averages
    df['20DMA'] = df['Close'].rolling(window=20).mean()
    df['50DMA'] = df['Close'].rolling(window=50).mean()

    return df

def fetch_and_clean_data(tickers):
    cleaned_data = {}

    for ticker in tickers:
        csv_path = f"data/{ticker.replace('.', '_')}_cleaned.csv"

        # ✅ If file exists locally, load it
        if os.path.exists(csv_path):
            print(f"📂 Loading cached data for {ticker}")
            df = pd.read_csv(csv_path)
            df['Date'] = pd.to_datetime(df['Date'])
            cleaned_data[ticker] = df
            continue

        print(f"\n🌐 Fetching from API: {ticker}")

        try:
            # Fetch daily OHLCV data from API
            response = td.time_series(
                symbol=ticker,
                interval="1day",
                outputsize=200,
                order="ASC"
            ).as_pandas()

            if response is None or response.empty:
                print(f"❌ No data returned for {ticker}")
                continue

            # Format and rename columns
            df = response.reset_index()
            df.rename(columns={
                'datetime': 'Date',
                'close': 'Close',
                'high': 'High',
                'low': 'Low',
                'open': 'Open',
                'volume': 'Volume'
            }, inplace=True)

            df = df[['Date', 'Close', 'High', 'Low', 'Open', 'Volume']]
            df = df.sort_values(by='Date').reset_index(drop=True)

            # Compute RSI and DMA indicators
            df = compute_indicators(df)

            # Drop rows with missing key values
            df.dropna(subset=['Date', 'Close'], inplace=True)
            df = df[forced_columns]
            df.reset_index(drop=True, inplace=True)

            # Save to CSV for future reuse
            df.to_csv(csv_path, index=False)
            print(f"✅ Saved {ticker} to {csv_path}")

            cleaned_data[ticker] = df

        except Exception as e:
            print(f"❌ Error fetching data for {ticker}: {e}")

    return cleaned_data
