import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="TradePal", layout="wide")
st.title("TradePal – Smart signalanalys för svenska aktier")

nasdaq_stocks = ["VOLV-B.ST", "ERIC-B.ST", "SAND.ST", "HM-B.ST", "ATCO-A.ST"]

# Sökfält med autocomplete
ticker_input = st.text_input("Sök ticker", "")
suggestions = [t for t in nasdaq_stocks if t.lower().startswith(ticker_input.lower())] if len(ticker_input) >= 2 else []

ticker = st.selectbox("Välj ticker", suggestions) if suggestions else ticker_input.upper() if ticker_input else None

chart_type = st.radio("Välj graftyp", ["Candlestick", "Linje"])
timeframe = st.selectbox("Välj tidsperiod", ["1d", "3d", "1w", "1m", "3m", "6m", "1y", "Max"])

interval_map = {"1d": "5m", "3d": "15m", "1w": "1h", "1m": "1d", "3m": "1d", "6m": "1d", "1y": "1d", "Max": "1d"}
period_map = {"1d": "1d", "3d": "3d", "1w": "7d", "1m": "1mo", "3m": "3mo", "6m": "6mo", "1y": "1y", "Max": "max"}

interval = interval_map[timeframe]
period = period_map[timeframe]

if ticker:
    if not ticker.endswith(".ST"):
        ticker += ".ST"
    
    try:
        data = yf.Ticker(ticker).history(period=period, interval=interval)
        if data.empty:
            st.error(f"Inget data hittades för {ticker} i vald tidsram.")
        else:
            # Fix för intraday: använd 'Datetime' om 'Date' saknas
            if 'Date' in data.columns:
                data['Date'] = pd.to_datetime(data['Date'])
            else:
                data.reset_index(inplace=True)
                if 'Datetime' in data.columns:
                    data['Date'] = pd.to_datetime(data['Datetime'])
            
            hover_text = [
                f"{row['Date']}: Open={row['Open']}, High={row['High']}, Low={row['Low']}, Close={row['Close']}"
                for _, row in data.iterrows()
            ]

            if chart_type == "Candlestick":
                fig = go.Figure(data=[go.Candlestick(
                    x=data['Date'], open=data['Open'], high=data['High'],
                    low=data['Low'], close=data['Close'], hovertext=hover_text, hoverinfo="text"
                )])
            else:
                fig = go.Figure(data=[go.Scatter(
                    x=data['Date'], y=data['Close'], mode='lines+markers',
                    hovertext=hover_text, hoverinfo="text"
                )])

            fig.update_layout(title=f"{ticker} – {timeframe} trend", xaxis_title="Datum", yaxis_title="Pris")
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Fel vid hämtning av data: {e}")
