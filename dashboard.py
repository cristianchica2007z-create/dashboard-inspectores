import sys
import os
import streamlit as st

# 1. Agregar la carpeta v1 al path para que Python encuentre core_logic.py y otros archivos
v1_path = os.path.join(os.path.dirname(__file__), "v1_streamlit")
if v1_path not in sys.path:
    sys.path.append(v1_path)

# 2. Cambiar el directorio de trabajo para que las imágenes y logos funcionen correctamente
os.chdir(v1_path)

# 3. Ejecutar el dashboard real que está en la subcarpeta
with open("dashboard.py", "r", encoding="utf-8") as f:
    exec(f.read(), globals())