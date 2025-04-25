import streamlit as st
import investpy
import pandas as pd
import ta  # Pour les indicateurs techniques

# Titre de l'application
st.title("Analyse Technique avec des Données d'Investing.com")

# Fonction pour récupérer les données depuis Investing.com
def load_data_from_investing(symbol, country, start_date, end_date):
    try:
        # Récupérer les données historiques pour l'action
        df = investpy.get_stock_historical_data(stock=symbol, country=country, from_date=start_date, to_date=end_date)
        df.reset_index(inplace=True)  # Convertir les dates en index
        return df
    except Exception as e:
        st.error(f"Erreur de récupération des données : {e}")
        return pd.DataFrame()

# Calcul des indicateurs
def compute_indicators(df):
    if 'Close' not in df.columns:
        st.error("La colonne 'Close' est manquante dans le DataFrame.")
        return df  # Retourner le DataFrame sans traitement

    # Supprimer les valeurs NaN dans la colonne 'Close'
    df = df.dropna(subset=["Close"])

    # Calcul des moyennes mobiles
    df['MA200'] = df['Close'].rolling(window=200).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()

    # Calcul du RSI (Relative Strength Index)
    df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()

    # Distance entre le prix de clôture et la MA200 en pourcentage
    df['Distance_MA200'] = ((df['Close'] - df['MA200']) / df['MA200']) * 100

    return df

# Interface utilisateur pour récupérer les données
st.sidebar.header("Paramètres de l'application")

symbol = st.sidebar.text_input("Symbole de l'action (ex: 'AAPL' pour Apple)", value="AAPL")
country = st.sidebar.text_input("Pays de l'action (ex: 'United States' pour USA)", value="United States")
start_date = st.sidebar.date_input("Date de début", value=pd.to_datetime("2021-01-01"))
end_date = st.sidebar.date_input("Date de fin", value=pd.to_datetime("2023-01-01"))

# Si l'utilisateur clique sur "Charger les données"
if st.sidebar.button("Charger les données"):
    df = load_data_from_investing(symbol, country, start_date.strftime('%d/%m/%Y'), end_date.strftime('%d/%m/%Y'))

    # Vérifier si les données sont chargées
    if df.empty:
        st.error("Aucune donnée trouvée pour cet actif.")
    else:
        # Calcul des indicateurs techniques
        df = compute_indicators(df)

        # Affichage des données et graphiques
        st.write(f"Voici les données de {symbol} :")
        st.write(df.head())

        # Affichage des graphiques
        st.subheader("Graphique des prix et moyennes mobiles")
        df_chart = df[['Close', 'MA200', 'MA50']]
        st.line_chart(df_chart)

        # Graphique du RSI
        st.subheader("Graphique du RSI")
        st.line_chart(df[['RSI']])

        # Graphique de la distance du prix à la MA200
        st.subheader("Graphique de la distance entre le prix et la MA200")
        st.line_chart(df[['Distance_MA200']])













