import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(page_title="TradePal", layout="wide")
st.title("📈 TradePal – Svenska aktier")

# -------------------------------------------------
# 1. Manuell, verifierad Nasdaq Stockholm-lista
# (Yahoo-kompatibel)
# -------------------------------------------------

@st.cache_data
def load_swedish_tickers():
    data = {
        "VOLV-B": "Volvo B",
        "ATCO-A": "Atlas Copco A",
        "ATCO-B": "Atlas Copco B",
        "ERIC-B": "Ericsson B",
        "HM-B": "H&M B",
        "SEB-A": "SEB A",
        "SWED-A": "Swedbank A",
        "SHB-A": "Handelsbanken A",
        "KINV-B": "Kinnevik B",
        "INVE-B": "Investor B",
        "SAND": "Sandvik",
        "SKF-B": "SKF B"
    }
    return pd.DataFrame.from_dict(data, orient="index", columns=["Namn"])

tickers_df = load_swedish_tickers()

# -------------------------------------------------
# 2. Sökbar dropdown (UTAN .ST)
# -------------------------------------------------

ticker_clean = st.selectbox(
    "🔎 Sök svensk aktie",
    options=tickers_df.index.tolist(),
    format_func=lambda x: f"{x} – {tickers_df.loc[x, 'Namn']}"
)

ticker = ticker_clean + ".ST"

# -------------------------------------------------
# 3. Tidsperiod
# -------------------------------------------------

period = st.selectbox(
    "Tidsperiod",
    ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
    index=3
)

# -------------------------------------------------
# 4. Hämta Yahoo-data
# -------------------------------------------------

@st.cache_data
def load_data(ticker, period):
    return yf.download(
        ticker,
        period=period,
        auto_adjust=True,
        progress=False
    )

df = load_data(ticker, period)

if df.empty:
    st.error(f"Ingen data hittades för {ticker_clean}")
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
    template="plotly_dark",
    height=600,
    title=f"{ticker_clean} – Kursutveckling"
)

st.plotly_chart(fig, use_container_width=True)
