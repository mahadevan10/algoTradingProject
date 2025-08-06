from modules.data_fetcher import fetch_and_clean_data
from modules.strategy import generate_signals
from modules.sheet_uploader import upload_to_google_sheet
import pandas as pd
import os

# ✅ US stock tickers
tickers = ["AAPL", "MSFT"]

# ✅ Fetch and clean data
cleaned_data = fetch_and_clean_data(tickers)

# ✅ Dictionaries to hold outputs
signals_dict = {}
trade_logs = []  # ✅ For detailed trade log
summary_rows = []  # ✅ For summary: ticker, PnL, #trades, #wins, win_ratio

os.makedirs("data", exist_ok=True)  # Ensure data folder exists

for ticker, df in cleaned_data.items():
    df_signals = generate_signals(df)
    signals_dict[ticker] = df_signals

    # ✅ Save to CSV
    df_signals.to_csv(f"data/{ticker}_with_signals.csv", index=False)

    # ✅ Trade Logic
    total_pnl = 0
    position = None
    win_count = 0
    trade_count = 0

    for _, row in df_signals.iterrows():
        if row['Signal'] == 1 and position is None:
            position = (row['Close'], row['Date'])  # Buy
        elif row['Signal'] == 0 and position is not None:
            sell_price = row['Close']
            buy_price, buy_date = position
            trade_pnl = sell_price - buy_price
            total_pnl += trade_pnl
            trade_logs.append([
                ticker,
                str(buy_date),
                str(row['Date']),
                round(buy_price, 2),
                round(sell_price, 2),
                round(trade_pnl, 2)
            ])
            trade_count += 1
            if trade_pnl > 0:
                win_count += 1
            position = None  # Reset position

    # ✅ Final exit at last candle if position is still open
    if position is not None:
        final_price = df_signals['Close'].iloc[-1]
        final_date = df_signals['Date'].iloc[-1]
        buy_price, buy_date = position

        trade_pnl = final_price - buy_price
        total_pnl += trade_pnl
        trade_count += 1
        if trade_pnl > 0:
            win_count += 1

        trade_logs.append([
            ticker,
            str(buy_date),
            str(final_date),
            round(buy_price, 2),
            round(final_price, 2),
            round(trade_pnl, 2)
        ])

    # ✅ Append summary for this ticker
    win_ratio = (win_count / trade_count * 100) if trade_count > 0 else 0
    summary_rows.append([ticker, round(total_pnl, 2), trade_count, win_count, round(win_ratio, 2)])

    # ✅ Print summary to console
    print(f"\n📊 {ticker} Summary:")
    print(f"🟢 Buy signals  : {(df_signals['Signal'] == 1).sum()}")
    print(f"🔴 Sell signals : {(df_signals['Signal'] == 0).sum()}")
    print(f"💰 Strategy P&L : {total_pnl:.2f} USD")
    print(f"💾 Saved with signals to: data/{ticker}_with_signals.csv")

    print("\n🔍 Summary Rows:", summary_rows)
    print("🔍 Trade Logs:", trade_logs)

# ✅ Upload everything to Google Sheets
upload_to_google_sheet(trade_logs, summary_rows)
