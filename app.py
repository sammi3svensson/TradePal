import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(
    page_title="TradePal – Smart signalanalys för svenska aktier",
    layout="wide"
)

st.title("📈 TradePal – Smart signalanalys för svenska aktier")

# -------------------------------------------------
# 1. Ladda HELA Nasdaq Stockholm automatiskt
# -------------------------------------------------

@st.cache_data
def load_nasdaq_stockholm():
    url = "https://raw.githubusercontent.com/datasets/nasdaq-listings/master/data/nasdaq-listed-symbols.csv"
    df = pd.read_csv(url)

    # Filtrera svenska aktier (.ST)
    df = df[df["Symbol"].str.endswith(".ST")]

    # Skapa visningsnamn utan .ST
    df["CleanSymbol"] = df["Symbol"].str.replace(".ST", "", regex=False)

    return df.sort_values("CleanSymbol")

nasdaq_df = load_nasdaq_stockholm()

# -------------------------------------------------
# 2. Sökbar ticker-väljare (utan .ST)
# -------------------------------------------------

ticker_display = st.selectbox(
    "🔎 Sök svensk aktie (skriv t.ex. VO, KINV, ATCO)",
    options=nasdaq_df["CleanSymbol"].tolist()
)

# Lägg till .ST internt (osynligt för användaren)
ticker = ticker_display + ".ST"

# -------------------------------------------------
# 3. Tidsintervall
# -------------------------------------------------

period = st.selectbox(
    "Tidsperiod",
    ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
    index=3
)

# -------------------------------------------------
# 4. Hämta data från Yahoo Finance
# -------------------------------------------------

@st.cache_data
def load_price_data(ticker, period):
    df = yf.download(
        ticker,
        period=period,
        auto_adjust=True,
        progress=False
    )
    return df

df = load_price_data(ticker, period)

if df.empty:
    st.error(f"Ingen data hittades för {ticker_display}")
    st.stop()

# -------------------------------------------------
# 5. Candlestick-graf
# -------------------------------------------------

fig = go.Figure()

fig.add_trace(go.Candlestick(
    x=df.index,
    open=df["Open"],
    high=df["High"],
    low=df["Low"],
    close=df["Close"],
    name="Pris"
))

fig.update_layout(
    title=f"{ticker_display} – Kursutveckling",
    xaxis_title="Datum",
    yaxis_title="Pris (SEK)",
    template="plotly_dark",
    height=600
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------
# 6. Info-box (placeholder för signaler)
# -------------------------------------------------

st.info(
    """
**TradePal – Signalinfo (kommer i nästa steg)**

🟢 **Köp (Strong)**  
🔴 **Sälj (Strong)**  

Signaler kommer väga samman:
- RSI
- ADX
- Volym
- Trendstruktur
- Mean Reversion

Poängskala: **0–100**
"""
)
