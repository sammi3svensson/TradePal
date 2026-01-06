import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, timedelta
import requests

# ======== FINNHUB CONFIG ========
FINNHUB_API_KEY = "<d5e8729r01qjckl2g1bgd5e8729r01qjckl2g1c0>"
FINNHUB_BASE = "https://finnhub.io/api/v1"

# ======== APP LAYOUT ========
st.set_page_config(page_title="TradePal – Smart signalanalys för svenska aktier", layout="wide")

st.title("TradePal – Smart signalanalys för svenska aktier")
st.markdown("Sök efter aktie, välj tidsintervall och visa trend med signaler.")

# ======== LOAD STOCK LIST ========
@st.cache_data
def load_nasdaq_stocks():
    url = f"{FINNHUB_BASE}/stock/symbol?exchange=STO&token={FINNHUB_API_KEY}"
    resp = requests.get(url).json()
    symbols = [s['symbol'] for s in resp if s['type'] == 'common']
    return symbols

nasdaq_stocks = load_nasdaq_stocks()

# ======== AUTOCOMPLETE SEARCH ========
def get_stock_suggestions(query):
    query = query.upper()
    return [s for s in nasdaq_stocks if s.startswith(query)]

ticker_input = st.text_input("Sök aktie (minst 2 bokstäver):")
suggestions = get_stock_suggestions(ticker_input) if len(ticker_input) >= 2 else []

selected_ticker = st.selectbox("Förslag:", suggestions) if suggestions else None

# ======== TIMEFRAME SELECTION ========
timeframe_map = {
    "1d": "5",  # 5-min
    "1w": "15",  # 15-min
    "1m": "30",  # 30-min
    "3m": "30",  # 30-min
    "6m": "60",  # 1h
    "1y": "D",   # daily
    "Max": "D"   # daily
}

selected_interval = st.selectbox("Välj tidsintervall:", list(timeframe_map.keys()))
resolution = timeframe_map[selected_interval]

# ======== FETCH DATA ========
def fetch_finnhub_data(symbol, resolution, selected_interval):
    now = int(datetime.now().timestamp())
    if selected_interval in ["1d", "1w", "1m", "3m", "6m"]:
        start = now - 60*60*24*30  # fallback 30 dagar
    else:
        start = now - 60*60*24*365*5  # 5 år
    url = f"{FINNHUB_BASE}/stock/candle?symbol={symbol}&resolution={resolution}&from={start}&to={now}&token={FINNHUB_API_KEY}"
    data = requests.get(url).json()
    if data.get("s") != "ok":
        return None
    df = pd.DataFrame({
        "Datetime": pd.to_datetime(data['t'], unit='s'),
        "Open": data['o'],
        "High": data['h'],
        "Low": data['l'],
        "Close": data['c'],
        "Volume": data['v']
    })
    return df

data = fetch_finnhub_data(selected_ticker, resolution, selected_interval) if selected_ticker else None

if data is None or data.empty:
    st.error(f"Inget data hittades för {selected_ticker} i valt tidsintervall.")
else:
    # ======== CHOOSE GRAPH TYPE ========
    chart_type = st.radio("Visa diagram:", ["Candlestick 🕯️", "Linje 📈"])
    if chart_type.startswith("Candlestick"):
        fig = go.Figure(data=[go.Candlestick(
            x=data['Datetime'], open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'],
            hovertext=[f"{d}<br>Open: {o}<br>High: {h}<br>Low: {l}<br>Close: {c}" for d,o,h,l,c in zip(
                data['Datetime'], data['Open'], data['High'], data['Low'], data['Close']
            )],
            hoverinfo="text"
        )])
    else:
        fig = go.Figure(data=[go.Scatter(
            x=data['Datetime'], y=data['Close'], mode='lines+markers',
            hovertext=[f"{d}<br>Close: {c}" for d,c in zip(data['Datetime'], data['Close'])],
            hoverinfo="text"
        )])

    fig.update_layout(
        xaxis_title="Tid",
        yaxis_title="Pris (SEK)",
        xaxis_rangeslider_visible=False,
        hovermode="x"
    )
    st.plotly_chart(fig, use_container_width=True)

    # ======== SIGNAL INFO BOX ========
    st.subheader("Signaler & poäng")
    st.markdown("""
    **Köp Observera / Stark:** Poäng 20-100  
    **Sälj Observera / Stark:** Poäng 20-100  
    **RSI:** 20 poäng  
    **Volymspik:** 15 poäng  
    **Stöd/Motstånd:** 25 poäng  
    **Trendvändning:** 20 poäng  
    **Mean Reversion:** 20 poäng  
    """)

