# modules/strategy.py

import pandas as pd

def generate_signals(df):
    """
    Generate a 'Signal' column based on the strategy:
    - Signal = 1 (Buy) if RSI < 30 AND 20DMA > 50DMA
    - Signal = 0 (Sell/Hold) otherwise
    """
    df = df.copy()  # Avoid modifying original DataFrame

    # Ensure necessary columns exist
    required_cols = {'RSI', '20DMA', '50DMA'}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"Missing one or more required columns: {required_cols}")

    # Create signal column
    df['Signal'] = ((df['RSI'] < 30) & (df['20DMA'] > df['50DMA'])).astype(int)

    # Optional: Add a 'Buy_Sell' label
    df['Buy_Sell'] = df['Signal'].map({1: 'Buy', 0: 'Sell'})

    return df
