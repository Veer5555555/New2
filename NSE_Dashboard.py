import yfinance as yf
import pandas as pd
import numpy as np

def fetch_stock_data(symbol):
    try:
        df = yf.download(symbol, period='6mo', interval='1d', progress=False)

        if df.empty or len(df) < 60:
            return None

        df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
        df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()

        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        df['RSI'] = 100 - (100 / (1 + rs))

        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_diff'] = df['MACD'] - df['Signal']

        close = float(df['Close'].iloc[-1])
        ema20 = float(df['EMA20'].iloc[-1])
        ema50 = float(df['EMA50'].iloc[-1])
        rsi = float(df['RSI'].iloc[-1])
        macd = float(df['MACD'].iloc[-1])
        signal = float(df['Signal'].iloc[-1])
        macd_diff = float(df['MACD_diff'].iloc[-1])

        breakout = close > ema20 and close > ema50
        if macd > signal and rsi > 55:
            sentiment = 'Bullish'
        elif macd < signal and rsi < 45:
            sentiment = 'Bearish'
        else:
            sentiment = 'Neutral'

        return {
            'Symbol': symbol,
            'Close': round(close, 2),
            'EMA20': round(ema20, 2),
            'EMA50': round(ema50, 2),
            'RSI': round(rsi, 2),
            'MACD': round(macd, 2),
            'Signal': round(signal, 2),
            'MACD_diff': round(macd_diff, 2),
            'Breakout': breakout,
            'Sentiment': sentiment,
            'Target 1': round(close * 1.02, 2),
            'Target 2': round(close * 1.04, 2),
            'Target 3': round(close * 1.06, 2),
            'Stop Loss': round(close * 0.98, 2)
        }

    except Exception as e:
        print(f"⚠️ Error with {symbol}: {e}")
        return None
