import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="TradePal", layout="wide")
st.title("TradePal – Smart signalanalys för svenska aktier")

# Lista över svenska aktier på Nasdaq Stockholm (exempel, ca 50 aktier)
nasdaq_stocks = [
    "VOLV-B.ST", "ERIC-B.ST", "SAND.ST", "HM-B.ST", "ATCO-A.ST",
    "SHB-A.ST", "SWED-A.ST", "ABB.ST", "INVE-B.ST", "TELIA.ST",
    "SEB-A.ST", "SKA-B.ST", "ALFA.ST", "HEXA-B.ST", "ESSITY-B.ST",
    "EKTAB.ST", "BOL.ST", "NDA-SE.ST", "NDA-A.ST", "NDA-B.ST",
    "SSAB-A.ST", "SSAB-B.ST", "ASSA-B.ST", "SKF-B.ST", "BULTEN.ST",
    "ELUX-B.ST", "SAAB-B.ST", "SCA-B.ST", "NIBE-B.ST", "EQT.ST",
    "MTG-B.ST", "HUSQ-B.ST", "KINV-B.ST", "BICO.ST", "APRO.ST",
    "STORA.ST", "ATCO-B.ST", "CAST.ST", "GARO-B.ST", "MIPS.ST",
    "SAND.ST", "VEONE.ST", "SBB.ST", "BHG.ST", "BONI-B.ST",
    "SOBI.ST", "TEL2-B.ST", "TREL.ST", "VOLATI.ST", "WALL-B.ST"
]

# --- Autocomplete sökfält ---
ticker_input = st.text_input("Skriv ticker", "")
suggestions = [t for t in nasdaq_stocks if t.lower().startswith(ticker_input.lower())] if len(ticker_input) >= 2 else []

ticker = None
if suggestions:
    ticker = st.selectbox("Välj från förslag", suggestions, index=0)
elif ticker_input:
    ticker = ticker_input.upper()

# --- Inställningar ---
chart_type = st.radio("Välj graftyp", ["Candlestick", "Linje"])
timeframe = st.selectbox("Välj tidsperiod", ["1d", "1w", "1m", "3m", "6m", "1y", "Max"])

interval_map = {"1d": "5m", "1w": "15m", "1m": "30m", "3m": "30m", "6m": "1h", "1y": "1d", "Max": "1d"}
period_map = {"1d": "1d", "1w": "7d", "1m": "1mo", "3m": "3mo", "6m": "6mo", "1y": "1y", "Max": "max"}

interval = interval_map[timeframe]
period = period_map[timeframe]

# --- Hämta data ---
if ticker:
    if not ticker.endswith(".ST"):
        ticker += ".ST"
    try:
        data = yf.Ticker(ticker).history(period=period, interval=interval)
        if data.empty:
            st.error(f"Inget data hittades för {ticker} i vald tidsram.")
        else:
            # Reset index om 'Datetime' finns
            data.reset_index(inplace=True)
            if 'Date' not in data.columns and 'Datetime' in data.columns:
                data['Date'] = pd.to_datetime(data['Datetime'])
            
            # Tooltip med datum, tid och pris på separata rader
            hover_text = [
                f"Datum & tid: {row['Date'].strftime('%Y-%m-%d %H:%M:%S')}<br>"
                f"Open: {row['Open']}<br>"
                f"High: {row['High']}<br>"
                f"Low: {row['Low']}<br>"
                f"Close: {row['Close']}"
                for _, row in data.iterrows()
            ]

            # Candlestick eller linje
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
