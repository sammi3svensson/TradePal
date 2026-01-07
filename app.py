import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="TradePal", layout="wide")

# --- Importera Inter-font ---
st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        html, body, [class*="css"]  {
            font-family: 'Inter', sans-serif;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# --- TradePal logga ---
logo_url = "https://raw.githubusercontent.com/sammi3svensson/TradePal/49f11e0eb22ef30a690cc74308b85c93c46318f0/tradepal_logo.png.png"
st.image(logo_url, width=250)

# --- Gradientbakgrund ---
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #1f1f2e 0%, #3a3a5a 100%);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Svenska Nasdaq aktier ---
nasdaq_stocks = {
    "VOLVO AB": "VOLV-B.ST",
    "Ericsson": "ERIC-B.ST",
    "Sandvik": "SAND.ST",
    "H&M": "HM-B.ST",
    "AstraZeneca": "ATCO-A.ST",
    "Telia": "TELIA.ST",
    "SEB": "SEB-A.ST",
    "Swedbank": "SWED-A.ST",
    "SKF": "SKF-B.ST",
    "Assa Abloy": "ASSA-B.ST",
    "Alfa Laval": "ALFA.ST",
    "NCC": "NCC-B.ST",
    "SSAB": "SSAB-A.ST",
    "Kinnevik B": "KINV-B.ST",
    "EQT": "EQT.ST",
    "Husqvarna": "HUSQ-B.ST",
    "Atlas Copco": "ATCO-B.ST",
    "Essity": "ESSITY-B.ST"
}

# --- Sökfält ---
def update_ticker():
    st.session_state.selected_ticker = st.session_state.ticker_input_upper

st.text_input("Sök ticker", key="ticker_input_upper", on_change=update_ticker)

if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = ""

with st.expander("Stockholmsbörsen"):
    for name, symbol in nasdaq_stocks.items():
        if st.button(f"{name} – {symbol.replace('.ST','')}"):
            st.session_state.selected_ticker = symbol

ticker = st.session_state.selected_ticker or st.session_state.ticker_input_upper.upper()
if ticker and not ticker.endswith(".ST"):
    ticker += ".ST"

# --- Grafinställningar ---
chart_type = st.radio("Välj graftyp", ["Candlestick", "Linje"], horizontal=True)

timeframes = ["1d", "1w", "1m", "3m", "6m", "1y", "Max"]
if "timeframe" not in st.session_state:
    st.session_state.timeframe = "1d"

cols = st.columns(len(timeframes))
for i, tf in enumerate(timeframes):
    if cols[i].button(tf, use_container_width=True):
        st.session_state.timeframe = tf

timeframe = st.session_state.timeframe

interval_map = {"1d": "5m", "1w": "15m", "1m": "30m", "3m": "1h", "6m": "1d", "1y": "1d", "Max": "1d"}
period_map = {"1d": "1d", "1w": "7d", "1m": "1mo", "3m": "3mo", "6m": "6mo", "1y": "1y", "Max": "max"}

# ========= SIGNALLOGIK (NYTT) =========

def calculate_indicators(data):
    data['EMA20'] = data['Close'].ewm(span=20).mean()
    data['EMA50'] = data['Close'].ewm(span=50).mean()

    delta = data['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    rs = gain.rolling(14).mean() / loss.rolling(14).mean()
    data['RSI'] = 100 - (100 / (1 + rs))

    ema12 = data['Close'].ewm(span=12).mean()
    ema26 = data['Close'].ewm(span=26).mean()
    data['MACD'] = ema12 - ema26
    data['MACD_signal'] = data['MACD'].ewm(span=9).mean()

    data['Vol_avg'] = data['Volume'].rolling(20).mean()
    return data


def calculate_score(curr, prev):
    score = 0
    if curr['EMA20'] > curr['EMA50']:
        score += 20
    if 40 < curr['RSI'] < 65:
        score += 20
    if curr['MACD'] > curr['MACD_signal']:
        score += 20
    if curr['Volume'] > curr['Vol_avg']:
        score += 20
    if curr['Close'] > prev['Close']:
        score += 20
    return score

# --- Rita graf ---
def plot_stock(ticker):
    data = yf.Ticker(ticker).history(
        period=period_map[timeframe],
        interval=interval_map[timeframe]
    )

    if data.empty:
        st.error("Ingen data")
        return

    data.reset_index(inplace=True)
    data['Date'] = pd.to_datetime(data['Datetime'] if 'Datetime' in data.columns else data['Date'])
    data = calculate_indicators(data)

    fig = go.Figure()

    if chart_type == "Candlestick":
        fig.add_trace(go.Candlestick(
            x=data['Date'],
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close']
        ))
    else:
        fig.add_trace(go.Scatter(
            x=data['Date'],
            y=data['Close'],
            mode="lines"
        ))

    # --- Signaler ---
    for i in range(1, len(data)):
        prev, curr = data.iloc[i - 1], data.iloc[i]

        buy = prev['EMA20'] < prev['EMA50'] and curr['EMA20'] > curr['EMA50'] and curr['RSI'] < 70
        sell = prev['EMA20'] > prev['EMA50'] and curr['EMA20'] < curr['EMA50'] and curr['RSI'] > 30

        if buy or sell:
            score = calculate_score(curr, prev)
            fig.add_trace(go.Scatter(
                x=[curr['Date']],
                y=[curr['Close']],
                mode="markers+text",
                marker=dict(
                    size=14,
                    color="lime" if buy else "red",
                    symbol="triangle-up" if buy else "triangle-down"
                ),
                text=[f"{'BUY' if buy else 'SELL'} {score}/100"],
                textposition="top center",
                showlegend=False
            ))

    st.plotly_chart(fig, use_container_width=True)


if ticker:
    plot_stock(ticker)
