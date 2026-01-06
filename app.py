import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

FINNHUB_API_KEY = "d5e8729r01qjckl2g1bgd5e8729r01qjckl2g1c0"

st.set_page_config(page_title="TradePal", layout="wide")

st.title("TradePal – Smart signalanalys för svenska aktier")

# -------------------------
# Ladda Nasdaq Stockholm aktier
# -------------------------
@st.cache_data
def load_nasdaq_stocks():
    url = f"https://finnhub.io/api/v1/stock/symbol?exchange=STO&token={d5e8729r01qjckl2g1bgd5e8729r01qjckl2g1c0}"
    try:
        resp = requests.get(url).json()
    except Exception as e:
        st.error(f"Fel vid API-anrop: {e}")
        return []

    if not isinstance(resp, list):
        st.error(f"Fel vid hämtning av aktier: {resp}")
        return []

    symbols = [s['symbol'] for s in resp if s.get('type') == 'common']
    return symbols

nasdaq_stocks = load_nasdaq_stocks()

# -------------------------
# Sökfält med autocomplete
# -------------------------
def ticker_autocomplete(input_text, symbols):
    input_text = input_text.upper()
    if len(input_text) < 2:
        return []
    return [s for s in symbols if s.startswith(input_text)]

input_ticker = st.text_input("Sök aktie (minst 2 bokstäver)", "").upper()
suggestions = ticker_autocomplete(input_ticker, nasdaq_stocks)
selected_ticker = st.selectbox("Välj aktie från förslag", suggestions) if suggestions else None

# -------------------------
# Hämta historisk data
# -------------------------
def get_stock_data(ticker, interval='1d', outputsize='6m'):
    url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={FINNHUB_API_KEY}"
    try:
        data = requests.get(url).json()
    except:
        return None
    if "c" not in data:
        return None
    # Dummy dataframe för exempel
    df = pd.DataFrame({
        "Datetime": [datetime.now()],
        "Open": [data['o']],
        "High": [data['h']],
        "Low": [data['l']],
        "Close": [data['c']],
        "Volume": [data['v']]
    })
    return df

# -------------------------
# Visa graf
# -------------------------
if selected_ticker:
    df = get_stock_data(selected_ticker)
    if df is None or df.empty:
        st.error(f"Ingen data hittades för {selected_ticker}")
    else:
        fig = go.Figure()

        fig.add_trace(go.Candlestick(
            x=df['Datetime'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="Candlestick"
        ))

        fig.add_trace(go.Scatter(
            x=df['Datetime'],
            y=df['Close'],
            mode='lines',
            name="Linje"
        ))

        fig.update_layout(
            title=f"{selected_ticker} trend",
            xaxis_title="Datum",
            yaxis_title="Pris (SEK)",
            xaxis_rangeslider_visible=False,
            hovermode="x unified"
        )

        st.plotly_chart(fig, use_container_width=True)
