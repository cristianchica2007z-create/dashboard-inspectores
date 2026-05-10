import pandas as pd
try:
    df = pd.read_excel('BITACORA.xlsx')
    print("BITACORA Columns:", df.columns.tolist())
    if 'prioridad' in df.columns:
        print("Prioridad values:", df['prioridad'].unique().tolist())
    if 'tipo de trabajo' in df.columns:
        print("Tipo de Trabajo values:", df['tipo de trabajo'].unique().tolist())
    
    df_prog = pd.read_excel('PROGRAMACION.xlsx')
    print("PROGRAMACION Columns:", df_prog.columns.tolist())
except Exception as e:
    print("Error:", e)
