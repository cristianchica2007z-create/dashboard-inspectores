import pandas as pd
try:
    df_prog = pd.read_excel('PROGRAMACION.xlsx')
    if 'CARTERA' in df_prog.columns:
        print("CARTERA column unique values:", df_prog['CARTERA'].unique().tolist())
    
    df_bit = pd.read_excel('BITACORA.xlsx')
    if 'PRIORIDAD' in df_bit.columns:
        print("PRIORIDAD column unique values:", df_bit['PRIORIDAD'].unique().tolist())
    if 'TIPO DE TRABAJO' in df_bit.columns:
        print("TIPO DE TRABAJO column unique values:", df_bit['TIPO DE TRABAJO'].unique().tolist()[:10])
except Exception as e:
    print("Error:", e)
