import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="TradePal", layout="wide")
st.title("TradePal – Smart signalanalys för svenska aktier")

# --- SIDOPANEL ---
st.sidebar.header("Inställningar")
ticker_input = st.sidebar.text_input("Sök ticker (ex: Volvo → VOLV.ST)", "VOLV.ST")
timeframe = st.sidebar.selectbox("Välj tidsram", ["1d", "3d", "1w", "1m", "3m", "6m", "1y", "Max"])
chart_type = st.sidebar.radio("Välj graftyp", ["Candlestick", "Linje"])

# --- FUNKTION: Lägg till .ST automatiskt ---
def fix_ticker(ticker):
    if not ticker.upper().endswith(".ST"):
        ticker += ".ST"
    return ticker.upper()

ticker = fix_ticker(ticker_input)

# --- FUNKTION: Hämta data med fallback ---
def get_yahoo_data(ticker, period="1y", interval="1d"):
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        if data.empty:
            return None
        data = data.reset_index()
        return data
    except Exception as e:
        return None

# --- BESTÄM INTERVAL ---
if timeframe in ["1d", "3d", "1w"]:
    interval = "15m"  # Försök intraday
    period_lookup = {"1d": "1d", "3d": "5d", "1w": "7d"}
    data = get_yahoo_data(ticker, period=period_lookup[timeframe], interval=interval)
    if data is None:
        st.info(f"Ingen intraday-data för {ticker}, fallbackar till daglig historik")
        data = get_yahoo_data(ticker, period="1y", interval="1d")
elif timeframe in ["1m", "3m", "6m", "1y", "Max"]:
    interval = "1d"
    period_lookup = {"1m": "1mo", "3m": "3mo", "6m": "6mo", "1y": "1y", "Max": "max"}
    data = get_yahoo_data(ticker, period=period_lookup[timeframe], interval=interval)
else:
    interval = "1d"
    data = get_yahoo_data(ticker, period="1y", interval="1d")

if data is None or data.empty:
    st.warning(f"Ingen data hittades för {ticker}")
    st.stop()

# --- RESAMPLE VECKA/MÅNAD ---
if timeframe.endswith("w"):
    data = data.resample("W-MON", on="Date").agg({
        "Open": "first",
        "High": "max",
        "Low": "min",
        "Close": "last",
        "Volume": "sum"
    }).reset_index()
elif timeframe.endswith("m"):
    data = data.resample("M", on="Date").agg({
        "Open": "first",
        "High": "max",
        "Low": "min",
        "Close": "last",
        "Volume": "sum"
    }).reset_index()

# --- GRAF ---
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
        name=ticker,
        hovertemplate='Datum: %{x}<br>Pris: %{y:.2f} SEK'
    ))

# Tooltip med pris + datum
fig.update_traces(
    hovertemplate='Datum: %{x}<br>Öppning: %{open:.2f}<br>Hög: %{high:.2f}<br>Låg: %{low:.2f}<br>Stäng: %{close:.2f}<extra></extra>'
)

fig.update_layout(
    xaxis_title="Datum",
    yaxis_title="Pris (SEK)",
    template="plotly_dark"  # Du kan ändra till "plotly_white" för light theme
)

st.plotly_chart(fig, use_container_width=True)
