import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

# =========================
# KONFIG
# =========================
st.set_page_config(page_title="TradePal", layout="wide")

API_KEY = "0DHMYBG3KZ5DZEOJ"  # <-- din API-nyckel är inlagd här

# =========================
# UI
# =========================
st.title("📊 TradePal – Smart signalanalys för svenska aktier")

ticker_input = st.text_input("Sök svensk aktie (ex: VOLV-B, KINV-B)", "VOLV-B")
timeframe = st.selectbox(
    "Tidsperiod",
    ["6 månader", "1 år", "3 år", "Max"]
)

# =========================
# HJÄLPFUNKTIONER
# =========================
def fetch_alpha_vantage(symbol):
    url = (
        "https://www.alphavantage.co/query?"
        f"function=TIME_SERIES_DAILY_ADJUSTED"
        f"&symbol={symbol}"
        f"&market=STO"
        f"&apikey={API_KEY}"
        f"&outputsize=full"
    )

    r = requests.get(url)
    data = r.json()

    if "Time Series (Daily)" not in data:
        return pd.DataFrame()

    df = pd.DataFrame.from_dict(
        data["Time Series (Daily)"],
        orient="index"
    )

    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    df = df.rename(columns={
        "1. open": "Open",
        "2. high": "High",
        "3. low": "Low",
        "4. close": "Close",
        "6. volume": "Volume"
    })

    df = df[["Open", "High", "Low", "Close", "Volume"]].astype(float)
    return df


def filter_timeframe(df, tf):
    if tf == "6 månader":
        return df.last("180D")
    if tf == "1 år":
        return df.last("365D")
    if tf == "3 år":
        return df.last("1095D")
    return df


# =========================
# HUVUDLOGIK
# =========================
if ticker_input:
    with st.spinner("Hämtar data..."):
        df = fetch_alpha_vantage(ticker_input.upper())

    if df.empty:
        st.error(f"Ingen data hittades för {ticker_input}")
        st.stop()

    df = filter_timeframe(df, timeframe)

    # =========================
    # GRAF
    # =========================
    fig = go.Figure()

    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Pris"
        )
    )

    fig.update_layout(
        height=600,
        template="plotly_dark",
        title=f"{ticker_input} – Pris",
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(fig, use_container_width=True)

    st.success(f"Visar {len(df)} datapunkter för {ticker_input}")
