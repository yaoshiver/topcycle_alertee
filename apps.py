import streamlit as st
import pandas as pd
import yfinance as yf
import ta

def load_data(symbol, period="5y", interval="1wk"):
    data = yf.download(symbol, period=period, interval=interval)
    data.dropna(inplace=True)
    return data

def compute_indicators(df):
    df["MA200"] = df["Close"].rolling(window=200).mean()
    df["MA111"] = df["Close"].rolling(window=111).mean()
    df["MA350_2"] = df["Close"].rolling(window=350).mean() * 2

    # Calcul uniquement si MA200 n’est pas NaN
    df["Distance_MA200"] = ((df["Close"] - df["MA200"]) / df["MA200"]) * 100
    df.loc[df["MA200"].isna(), "Distance_MA200"] = None

    # RSI
    df["RSI"] = ta.momentum.RSIIndicator(df["Close"], window=14).rsi()

    return df


def detect_signals(df):
    last = df.iloc[-1]

    signals = {
        "Close > MA200": last.get("Close", 0) > last.get("MA200", float("inf")),
        "Distance MA200 > 50%": last.get("Distance_MA200", 0) > 50,
        "RSI > 85": bool(last["RSI"] > 85) if pd.notna(last.get("RSI")) else False,
        "Close > MA111": last.get("Close", 0) > last.get("MA111", float("inf")),
        "Close > MA350 x2": last.get("Close", 0) > last.get("MA350_2", float("inf"))
    }

    score = sum(signals.values()) / len(signals) * 100  # % de conditions remplies
    return signals, score

st.set_page_config(page_title="Top Cycle Alerte", layout="centered")
st.title("📈 Top Cycle Alerte – Vente au Sommet ?")

symbol = st.text_input("Ticker (ex: BTC-USD, ETH-USD, SPY...)", value="BTC-USD")

if symbol:
    df = load_data(symbol)
    df = compute_indicators(df)

    signals, score = detect_signals(df)

    st.subheader("🔍 Analyse des Signaux")
    for name, value in signals.items():
        st.write(f"- {name} : {'✅' if value else '❌'}")

    st.markdown(f"### 🧠 Score global : `{score:.2f}%`")

    if score >= 80:
        st.success("🚨 Le sommet semble proche, envisagez de prendre des profits !")
    elif score >= 50:
        st.warning("⚠️ Prudence, plusieurs signaux sont en zone de sommet.")
    else:
        st.info("✅ Aucun signal majeur de sommet détecté.")

    st.subheader("📊 Graphique des Moyennes Mobiles")
    columns_to_plot = ["Close", "MA200", "MA111", "MA350_2"]
    available_columns = [col for col in columns_to_plot if col in df.columns]
    df_chart = df[available_columns].dropna().reset_index()

    if not df_chart.empty and len(available_columns) > 1:
        st.line_chart(df_chart)
    else:
        st.info("Pas assez de données pour afficher le graphique.")





