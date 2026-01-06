import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from alpha_vantage.timeseries import TimeSeries
import yfinance as yf

# --- Inställningar ---
st.set_page_config(page_title="TradePal", layout="wide")
st.title("TradePal – Smart signalanalys för svenska aktier")

ALPHA_KEY = "0DHMYBG3KZ5DZEOJ"  # Din Alpha Vantage API-nyckel

# --- Autocomplete Nasdaq Stockholm tickers ---
nasdaq_tickers = ["VOLV-B.ST", "ERIC-B.ST", "SAND.ST", "KINV-B.ST", "SEB-A.ST", "ATCO-A.ST"]
ticker_input = st.text_input("Sök ticker (minst 2 bokstäver):")

if len(ticker_input) >= 2:
    suggestions = [t for t in nasdaq_tickers if t.lower().startswith(ticker_input.lower())]
    selected_ticker = st.selectbox("Välj ticker", suggestions)
else:
    selected_ticker = None

# --- Välj tidsram ---
timeframe = st.selectbox("Välj tidsperiod", ["1d","3d","1w","1m","3m","6m","1y","Max"])
chart_type = st.selectbox("Välj graftyp", ["Candlestick","Linje"])

# --- Hämta data ---
data = None
if selected_ticker:
    try:
        if timeframe in ["1d","3d","1w"]:  # Använd Alpha Vantage intraday
            ts = TimeSeries(key=ALPHA_KEY, output_format='pandas')
            intraday, meta = ts.get_intraday(symbol=selected_ticker.replace(".ST",""), interval='15min', outputsize='full')
            intraday = intraday.rename(columns=lambda x: x.capitalize())
            intraday['Date'] = intraday.index
            data = intraday
            # Anpassa kort tidsperiod
            if timeframe=="1d":
                data = data.last('1D')
            elif timeframe=="3d":
                data = data.last('3D')
            elif timeframe=="1w":
                data = data.last('7D')
        else:  # Använd Yahoo daglig data
            yf_ticker = selected_ticker
            yf_data = yf.download(yf_ticker, period="max", interval="1d")
            yf_data['Date'] = yf_data.index
            if timeframe=="1m":
                data = yf_data.last('30D')
            elif timeframe=="3m":
                data = yf_data.last('90D')
            elif timeframe=="6m":
                data = yf_data.last('180D')
            elif timeframe=="1y":
                data = yf_data.last('365D')
            elif timeframe=="Max":
                data = yf_data
    except Exception as e:
        st.error(f"Inget data hittades för {selected_ticker} ({e})")

# --- Plotta graf ---
if data is not None and not data.empty:
    fig = go.Figure()
    if chart_type == "Candlestick" and {'Open','High','Low','Close'}.issubset(data.columns):
        fig.add_trace(go.Candlestick(
            x=data['Date'],
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name=selected_ticker
        ))
    else:
        fig.add_trace(go.Scatter(
            x=data['Date'],
            y=data['Close'] if 'Close' in data.columns else data.iloc[:,3],
            mode='lines+markers',
            name=selected_ticker
        ))
    fig.update_layout(
        title=f"{selected_ticker} – {timeframe}",
        xaxis_title="Datum",
        yaxis_title="Pris (SEK)",
        template="plotly_dark"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Ingen data hittades i vald tidsperiod.")
