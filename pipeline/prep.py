import argparse
import os
import pandas as pd

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, required=True, help="CSV d'entrée")
    parser.add_argument("--output", type=str, required=True, help="Dossier de sortie")
    args = parser.parse_args()

    df = pd.read_csv(args.data, index_col=0)
    print("Lignes en entrée :", len(df))

    df = df.dropna()
    df = df.drop_duplicates()

    print("Lignes en sortie :", len(df))

    os.makedirs(args.output, exist_ok=True)
    chemin = os.path.join(args.output, "clean.csv")
    df.to_csv(chemin, index=False)
    print("Fichier écrit :", chemin)

if __name__ == "__main__":
    main()
