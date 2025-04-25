import streamlit as st
import pandas as pd
import ta  # Bibliothèque pour les indicateurs techniques

# Titre de l'application
st.title("Analyse Technique et Indicateurs Financiers")

# Charger un fichier CSV contenant les données boursières
def load_data_from_csv(file):
    try:
        df = pd.read_csv(file)
        df['Date'] = pd.to_datetime(df['Date'])  # Convertir la colonne 'Date' en datetime si nécessaire
        df.set_index('Date', inplace=True)
        return df
    except Exception as e:
        st.error(f"Erreur de chargement du fichier : {e}")
        return pd.DataFrame()

# Calcul des indicateurs
def compute_indicators(df):
    # Vérification de la présence de la colonne 'Close'
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

# Affichage des données et des graphiques
st.sidebar.header("Paramètres de l'application")
uploaded_file = st.sidebar.file_uploader("Télécharger un fichier CSV", type=["csv"])

# Si un fichier est téléchargé
if uploaded_file is not None:
    df = load_data_from_csv(uploaded_file)

    # Vérifier si les données sont chargées
    if df.empty:
        st.error("Le fichier est vide ou ne contient pas de données valides.")
    else:
        # Calcul des indicateurs
        df = compute_indicators(df)

        # Affichage des 5 premières lignes des données pour vérification
        st.write(df.head())

        # Affichage des graphiques
        st.subheader("Graphique des prix et moyennes mobiles")
        df_chart = df[['Close', 'MA200', 'MA50']]
        st.line_chart(df_chart)

        # Graphique de RSI
        st.subheader("Graphique du RSI")
        st.line_chart(df[['RSI']])

        # Graphique de la distance du prix à la MA200
        st.subheader("Graphique de la distance entre le prix et la MA200")
        st.line_chart(df[['Distance_MA200']])

else:
    st.info("Veuillez télécharger un fichier CSV contenant les données boursières.")











