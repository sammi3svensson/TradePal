import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(page_title="TradePal", layout="wide")
st.title("📈 TradePal – Svenska aktier")

# -------------------------------------------------
# Ticker-lista (verifierad)
# -------------------------------------------------

tickers = {
    "VOLV-B": "Volvo B",
    "ATCO-A": "Atlas Copco A",
    "ATCO-B": "Atlas Copco B",
    "ERIC-B": "Ericsson B",
    "HM-B": "H&M B",
    "INVE-B": "Investor B",
    "KINV-B": "Kinnevik B",
    "SAND": "Sandvik",
    "SKF-B": "SKF B"
}

# -------------------------------------------------
# UI
# -------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    ticker_clean = st.selectbox(
        "Aktie",
        options=list(tickers.keys()),
        format_func=lambda x: f"{x} – {tickers[x]}"
    )

with col2:
    period = st.selectbox(
        "Tidsperiod",
        ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
        index=3
    )

with col3:
    chart_type = st.selectbox(
        "Diagramtyp",
        ["Candlestick", "Linje"]
    )

ticker = ticker_clean + ".ST"

# -------------------------------------------------
# Datahämtning
# -------------------------------------------------

@st.cache_data
def load_data(ticker, period):
    df = yf.download(
        ticker,
        period=period,
        progress=False
    )
    return df

df = load_data(ticker, period)

if df.empty:
    st.error("Ingen data hittades – Yahoo Finance svarade tomt.")
    st.stop()

# -------------------------------------------------
# Graf (robust)
# -------------------------------------------------

fig = go.Figure()

if chart_type == "Candlestick" and {"Open","High","Low","Close"}.issubset(df.columns):
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
        name="Stängningspris"
    ))

fig.update_layout(
    template="plotly_dark",
    height=600,
    title=f"{ticker_clean} – Kursutveckling"
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------
# Info (placeholder)
# -------------------------------------------------

st.info(
    """
**TradePal – nästa steg**

✔ Stabil data  
✔ Valbar tidsperiod  
✔ Candlestick / linje  

🔜 Nästa:
- Köp / Sälj-signaler
- Poängsystem (0–100)
- Backtesting
"""
)
