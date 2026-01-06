import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="TradePal", layout="wide")

# ----- Tickerväljare -----
st.title("TradePal – Smart signalanalys för svenska aktier")

# Dummy lista för Nasdaq Stockholm-exempel (byt ut mot full lista)
nasdaq_stocks = ["VOLV-B.ST", "KINV-B.ST", "SAND.ST", "ERIC-B.ST", "HUSQ-B.ST"]

# Autocomplete ticker input
ticker_input = st.text_input("Sök aktie (minst 2 bokstäver):").upper()
suggestions = [t for t in nasdaq_stocks if ticker_input in t] if len(ticker_input) >= 2 else []
ticker = st.selectbox("Välj ticker:", suggestions) if suggestions else None

# ----- Välj trendperiod och typ -----
trend_period = st.selectbox("Välj trendperiod:", ["1d", "1w", "1mo", "3m", "6m", "1y", "Max"])
chart_type = st.radio("Välj graf:", ["Candlestick", "Linje"])

# ----- Signaler info -----
st.markdown("""
**Signaler (poäng):**  
- 🟢 Köp Strong / Sälj Strong: 75p  
- 🟡 Köp Observera / Sälj Observera: 60p  
- ⚪ Neutral: 0p  
""")

# ----- Hämta data -----
def fetch_data(ticker, period):
    interval_map = {
        "1d": "5m",
        "1w": "15m",
        "1mo": "30m",
        "3m": "1h",
        "6m": "1h",
        "1y": "1d",
        "Max": "1d"
    }
    interval = interval_map[period]

    # Yahoo intraday/daily fallback
    try:
        if period in ["3m", "6m"]:
            # max 60 dagar intraday, äldre dagligt
            intraday_days = 60
            df_intraday = yf.download(ticker, period=f"{intraday_days}d", interval=interval)
            df_intraday.reset_index(inplace=True)
            # fallback daily data
            total_days = {"3m": 90, "6m": 180}[period]
            df_daily = yf.download(ticker, period=f"{total_days}d", interval="1d")
            df_daily.reset_index(inplace=True)
            df = pd.concat([df_daily, df_intraday])
            df.drop_duplicates(subset="Datetime", inplace=True)
        else:
            df = yf.download(ticker, period=period if period != "Max" else "max", interval=interval)
            df.reset_index(inplace=True)
        if df.empty:
            return None
        return df
    except Exception as e:
        st.error(f"Fel vid hämtning av data: {e}")
        return None

# ----- Visa graf -----
if ticker:
    data = fetch_data(ticker, trend_period)
    if data is None or data.empty:
        st.warning(f"Inget data hittades för {ticker} i vald tidsram.")
    else:
        if chart_type == "Candlestick":
            fig = go.Figure(data=[go.Candlestick(
                x=data['Datetime'] if 'Datetime' in data.columns else data['Date'],
                open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'],
                increasing_line_color='green', decreasing_line_color='red',
                hovertext=[f"Datum: {d}<br>Pris: {c}" for d, c in zip(
                    data['Datetime'] if 'Datetime' in data.columns else data['Date'], data['Close']
                )],
                hoverinfo='text'
            )])
        else:  # Linje
            fig = go.Figure(data=[go.Scatter(
                x=data['Datetime'] if 'Datetime' in data.columns else data['Date'],
                y=data['Close'], mode='lines',
                hovertext=[f"Datum: {d}<br>Pris: {c}" for d, c in zip(
                    data['Datetime'] if 'Datetime' in data.columns else data['Date'], data['Close']
                )],
                hoverinfo='text'
            )])

        fig.update_layout(title=f"{ticker} – {trend_period} trend",
                          xaxis_title="Tid", yaxis_title="Pris (SEK)",
                          xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
