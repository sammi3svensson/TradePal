import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# ---------- CONFIG ----------
API_KEY = "d5e8729r01qjckl2g1bgd5e8729r01qjckl2g1c0"
BASE_URL = "https://finnhub.io/api/v1"

# ---------- STOCK LIST ----------
# Här laddas hela Nasdaq Stockholm för autocomplete
@st.cache_data(ttl=3600)
def load_nasdaq_stocks():
    url = f"{BASE_URL}/stock/symbol?exchange=STO&token={API_KEY}"
    resp = requests.get(url).json()
    symbols = [s['symbol'] for s in resp if s['type'] == 'common']
    return symbols

nasdaq_stocks = load_nasdaq_stocks()

# ---------- STREAMLIT UI ----------
st.set_page_config(page_title="TradePal", layout="wide")
st.title("TradePal – Smart signalanalys för svenska aktier")

# Autocomplete search box
ticker_input = st.text_input("Sök aktie (minst 2 bokstäver)", "")
filtered_tickers = [t for t in nasdaq_stocks if ticker_input.upper() in t.upper()] if len(ticker_input)>=2 else []

ticker = st.selectbox("Välj aktie från förslag", options=filtered_tickers) if filtered_tickers else None

# ---------- TIMEFRAME SELECTION ----------
timeframe = st.selectbox(
    "Välj trendperiod",
    ["1d", "1w", "1mo", "3m", "6m", "1y", "Max"]
)

# ---------- RESOLUTION MAPPING ----------
resolution_map = {
    "1d": "5",     # 5 min
    "1w": "15",    # 15 min
    "1mo": "30",   # 30 min
    "3m": "60",    # 1h
    "6m": "60",    # 1h
    "1y": "D",     # Daily
    "Max": "D"     # Daily
}

resolution = resolution_map[timeframe]

# ---------- FETCH DATA ----------
def fetch_stock_data(symbol, resolution, timeframe):
    now = int(time.time())
    if timeframe == "1d":
        start = now - 24*60*60
    elif timeframe == "1w":
        start = now - 7*24*60*60
    elif timeframe == "1mo":
        start = now - 30*24*60*60
    elif timeframe == "3m":
        start = now - 90*24*60*60
    elif timeframe == "6m":
        start = now - 180*24*60*60
    elif timeframe == "1y":
        start = now - 365*24*60*60
    else:  # Max
        start = now - 5*365*24*60*60  # 5 år fallback

    url = f"{BASE_URL}/stock/candle?symbol={symbol}&resolution={resolution}&from={start}&to={now}&token={API_KEY}"
    resp = requests.get(url).json()
    
    if resp.get('s') != 'ok':
        return None
    
    df = pd.DataFrame({
        'Datetime': pd.to_datetime(resp['t'], unit='s'),
        'Open': resp['o'],
        'High': resp['h'],
        'Low': resp['l'],
        'Close': resp['c'],
        'Volume': resp['v']
    })
    return df

# ---------- PLOT ----------
if ticker:
    data = fetch_stock_data(ticker, resolution, timeframe)
    if data is None or data.empty:
        st.warning(f"Inget data hittades för {ticker} i vald tidsram")
    else:
        chart_type = st.radio("Välj diagramtyp", ["Candlestick", "Linje"])
        if chart_type == "Candlestick":
            fig = go.Figure(data=[go.Candlestick(
                x=data['Datetime'],
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                hovertext=[f"{d.date()} {d.time()}<br>O:{o} H:{h} L:{l} C:{c}" 
                           for d, o, h, l, c in zip(data['Datetime'], data['Open'], data['High'], data['Low'], data['Close'])]
            )])
        else:
            fig = go.Figure(data=[go.Scatter(
                x=data['Datetime'],
                y=data['Close'],
                mode='lines+markers',
                hovertext=[f"{d.date()} {d.time()}<br>C:{c}" 
                           for d, c in zip(data['Datetime'], data['Close'])]
            )])

        fig.update_layout(
            xaxis_title="Datum & Tid",
            yaxis_title="Pris (SEK)",
            hovermode="x unified",
            template="plotly_dark"  # Du kan byta till "plotly_white" för light
        )
        st.plotly_chart(fig, use_container_width=True)
