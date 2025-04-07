
import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
from ta.trend import MACD, EMAIndicator
from ta.momentum import RSIIndicator
import datetime

# -------------------------- Settings --------------------------
st.set_page_config(layout="wide")
st.title("📈 NSE Stock Breakout Dashboard")

symbols = [ "INFY.NS", "WIPRO.NS", "TCS.NS", "SBIN.NS", "LICI.NS",
    "ADANIPORTS.NS", "TATAMOTORS.NS", "TATASTEEL.NS", "HAL.NS", "IRCTC.NS",
    "IOC.NS", "COALINDIA.NS", "HINDUNILVR.NS", "PNB.NS", "RELIANCE.NS",
    "ITC.NS", "VEDL.NS", "JSWSTEEL.NS", "NTPC.NS", "POWERGRID.NS",
    "BPCL.NS", "ONGC.NS", "NHPC.NS", "ADANIGREEN.NS", "GAIL.NS", "TECHM.NS",
    "HCLTECH.NS", "CIPLA.NS", "DIVISLAB.NS", "SUNPHARMA.NS", "BAJAJFINSV.NS",
    "BAJFINANCE.NS", "MARUTI.NS", "EICHERMOT.NS", "M&M.NS", "HDFCBANK.NS",
    "ICICIBANK.NS", "AXISBANK.NS", "BANKBARODA.NS", "INDUSINDBK.NS", "IDFCFIRSTB.NS",
    "FEDERALBNK.NS", "CANBK.NS", "UNIONBANK.NS", "NAUKRI.NS", "PAYTM.NS",
    "ZOMATO.NS", "DELHIVERY.NS", "TATAPOWER.NS", "UPL.NS", "LT.NS",
    "SBICARD.NS", "INDIGO.NS", "BHARTIARTL.NS", "IDEA.NS", "BEL.NS",
    "TITAN.NS", "DMART.NS", "ASIANPAINT.NS", "DIXON.NS", "ABB.NS",
    "BHEL.NS", "IRFC.NS", "RVNL.NS", "PFC.NS", "RECLTD.NS", "SJVN.NS",
    "HFCL.NS", "TATACHEM.NS", "HDFCLIFE.NS", "ICICIPRULI.NS", "ICICIGI.NS",
    "SBILIFE.NS", "HDFCAMC.NS", "CHOLAFIN.NS", "MUTHOOTFIN.NS", "LTIM.NS",
    "PERSISTENT.NS", "COFORGE.NS", "NESTLEIND.NS", "COLPAL.NS", "GODREJCP.NS",
    "MARICO.NS", "BRITANNIA.NS", "HAVELLS.NS", "BLUEDART.NS", "DRREDDY.NS",
    "AUROPHARMA.NS", "GLAND.NS", "LUPIN.NS", "BIOCON.NS", "BOSCHLTD.NS",
    "ESCORTS.NS", "ASHOKLEY.NS", "TIINDIA.NS", "SRF.NS", "DEEPAKNTR.NS",
    "PIIND.NS", "ASTRAL.NS", "TATVA.NS", "ADANIENT.NS", "VBL.NS", "SIEMENS.NS",
    "KPRMILL.NS", "AIAENG.NS", "POLYCAB.NS", "INDUSTOWER.NS", "KALYANKJIL.NS"
]

# -------------------------- Utility Functions --------------------------
@st.cache_data(ttl=3600)
def fetch_data(symbol):
    try:
        df = yf.download(symbol, period="3mo", interval="1d", progress=False)
        if df.empty:
            return None
        df.dropna(inplace=True)
        df["EMA20"] = EMAIndicator(df["Close"], window=20).ema_indicator()
        df["EMA50"] = EMAIndicator(df["Close"], window=50).ema_indicator()
        df["EMA100"] = EMAIndicator(df["Close"], window=100).ema_indicator()
        df["RSI"] = RSIIndicator(df["Close"], window=14).rsi()
        macd = MACD(df["Close"])
        df["MACD"] = macd.macd()
        df["Signal"] = macd.macd_signal()
        df["MACD_Diff"] = macd.macd_diff()
        df["Gann_Level"] = round((df["High"] * df["Low"])**0.5, 2)
        df["Bullish"] = (df["Close"] > df["EMA20"]) & (df["RSI"] > 50) & (df["MACD_Diff"] > 0)
        df["Bearish"] = (df["Close"] < df["EMA20"]) & (df["RSI"] < 50) & (df["MACD_Diff"] < 0)
        df["Target 1"] = round(df["Close"] * 1.02, 2)
        df["Target 2"] = round(df["Close"] * 1.04, 2)
        df["Target 3"] = round(df["Close"] * 1.06, 2)
        df["Stop Loss"] = round(df["Close"] * 0.97, 2)
        return df
    except Exception as e:
        print(f"⚠️ Error with {symbol}: {e}")
        return None

# -------------------------- Main Dashboard --------------------------
final_data = []
for symbol in symbols:
    df = fetch_data(symbol)
    if df is not None:
        latest = df.iloc[-1]
        sentiment = "Bullish" if latest["Bullish"] else "Bearish" if latest["Bearish"] else "Neutral"
        final_data.append({
            "Symbol": symbol,
            "Close": latest["Close"],
            "EMA20": latest["EMA20"],
            "EMA50": latest["EMA50"],
            "RSI": latest["RSI"],
            "MACD": latest["MACD"],
            "Signal": latest["Signal"],
            "MACD_Diff": latest["MACD_Diff"],
            "Gann Level": latest["Gann_Level"],
            "Sentiment": sentiment,
            "Target 1": latest["Target 1"],
            "Target 2": latest["Target 2"],
            "Target 3": latest["Target 3"],
            "Stop Loss": latest["Stop Loss"],
        })

if final_data:
    df_final = pd.DataFrame(final_data)
    st.dataframe(df_final, use_container_width=True)
else:
    st.warning("🚫 No data to display. Check your internet connection or stock symbols.")
