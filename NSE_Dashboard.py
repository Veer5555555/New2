import yfinance as yf
import pandas as pd
import streamlit as st
import datetime

st.set_page_config(layout="wide")
st.title("📈 NSE Stock Breakout Dashboard")

stock_list = [
    'RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'KOTAKBANK.NS', 'LT.NS', 'HINDUNILVR.NS',
    'SBIN.NS', 'BHARTIARTL.NS', 'ASIANPAINT.NS', 'AXISBANK.NS', 'MARUTI.NS', 'WIPRO.NS', 'SUNPHARMA.NS', 'ITC.NS',
    'TECHM.NS', 'POWERGRID.NS', 'TATAMOTORS.NS', 'TATASTEEL.NS', 'HCLTECH.NS', 'ULTRACEMCO.NS', 'NTPC.NS',
    'GRASIM.NS', 'NESTLEIND.NS', 'ADANIPORTS.NS', 'CIPLA.NS', 'BAJAJ-AUTO.NS', 'COALINDIA.NS', 'JSWSTEEL.NS',
    'BPCL.NS', 'EICHERMOT.NS', 'HEROMOTOCO.NS', 'INDUSINDBK.NS', 'IOC.NS', 'M&M.NS', 'ONGC.NS', 'SHREECEM.NS',
    'TITAN.NS', 'UPL.NS', 'DIVISLAB.NS', 'HDFCLIFE.NS', 'BAJFINANCE.NS', 'BAJAJFINSV.NS', 'HAVELLS.NS',
    'PIDILITIND.NS', 'DMART.NS', 'GODREJCP.NS', 'ICICIGI.NS', 'ICICIPRULI.NS', 'PEL.NS', 'SBILIFE.NS', 'SIEMENS.NS',
    'SRF.NS', 'TORNTPHARM.NS', 'VEDL.NS', 'VOLTAS.NS', 'ZEEL.NS', 'LICI.NS', 'IRCTC.NS', 'HAL.NS', 'BLUEDART.NS',
    'BANKBARODA.NS', 'BANKINDIA.NS', 'UNIONBANK.NS', 'IDFCFIRSTB.NS', 'PNB.NS', 'FEDERALBNK.NS', 'CANBK.NS',
    'IEX.NS', 'INDIGO.NS', 'RVNL.NS', 'PERSISTENT.NS', 'TATAELXSI.NS', 'BOSCHLTD.NS'
]

def fetch_stock_data(symbol):
    try:
        end = datetime.datetime.now()
        start = end - datetime.timedelta(days=90)
        df = yf.download(symbol, start=start, end=end)
        if df.empty:
            return None

        df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
        df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
        df['RSI'] = compute_rsi(df['Close'])
        df['MACD'], df['Signal'] = compute_macd(df['Close'])
        df['MACD_diff'] = df['MACD'] - df['Signal']

        # Breakout Detection
        df['Breakout'] = df['Close'] > df['Close'].rolling(window=20).max().shift(1)
        breakout = df['Breakout'].iloc[-1]

        sentiment = 'Bullish' if df['EMA20'].iloc[-1] > df['EMA50'].iloc[-1] and df['MACD_diff'].iloc[-1] > 0 else 'Bearish'

        # Target & SL logic
        close_price = df['Close'].iloc[-1]
        target1 = round(close_price * 1.02, 2)
        target2 = round(close_price * 1.04, 2)
        target3 = round(close_price * 1.06, 2)
        stop_loss = round(close_price * 0.98, 2)

        return {
            'Symbol': symbol,
            'Close': round(close_price, 2),
            'EMA20': round(df['EMA20'].iloc[-1], 2),
            'EMA50': round(df['EMA50'].iloc[-1], 2),
            'RSI': round(df['RSI'].iloc[-1], 2),
            'MACD': round(df['MACD'].iloc[-1], 2),
            'Signal': round(df['Signal'].iloc[-1], 2),
            'MACD_diff': round(df['MACD_diff'].iloc[-1], 2),
            'Breakout': breakout,
            'Sentiment': sentiment,
            'Target 1': target1,
            'Target 2': target2,
            'Target 3': target3,
            'Stop Loss': stop_loss
        }
    except Exception as e:
        st.warning(f"⚠️ Error with {symbol}: {e}")
        return None

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def compute_macd(series):
    ema12 = series.ewm(span=12, adjust=False).mean()
    ema26 = series.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal

data = []
for symbol in stock_list:
    result = fetch_stock_data(symbol)
    if result:
        data.append(result)

if data:
    df = pd.DataFrame(data)
    df = df.sort_values(by='RSI', ascending=False)
    st.dataframe(df, use_container_width=True)
else:
    st.error("🚫 No data to display. Check your internet connection or stock symbols.")
