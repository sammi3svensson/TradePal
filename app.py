import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="TradePal", layout="wide")
st.title("TradePal – Smart signalanalys för svenska aktier")

# --- Sidebar ---
st.sidebar.header("Inställningar")
ticker_input = st.sidebar.text_input("Skriv ticker (t.ex. VOLV-B)", "VOLV-B")
chart_type = st.sidebar.radio("Välj graf typ", ["Linje", "Candlestick"])
timeframe = st.sidebar.selectbox(
    "Välj tidsperiod",
    ["1d", "3d", "1w", "1m", "3m", "6m", "1y", "Max"]
)

# --- Funktion för Yahoo Finance ---
def get_yahoo_data(ticker, period="1y", interval="1d"):
    if not ticker.upper().endswith(".ST"):
        ticker += ".ST"
    try:
        yf_ticker = yf.Ticker(ticker)
        df = yf_ticker.history(period=period, interval=interval)
        if df.empty:
            return None
        df.reset_index(inplace=True)
        return df
    except Exception as e:
        st.error(f"Fel vid hämtning av data: {e}")
        return None

# --- Konvertera timeframe till Yahoo interval ---
interval_map = {
    "1d": "15m",
    "3d": "30m",
    "1w": "1h",
    "1m": "1d",
    "3m": "1d",
    "6m": "1d",
    "1y": "1d",
    "Max": "1d"
}
interval = interval_map.get(timeframe, "1d")

# --- Hämta data ---
data = get_yahoo_data(ticker_input, period=timeframe, interval=interval)
if data is None:
    st.warning(f"Ingen data hittades för {ticker_input}")
    st.stop()

# --- Skapa graf ---
fig = go.Figure()

if chart_type == "Linje":
    fig.add_trace(go.Scatter(
        x=data['Date'],
        y=data['Close'],
        mode='lines+markers',
        name='Close',
        hovertemplate='Datum: %{x}<br>Pris: %{y:.2f} SEK<extra></extra>'
    ))
else:  # Candlestick
    fig.add_trace(go.Candlestick(
        x=data['Date'],
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name='Candlestick',
        increasing_line_color='green',
        decreasing_line_color='red',
        hovertemplate=
            'Datum: %{x}<br>Open: %{open:.2f} <br>High: %{high:.2f} <br>Low: %{low:.2f} <br>Close: %{y:.2f}<extra></extra>'
    ))

fig.update_layout(
    xaxis_title="Datum",
    yaxis_title="Pris (SEK)",
    template="plotly_dark",
    height=600
)

st.plotly_chart(fig, use_container_width=True)
