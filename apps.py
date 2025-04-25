import streamlit as st
import yfinance as yf
import pandas as pd

# RSI manuel
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# MACD manuel
def compute_macd(close, short=12, long=26, signal=9):
    ema_short = close.ewm(span=short, adjust=False).mean()
    ema_long = close.ewm(span=long, adjust=False).mean()
    macd = ema_short - ema_long
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd, signal_line

# Charger données BTC
@st.cache_data
def load_data():
    data = yf.download("BTC-USD", start="2016-01-01", interval="1wk")
    data.dropna(inplace=True)
    return data

# Calcul des indicateurs
def compute_indicators(df):
    df["RSI"] = compute_rsi(df["Close"])
    df["MACD"], df["MACD_signal"] = compute_macd(df["Close"])
    df["MA200"] = df["Close"].rolling(window=200).mean()
    df["MA111"] = df["Close"].rolling(window=111).mean()
    df["MA350_2"] = df["Close"].rolling(window=350).mean() / 2
    df["Pi_Cycle"] = abs(df["MA111"] - df["MA350_2"]) < 1000

    # Distance à la MA200 avec gestion des NaN
    df["Distance_MA200"] = None
    valid = df["MA200"].notnull()
    df.loc[valid, "Distance_MA200"] = ((df["Close"] - df["MA200"]) / df["MA200"]) * 100

    return df

# Détection des signaux
def detect_signals(df):
    last = df.iloc[-1]
    signals = {
        "RSI > 85": bool(last['RSI'] > 85) if pd.notna(last['RSI']) else False,
        "MACD croisement baissier": last['MACD'] < last['MACD_signal'] if pd.notna(last['MACD']) and pd.notna(last['MACD_signal']) else False,
        "Écart > 100% avec MA200": last['Distance_MA200'] > 100 if pd.notna(last['Distance_MA200']) else False,
        "Pi Cycle Top": last['Pi_Cycle'] if pd.notna(last['Pi_Cycle']) else False
    }
    score = sum(signals.values())
    return signals, score

# Interface Streamlit
st.set_page_config(page_title="TopCycle Alert", layout="wide")
st.title("🔔 TopCycle Alert – Détection de sommet de cycle BTC")

df = load_data()
df = compute_indicators(df)
signals, score = detect_signals(df)

st.subheader("📊 Statut du marché :")
if score >= 3:
    st.error("🚨 ALERTE : Probable sommet de cycle détecté !")
elif score == 2:
    st.warning("⚠️ PRUDENCE : 2 signaux détectés.")
else:
    st.success("✅ Aucun signe de sommet majeur.")

st.subheader("🧠 Signaux actifs :")
st.json(signals)

st.subheader("📈 Graphique BTC + indicateurs")
st.line_chart(df[['Close', 'MA200', 'MA111', 'MA350_2']].dropna())


