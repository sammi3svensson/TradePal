import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- SIDINSTÄLLNINGAR ---
st.set_page_config(page_title="TradePal", layout="wide", page_icon=":chart_with_upwards_trend:")

# --- CSS FÖR MODERN DESIGN ---
st.markdown(
    """
    <style>
    /* Body & bakgrund */
    .stApp {
        background: linear-gradient(160deg, #f3f0ff 0%, #ffffff 100%);
        color: #1e1e2f;
        font-family: 'Segoe UI', 'Roboto', sans-serif;
    }
    /* Header logga */
    .header-logo {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
    }
    .header-logo img {
        width: 100px;  /* mindre logga */
        height: auto;
    }
    /* Inputs, selectbox, radiobuttons */
    .stTextInput>div>div>input, .stSelectbox>div>div>div>div {
        background-color: rgba(255,255,255,0.9);
        color: #1e1e2f;
        font-weight: 600;
        border-radius: 8px;
        padding: 6px 10px;
    }
    .stRadio>div>div>label {
        font-weight: 600;
        color: #1e1e2f;
    }
    /* Buttons */
    button {
        background-color: #7e6ca0;
        color: white;
        border-radius: 8px;
        padding: 5px 12px;
        border: none;
        font-weight: 600;
    }
    button:hover {
        background-color: #9a81c2;
    }
    /* Expander scrollbar */
    div[aria-expanded="false"] > .streamlit-expanderHeader {
        font-weight: 600;
        color: #1e1e2f;
    }
    /* Trend graf bakgrund */
    .stPlotlyChart {
        background-color: rgba(255,255,255,0.0);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- HEADER MED ENDAST LOGGA ---
st.markdown(
    """
    <div class="header-logo">
        <img src="https://raw.githubusercontent.com/sammi3svensson/TradePal/49f11e0eb22ef30a690cc74308b85c93c46318f0/tradepal_logo.png" alt="TradePal Logo">
    </div>
    """,
    unsafe_allow_html=True
)

# --- Svenska Nasdaq aktier med företagsnamn ---
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
    "Telge": "TELGE.ST",
    "NCC": "NCC-B.ST",
    "SSAB": "SSAB-A.ST",
    "Investor": "KINV-B.ST",
    "EQT": "EQT.ST",
    "Husqvarna": "HUSQ-B.ST",
    "Atlas Copco": "ATCO-B.ST",
    "Essity": "ESSITY-B.ST"
}

# --- Sökfält ---
ticker_input = st.text_input("Sök ticker", "")

if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = ""

with st.expander("Stockholmsbörsen", expanded=False):
    st.markdown('<div style="max-height: 300px; overflow-y: auto; width: fit-content;">', unsafe_allow_html=True)
    for name, symbol in nasdaq_stocks.items():
        if st.button(f"{name} – {symbol.replace('.ST','')}"):
            st.session_state.selected_ticker = symbol
            ticker_input = symbol.replace(".ST", "")
    st.markdown("</div>", unsafe_allow_html=True)

ticker = st.session_state.selected_ticker if st.session_state.selected_ticker else ticker_input.upper()
if ticker and not ticker.endswith(".ST"):
    ticker += ".ST"

# --- Grafinställningar ---
chart_type = st.radio("Välj graftyp", ["Candlestick", "Linje"])
timeframe = st.selectbox("Välj tidsperiod", ["1d", "1w", "1m", "3m", "6m", "1y", "Max"])

interval_map = {"1d": "5m", "1w": "15m", "1m": "30m", "3m": "1h", "6m": "1d", "1y": "1d", "Max": "1d"}
period_map = {"1d": "1d", "1w": "7d", "1m": "1mo", "3m": "3mo", "6m": "6mo", "1y": "1y", "Max": "max"}

interval = interval_map[timeframe]
period = period_map[timeframe]

try:
    data = yf.Ticker(ticker).history(period=period, interval=interval)

    if data.empty:
        st.error(f"Inget data hittades för {ticker} i vald tidsram.")
    else:
        data.reset_index(inplace=True)
        data['Date'] = pd.to_datetime(
            data['Datetime'] if 'Datetime' in data.columns else data['Date']
        )

        if chart_type == "Candlestick":
            fig = go.Figure(data=[go.Candlestick(
                x=data['Date'],
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                increasing_line_color='green',
                decreasing_line_color='red',
                whiskerwidth=0.2
            )])
        else:
            fig = go.Figure(data=[go.Scatter(
                x=data['Date'],
                y=data['Close'],
                mode='lines'
            )])

        # --- FIX: 1w, 1m, 3m → snygga ticklabels utan mikrosekunder ---
        if timeframe in ["1w", "1m", "3m"]:
            if timeframe in ["1w", "1m"]:
                tick_labels = data['Date'].dt.strftime('%d-%m')
            else:
                tick_labels = data['Date'].dt.strftime('%H:%M')

            fig.update_xaxes(
                type="category",
                categoryorder="category ascending",
                tickvals=data['Date'],
                ticktext=tick_labels,
                tickmode="auto",
                nticks=10
            )

        # --- Öka höjden på trendfönstret ---
        fig.update_layout(height=700)

        # 🔽 Y-AXELN – bibehåll som tidigare 🔽
        price_min = data['Low'].min()
        price_max = da_
