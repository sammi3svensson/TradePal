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

# --- TradePal logga istället för texttitel (mindre storlek) ---
logo_url = "https://raw.githubusercontent.com/sammi3svensson/TradePal/49f11e0eb22ef30a690cc74308b85c93c46318f0/tradepal_logo.png.png"
st.image(logo_url, width=250)  # Minska loggans bredd till 250px

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

# --- Lista med bolag som knappar i expander (scrollbar) ---
with st.expander("Stockholmsbörsen", expanded=False):
    st.markdown(
        """
        <div style="max-height: 300px; overflow-y: auto; width: fit-content; color: #000000; font-weight: 600;">
    """, unsafe_allow_html=True)
    for name, symbol in nasdaq_stocks.items():
        if st.button(f"{name} – {symbol.replace('.ST','')}"):
            st.session_state.selected_ticker = symbol
            ticker_input = symbol.replace(".ST", "")
    st.markdown("</div>", unsafe_allow_html=True)

# --- Bestäm ticker ---
ticker = st.session_state.selected_ticker if st.session_state.selected_ticker else ticker_input.upper()
if ticker and not ticker.endswith(".ST"):
    ticker += ".ST"

# --- Grafinställningar ---
chart_type = st.radio("Välj graftyp", ["Candlestick", "Linje"], horizontal=True)

# --- Ny: Horisontella tidsknappar istället för selectbox ---
timeframe_options = ["1d", "1w", "1m", "3m", "6m", "1y", "Max"]
if "selected_timeframe" not in st.session_state:
    st.session_state.selected_timeframe = "1d"

def set_timeframe(tf):
    st.session_state.selected_timeframe = tf

st.markdown("**Välj tidsperiod:**")
container = st.container()
container.markdown('<div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:10px;">', unsafe_allow_html=True)
for tf in timeframe_options:
    if container.button(tf, key=tf, on_click=set_timeframe, args=(tf,)):
        st.session_state.selected_timeframe = tf
container.markdown('</div>', unsafe_allow_html=True)

timeframe = st.session_state.selected_timeframe

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
            else:  # 3m
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
        fig.update_layout(
            height=700
        )

        # --- Y-axel ---
        price_min = data['Low'].min()
        price_max = data['High'].max()

        pad_down = max((price_max - price_min) * 0.15, price_max * 0.005)
        pad_up   = max((price_max - price_min) * 0.20, price_max * 0.007)

        fig.update_layout(
            title=f"{ticker} – {timeframe} trend",
            xaxis_title="Datum",
            yaxis_title="Pris",
            yaxis=dict(
                range=[price_min - pad_down, price_max + pad_up],
                autorange=False,
                rangemode="normal"
            )
        )

        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Fel vid hämtning av data: {e}")
