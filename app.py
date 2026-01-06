# app.py
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="TradePal", layout="wide")

st.title("TradePal – Smart signalanalys för svenska aktier")

# --- Autocomplete ticker ---
all_tickers = ["VOLV-B.ST", "SAN.ST", "ERIC-B.ST", "HM-B.ST", "SEB-A.ST"]  # Lägg till hela Nasdaq Stockholm-listan
ticker_input = st.text_input("Sök aktie (minst 2 bokstäver för förslag)")
suggestions = [t for t in all_tickers if t.upper().startswith(ticker_input.upper())] if len(ticker_input) >= 2 else []
selected_ticker = st.selectbox("Välj aktie", suggestions) if suggestions else None

# --- Trendintervall ---
interval_options = {
    "1d": "5m",
    "1w": "15m",
    "1mo": "30m",
    "3mo": "30m",
    "6mo": "1h",
    "1y": "1d",
    "Max": "1d"
}
selected_period = st.selectbox("Välj trendperiod", list(interval_options.keys()))
selected_interval = interval_options[selected_period]

# --- Candlestick eller linje ---
chart_type = st.radio("Välj graftyp", ["Candlestick", "Linje"])

if selected_ticker:
    try:
        # Hämta data
        if selected_interval.endswith("m") or selected_interval.endswith("h"):
            # Intraday
            data = yf.download(selected_ticker, period="60d", interval=selected_interval)
        else:
            # Daglig
            data = yf.download(selected_ticker, period=selected_period, interval=selected_interval)

        if data.empty:
            st.error(f"Inget data hittades för {selected_ticker} i vald tidsram")
        else:
            data.reset_index(inplace=True)

            # Hantera kolumnnamn
            if "Datetime" in data.columns:
                x_col = "Datetime"
            elif "Date" in data.columns:
                x_col = "Date"
            else:
                x_col = data.columns[0]  # fallback

            # --- Plotta ---
            fig = go.Figure()

            if chart_type == "Candlestick":
                fig.add_trace(go.Candlestick(
                    x=data[x_col],
                    open=data['Open'],
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close'],
                    name=selected_ticker,
                    increasing_line_color='green',
                    decreasing_line_color='red',
                    hovertext=[f"Datum: {str(dt.date())}\nTid: {str(dt.time()) if hasattr(dt, 'time') else ''}\nPris: {c}" for dt, c in zip(data[x_col], data['Close'])],
                    hoverinfo="text"
                ))
            else:
                fig.add_trace(go.Scatter(
                    x=data[x_col],
                    y=data['Close'],
                    mode='lines+markers',
                    name=selected_ticker,
                    hovertext=[f"Datum: {str(dt.date())}\nTid: {str(dt.time()) if hasattr(dt, 'time') else ''}\nPris: {c}" for dt, c in zip(data[x_col], data['Close'])],
                    hoverinfo="text"
                ))

            fig.update_layout(
                xaxis_title="Tid",
                yaxis_title="Pris",
                hovermode="x unified",
                template="plotly_dark"
            )

            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Fel vid hämtning av data: {e}")
