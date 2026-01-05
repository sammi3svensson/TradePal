import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import timedelta

# ======================
# APP CONFIG
# ======================
st.set_page_config(
    page_title="TradePal",
    layout="wide"
)

st.title("📊 TradePal – Smart signalanalys för svenska aktier")

# ======================
# SIDEBAR – INPUT
# ======================
with st.sidebar:
    st.header("🔍 Sök aktie")

    ticker = st.text_input(
        "Ticker (ex: KINV-B.ST, VOLV-B.ST)",
        value="KINV-B.ST"
    )

    timeframe = st.selectbox(
        "Tidsperiod",
        ["1D", "3D", "1W", "1M", "3M", "6M", "1Y", "MAX"],
        index=5
    )

    chart_type = st.radio(
        "Graftyp",
        ["Linjegraf", "Candlestick"],
        horizontal=True
    )

# ======================
# INFOBOX – SIGNALMODELL
# ======================
st.markdown("""
### 🧠 Signalmodell (under utveckling)

TradePal använder en **poängbaserad modell (0–100)**.

**KÖP (bottenlogik)**  
- RSI < 30 → 25p  
- Volymspik → 20p  
- Stöd-nivå → 30p  
- Mean reversion → 25p  

**SÄLJ (topplogik)**  
- RSI > 70 → 25p  
- Volymspik → 20p  
- Motstånd → 30p  
- Trendutmattning → 25p  

🟡 Observera: 60–74  
🟢 Stark signal: 75–100  

> *Inga signaler visas ännu – redo för backtesting.*
""")

st.divider()

# ======================
# DATAHÄMTNING
# ======================
@st.cache_data
def load_data(ticker):
    df = yf.downloadst.write("Rådata:")
st.write(df.head())
st.write("Antal rader:", len(df))
(ticker, period="max")
    df.dropna(inplace=True)
    df = df.sort_index()
    return df

try:
    df = load_data(ticker)
except:
    st.error("❌ Kunde inte hämta data för vald ticker.")
    st.stop()

if df.empty:
    st.error("❌ Ingen data hittades.")
    st.stop()

# ======================
# TIDSRAM-FILTER
# ======================
TIMEFRAME_MAP = {
    "1D": 1,
    "3D": 3,
    "1W": 7,
    "1M": 30,
    "3M": 90,
    "6M": 180,
    "1Y": 365
}

if timeframe != "MAX":
    end_date = df.index.max()
    start_date = end_date - timedelta(days=TIMEFRAME_MAP[timeframe])
    df = df[df.index >= start_date]

# ======================
# GRAF (INGA SIGNALER ÄN)
# ======================
fig = go.Figure()

if chart_type == "Candlestick":
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="Pris"
    ))
else:
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["Close"],
        mode="lines",
        name="Pris"
    ))

fig.update_layout(
    height=650,
    margin=dict(l=40, r=40, t=40, b=40),
    xaxis_rangeslider_visible=False
)

st.plotly_chart(fig, use_container_width=True)

st.caption("🔧 Inga köp/sälj-signaler visas ännu – signal engine kopplas på i nästa steg.")
