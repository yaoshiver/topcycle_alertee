import streamlit as st
import yfinance as yf
import pandas as pd
import talib

# Charger les données BTC en Weekly
@st.cache_data
def load_data():
    data = yf.download("BTC-USD", start="2016-01-01", interval="1wk")
    data.dropna(inplace=True)
    return data

# Calcul des indicateurs
def compute_indicators(df):
    df['RSI'] = talib.RSI(df['Close'], timeperiod=14)
    df['MACD'], df['MACD_signal'], _ = talib.MACD(df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
    df['MA200'] = df['Close'].rolling(window=200).mean()
    df['Distance_MA200'] = (df['Close'] - df['MA200']) / df['MA200'] * 100
    df['MA111'] = df['Close'].rolling(window=111).mean()
    df['MA350_2'] = df['Close'].rolling(window=350).mean() / 2
    df['Pi_Cycle'] = abs(df['MA111'] - df['MA350_2']) < 1000
    return df

# Analyse des signaux de sommet
def detect_signals(df):
    last = df.iloc[-1]
    signals = {
        "RSI > 85": last['RSI'] > 85,
        "MACD croisement baissier": last['MACD'] < last['MACD_signal'],
        "Écart > 100% avec MA200": last['Distance_MA200'] > 100,
        "Pi Cycle Top": last['Pi_Cycle']
    }
    score = sum(signals.values())
    return signals, score

# UI Streamlit
st.set_page_config(page_title="TopCycle Alert", layout="wide")
st.title("TopCycle Alert - Détection de sommet de cycle BTC")

df = load_data()
df = compute_indicators(df)
signals, score = detect_signals(df)

st.subheader("Statut du marché :")
if score >= 3:
    st.error("ALERTE : Probable sommet de cycle détecté !")
elif score == 2:
    st.warning("PRUDENCE : 2 signaux détectés.")
else:
    st.success("Aucun signe de sommet majeur.")

st.subheader("Signaux techniques actifs :")
st.write(signals)

st.subheader("Graphique des indicateurs :")
st.line_chart(df[['Close', 'MA200', 'MA111', 'MA350_2']].dropna())
