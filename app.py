
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
    </style>
    """,
    unsafe_allow_html=True
)

# --- TradePal logga istället för texttitel (mindre storlek) ---
logo_url = "https://raw.githubusercontent.com/sammi3svensson/TradePal/49f11e0eb22ef30a690cc74308b85c93c46318f0/tradepal_logo.png.png"
st.image(logo_url, width=250)  # Minska loggans bredd till 250px

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
    "Kinnevik B": "KINV-B.ST",
    "EQT": "EQT.ST",
    "Husqvarna": "HUSQ-B.ST",
    "Atlas Copco": "ATCO-B.ST",
    "Essity": "ESSITY-B.ST"
}

# --- Sökfält ---
st.markdown(
    """
    <style>
    input[type="text"] {
        background-color: #2e2e4a !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
        border-radius: 4px;
    }

    label[data-baseweb="label"] {
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Sökfält med on_change ---
def update_ticker():
    st.session_state.selected_ticker = st.session_state.ticker_input_upper

st.text_input(
    "Sök ticker",
    key="ticker_input_upper",
    on_change=update_ticker
)


if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = ""
    
    ticker_input = ""


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

# --- Bestäm ticker ---
ticker = st.session_state.selected_ticker if st.session_state.selected_ticker else ticker_input.upper()
if ticker and not ticker.endswith(".ST"):
    ticker += ".ST"

# --- Grafinställningar ---
chart_type = st.radio("Välj graftyp", ["Candlestick", "Linje"], horizontal=True)

# --- Tidperioder med interaktiva horisontella knappar ---
timeframes = ["1d", "1w", "1m", "3m", "6m", "1y", "Max"]
if "timeframe" not in st.session_state:
    st.session_state.timeframe = "1d"

cols = st.columns(len(timeframes))
for i, tf in enumerate(timeframes):
    if st.session_state.timeframe == tf:
        btn_color = "#6c63ff"  # aktiv knapp
    else:
        btn_color = "#FFFFFF"  # inaktiv knapp
    if cols[i].button(tf, key=tf, help=f"Visa {tf} trend", use_container_width=True):
        st.session_state.timeframe = tf

timeframe = st.session_state.timeframe

interval_map = {"1d": "5m", "1w": "15m", "1m": "30m", "3m": "1h", "6m": "1d", "1y": "1d", "Max": "1d"}
period_map = {"1d": "1d", "1w": "7d", "1m": "1mo", "3m": "3mo", "6m": "6mo", "1y": "1y", "Max": "max"}

interval = interval_map[timeframe]
period = period_map[timeframe]
# =========================
# SIGNAL ENGINE (TradePal)
# =========================

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def buy_rsi_signal(data):
    rsi = calculate_rsi(data['Close'])
    if rsi.iloc[-1] < 30:
        return {"points": 20, "reason": f"RSI översåld ({int(rsi.iloc[-1])})"}
    elif rsi.iloc[-1] < 35:
        return {"points": 10, "reason": f"RSI låg ({int(rsi.iloc[-1])})"}
    return {"points": 0, "reason": ""}


def sell_rsi_signal(data):
    rsi = calculate_rsi(data['Close'])
    if rsi.iloc[-1] > 70:
        return {"points": 20, "reason": f"RSI överköpt ({int(rsi.iloc[-1])})"}
    elif rsi.iloc[-1] > 65:
        return {"points": 10, "reason": f"RSI hög ({int(rsi.iloc[-1])})"}
    return {"points": 0, "reason": ""}


def volume_spike_signal(data):
    avg_vol = data['Volume'].rolling(20).mean()
    if data['Volume'].iloc[-1] > avg_vol.iloc[-1] * 1.8:
        return {"points": 20, "reason": "Volymspik"}
    return {"points": 0, "reason": ""}


def trend_reversal_candle(data):
    candle = data.iloc[-1]
    body = abs(candle['Close'] - candle['Open'])
    wick = candle['Low'] < min(candle['Open'], candle['Close']) - body * 2

    if wick:
        return {"points": 20, "reason": "Reversal-candle"}
    return {"points": 0, "reason": ""}


def mean_reversion_signal(data):
    ema = data['Close'].ewm(span=20).mean()
    deviation = (data['Close'].iloc[-1] - ema.iloc[-1]) / ema.iloc[-1]

    if deviation < -0.05:
        return {"points": 20, "reason": "Mean reversion (nedåt)"}
    if deviation > 0.05:
        return {"points": 20, "reason": "Mean reversion (uppåt)"}
    return {"points": 0, "reason": ""}


def calculate_signal_scores(data):
    buy_score = 0
    sell_score = 0
    buy_reasons = []
    sell_reasons = []

    # KÖP
    for signal in [
        buy_rsi_signal,
        volume_spike_signal,
        trend_reversal_candle,
        mean_reversion_signal
    ]:
        result = signal(data)
        buy_score += result["points"]
        if result["reason"]:
            buy_reasons.append(result["reason"])

    # SÄLJ
    rsi_sell = sell_rsi_signal(data)
    sell_score += rsi_sell["points"]
    if rsi_sell["reason"]:
        sell_reasons.append(rsi_sell["reason"])

    mean_rev_sell = mean_reversion_signal(data)
    sell_score += mean_rev_sell["points"]
    if mean_rev_sell["reason"]:
        sell_reasons.append(mean_rev_sell["reason"])

    return {
        "buy_score": min(buy_score, 100),
        "sell_score": min(sell_score, 100),
        "buy_reasons": buy_reasons,
        "sell_reasons": sell_reasons
    }

# --- Funktion för att rita graf ---
def plot_stock(ticker, timeframe, interval, period, chart_type):
    try:
        data = yf.Ticker(ticker).history(period=period, interval=interval)
        if data.empty:
            st.error(f"Inget data hittades för {ticker} i vald tidsram.")
            return
        data.reset_index(inplace=True)
        
        # Säkerställa att Date-kolumn finns
        if 'Datetime' in data.columns:
            data['Date'] = pd.to_datetime(data['Datetime'])
        elif 'Date' in data.columns:
            data['Date'] = pd.to_datetime(data['Date'])
        else:
            st.error(f"Data innehåller varken 'Date' eller 'Datetime'.")
            return

        # --- SIGNALER (KÖP / SÄLJ) ---
        signals = []

        # RSI
        delta = data['Close'].diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = -delta.clip(upper=0).rolling(14).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))

        # Glidande medelvärden
        data['MA20'] = data['Close'].rolling(20).mean()
        data['MA50'] = data['Close'].rolling(50).mean()

        # --- KÖP / SÄLJ SIGNALER ---
        for i in range(50, len(data)):
            score_buy = 0
            score_sell = 0

            # --- KÖPSIGNALER ---
            if data['RSI'].iloc[i] < 30:
                score_buy += 20
            if data['Close'].iloc[i] > data['MA20'].iloc[i] and data['Close'].iloc[i-1] <= data['MA20'].iloc[i-1]:
                score_buy += 20
            if data['MA20'].iloc[i] > data['MA50'].iloc[i]:
                score_buy += 20
            if data['Low'].iloc[i] == data['Low'].rolling(10).min().iloc[i]:
                score_buy += 20
            if data['Close'].iloc[i] > data['Close'].iloc[i-1]:
                score_buy += 20

            # --- SÄLJSIGNALER ---
            if data['RSI'].iloc[i] > 70:
                score_sell += 20
            if data['Close'].iloc[i] < data['MA20'].iloc[i] and data['Close'].iloc[i-1] >= data['MA20'].iloc[i-1]:
                score_sell += 20
            if data['MA20'].iloc[i] < data['MA50'].iloc[i]:
                score_sell += 20
            if data['High'].iloc[i] == data['High'].rolling(10).max().iloc[i]:
                score_sell += 20
            if data['Close'].iloc[i] < data['Close'].iloc[i-1]:
                score_sell += 20

            # Lägg till signaler endast om score >= 60
            if score_buy >= 60:
                signals.append({
                    "type": "KÖP",
                    "date": data['Date'].iloc[i],
                    "price": data['Close'].iloc[i],
                    "score": score_buy
                })

            if score_sell >= 60:
                signals.append({
                    "type": "SÄLJ",
                    "date": data['Date'].iloc[i],
                    "price": data['Close'].iloc[i],
                    "score": score_sell
                })

        # --- Lägg till beräkning från signal engine ---
        signals_engine = calculate_signal_scores(data)

        # Lägg till "signals_engine" på ett säkert sätt
        if signals_engine.get("buy_score", 0) > 0:
            signals.append({
                "type": "KÖP",
                "date": data['Date'].iloc[-1],
                "price": data['Close'].iloc[-1],
                "score": signals_engine["buy_score"]
            })
        if signals_engine.get("sell_score", 0) > 0:
            signals.append({
                "type": "SÄLJ",
                "date": data['Date'].iloc[-1],
                "price": data['Close'].iloc[-1],
                "score": signals_engine["sell_score"]
            })

        # --- Rita graf ---
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

        # --- Rita K / S-symboler ---
        buy_signals = [
            s for s in signals 
            if isinstance(s, dict) and s.get("type") == "KÖP" and s.get("score", 0) >= 80
        ]
        sell_signals = [
            s for s in signals 
            if isinstance(s, dict) and s.get("type") == "SÄLJ" and s.get("score", 0) >= 80
        ]

        if buy_signals:
            fig.add_trace(go.Scatter(
                x=[s["date"] for s in buy_signals],
                y=[s["price"] for s in buy_signals],
                mode="markers+text",
                marker=dict(
                    size=20,       # Storlek på cirkeln
                    color="lime",  # Grön cirkel
                    symbol="circle",
                    line=dict(color="black", width=2)  # Svart kantlinje
                ),
                text=["K"]*len(buy_signals),
                textposition="middle center",
                name="Köp",
                hovertext=[
                    f"KÖP<br>Datum: {s['date'].date()}<br>Pris: {s['price']:.2f}<br>Poäng: {s['score']}/100"
                    for s in buy_signals
                ],
                hoverinfo="text"
            ))

        if sell_signals:
            fig.add_trace(go.Scatter(
                x=[s["date"] for s in sell_signals],
                y=[s["price"] for s in sell_signals],
                mode="markers+text",
                marker=dict(
                   size=20,       # Storlek på cirkeln
                   color="red",   # Röd cirkel
                   symbol="circle",
                   line=dict(color="black", width=2)  # Svart kantlinje
                ),
                text=["S"]*len(sell_signals),
                textposition="middle center",
                name="Sälj",
                hovertext=[
                    f"SÄLJ<br>Datum: {s['date'].date()}<br>Pris: {s['price']:.2f}<br>Poäng: {s['score']}/100"
                    for s in sell_signals
                ],
                hoverinfo="text"
           ))

        # --- Ticklabels ---
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
        pad_up = max((price_max - price_min) * 0.20, price_max * 0.007)

        company_name = next((name for name, sym in nasdaq_stocks.items() if sym == ticker), ticker)

        fig.update_layout(
            title=f"{company_name} – {timeframe} trend",
            xaxis_title="Datum",
            yaxis_title="Pris",
            yaxis=dict(
                range=[price_min - pad_down, price_max + pad_up],
                autorange=False,
                rangemode="normal"
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Fel vid hämtning av data: {e}")

# --- Rita graf ---
plot_stock(ticker, timeframe, interval, period, chart_type)
