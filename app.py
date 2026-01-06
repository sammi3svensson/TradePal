import streamlit as st
import yfinance as yf

st.title("Yahoo test – måste fungera")

ticker = "VOLV-B.ST"

st.write("Hämtar data för:", ticker)

df = yf.download(ticker, period="6mo")

st.write(df.head())
