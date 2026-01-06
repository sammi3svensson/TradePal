import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- SIDINSTÄLLNINGAR ---
st.set_page_config(page_title="TradePal", layout="wide")

# --- MODERN STIL: Bakgrund & CSS ---
st.markdown("""
<style>
    /* Gradient bakgrund */
    .stApp {
        background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
        color: #ffffff;
    }

    /* Titeln */
    h1 {
        color: #00bfff;
        font-family: 'Arial Black', sans-serif;
    }

    /* Knappar */
    div.stButton > button {
        background: linear-gradient(90deg, #00bfff, #1e90ff);
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.5em 1.5em;
        transition: transform 0.2s;
    }
    div.stButton > button:hover {
        transform: scale(1.05);
        background: linear-gradient(90deg, #1e90ff, #00bfff);
    }

    /* Expander scroll */
    .streamlit-expanderHeader {
        color: #00bfff !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.title("TradePal – Smart signalanalys för svenska aktier")

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
    st.markdown("""
        <div style="max-height: 300px; overflow-y: auto; width: fit-content;">
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

        # --- GRAF ---
        if chart_type == "Candlestick":
            fig = go.Figure(data=[go.Candlestick(
                x=data['Date'],
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                increasing_line_color='rgba(0,191,255,0.8)',
                decreasing_line_color='rgba(255,99,71,0.8)',
                whiskerwidth=0.2,
                hovertemplate=
                    "<b>%{x|%d-%m %H:%M}</b><br>" +
                    "Open: %{open:.2f} SEK<br>" +
                    "High: %{high:.2f} SEK<br>" +
                    "Low: %{low:.2f} SEK<br>" +
                    "Close: %{close:.2f} SEK<br><extra></extra>"
            )])
        else:
            fig = go.Figure(data=[go.Scatter(
                x=data['Date'],
                y=data['Close'],
                mode='lines+markers',
                line=dict(color='rgba(0,191,255,0.9)', width=2),
                marker=dict(size=4),
                hovertemplate="<b>%{x|%d-%m %H:%M}</b><br>Pris: %{y:.2f} SEK<extra></extra>"
            )])

        # --- FIX: 1w, 1m, 3m → snygga ticklabels ---
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

        # --- Öka höjd på trendfönster ---
        fig.update_layout(height=700)

        # 🔽🔽🔽 Y-AXELN – MÅSTE LIGGA HÄR 🔽🔽🔽
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
            ),
            plot_bgcolor='rgba(20,20,30,0.9)',  # mörk bakgrund i plot
            paper_bgcolor='rgba(20,20,30,0.9)',
            font=dict(color='white')
        )

        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Fel vid hämtning av data: {e}")
