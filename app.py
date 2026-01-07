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
        /* Horisontella tidsknappar */
        .time-btn {
            display: inline-block;
            margin: 0 5px 5px 0;
            padding: 6px 14px;
            background-color: #5a5a8a;
            color: #ffffff;
            font-weight: 600;
            border-radius: 6px;
            cursor: pointer;
            border: none;
            transition: all 0.2s ease;
        }
        .time-btn:hover {
            background-color: #7a7ab0;
        }
        .time-btn-active {
            background-color: #b39ddb;
            color: #1f1f2e;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# --- TradePal logga istället för texttitel (mindre storlek) ---
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

# Bestäm vilken ticker som ska användas
ticker = st.session_state.selected_ticker if st.session_state.selected_ticker else ticker_input.upper()
if ticker and not ticker.endswith(".ST"):
    ticker += ".ST"

# --- Horisontella knappar för tidsperiod ---
timeframe_options = ["1d", "1w", "1m", "3m", "6m", "1y", "Max"]
st.markdown("**Välj tidsperiod:**")
if "selected_timeframe" not in st.session_state:
    st.session_state.selected_timeframe = "1d"

# Rendera knappar
time_btns_html = ""
for tf in timeframe_options:
    active_class = "time-btn-active" if st.session_state.selected_timeframe == tf else ""
    # Generera en knapp som använder Streamlit forms för att uppdatera session_state
    time_btns_html += f"""
        <form action="" method="post" style="display:inline;">
            <input type="submit" name="tf" value="{tf}" class="time-btn {active_class}">
        </form>
    """
st.markdown(time_btns_html, unsafe_allow_html=True)

# Fallback: hantera knapptryck
if st.experimental_get_query_params().get("tf"):
    st.session_state.selected_timeframe = st.experimental_get_query_params()["tf"][0]

timeframe = st.session_state.selected_timeframe

# --- Grafinställningar ---
chart_type = st.radio("Välj graftyp", ["Candlestick", "Linje"], horizontal=True)

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

        fig.update_layout(height=700)

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
