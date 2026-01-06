import streamlit as st
import pandas as pd
import requests
import plotly.graph_objs as go
from datetime import datetime, timedelta

# --- Din Finnhub API-nyckel ---
API_KEY = "d5e8n9hr01qjckl2ipt0d5e8n9hr01qjckl2iptg"

st.set_page_config(page_title="TradePal", layout="wide")

st.title("TradePal – Smart signalanalys för svenska aktier")

# --- Hårdkodad lista med svenska tickers ---
swedish_stocks = [
    "VOLV-B", "ERIC-B", "SAND.ST", "ATCO-A", "ASSA-B", "H&M-B", "SEB-A", 
    "SKF-B", "TELIA", "ALFA", "ESSITY-B", "SWED-A", "NDA-SEK", "KINV-B",
    "SCA-B", "TEL2-B", "INVE-B", "HM-B", "STORA-B", "NIBE-B"
    # Lägg till fler tickers här
]

# --- Sökfält med autocomplete ---
ticker_input = st.text_input(
    "Sök aktie (minst 2 bokstäver):"
)

if len(ticker_input) >= 2:
    matches = [s for s in swedish_stocks if s.startswith(ticker_input.upper())]
else:
    matches = []

selected_ticker = st.selectbox("Välj aktie från förslag", matches)

# --- Välj tidsintervall ---
time_interval = st.selectbox("Välj tidsintervall", ["1d", "1w", "1mo", "3mo", "6mo", "1y", "max"])
chart_type = st.radio("Välj graf", ["Candlestick", "Linje"])

def fetch_finnhub_data(symbol, interval):
    """Hämtar historik från Finnhub."""
    now = int(datetime.now().timestamp())
    if interval == "1d":
        resolution = "5"   # 5-minuters
        start = int((datetime.now() - timedelta(days=1)).timestamp())
    elif interval == "1w":
        resolution = "15"  # 15-minuters
        start = int((datetime.now() - timedelta(7)).timestamp())
    elif interval == "1mo":
        resolution = "30"  # 30-minuters
        start = int((datetime.now() - timedelta(30)).timestamp())
    elif interval == "3mo":
        resolution = "60"  # 1-timmes
        start = int((datetime.now() - timedelta(90)).timestamp())
    elif interval == "6mo":
        resolution = "60"  # 1-timmes
        start = int((datetime.now() - timedelta(180)).timestamp())
    elif interval in ["1y", "max"]:
        resolution = "D"   # Daglig
        start = 0
    else:
        resolution = "D"
        start = 0

    url = f"https://finnhub.io/api/v1/stock/candle?symbol={symbol}.ST&resolution={resolution}&from={start}&to={now}&token={API_KEY}"
    resp = requests.get(url).json()

    if resp.get("s") != "ok":
        st.error(f"Inget data hittades för {symbol} ({resp})")
        return None

    df = pd.DataFrame({
        "Datetime": [datetime.fromtimestamp(ts) for ts in resp["t"]],
        "Open": resp["o"],
        "High": resp["h"],
        "Low": resp["l"],
        "Close": resp["c"],
        "Volume": resp["v"]
    })
    return df

if selected_ticker:
    data = fetch_finnhub_data(selected_ticker, time_interval)
    if data is not None and not data.empty:
        if chart_type == "Candlestick":
            fig = go.Figure(data=[go.Candlestick(
                x=data['Datetime'],
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                increasing_line_color='green',
                decreasing_line_color='red',
                hovertext=[f"Pris: {c}<br>Datum: {d.strftime('%Y-%m-%d %H:%M')}" for c,d in zip(data['Close'], data['Datetime'])]
            )])
        else:
            fig = go.Figure(data=[go.Scatter(
                x=data['Datetime'],
                y=data['Close'],
                mode='lines+markers',
                hovertext=[f"Pris: {c}<br>Datum: {d.strftime('%Y-%m-%d %H:%M')}" for c,d in zip(data['Close'], data['Datetime'])]
            )])

        fig.update_layout(
            title=f"{selected_ticker} – {time_interval} trend",
            xaxis_title="Tid",
            yaxis_title="Pris (SEK)",
            hovermode="x",
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)
