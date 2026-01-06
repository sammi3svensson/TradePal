import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- SIDOPANEL ---
st.set_page_config(page_title="TradePal", layout="wide")
st.title("TradePal – Smart signalanalys för svenska aktier")

st.sidebar.header("Inställningar")

# --- Dummy tickers för Nasdaq Stockholm, kan bytas mot komplett lista ---
nasdaq_se_tickers = [
    "VOLV-B.ST", "ERIC-B.ST", "H&M-B.ST", "ATCO-A.ST", "KINV-B.ST",
    "SAND.ST", "SEB-A.ST", "SWED-A.ST"
]

# --- AUTOCOMPLETE TEXTINPUT ---
ticker_input = st.sidebar.text_input("Sök ticker (minst 2 bokstäver)").upper()
ticker_suggestions = []
if len(ticker_input) >= 2:
    ticker_suggestions = [t for t in nasdaq_se_tickers if t.startswith(ticker_input)]
selected_ticker = st.sidebar.selectbox("Välj ticker", ticker_suggestions)

# --- Lägg till .ST automatiskt ---
def fix_ticker(ticker):
    if ticker and not ticker.upper().endswith(".ST"):
        ticker += ".ST"
    return ticker.upper()

ticker = fix_ticker(selected_ticker)

# --- Tidsram & graf ---
timeframe = st.sidebar.selectbox("Välj tidsram", ["1d", "3d", "1w", "1m", "3m", "6m", "1y", "Max"])
chart_type = st.sidebar.radio("Välj graftyp", ["Candlestick", "Linje"])

# --- Signalpoäng & info ---
signals = {
    "RSI": 20,
    "Volymspik": 15,
    "Stöd/Motstånd": 25,
    "Trendvändning": 20,
    "Mean Reversion": 20
}

signal_colors = {
    "Köp Observera": "#F7DC6F",
    "Köp Stark": "#2ECC71",
    "Sälj Observera": "#F1948A",
    "Sälj Stark": "#C0392B"
}

st.sidebar.subheader("Signalinfo")
for s, p in signals.items():
    st.sidebar.markdown(f"**{s}** – {p} poäng")

# --- Hämta data ---
def get_data(ticker, timeframe):
    try:
        if timeframe in ["1d", "3d", "1w"]:
            intraday_map = {"1d": "15m", "3d": "15m", "1w": "30m"}
            period_map = {"1d": "1d", "3d": "5d", "1w": "7d"}
            data = yf.download(ticker, period=period_map[timeframe], interval=intraday_map[timeframe], progress=False)
            if data.empty:
                data = yf.download(ticker, period="1y", interval="1d", progress=False)
        else:
            interval = "1d"
            period_map = {"1m": "1mo", "3m": "3mo", "6m": "6mo", "1y": "1y", "Max": "max"}
            data = yf.download(ticker, period=period_map[timeframe], interval=interval, progress=False)
        if data.empty:
            return None
        data = data.reset_index()
        return data
    except:
        return None

data = get_data(ticker, timeframe)
if data is None:
    st.warning(f"Ingen data hittades för {ticker}")
    st.stop()

# --- Plot ---
fig = go.Figure()
if chart_type == "Candlestick":
    fig.add_trace(go.Candlestick(
        x=data['Date'],
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name=ticker
    ))
else:
    fig.add_trace(go.Scatter(
        x=data['Date'],
        y=data['Close'],
        mode='lines+markers',
        name=ticker
    ))

# Tooltip med pris + datum + tid (om intraday)
fig.update_traces(
    hovertemplate='Datum: %{x}<br>Öppning: %{open:.2f}<br>Hög: %{high:.2f}<br>Låg: %{low:.2f}<br>Stäng: %{close:.2f}<extra></extra>'
)

fig.update_layout(
    xaxis_title="Datum",
    yaxis_title="Pris (SEK)",
    template="plotly_dark"
)

st.plotly_chart(fig, use_container_width=True)
