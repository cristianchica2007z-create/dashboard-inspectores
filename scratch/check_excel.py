import pandas as pd
import requests
import io

TOKEN = "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"
REPO = "cristianchica2007z-create/dashboard-inspectores"
PATH = "BITACORA.xlsx"

def check():
    headers = {"Authorization": f"Bearer {TOKEN}"}
    url = f"https://api.github.com/repos/{REPO}/contents/{PATH}"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json()
        resp = requests.get(data['download_url'], headers=headers)
        df = pd.read_excel(io.BytesIO(resp.content))
        print("Columnas encontradas:", df.columns.tolist())
        print("\nPrimeros valores de la columna 'SUPERVISOR' (si existe):")
        if 'SUPERVISOR' in [c.upper() for c in df.columns]:
            col = [c for c in df.columns if c.upper() == 'SUPERVISOR'][0]
            print(df[col].unique())
        else:
            print("No se encontró columna de Supervisor")

if __name__ == "__main__":
    check()
