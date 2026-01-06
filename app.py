import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="TradePal", layout="wide")
st.title("TradePal – Smart signalanalys för svenska aktier")

# Lista på några Nasdaq Stockholm-tickers som exempel
nasdaq_stocks = ["VOLV-B.ST", "ERIC-B.ST", "SAND.ST", "HM-B.ST", "ATCO-A.ST"]

# --- Sökfält med inline-autocomplete ---
ticker_input = st.text_input("Skriv ticker (minst 2 bokstäver för förslag):", "")
ticker = ticker_input.upper() if ticker_input else None

# Visa autocomplete-förslag om minst 2 bokstäver skrivits
if ticker_input and len(ticker_input) >= 2:
    matches = [t for t in nasdaq_stocks if t.startswith(ticker_input.upper())]
    if matches:
        st.markdown("**Förslag:**")
        # Klickbara knappar som fyller i ticker när man klickar
        for m in matches:
            if st.button(m):
                ticker = m

# --- Val av grafik och tidsperiod ---
chart_type = st.radio("Välj graftyp", ["Candlestick", "Linje"])
timeframe = st.selectbox("Välj tidsperiod", ["1d", "1w", "1m", "3m", "6m", "1y", "Max"])

interval_map = {"1d": "5m", "1w": "1h", "1m": "1d", "3m": "1d", "6m": "1h", "1y": "1d", "Max": "1d"}
period_map = {"1d": "1d", "1w": "7d", "1m": "1mo", "3m": "3mo", "6m": "6mo", "1y": "1y", "Max": "max"}

interval = interval_map[timeframe]
period = period_map[timeframe]

# --- Hämta och visa data ---
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
