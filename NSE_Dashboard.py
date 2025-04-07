import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")
st.title("📈 NSE Stock Breakout Dashboard")

symbols = [ 'INFY.NS', 'WIPRO.NS', 'TCS.NS', 'SBIN.NS', 'LICI.NS',
    'ADANIPORTS.NS', 'TATAMOTORS.NS', 'TATASTEEL.NS', 'HAL.NS', 'IRCTC.NS',
    'IOC.NS', 'COALINDIA.NS', 'HINDUNILVR.NS', 'PNB.NS', 'RELIANCE.NS',
    'ITC.NS', 'VEDL.NS', 'JSWSTEEL.NS', 'NTPC.NS', 'POWERGRID.NS',
    'BPCL.NS', 'ONGC.NS', 'NHPC.NS', 'ADANIGREEN.NS', 'GAIL.NS', 'TECHM.NS',
    'HCLTECH.NS', 'CIPLA.NS', 'DIVISLAB.NS', 'SUNPHARMA.NS', 'BAJAJFINSV.NS',
    'BAJFINANCE.NS', 'MARUTI.NS', 'EICHERMOT.NS', 'M&M.NS', 'HDFCBANK.NS',
    'ICICIBANK.NS', 'AXISBANK.NS', 'BANKBARODA.NS', 'INDUSINDBK.NS', 'IDFCFIRSTB.NS',
    'FEDERALBNK.NS', 'CANBK.NS', 'UNIONBANK.NS', 'NAUKRI.NS', 'PAYTM.NS',
    'ZOMATO.NS', 'DELHIVERY.NS', 'TATAPOWER.NS', 'UPL.NS', 'LT.NS',
    'SBICARD.NS', 'INDIGO.NS', 'BHARTIARTL.NS', 'IDEA.NS', 'BEL.NS',
    'TITAN.NS', 'DMART.NS', 'ASIANPAINT.NS', 'DIXON.NS', 'ABB.NS',
    'BHEL.NS', 'IRFC.NS', 'RVNL.NS', 'PFC.NS', 'RECLTD.NS', 'SJVN.NS',
    'HFCL.NS', 'TATACHEM.NS', 'HDFCLIFE.NS', 'ICICIPRULI.NS', 'ICICIGI.NS',
    'SBILIFE.NS', 'HDFCAMC.NS', 'CHOLAFIN.NS', 'MUTHOOTFIN.NS', 'LTIM.NS',
    'PERSISTENT.NS', 'COFORGE.NS', 'NESTLEIND.NS', 'COLPAL.NS', 'GODREJCP.NS',
    'MARICO.NS', 'BRITANNIA.NS', 'HAVELLS.NS', 'BLUEDART.NS', 'DRREDDY.NS',
    'AUROPHARMA.NS', 'GLAND.NS', 'LUPIN.NS', 'BIOCON.NS', 'BOSCHLTD.NS',
    'ESCORTS.NS', 'ASHOKLEY.NS', 'TIINDIA.NS', 'SRF.NS', 'DEEPAKNTR.NS',
    'PIIND.NS', 'ASTRAL.NS', 'TATVA.NS', 'ADANIENT.NS', 'VBL.NS', 'SIEMENS.NS',
    'KPRMILL.NS', 'AIAENG.NS', 'POLYCAB.NS', 'INDUSTOWER.NS', 'KALYANKJIL.NS'
]

def calculate_indicators(df):
    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['EMA100'] = df['Close'].ewm(span=100, adjust=False).mean()

    df['MACD'] = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
    df['Signal'] = df['MACD'].ewm(span=9).mean()
    df['MACD_diff'] = df['MACD'] - df['Signal']

    df['RSI'] = compute_rsi(df['Close'], 14)
    return df

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def analyze_stock(symbol):
    try:
        df = yf.download(symbol, period='3mo', interval='1d')
        if df.empty:
            return None
        df = calculate_indicators(df)

        last = df.iloc[-1]
        signal = "Neutral"
        if last['MACD_diff'] > 0 and last['RSI'] > 60 and last['Close'] > last['EMA20']:
            signal = "Bullish"
        elif last['MACD_diff'] < 0 and last['RSI'] < 40 and last['Close'] < last['EMA20']:
            signal = "Bearish"

        target1 = round(last['Close'] * 1.02, 2)
        target2 = round(last['Close'] * 1.04, 2)
        target3 = round(last['Close'] * 1.06, 2)
        stoploss = round(last['Close'] * 0.98, 2)

        return {
            'Symbol': symbol,
            'Price': round(last['Close'], 2),
            'EMA20': round(last['EMA20'], 2),
            'RSI': round(last['RSI'], 2),
            'MACD_diff': round(last['MACD_diff'], 2),
            'Signal': signal,
            'Target 1': target1,
            'Target 2': target2,
            'Target 3': target3,
            'Stoploss': stoploss
        }

    except Exception as e:
        st.warning(f"⚠️ Error with {symbol}: {e}")
        return None

results = []
for sym in symbols:
    res = analyze_stock(sym)
    if res:
        results.append(res)

if results:
    df = pd.DataFrame(results)
    st.dataframe(df, use_container_width=True)
else:
    st.error("🚫 No data to display. Check your internet connection or stock symbols.")
