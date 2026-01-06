# app.py
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="TradePal", layout="wide")

st.title("TradePal – Smart signalanalys för svenska aktier")

# --- Ticker autocomplete ---
# Ladda Nasdaq Stockholm tickers (exempel, kan ersättas med full lista)
nasdaq_stocks = ["VOLV-B.ST", "ERIC-B.ST", "SAND.ST", "KINV-B.ST", "SEB-A.ST", "TEL2-B.ST"]
ticker_input = st.text_input("Sök ticker (minst 2 bokstäver)", "")
filtered_tickers = [t for t in nasdaq_stocks if ticker_input.upper() in t.upper()]
ticker = st.selectbox("Välj ticker", filtered_tickers) if filtered_tickers else None

# --- Välj tidsram ---
timeframe = st.selectbox("Välj trend", ["1d","3d","1w","1m","3m","6m","1y","Max"])

# --- Välj graftyp ---
chart_type = st.selectbox("Välj graftyp", ["Candlestick", "Linje"])

# --- Signal info ---
st.markdown("### Signalvärden (0-100 poäng)")
st.markdown("""
- **Köp Observera / Stark**: värde baserat på RSI, Volymspik, Stöd/Motstånd, Trendvändning, Mean Reversion  
- **Sälj Observera / Stark**: samma signaler men för toppar  
*Observera: info visas på hoovern över symbolerna*
""")

# --- Funktion för att hämta data ---
@st.cache_data
def get_data(ticker, timeframe):
    try:
        # --- Intraday ---
        if timeframe in ["1d", "3d", "1w"]:
            intraday_map = {"1d": "15m", "3d": "15m", "1w": "30m"}
            period_map = {"1d": "1d", "3d": "5d", "1w": "7d"}
            data = yf.download(ticker, period=period_map[timeframe], interval=intraday_map[timeframe], progress=False)
            if data.empty:
                return None
            data = data.reset_index()
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = [col[1] if col[1] != "" else col[0] for col in data.columns]
            if 'Datetime' in data.columns:
                data.rename(columns={'Datetime':'Date'}, inplace=True)

        # --- Daglig ---
        else:
            period_map = {"1m": "1mo", "3m": "3mo", "6m": "6mo", "1y": "1y", "Max": "max"}
            data = yf.download(ticker, period=period_map[timeframe], interval="1d", progress=False)
            if data.empty:
                return None
            data = data.reset_index()
            if 'Date' not in data.columns:
                data.rename(columns={'index':'Date'}, inplace=True)
        return data
    except Exception as e:
        st.error(f"Datafel: {e}")
        return None

# --- Hämta data ---
if ticker:
    data = get_data(ticker, timeframe)
    if data is None or data.empty:
        st.warning(f"Ingen data hittades för {ticker} i vald tidsram.")
    else:
        # --- Exempel signaler (dummy poängvärden 0-100) ---
        data['BuySignal'] = 0
        data['SellSignal'] = 0
        # Du kan här implementera dina faktiska signaler baserat på RSI, Volym, etc.

        # --- Plotly chart ---
        fig = go.Figure()
        if chart_type == "Candlestick":
            fig.add_trace(go.Candlestick(
                x=data['Date'],
                open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'],
                name="Candlestick"
            ))
        else:
            fig.add_trace(go.Scatter(
                x=data['Date'],
                y=data['Close'],
                mode='lines+markers',
                name="Linje"
            ))

        # --- Lägg till signalpunkter på grafen ---
        buy_points = data[data['BuySignal'] > 0]
        sell_points = data[data['SellSignal'] > 0]
        fig.add_trace(go.Scatter(
            x=buy_points['Date'],
            y=buy_points['Close'],
            mode='markers+text',
            marker=dict(color='green', size=12, symbol='triangle-up'),
            text=[f"Köp {v}" for v in buy_points['BuySignal']],
            textposition="top center",
            name="Köp"
        ))
        fig.add_trace(go.Scatter(
            x=sell_points['Date'],
            y=sell_points['Close'],
            mode='markers+text',
            marker=dict(color='red', size=12, symbol='triangle-down'),
            text=[f"Sälj {v}" for v in sell_points['SellSignal']],
            textposition="bottom center",
            name="Sälj"
        ))

        fig.update_layout(
            title=f"{ticker} – {chart_type} ({timeframe})",
            xaxis_title="Datum",
            yaxis_title="Pris (SEK)",
            xaxis_rangeslider_visible=False
        )
        st.plotly_chart(fig, use_container_width=True)
