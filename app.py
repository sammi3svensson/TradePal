# app.py
import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="TradePal", layout="wide")

st.title("TradePal – Smart signalanalys för svenska aktier")

# --- NASDAQ Stockholm tickers ---
nasdaq_stocks = [
    "VOLV-B", "ERIC-B", "SAND", "HM-B", "ATCO-A", "ATCO-B", "TELIA", "SKF-B", "ASSA-B",
    # Lägg till fler tickers här
]

# --- Autocomplete sökfält ---
ticker_input = st.text_input(
    "Sök aktie (minst 2 bokstäver):",
    ""
)

suggestions = []
if len(ticker_input) >= 2:
    suggestions = [t for t in nasdaq_stocks if t.upper().startswith(ticker_input.upper())]

selected_ticker = None
if suggestions:
    selected_ticker = st.selectbox("Välj aktie från förslag:", suggestions)

# --- Lägg till .ST automatiskt ---
if selected_ticker and not selected_ticker.endswith(".ST"):
    selected_ticker += ".ST"

# --- Tidsintervall ---
timeframe_map = {
    "1d": "5m",
    "1w": "15m",
    "1mo": "30m",
    "3m": "30m",
    "6m": "1h",
    "1y": "1d",
    "Max": "1d"
}

timeframe_options = list(timeframe_map.keys())
selected_timeframe = st.selectbox("Välj trendperiod:", timeframe_options)
interval = timeframe_map[selected_timeframe]

# --- Hämta data ---
data = None
if selected_ticker:
    try:
        if interval in ["1d","5m","15m","30m","60m","1h"]:
            # Intraday
            data = yf.download(
                tickers=selected_ticker,
                period="60d",
                interval=interval,
                progress=False
            )
        else:
            data = yf.download(
                tickers=selected_ticker,
                period="max",
                interval="1d",
                progress=False
            )
        data.reset_index(inplace=True)
    except Exception as e:
        st.error(f"Fel vid hämtning av data: {e}")

# --- Plotta graf ---
if data is not None and not data.empty:
    fig = go.Figure()

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=data['Datetime'] if 'Datetime' in data.columns else data['Date'],
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name="Candlestick"
    ))

    # Linje för stängningspris
    fig.add_trace(go.Scatter(
        x=data['Datetime'] if 'Datetime' in data.columns else data['Date'],
        y=data['Close'],
        mode='lines',
        name='Stängningspris'
    ))

    # Tooltip-format
    fig.update_traces(
        hovertemplate=
        "<b>%{x}</b><br>" +
        "Open: %{open}<br>" +
        "High: %{high}<br>" +
        "Low: %{low}<br>" +
        "Close: %{close}<br><extra></extra>"
    )

    fig.update_layout(
        xaxis_rangeslider_visible=False,
        title=f"{selected_ticker} - {selected_timeframe} trend",
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    if selected_ticker:
        st.warning(f"Inget data hittades för {selected_ticker} i vald tidsram")
