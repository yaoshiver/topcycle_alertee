import streamlit as st
import pandas as pd
import yfinance as yf
import ta

def load_data(symbol, period="5y", interval="1wk"):
    data = yf.download(symbol, period=period, interval=interval)
    data.dropna(inplace=True)
    return data

def compute_indicators(df):
    # Vérifier si la colonne "Close" existe avant de l'utiliser
    if "Close" not in df.columns:
        raise KeyError("La colonne 'Close' n'existe pas dans le DataFrame")

    # Afficher les colonnes pour débogage
    print("Colonnes disponibles dans df : ", df.columns)

    # Calcul des moyennes mobiles
    df["MA200"] = df["Close"].rolling(window=200).mean()
    df["MA111"] = df["Close"].rolling(window=111).mean()
    df["MA350_2"] = df["Close"].rolling(window=350).mean() * 2

    # Calcul de la Distance_MA200 uniquement si MA200 est non-NaN
    df["Distance_MA200"] = None
    df.loc[df["MA200"].notna(), "Distance_MA200"] = ((df["Close"] - df["MA200"]) / df["MA200"]) * 100

    # Vérification que la colonne "Close" existe avant de procéder à dropna
    if "Close" in df.columns:
        df_clean = df.dropna(subset=["Close"])
    else:
        raise KeyError("La colonne 'Close' n'est pas présente après traitement")

    # Calcul de l'indicateur RSI
    rsi_indicator = ta.momentum.RSIIndicator(df_clean["Close"], window=14)
    df_clean["RSI"] = rsi_indicator.rsi()

    # Remplacer les NaN de RSI dans le DataFrame original
    df["RSI"] = df_clean["RSI"]

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





