import streamlit as st
import pandas as pd
import numpy as np
import ta  # Bibliothèque pour les indicateurs techniques
import yfinance as yf

# Titre de l'application
st.title("Analyse Technique et Indicateurs Financiers")

# Téléchargement des données
def load_data(ticker="AAPL", start_date="2020-01-01", end_date="2025-01-01"):
    data = yf.download(ticker, start=start_date, end=end_date)
    data['Date'] = data.index
    return data

# Calcul des indicateurs
def compute_indicators(df):
    # Calcul des moyennes mobiles
    df['MA200'] = df['Close'].rolling(window=200).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()

    # Calcul du RSI (Relative Strength Index)
    df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()

    # Distance entre le prix de clôture et la MA200 en pourcentage
    df['Distance_MA200'] = ((df['Close'] - df['MA200']) / df['MA200']) * 100

    return df

# Calcul des signaux d'achat/vente
def detect_signals(df):
    last = df.iloc[-1]
    signals = {
        "RSI > 70": last['RSI'] > 70 if pd.notna(last['RSI']) else False,
        "RSI < 30": last['RSI'] < 30 if pd.notna(last['RSI']) else False,
        "Prix au-dessus de MA50": last['Close'] > last['MA50'] if pd.notna(last['MA50']) else False,
        "Prix au-dessus de MA200": last['Close'] > last['MA200'] if pd.notna(last['MA200']) else False,
    }
    score = sum(signals.values())
    return signals, score

# Affichage des données et des graphiques
st.sidebar.header("Paramètres de l'application")
ticker = st.sidebar.text_input("Symbole boursier (par défaut: AAPL)", "AAPL")
start_date = st.sidebar.date_input("Date de début", pd.to_datetime("2020-01-01"))
end_date = st.sidebar.date_input("Date de fin", pd.to_datetime("2025-01-01"))

# Charger les données et calculer les indicateurs
df = load_data(ticker, start_date=start_date, end_date=end_date)

# Vérifier si les données sont chargées
if df.empty:
    st.error("Les données sont vides. Veuillez vérifier le symbole boursier et les dates.")
else:
    # Calcul des indicateurs
    df = compute_indicators(df)
    
    # Afficher les 5 premières lignes des données pour vérification
    st.write(df.head())

    # Affichage des signaux
    signals, score = detect_signals(df)
    st.write("Signaux d'achat/vente actuels :", signals)
    st.write(f"Score global des signaux : {score}")

    # Affichage des graphiques
    st.subheader(f"Graphique des prix et moyennes mobiles pour {ticker}")
    
    # Graphique de prix de clôture et des moyennes mobiles
    df_chart = df[['Close', 'MA200', 'MA50']]
    df_chart = df_chart.dropna()  # Enlever les valeurs manquantes avant de tracer
    st.line_chart(df_chart)

    # Graphique de RSI
    st.subheader(f"Graphique du RSI pour {ticker}")
    st.line_chart(df[['RSI']].dropna())

    # Graphique de la distance du prix à la MA200
    st.subheader(f"Graphique de la distance entre le prix et la MA200 pour {ticker}")
    st.line_chart(df[['Distance_MA200']].dropna())









