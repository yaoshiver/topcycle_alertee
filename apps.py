import pandas as pd
import ta

def compute_indicators(df):
    # Vérification de la présence de la colonne "Close"
    if "Close" not in df.columns:
        raise KeyError("La colonne 'Close' n'existe pas dans le DataFrame initial")

    # Affichage des colonnes du DataFrame pour débogage
    print("Colonnes disponibles dans df avant calcul : ", df.columns)

    # Calcul des moyennes mobiles
    df["MA200"] = df["Close"].rolling(window=200).mean()
    df["MA111"] = df["Close"].rolling(window=111).mean()
    df["MA350_2"] = df["Close"].rolling(window=350).mean() * 2

    # Calcul de la Distance_MA200 uniquement si MA200 est non-NaN
    df["Distance_MA200"] = None
    df.loc[df["MA200"].notna(), "Distance_MA200"] = ((df["Close"] - df["MA200"]) / df["MA200"]) * 100

    # Vérification de la colonne "Close" avant d'appeler dropna()
    if "Close" in df.columns:
        df_clean = df.dropna(subset=["Close"])
    else:
        raise KeyError("La colonne 'Close' n'est plus présente dans le DataFrame après traitement")

    # Calcul de l'indicateur RSI
    rsi_indicator = ta.momentum.RSIIndicator(df_clean["Close"], window=14)
    df_clean["RSI"] = rsi_indicator.rsi()

    # Vérification de l'existence de la colonne "RSI" avant de l'ajouter au DataFrame
    if "RSI" in df_clean.columns:
        df["RSI"] = df_clean["RSI"]
    else:
        raise KeyError("L'indicateur RSI n'a pas été calculé correctement")

    # Vérification de la présence de la colonne "MA200"
    if "MA200" not in df.columns:
        raise KeyError("La colonne 'MA200' est manquante dans le DataFrame après traitement")

    return df

# Exemple de DataFrame pour tester
data = {
    'Close': [150, 152, 153, 154, 155, 153, 156, 157, 158, 159],
}
df = pd.DataFrame(data)

# Test de la fonction compute_indicators
try:
    df = compute_indicators(df)
    print(df)
except Exception as e:
    print("Erreur:", e)







