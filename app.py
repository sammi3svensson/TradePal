# app.py
import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- KONFIGURATION ---
FINNHUB_API_KEY = "d5e8729r01qjckl2g1bgd5e8729r01qjckl2g1c0"

st.set_page_config(page_title="TradePal", layout="wide")

# --- LOAD NASDAQ STOCKS ---
@st.cache_data
def load_nasdaq_stocks():
    url = f"https://finnhub.io/api/v1/stock/symbol?exchange=STO&token={FINNHUB_API_KEY}"
    resp = requests.get(url).json()
    symbols = [s['symbol'] for s in resp if s['type'] == 'common']
    return symbols

nasdaq_stocks = load_nasdaq_stocks()

# --- SIDHUVUD ---
st.title("TradePal – Smart signalanalys för svenska aktier")

# --- AUTOCOMPLETE TICKER INPUT ---
def ticker_autocomplete(input_text):
    suggestions = [s for s in nasdaq_stocks if s.startswith(input_text.upper())]
    return suggestions

ticker_input = st.text_input("Sök aktie (minst 2 bokstäver för förslag):")

selected_ticker = None
if len(ticker_input) >= 2:
    suggestions = ticker_autocomplete(ticker_input)
    if suggestions:
        selected_ticker = st.selectbox("Välj aktie från förslag:", suggestions)
        if not selected_ticker.endswith(".ST"):
            selected_ticker += ".ST"

# --- TIDSINTERVALL ---
timeframe_map = {
    "1D": "5",
    "1W": "15",
    "1M": "30",
    "3M": "60",
    "6M": "60",
    "1Y": "D",
    "Max": "D"
}
timeframe = st.selectbox("Välj trend tidsperiod:", list(timeframe_map.keys()))

# --- DIAGRAMVAL ---
chart_type = st.radio("Välj diagramtyp:", ["Candlestick", "Linje"])

# --- SIGNAL INFO BOX ---
st.info("""
**Signaler (poängvärden):**
- RSI: 20p  
- Volymspik: 15p  
- Stöd/Motstånd: 25p  
- Trendvändning: 20p  
- Mean Reversion: 20p  

**Signaltyper:**  
- 🟢 Stark köp / sälj  
- 🟡 Observera köp / sälj
""")

# --- HÄMTA DATA ---
def fetch_finnhub_candles(ticker, interval, timeframe_key):
    try:
        now = int(datetime.now().timestamp())
        if timeframe_key == "1D":
            start = int((datetime.now() - timedelta(days=1)).timestamp())
        elif timeframe_key == "1W":
            start = int((datetime.now() - timedelta(days=7)).timestamp())
        elif timeframe_key == "1M":
            start = int((datetime.now() - timedelta(days=30)).timestamp())
        elif timeframe_key == "3M":
            start = int((datetime.now() - timedelta(days=90)).timestamp())
        elif timeframe_key == "6M":
            start = int((datetime.now() - timedelta(days=180)).timestamp())
        elif timeframe_key == "1Y":
            start = int((datetime.now() - timedelta(days=365)).timestamp())
        else:
            start = int((datetime.now() - timedelta(days=2000)).timestamp())  # Max

        url = f"https://finnhub.io/api/v1/stock/candle?symbol={ticker}&resolution={interval}&from={start}&to={now}&token={FINNHUB_API_KEY}"
        resp = requests.get(url).json()
        if resp.get("s") != "ok":
            return None
        data = pd.DataFrame({
            "Datetime": pd.to_datetime(resp['t'], unit='s'),
            "Open": resp['o'],
            "High": resp['h'],
            "Low": resp['l'],
            "Close": resp['c'],
            "Volume": resp['v']
        })
        return data
    except Exception as e:
        st.error(f"Fel vid hämtning av data: {e}")
        return None

# --- RITA DIAGRAM ---
if selected_ticker:
    interval = timeframe_map[timeframe]
    data = fetch_finnhub_candles(selected_ticker, interval, timeframe)
    if data is None or data.empty:
        st.warning(f"Inget data hittades för {selected_ticker} i vald tidsram.")
    else:
        fig = go.Figure()
        if chart_type == "Candlestick":
            fig.add_trace(go.Candlestick(
                x=data["Datetime"],
                open=data["Open"],
                high=data["High"],
                low=data["Low"],
                close=data["Close"],
                name=selected_ticker
            ))
        else:
            fig.add_trace(go.Scatter(
                x=data["Datetime"],
                y=data["Close"],
                mode="lines+markers",
                name=selected_ticker
            ))

        # Tooltip med pris, datum, tid
        fig.update_traces(
            hovertemplate='Datum: %{x|%Y-%m-%d %H:%M}<br>Pris: %{y}'
        )
        fig.update_layout(
            title=f"{selected_ticker} – {timeframe} trend",
            xaxis_title="Tid",
            yaxis_title="Pris",
            template="plotly_dark",
            autosize=True
        )
        st.plotly_chart(fig, use_container_width=True)
