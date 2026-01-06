import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="TradePal", layout="wide")

st.title("TradePal – Smart signalanalys för svenska aktier")

# --- NASDAQ Stockholm tickers (exempel, fyll på fler om du vill) ---
nasdaq_stocks = [
    "VOLV-B.ST", "ERIC-B.ST", "KINV-B.ST", "SAND.ST", "ASSA-B.ST"
]

# --- Autocomplete ticker input ---
ticker_input = st.text_input("Sök aktie:", "")
suggestions = [t for t in nasdaq_stocks if t.startswith(ticker_input.upper())]
ticker = st.selectbox("Välj aktie från förslag:", suggestions) if suggestions else None

# --- Tidsintervall ---
interval_map = {
    "1d": "5m",
    "1w": "15m",
    "1mo": "30m",
    "3mo": "30m",
    "6mo": "60m",
    "1y": "1d",
    "Max": "1d"
}

timeframe = st.selectbox("Välj tidsperiod:", list(interval_map.keys()))
interval = interval_map[timeframe]

# --- Candlestick eller linje ---
chart_type = st.radio("Välj graftyp:", ["Candlestick", "Linje"])

if ticker:
    try:
        # --- Hämta data ---
        if interval.endswith("m"):  # intraday
            data = yf.download(tickers=ticker, period=timeframe, interval=interval)
        else:  # daily
            data = yf.download(tickers=ticker, period=timeframe, interval=interval)

        if data.empty:
            st.error(f"Inget data hittades för {ticker} i vald tidsram.")
        else:
            data.reset_index(inplace=True)
            # --- Plotly chart ---
            fig = go.Figure()

            if chart_type == "Candlestick":
                fig.add_trace(go.Candlestick(
                    x=data['Datetime'] if 'Datetime' in data.columns else data['Date'],
                    open=data['Open'],
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close'],
                    name=ticker,
                    increasing_line_color='green',
                    decreasing_line_color='red'
                ))
            else:  # Linje
                fig.add_trace(go.Scatter(
                    x=data['Datetime'] if 'Datetime' in data.columns else data['Date'],
                    y=data['Close'],
                    mode='lines+markers',
                    name=ticker
                ))

            fig.update_layout(
                xaxis_title="Datum",
                yaxis_title="Pris (SEK)",
                hovermode="x unified",
                width=1000,
                height=600
            )

            # Tooltip med datum, tid, pris
            fig.update_traces(
                hovertemplate=
                "Datum: %{x}<br>" +
                "Pris: %{y:.2f} SEK<extra></extra>"
            )

            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Fel vid hämtning av data: {e}")
