# Module for backtesting strategies
import pandas as pd

def backtest_strategy(df: pd.DataFrame, hold_days: int = 5) -> pd.DataFrame:
    """
    Backtest strategy: Buy on signal, hold for `hold_days`, then sell.
    Returns a DataFrame with trade history and PnL.
    """
    trades = []
    df = df.reset_index(drop=True)

    for i in range(len(df)):
        if df.loc[i, 'Signal'] == 1:
            buy_date = df.loc[i, 'Date']
            buy_price = df.loc[i, 'Close']

            # Determine sell index
            sell_index = i + hold_days
            if sell_index >= len(df):
                break  # Skip if we don't have enough future data

            sell_date = df.loc[sell_index, 'Date']
            sell_price = df.loc[sell_index, 'Close']

            pnl = sell_price - buy_price
            return_pct = (pnl / buy_price) * 100

            trades.append({
                'Buy Date': buy_date,
                'Buy Price': buy_price,
                'Sell Date': sell_date,
                'Sell Price': sell_price,
                'PnL': pnl,
                'Return (%)': return_pct
            })

    trades_df = pd.DataFrame(trades)

    if not trades_df.empty:
        print("\n📊 Backtest Summary:")
        print(f"Total Trades: {len(trades_df)}")
        print(f"Win Rate: {round((trades_df['PnL'] > 0).mean() * 100, 2)}%")
        print(f"Total Return: {round(trades_df['PnL'].sum(), 2)}")
    else:
        print("\n⚠️ No trades triggered in backtest window.")

    return trades_df
