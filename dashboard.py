import sys
import os
import streamlit as st

# 1. Agregar la carpeta v1 al path para que Python encuentre core_logic.py y otros archivos
v1_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "v1_streamlit")
if v1_path not in sys.path:
    sys.path.append(v1_path)

# 2. Ejecutar el dashboard real que está en la subcarpeta
# Nota: No cambiamos el directorio (chdir) para que el script encuentre USUARIOS.json y logos en la raíz
dashboard_script = os.path.join(v1_path, "dashboard.py")
with open(dashboard_script, "r", encoding="utf-8") as f:
    exec(f.read(), globals())