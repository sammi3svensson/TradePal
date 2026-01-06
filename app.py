# app.py - TradePal (Yahoo Finance)
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="TradePal", layout="wide")

# --- Sätt tema ---
st.markdown("<h1 style='text-align:center;color:#4B0082;'>TradePal – Smart signalanalys för svenska aktier</h1>", unsafe_allow_html=True)

# --- List of Swedish tickers for suggestions ---
# Här kan man uppdatera med hela Nasdaq Stockholm listan
nasdaq_st = [
    "VOLV-B.ST","ERIC-B.ST","SAND.ST","SEB-A.ST","H&M-B.ST",
    "ATCO-A.ST","SKF-B.ST","SWED-A.ST","SSAB-A.ST","TEL2-B.ST"
]

# --- Sidebar för inställningar ---
st.sidebar.header("Inställningar")
ticker_input = st.sidebar.text_input("Sök ticker (minst 2 bokstäver för förslag)")
suggestions = [t for t in nasdaq_st if ticker_input.upper() in t] if len(ticker_input) >= 2 else []
selected_ticker = st.sidebar.selectbox("Välj ticker", suggestions) if suggestions else None

if selected_ticker:
    st.sidebar.markdown("**Signalinfo**:")
    st.sidebar.markdown("""
    - **Köp-Observera**: RSI < 30, Volymspik, Stöd/Motstånd, Trendvändning, Mean Reversion  
      Poäng: 0-100  
    - **Köp-Stark**: samma signaler men högre poäng  
    - **Sälj-Observera**: RSI > 70, Volymspik, Stöd/Motstånd, Trendvändning, Mean Reversion  
      Poäng: 0-100  
    - **Sälj-Stark**: samma signaler men högre poäng
    """)

# --- Välj tidsram och graf ---
timeframe = st.sidebar.selectbox("Tidsram", ["1d","3d","1w","1m","3m","6m","1y","Max"])
chart_type = st.sidebar.radio("Graftyp", ["Candlestick", "Linje"])

# --- Hämta data ---
def fetch_data(ticker, period):
    try:
        yf_ticker = ticker if ticker.endswith(".ST") else ticker + ".ST"
        data = yf.Ticker(yf_ticker).history(period=period, interval="1d")
        if data.empty:
            return None
        data.reset_index(inplace=True)
        data['Date'] = pd.to_datetime(data['Date'])
        return data
    except Exception as e:
        st.error(f"Fel vid hämtning av data: {e}")
        return None

period_map = {
    "1d": "5d",
    "3d": "7d",
    "1w": "1mo",
    "1m": "3mo",
    "3m": "6mo",
    "6m": "1y",
    "1y": "2y",
    "Max": "max"
}

if selected_ticker:
    data = fetch_data(selected_ticker, period_map[timeframe])
    if data is None or data.empty:
        st.warning(f"Inget data hittades för {selected_ticker} i vald tidsram.")
    else:
        # --- Plotly graf ---
        fig = go.Figure()
        if chart_type == "Candlestick":
            fig.add_trace(go.Candlestick(
                x=data['Date'],
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name="Candlestick"
            ))
        else:
            fig.add_trace(go.Scatter(
                x=data['Date'],
                y=data['Close'],
                mode="lines+markers",
                name="Linje"
            ))

        # --- Tooltip: pris & datum ---
        fig.update_traces(
            hovertemplate='Datum: %{x}<br>Pris: %{y:.2f} SEK<extra></extra>'
        )

        fig.update_layout(
            xaxis_title="Datum",
            yaxis_title="Pris (SEK)",
            template="plotly_dark",
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)
