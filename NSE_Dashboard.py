import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime as dt
import time

# List of NSE stock symbols (100+)
stock_symbols = [
    'INFY.NS', 'WIPRO.NS', 'TCS.NS', 'SBIN.NS', 'LICI.NS', 'ADANIPORTS.NS', 'TATAMOTORS.NS',
    'TATASTEEL.NS', 'HAL.NS', 'IRCTC.NS', 'IOC.NS', 'COALINDIA.NS', 'HINDUNILVR.NS',
    'PNB.NS', 'RELIANCE.NS', 'ITC.NS', 'VEDL.NS', 'JSWSTEEL.NS', 'NTPC.NS', 'POWERGRID.NS',
    'BPCL.NS', 'ONGC.NS', 'NHPC.NS', 'ADANIGREEN.NS', 'GAIL.NS', 'TECHM.NS', 'HCLTECH.NS',
    'CIPLA.NS', 'DIVISLAB.NS', 'SUNPHARMA.NS', 'BAJAJFINSV.NS', 'BAJFINANCE.NS', 'MARUTI.NS',
    'EICHERMOT.NS', 'M&M.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'AXISBANK.NS', 'BANKBARODA.NS',
    'INDUSINDBK.NS', 'IDFCFIRSTB.NS', 'FEDERALBNK.NS', 'CANBK.NS', 'UNIONBANK.NS',
    'NAUKRI.NS', 'PAYTM.NS', 'ZOMATO.NS', 'DELHIVERY.NS', 'TATAPOWER.NS', 'UPL.NS',
    'LT.NS', 'SBICARD.NS', 'INDIGO.NS', 'BHARTIARTL.NS', 'IDEA.NS', 'BEL.NS', 'TITAN.NS',
    'DMART.NS', 'ASIANPAINT.NS', 'DIXON.NS', 'ABB.NS', 'BHEL.NS', 'IRFC.NS', 'RVNL.NS',
    'PFC.NS', 'RECLTD.NS', 'SJVN.NS', 'HFCL.NS', 'TATACHEM.NS', 'HDFCLIFE.NS', 'ICICIPRULI.NS',
    'ICICIGI.NS', 'SBILIFE.NS', 'HDFCAMC.NS', 'CHOLAFIN.NS', 'MUTHOOTFIN.NS', 'LTIM.NS',
    'PERSISTENT.NS', 'COFORGE.NS', 'NESTLEIND.NS', 'COLPAL.NS', 'GODREJCP.NS', 'MARICO.NS',
    'BRITANNIA.NS', 'HAVELLS.NS', 'BLUEDART.NS', 'DRREDDY.NS', 'AUROPHARMA.NS', 'GLAND.NS',
    'LUPIN.NS', 'BIOCON.NS', 'BOSCHLTD.NS', 'ESCORTS.NS', 'ASHOKLEY.NS', 'TIINDIA.NS',
    'SRF.NS', 'DEEPAKNTR.NS', 'PIIND.NS', 'ASTRAL.NS', 'TATVA.NS', 'ADANIENT.NS',
    'VBL.NS', 'SIEMENS.NS', 'KPRMILL.NS', 'AIAENG.NS', 'POLYCAB.NS', 'INDUSTOWER.NS',
    'KALYANKJIL.NS'
]

# Technical indicator calculations
def calculate_indicators(df):
    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['EMA100'] = df['Close'].ewm(span=100, adjust=False).mean()
    df['EMA200'] = df['Close'].ewm(span=200, adjust=False).mean()
    df['RSI'] = compute_rsi(df['Close'])
    df['MACD'], df['Signal'], df['MACD_diff'] = compute_macd(df['Close'])
    return df

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=period).mean()
    avg_loss = pd.Series(loss).rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return pd.Series(rsi, index=series.index)

def compute_macd(price, fast=12, slow=26, signal=9):
    exp1 = price.ewm(span=fast, adjust=False).mean()
    exp2 = price.ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    macd_diff = macd - signal_line
    return macd, signal_line, macd_diff

def compute_gann_levels(close):
    gann_levels = {
        'Target1': round(close * 1.02, 2),
        'Target2': round(close * 1.04, 2),
        'Target3': round(close * 1.06, 2),
        'StopLoss': round(close * 0.98, 2)
    }
    return gann_levels

def analyze_stock(symbol):
    try:
        df = yf.download(symbol, period='6mo', interval='1d', progress=False)
        if df.empty or len(df) < 50:
            return None
        df = calculate_indicators(df)
        last = df.iloc[-1]
        sentiment = 'Bullish' if last['MACD_diff'] > 0 and last['MACD'] > last['Signal'] and last['RSI'] > 55 else 'Bearish' if last['RSI'] < 45 else 'Neutral'
        gann = compute_gann_levels(last['Close'])

        return {
            'Symbol': symbol,
            'Close': round(last['Close'], 2),
            'EMA20': round(last['EMA20'], 2),
            'EMA50': round(last['EMA50'], 2),
            'RSI': round(last['RSI'], 2),
            'MACD': round(last['MACD'], 2),
            'Signal Line': round(last['Signal'], 2),
            'MACD Diff': round(last['MACD_diff'], 2),
            'Gann Target 1': gann['Target1'],
            'Gann Target 2': gann['Target2'],
            'Gann Target 3': gann['Target3'],
            'Stop Loss': gann['StopLoss'],
            'Signal': sentiment
        }
    except Exception as e:
        return None

# Streamlit App Layout
st.set_page_config(page_title="📈 NSE Stock Breakout Dashboard", layout="wide")
st.title("📈 NSE Stock Breakout Dashboard")

progress = st.progress(0)
data = []
for i, symbol in enumerate(stock_symbols):
    result = analyze_stock(symbol)
    if result:
        data.append(result)
    progress.progress((i + 1) / len(stock_symbols))

if data:
    df_result = pd.DataFrame(data)
    st.dataframe(df_result, use_container_width=True)
else:
    st.error("🚫 No data to display. Check your internet connection or stock symbols.")
