import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="📈 NSE Stock Breakout Dashboard", layout="wide")
st.title("📈 NSE Stock Breakout Dashboard")

stock_list = [
    "INFY.NS", "TCS.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS", "LTIM.NS", "COFORGE.NS",
    "MPHASIS.NS", "PERSISTENT.NS", "SBIN.NS", "PNB.NS", "BANKBARODA.NS", "UNIONBANK.NS",
    "CANBK.NS", "INDIANB.NS", "LICI.NS", "ICICIBANK.NS", "HDFCBANK.NS", "AXISBANK.NS",
    "KOTAKBANK.NS", "IDFCFIRSTB.NS", "FEDERALBNK.NS", "BANDHANBNK.NS", "AUBANK.NS",
    "YESBANK.NS", "RBLBANK.NS", "IDBI.NS", "BANKINDIA.NS", "CENTRALBK.NS", "IOB.NS",
    "UCOBANK.NS", "ADANIPORTS.NS", "TATAMOTORS.NS", "TATASTEEL.NS", "JSWSTEEL.NS",
    "SAIL.NS", "HAL.NS", "BEL.NS", "BEML.NS", "IRCTC.NS", "IRFC.NS", "RVNL.NS", "RITES.NS",
    "NHPC.NS", "NTPC.NS", "POWERGRID.NS", "ONGC.NS", "GAIL.NS", "OIL.NS", "BPCL.NS",
    "HPCL.NS", "IOC.NS", "COALINDIA.NS", "NLCINDIA.NS", "CONCOR.NS", "SCI.NS", "NBCC.NS",
    "HUDCO.NS", "BEL.NS", "ITC.NS", "HINDUNILVR.NS", "DABUR.NS", "MARICO.NS", "COLPAL.NS",
    "GODREJCP.NS", "EMAMILTD.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "HDFCLIFE.NS",
    "ICICIPRULI.NS", "ICICIGI.NS", "SBILIFE.NS", "RECLTD.NS", "PFC.NS", "HDFC.NS",
    "L&TFH.NS", "CHOLAFIN.NS", "M&MFIN.NS", "SHRIRAMFIN.NS", "LICHSGFIN.NS", "CANFINHOME.NS",
    "INDOSTAR.NS", "KARURVYSYA.NS", "DCBBANK.NS", "J&KBANK.NS", "SOUTHBANK.NS", "BLUEDART.NS"
]

@st.cache_data(ttl=3600)
def analyze_stock(ticker):
    try:
        df = yf.download(ticker, period='3mo', interval='1d')
        if df.empty or len(df) < 60:
            return None

        df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
        df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
        df['EMA100'] = df['Close'].ewm(span=100, adjust=False).mean()
        df['EMA200'] = df['Close'].ewm(span=200, adjust=False).mean()

        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        df['RSI'] = 100 - (100 / (1 + rs))

        df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
        df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = df['EMA12'] - df['EMA26']
        df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_diff'] = df['MACD'] - df['Signal_Line']

        last = df.iloc[-1]

        signal = "Neutral"
        if float(last['MACD_diff']) > 0 and float(last['RSI']) > 60 and float(last['Close']) > float(last['EMA20']):
            signal = "Bullish"
        elif float(last['MACD_diff']) < 0 and float(last['RSI']) < 40 and float(last['Close']) < float(last['EMA20']):
            signal = "Bearish"

        target1 = round(float(last['Close']) * 1.02, 2)
        target2 = round(float(last['Close']) * 1.04, 2)
        target3 = round(float(last['Close']) * 1.06, 2)
        stop_loss = round(float(last['Close']) * 0.98, 2)

        return {
            "Ticker": ticker,
            "Current Price": round(float(last['Close']), 2),
            "EMA20": round(float(last['EMA20']), 2),
            "EMA50": round(float(last['EMA50']), 2),
            "RSI": round(float(last['RSI']), 2),
            "MACD": round(float(last['MACD']), 2),
            "MACD Signal": round(float(last['Signal_Line']), 2),
            "MACD Diff": round(float(last['MACD_diff']), 2),
            "Breakout": "TRUE" if float(last['Close']) > float(last['EMA20']) and float(last['MACD_diff']) > 0 else "FALSE",
            "Sentiment": signal,
            "Target 1": target1,
            "Target 2": target2,
            "Target 3": target3,
            "Stop Loss": stop_loss
        }

    except Exception as e:
        st.warning(f"⚠️ Error with {ticker}: {e}")
        return None

results = []
with st.spinner("🔄 Analyzing all stocks..."):
    for ticker in stock_list:
        result = analyze_stock(ticker)
        if result:
            results.append(result)

if results:
    df_results = pd.DataFrame(results)
    st.dataframe(df_results, use_container_width=True)
else:
    st.error("🚫 No data to display. Check your internet connection or stock symbols.")
