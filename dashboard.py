import streamlit as st
import pandas as pd
import os
import plotly.express as px
import json
import datetime
from zoneinfo import ZoneInfo
import base64
import requests
import io
import io

# ---------------------------------------------------
# ✅ CONSTANTES GLOBALES
# ---------------------------------------------------
TZ_CO = ZoneInfo("America/Bogota")
GRUPOS_OPERATIVOS = ["INSP-CALDAS", "INSP-RIS"]
CODIGOS_ADICIONALES = ["12163", "12164", "10793", "12170", "10842", "10772", "10445"]

# Mapeo maestro de inspectores a supervisores
SUPERVISORES_DICT = {k.upper(): v for k, v in {
    "ARIZA MARIN SERGIO": "ANDRES ARROYAVE", "ANDRES ARROYAVE": "ANDRES ARROYAVE",
    "BEDOYA DIEGO ALEJANDRO": "DANNY DE LA CRUZ", "DANNY DE LA CRUZ": "DANNY DE LA CRUZ",
    "CARVAJAL RESTREPO JUAN DAVID": "JANIER MARIN", "JANIER MARIN": "JANIER MARIN",
    "CHAVARRIAGA JUAN MANUEL": "CRISTIAN CHICA", "CRISTIAN CHICA": "CRISTIAN CHICA",
    "ECHEVERRY CARDONA JHON STIVEN": "JANIER MARIN", "GALLEGO CADAVID NORBEY": "DANNY DE LA CRUZ",
    "GIRALDO GARCIA SIGIFREDO": "ANDRES ARROYAVE", "LOPEZ PINEDA CESAR AUGUSTO": "JANIER MARIN",
    "NOREÑA GIRALDO GEOVANNY": "ANDRES ARROYAVE", "OSPINA CASTELLANOS ANDERSON": "CRISTIAN CHICA",
    "OSPINA RODRIGUEZ DANIEL ALBERTO": "ANDRES ARROYAVE", "RUIZ DILON MARLON ANDREY": "ANDRES ARROYAVE",
    "LARGO OSORIO JOSE OMAR": "ANDRES ARROYAVE", "PULGARIN QUINTERO JULIAN ANDRES": "DANNY DE LA CRUZ",
    "TAYACK TRUJILLO DEIVER EVELIO": "ANDRES ARROYAVE", "RUIZ ARENAS JUAN CAMILO": "CRISTIAN CHICA",
    "PATIÑO CIFUENTES RICARDO": "JANIER MARIN", "VARGAS FRANCO JHON EDISON": "CRISTIAN CHICA",
    "CARDONA CANO NELSON": "CRISTIAN CHICA", "CARDONA OROZCO JULIAN ANDRES": "ANDRES ARROYAVE",
    "GRISALES CUERVO JUAN DAVID": "JANIER MARIN", "LEON MARIN LEONARDO FABIO": "JANIER MARIN",
    "VELASQUEZ TAPASCO JHON DIEGO": "ANDRES ARROYAVE", "CARDONA CASTANO DIDIER ORLANDO": "CRISTIAN CHICA",
    "TORRES HERNANDEZ JOHN JAMES": "ANDRES ARROYAVE", "COBO HOYOS JUAN MANUEL": "CRISTIAN CHICA",
    "OSPINA NARANJO BERNARDO": "CRISTIAN CHICA", "COGOLLO FIGUEROA RANDY": "DANNY DE LA CRUZ",
    "ARIAS TORO YEISON": "DANNY DE LA CRUZ", "MIRANDA FRANCO EFRAIN": "DANNY DE LA CRUZ",
    "ARDILA MORA GUSTAVO ADOLFO": "DANNY DE LA CRUZ", "LOPEZ VELEZ ESTEBAN": "JANIER MARIN",
    "GALEANO GRISALEZ RICARDO": "DANNY DE LA CRUZ", "CAICEDO ESCOBAR JUNIOR SANTIAGO": "JANIER MARIN",
    "OTERO CAICEDO ANYEMBER": "DANNY DE LA CRUZ", "BUITRAGO RAMIREZ LEONARD": "CRISTIAN CHICA",
    "BORJAS WILLY ALEXANDER": "ANDRES ARROYAVE", "MARIN LEON JAISSON JOAQUIN": "CRISTIAN CHICA",
    "AMAYA HINCAPIE JUAN CARLOS": "CRISTIAN CHICA", "BEDOYA SANCHEZ CRISTIAN DAVID": "ANDRES ARROYAVE",
    "RAMIREZ WILSON ENRIQUE": "CRISTIAN CHICA", "CANO MORALES JIMY ALFREDO": "ANDRES ARROYAVE",
    "CASTRO CASTAÑO JUAN DAVID": "CRISTIAN CHICA", "LOAIZA GAMBA JHON ALEXANDER": "ANDRES ARROYAVE",
    "VILLA LOAIZA JHEISON ESTIBEN": "CRISTIAN CHICA", "CÁRDENAS GALIANO HAROLD MAURICIO": "JANIER MARIN",
    "VARGAS CORREA VICTOR ALFONSO": "DANNY DE LA CRUZ", "VILLA MERA CHRISTIAN DAVID": "JANIER MARIN",
    "AVENDAÑO GARCIA JUAN NEPOMUCENO": "ANDRES ARROYAVE", "PELAEZ TATIS GABRIEL ESTEBAN": "CRISTIAN CHICA",
    "CHICA RAMIREZ CRISTIAN ALBERTO": "CRISTIAN CHICA"
}.items()}

# ---------------------------------------------------
# ✅ CONFIGURACIÓN GENERAL DEL DASHBOARD
# ---------------------------------------------------
st.set_page_config(
    page_title="DASHBOARD INSPECTORES e&c",
    layout="wide"
)

# -------------------------------------------------
# ✅ FUNCIONES DE CACHÉ (MEJORA DE RENDIMIENTO)
# -------------------------------------------------

@st.cache_data(ttl=600)  # Cache por 10 minutos para datos de GitHub
def fetch_github_excel(repo, path, token, branch="main"):
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json()
        sha = data.get("sha")
        try:
            # Usar download_url es más confiable para archivos binarios y evita el límite de 1MB de la API
            download_url = data.get("download_url")
            if download_url:
                resp = requests.get(download_url, headers=headers)
                content = resp.content
            elif "content" in data:
                content = base64.b64decode(data["content"])
            else:
                return pd.DataFrame(), sha
            
            # Dejamos que pandas detecte el motor (engine) automáticamente para soportar .xls y .xlsx
            return pd.read_excel(io.BytesIO(content)), sha
        except Exception as e:
            st.error(f"❌ Error al procesar el Excel '{path}' desde GitHub: {e}")
            return pd.DataFrame(), sha
    return pd.DataFrame(), None

@st.cache_data(ttl=300)
def fetch_github_json(repo, path, token):
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        try:
            data = r.json()
            content = base64.b64decode(data["content"]).decode("utf-8")
            return json.loads(content), data.get("sha")
        except Exception:
            return {}, None
    return {}, None

@st.cache_data(ttl=600)
def load_local_bitacora(path):
    if os.path.exists(path):
        try:
            df = pd.read_excel(path)
        except Exception:
            return None
            
        df.columns = df.columns.str.strip().str.lower()
        
        # Pre-procesamiento de nombres e inspectores
        if "inspector" in df.columns:
            df["inspector"] = df["inspector"].astype(str).str.upper().str.strip().str.replace(r"\s+", " ", regex=True)
            
        # Mapeo de supervisores usando la constante global
        df["supervisor"] = df["inspector"].map(SUPERVISORES_DICT).fillna("SIN SUPERVISOR")
        
        # Conversión de Fechas y Horas una sola vez
        if "fecha de ejecucion" in df.columns:
            df["fecha"] = pd.to_datetime(df["fecha de ejecucion"], errors="coerce").dt.date
            
        # Parseo de horas (simplificado)
        for col in ["hora inicio", "hora inicio de recorrido", "hora final"]:
            if col in df.columns:
                df[col + "_parsed"] = pd.to_datetime(df[col].astype(str), errors='coerce').dt.time

        if "tiempo de tarea" in df.columns:
            df["tiempo_tarea_td"] = pd.to_timedelta(df["tiempo de tarea"].astype(str), errors="coerce")

        return df
    return None

@st.cache_data(ttl=600)
def process_adicionales_data(df):
    """Procesa los datos de programación de forma cacheada para evitar lentitud en filtros."""
    if df.empty: return df
    df.columns = df.columns.str.strip().str.lower()
    
    # Inicializamos la columna para evitar KeyError si no se encuentra una fecha válida
    df["dias de asignacion"] = 0

    # Filtro de códigos
    if "codigo_tipo_trabajo" in df.columns:
        df = df[df["codigo_tipo_trabajo"].astype(str).isin(CODIGOS_ADICIONALES)]
        
    # Cálculo de fechas (heurística)
    posibles_fechas = [
        "fecha de asignacion", "fecha asignacion", "asignacion", "fecha", 
        "fecha cargue", "fecha programacion", "f_asignacion", "fecha_asignacion"
    ]
    col_fecha = next((c for c in df.columns if c in posibles_fechas), None)
    
    if col_fecha:
        df[col_fecha] = pd.to_datetime(df[col_fecha], errors="coerce")
        hoy = datetime.datetime.now(TZ_CO).date()
        df["dias de asignacion"] = df[col_fecha].apply(lambda x: (hoy - x.date()).days if pd.notna(x) else 0)
    
    return df

@st.cache_data(ttl=600)
def extract_excel_links(path):
    from openpyxl import load_workbook
    if not os.path.exists(path): return pd.DataFrame()
    wb = load_workbook(path, data_only=True)
    ws = wb.active
    headers = [str(cell.value).strip().lower() if cell.value else "" for cell in ws[1]]
    try:
        c_ins, c_fac, c_vp = headers.index("inspector")+1, headers.index("foto de fachada")+1, headers.index("foto de vp")+1
    except ValueError: return pd.DataFrame()
    
    links = []
    for row in ws.iter_rows(min_row=2):
        links.append({
            "inspector": row[c_ins-1].value,
            "link_fachada": row[c_fac-1].hyperlink.target if row[c_fac-1].hyperlink else None,
            "link_vp": row[c_vp-1].hyperlink.target if row[c_vp-1].hyperlink else None
        })
    return pd.DataFrame(links)



# -------------------------------------------------
# ZONA HORARIA COLOMBIA
# -------------------------------------------------



if "usuario" not in st.session_state:
    st.session_state.usuario = None
    st.session_state.rol = None

# --- LÓGICA DE CIERRE DE SESIÓN POR INACTIVIDAD (5 MINUTOS) ---
if "last_activity" not in st.session_state:
    st.session_state.last_activity = datetime.datetime.now()

if st.session_state.usuario is not None:
    ahora = datetime.datetime.now()
    segundos_inactivo = (ahora - st.session_state.last_activity).total_seconds()
    
    if segundos_inactivo > 300:  # 300 segundos = 5 minutos
        st.session_state.usuario = None
        st.session_state.rol = None
        st.warning("⚠️ Sesión cerrada por inactividad (5 minutos).")
        st.rerun()
    st.session_state.last_activity = ahora

def cargar_usuarios():
    if os.path.exists("USUARIOS.json"):
        with open("USUARIOS.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

if st.session_state.usuario is None:
    # Estilos CSS para mejorar la interfaz de inicio de sesión y centrar los elementos
    st.markdown("""
        <style>
        /* Fondo blanco puro para limpieza visual */
        .stApp {
            background-color: #ffffff;
        }
        /* Centrado de los mensajes de error y botones */
        div[data-testid="stVerticalBlock"] > div:has(div.stButton) {
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

    # Layout de columnas para centrar horizontalmente el login
    _, col_login, _ = st.columns([1, 1.5, 1])

    with col_login:
        st.write("") # Espaciado vertical superior
        st.write("")
        
        # El logo ahora se ajusta al contenedor central, garantizando su centrado respecto al formulario
        st.image("logo.png", use_container_width=True)
        
        # Uso de container con borde para crear un efecto de tarjeta (Card)
        with st.container(border=True):
            st.markdown("<h2 style='text-align: center; color: #0d3b66; margin-bottom: 20px;'>INICIAR SESIÓN</h2>", unsafe_allow_html=True)
            
            usuarios = cargar_usuarios()
            usuario = st.text_input("Usuario", placeholder="Tu nombre de usuario")
            pin = st.text_input("PIN", type="password", max_chars=4, placeholder="****")

            st.write("")
            if st.button("🔐 ACCEDER", use_container_width=True, type="primary"):
                if usuario in usuarios and pin == usuarios[usuario]["pin"]:
                    st.session_state.usuario = usuario
                    st.session_state.rol = usuarios[usuario]["rol"]
                    st.rerun()
                else:
                    st.error("❌ Usuario o PIN incorrectos")

    st.stop()

# -------------------------------------------------
# BOTÓN CERRAR SESIÓN
# -------------------------------------------------
col_vacio, col_logout = st.columns([8, 1])

with col_logout:
    if st.button("🚪 Cerrar sesión"):
        st.session_state.usuario = None
        st.session_state.rol = None
        st.rerun()

    
# ---------------------------------------------------
# ✅ LISTA MAESTRA DE INSPECTORES
# ---------------------------------------------------
inspectores_lista = sorted([
  
    "ARIZA MARIN SERGIO",
    "ANDRES ARROYAVE",
    "BEDOYA DIEGO ALEJANDRO",
    "DANNY DE LA CRUZ",
    "CARVAJAL RESTREPO JUAN DAVID",
    "JANIER MARIN",
    "CHAVARRIAGA JUAN MANUEL",
    "CRISTIAN CHICA",
    "ECHEVERRY CARDONA JHON STIVEN",
    "GALLEGO CADAVID NORBEY",
    "GIRALDO GARCIA SIGIFREDO",
    "LOPEZ PINEDA CESAR AUGUSTO",
    "NOREÑA GIRALDO GEOVANNY",
    "OSPINA CASTELLANOS ANDERSON",
    "OSPINA RODRIGUEZ DANIEL ALBERTO",
    "RUIZ DILON MARLON ANDREY",
    "LARGO OSORIO JOSE OMAR",
    "PULGARIN QUINTERO JULIAN ANDRES",
    "TAYACK TRUJILLO DEIVER EVELIO",
    "RUIZ ARENAS JUAN CAMILO",
    "PATIÑO CIFUENTES RICARDO",
    "VARGAS FRANCO JHON EDISON",
    "CARDONA CANO NELSON",
    "CARDONA OROZCO JULIAN ANDRES",
    "GRISALES CUERVO JUAN DAVID",
    "LEON MARIN LEONARDO FABIO",
    "VELASQUEZ TAPASCO JHON DIEGO",
    "CARDONA CASTANO DIDIER ORLANDO",
    "TORRES HERNANDEZ JOHN JAMES",
    "COBO HOYOS JUAN MANUEL",
    "OSPINA NARANJO BERNARDO",
    "COGOLLO FIGUEROA RANDY",
    "ARIAS TORO YEISON",
    "MIRANDA FRANCO EFRAIN",
    "ARDILA MORA GUSTAVO ADOLFO",
    "LOPEZ VELEZ ESTEBAN",
    "GALEANO GRISALEZ RICARDO",
    "CAICEDO ESCOBAR JUNIOR SANTIAGO",
    "OTERO CAICEDO ANYEMBER",
    "BUITRAGO RAMIREZ LEONARD",
    "BORJAS WILLY ALEXANDER",
    "MARIN LEON JAISSON JOAQUIN",
    "AMAYA HINCAPIE JUAN CARLOS",
    "BEDOYA SANCHEZ CRISTIAN DAVID",
    "RAMIREZ WILSON ENRIQUE",
    "CANO MORALES JIMY ALFREDO",
    "CASTRO CASTAÑO JUAN DAVID",
    "LOAIZA GAMBA JHON ALEXANDER",
    "VILLA LOAIZA JHEISON ESTIBEN",
    "CÁRDENAS GALIANO HAROLD MAURICIO",
    "VARGAS CORREA VICTOR ALFONSO",
    "VILLA MERA CHRISTIAN DAVID",
    "AVENDAÑO GARCIA JUAN NEPOMUCENO",
    "PELAEZ TATIS GABRIEL ESTEBAN",
    "CHICA RAMIREZ CRISTIAN ALBERTO",
])
# ---------------------------------------------------
# HEADER CON LOGO A LA DERECHA (CORRECTO)
# -------------------------------------------------
col_titulo, col_logo = st.columns([8, 2])

with col_titulo:
    st.markdown(
        "<h1 style='margin-bottom: 0;'>📊 DASHBOARD INSPECTORES E&C</h1>",
        unsafe_allow_html=True
    )

with col_logo:
    st.image(
        "logo.png",
        use_container_width=True,
        caption=""
    )
# ---------------------------------------------------

# ===================================================
# CARGA ÚNICA DE BITÁCORA (BASE GLOBAL)
# ===================================================
archivo_bitacora = "BITACORA.xlsx"

df_bitacora_base = load_local_bitacora(archivo_bitacora)

if df_bitacora_base is None:
    st.error("❌ No se encontró el archivo BITACORA.xlsx.")
    st.stop()

# ✅ CREAR PESTAÑAS
# ---------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab_inv, tab7 = st.tabs([
    "📦 Inventario Papelería",
    "🕒 Seguimiento Diario",
    "📈 Subir Archivos",
     "📅 Seguimiento agendas",
    "📌 Órdenes Asignadas",
    "🦺 SST",
    "🏭 Inventario V2",
    "🏭 SEGUIMIENTO ADICIONALES",
    

    
])

# ===================================================
# ===================================================
# ✅ TAB 1 — INVENTARIO DE PAPELERÍA
# ===================================================
with tab1:
    st.subheader("📦 Control de entrega de papelería e inventario")

    # ==============================
    # LEER INVENTARIO DESDE GITHUB
    # ==============================
    archivo_inventario = "inventario.xlsx"

    token = st.secrets["github"]["token"]
    repo = st.secrets["github"]["repo"]
    branch = st.secrets["github"].get("branch", "main")

    df_inv, sha_inv = fetch_github_excel(repo, archivo_inventario, token, branch)
    
    if df_inv.empty:
        df_inv = pd.DataFrame(columns=[
            "Fecha", "Sede", "Inspector",
            "Responsable", "Observación", "Ítems"
        ])

    df_inv.columns = df_inv.columns.str.strip()

    # ===================================================
    # FORMULARIO DE REGISTRO
    # ===================================================
    with st.form("form_entrega", clear_on_submit=True):
        st.markdown("### Registrar entrega")

        col1, col2, col3 = st.columns(3)

        sede = col1.selectbox("Sede", ["CALDAS", "RISARALDA"])
        inspector = col2.selectbox("Inspector", inspectores_lista)
        fecha = col3.date_input("Fecha")

        responsable = st.selectbox(
            "Responsable",
            [
                "JUAN DIEGO SANCHEZ",
                "CRISTIAN CHICA",
                "ANDRES ARROYAVE",
                "MARIA CAMILA",
                "JANIER",
                "DANNY DE LA CRUZ"
            ]
        )

        observacion = st.text_input("Observación (opcional)")

        st.markdown("### Ítems entregados")

        items_def = [
            "Stickers 🔵", "Cepo 🔒", "Guantes 🧤", "Piernera 🦿",
            "Monogafas 🥽", "Llaves de cepo 🗝️","Papelería general 📦"
        ]

        items_seleccionados = []

        filas = [items_def[i:i+4] for i in range(0, len(items_def), 4)]
        for f_idx, fila in enumerate(filas):
            cols = st.columns(4)
            for c_idx, item in enumerate(fila):
                marcar = cols[c_idx].checkbox(item, key=f"item_{f_idx}_{c_idx}")
                cantidad = cols[c_idx].number_input(
                    "Cantidad",
                    min_value=0,
                    step=1,
                    label_visibility="collapsed",
                    key=f"qty_{f_idx}_{c_idx}"
                )
                if marcar and cantidad > 0:
                    items_seleccionados.append(f"{item} x{cantidad}")

        submitted = st.form_submit_button("✅ Guardar entrega")

    # ===================================================
    # GUARDAR ENTREGA (SOLO CUANDO SUBMITTED)
    # ===================================================
    if submitted:
        if not items_seleccionados:
            st.warning("⚠️ Debes seleccionar al menos un ítem con cantidad")
        else:
            nueva_fila = pd.DataFrame([{
                "Fecha": fecha.strftime("%Y-%m-%d"),
                "Sede": sede,
                "Inspector": inspector,
                "Responsable": responsable,
                "Observación": observacion,
                "Ítems": ", ".join(items_seleccionados)
            }])

            df_inv = pd.concat([df_inv, nueva_fila], ignore_index=True)

            buffer = io.BytesIO()
            df_inv.to_excel(buffer, index=False, engine="openpyxl")
            buffer.seek(0)

            contenido_b64 = base64.b64encode(buffer.read()).decode("utf-8")
            
            # Para el PUT necesitamos el SHA actual (esto no se cachea para evitar conflictos)
            headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
            url_inv = f"https://api.github.com/repos/{repo}/contents/{archivo_inventario}"
            r = requests.get(url_inv, headers=headers)
            sha = r.json().get("sha") if r.status_code == 200 else None

            payload = {
                "message": "Registro de entrega de papelería",
                "content": contenido_b64,
                "branch": branch
            }

            if sha:
                payload["sha"] = sha

            requests.put(url_inv, headers=headers, json=payload)

            st.cache_data.clear() # Limpiar caché para forzar recarga
            st.success("✅ Entrega registrada y guardada correctamente")

    # ===================================================
    # HISTORIAL (SIEMPRE SE MUESTRA)
    # ===================================================
    st.markdown("### 📋 Historial de entregas")

    filtro_inspector = st.selectbox(
        "Filtrar por inspector",
        ["TODOS"] + inspectores_lista
    )

    df_hist = df_inv.copy()
    if filtro_inspector != "TODOS":
        df_hist = df_hist[df_hist["Inspector"] == filtro_inspector]

    st.dataframe(df_hist, use_container_width=True)

    # ===================================================
    # CONSUMO MENSUAL
    # ===================================================
    st.markdown("## 📊 Consumo mensual consolidado por ítem")

    df_cons = df_inv.copy()
    df_cons["Fecha"] = pd.to_datetime(df_cons["Fecha"], errors="coerce")
    df_cons["Mes"] = df_cons["Fecha"].dt.to_period("M").astype(str)

    registros = []
    for _, row in df_cons.iterrows():
        if pd.isna(row["Ítems"]):
            continue
        for it in row["Ítems"].split(","):
            it = it.strip()
            nombre, cantidad = it.rsplit(" x", 1) if " x" in it else (it, 1)
            registros.append({"Mes": row["Mes"], "Ítem": nombre, "Cantidad": int(cantidad)})

    df_plot = pd.DataFrame(registros)
    if not df_plot.empty:
        df_plot = df_plot.groupby(["Mes", "Ítem"], as_index=False).sum()
        fig = px.bar(df_plot, x="Mes", y="Cantidad", color="Ítem", barmode="group")
        st.plotly_chart(fig, use_container_width=True)

    for _, row in df_cons.iterrows():
        if pd.isna(row["Ítems"]):
            continue

        for it in row["Ítems"].split(","):
            it = it.strip()
            if " x" in it:
                nombre, cantidad = it.rsplit(" x", 1)
                cantidad = int(cantidad)
            else:
                nombre = it
                cantidad = 1

            registros.append({
                "Mes": row["Mes"],
                "Ítem": nombre,
                "Cantidad": cantidad
            })

    df_plot = pd.DataFrame(registros)

    if not df_plot.empty:
        df_plot = df_plot.groupby(
            ["Mes", "Ítem"],
            as_index=False
        ).sum()

        fig = px.bar(
            df_plot,
            x="Mes",
            y="Cantidad",
            color="Ítem",
            barmode="group",
            text="Cantidad",
            title="Consumo mensual consolidado por ítem"
        )

        fig.update_traces(textposition="outside")
        fig.update_layout(
            xaxis_title="Mes",
            yaxis_title="Cantidad entregada",
            legend_title="Ítem"
        )

        st.plotly_chart(fig, use_container_width=True)



# ===================================================
# ===================================================
with tab2:
    st.subheader("🕒 Control Operativo e&c")
    st.subheader("Eje Cafetero")

    # Usar la base ya cargada y procesada
    df_bitacora = df_bitacora_base.copy()
    # Los links si se extraen aparte por ser un proceso distinto (openpyxl)
    df_links = extract_excel_links(archivo_bitacora) 

    if df_bitacora is None or df_links.empty:
        st.error(
            "❌ Error al procesar la bitácora o los enlaces."
        )
        st.stop()

    # -------------------------------------------------
    # ✅ EXCLUIR GRUPOS NO OPERATIVOS
    # -------------------------------------------------
    if "grupo" in df_bitacora.columns:
        df_bitacora["grupo"] = (
            df_bitacora["grupo"]
            .astype(str)
            .str.upper()
            .str.strip()
        )

        grupos_no_operativos = ["SST-NAL", "SUPERVISIONES", "SUSP-ANT"]

        df_bitacora = df_bitacora[
            ~df_bitacora["grupo"].isin(grupos_no_operativos)
        ]

    if df_bitacora.empty:
        st.warning(
            "⚠️ No hay datos disponibles después del filtro por GRUPO.\n"
            "Esto indica que el archivo solo contiene grupos no operativos."
        )
        st.stop()

    # -------------------------------------------------
    # FECHA Y USUARIO DE ÚLTIMA ACTUALIZACIÓN
    # -------------------------------------------------
    TZ_UTC = ZoneInfo("UTC")
    TZ_CO = ZoneInfo("America/Bogota")

    info_path = "BITACORA_INFO.json"
    ultima_actualizacion = "—"
    usuario_actualizo = "—"

    try:
        if os.path.exists(info_path):
            with open(info_path, "r", encoding="utf-8") as f:
                info = json.load(f)

                fecha_utc = datetime.datetime.strptime(
                    info.get("ultima_actualizacion"),
                    "%Y-%m-%d %H:%M:%S"
                ).replace(tzinfo=TZ_UTC)

                fecha_colombia = fecha_utc.astimezone(TZ_CO)

                ultima_actualizacion = fecha_colombia.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                usuario_actualizo = info.get("usuario_actualizo", "—")
    except Exception:
        pass

    st.caption(
        f"🕓 Última actualización: {ultima_actualizacion} "
        f"| 👤 Actualizó: {usuario_actualizo}"
    )

    # -------------------------------------------------
    # FUNCIONES UTILITARIAS DE TIEMPO
    # -------------------------------------------------

    def parse_tiempo_tarea(valor):
        try:
            return pd.to_timedelta(str(valor))
        except Exception:
            return pd.NaT

    def hora_to_decimal(h):
        if h is None or h == "SIN HORA":
            return None
        return h.hour + h.minute / 60 + h.second / 3600

    def decimal_to_hora(d):
        if d is None or pd.isna(d):
            return None
        h = int(d)
        m = int((d - h) * 60)
        return datetime.time(h, m)

    def hora_to_string(h):
        return h.strftime("%I:%M %p") if h else "—"

    def td_to_str(td):
        if pd.isna(td):
            return "—"
        s = int(td.total_seconds())
        h = s // 3600
        m = (s % 3600) // 60
        s2 = s % 60
        return f"{h}h {m}m {s2}s" if h > 0 else f"{m}m {s2}s"

    # Renombrar columnas parseadas para lógica existente
    df_bitacora["hora_inicio"] = df_bitacora["hora inicio_parsed"].fillna("SIN HORA")
    df_bitacora["hora_inicio_recorrido"] = df_bitacora["hora inicio de recorrido_parsed"]
    df_bitacora["hora_final"] = df_bitacora["hora final_parsed"]

    # -------------------------------------------
    # -------------------------------------------
    # FILTRO DE FECHA
    # -------------------------------------------
    fechas_validas = sorted(df_bitacora["fecha"].dropna().unique())
    fecha_sel = st.selectbox("Selecciona fecha:", fechas_validas)

    df2 = df_bitacora[df_bitacora["fecha"] == fecha_sel]


    # -------------------------------------------
    # ⏱️ TIEMPO DE RECORRIDO
    # Diferencia: hora_inicio - hora_inicio_recorrido (por orden)
    # -------------------------------------------

    def calcular_tiempo_recorrido(row):
        hi = row.get("hora inicio_parsed")
        hr = row.get("hora inicio de recorrido_parsed")

        # Si falta cualquiera de las 2 horas, no se puede calcular
        if not isinstance(hi, datetime.time) or not isinstance(hr, datetime.time):
            return pd.NaT

        dt_hi = datetime.datetime.combine(datetime.date.today(), hi)
        dt_hr = datetime.datetime.combine(datetime.date.today(), hr)

        # Evitar negativos por datos inconsistentes
        return dt_hi - dt_hr if dt_hi >= dt_hr else pd.NaT

    # Cálculo por orden (si no existe recorrido queda NaT)
    try:
        df2["tiempo_recorrido_td"] = df2.apply(calcular_tiempo_recorrido, axis=1)
    except Exception:
        df2["tiempo_recorrido_td"] = pd.NaT

    # -------------------------------------------
    # FILTRO DE SUPERVISORES (CHECKLIST TIPO EXCEL ✅)
    # -------------------------------------------
    supervisores_disponibles = sorted(df2["supervisor"].unique())

    with st.expander("Seleccionar supervisores", expanded=True):
        supervisores_sel = []
        for sup in supervisores_disponibles:
            if st.checkbox(
                sup,
                value=True,
                key=f"sup_{fecha_sel}_{sup}"
            ):
                supervisores_sel.append(sup)
    
    # Aplicar el filtro de supervisores a los datos
    df2 = df2[df2["supervisor"].isin(supervisores_sel)]
    
    # Reemplazado st.stop por condicional
    if not supervisores_sel:
        st.warning("⚠️ Selecciona al menos un supervisor para ver datos.")

    elif df2.empty:
        st.warning("⚠️ No hay datos para los supervisores seleccionados.")

    # -------------------------------------------
    # FILTRO DE INSPECTORES (DEPENDIENTE)
    # -------------------------------------------
    inspectores_disponibles = sorted(df2["inspector"].unique())

    inspectores_sel = st.multiselect(
        "Selecciona inspectores:",
        inspectores_disponibles,
        default=inspectores_disponibles
    )

    if not df2.empty:
        df2 = df2[df2["inspector"].isin(inspectores_sel)]

# ===================================================
  # ===================================================
    # ✅ TAB 2 — PARTE 4 / 5
    # Agrupación diaria, puntualidad y estado
    # ===================================================

    # ---------------------------------------------------
    # AGRUPACIÓN DIARIA POR INSPECTOR (ESTABLE)
    # ---------------------------------------------------
    primeras = (
        df2.sort_values("hora_inicio")
        .groupby("inspector", as_index=False)
        .first()[["inspector", "hora_inicio", "localidad", "supervisor"]]
    )

    ultimas = (
        df2.sort_values("hora_final")
        .groupby("inspector", as_index=False)
        .last()[["inspector", "hora_final"]]
    )

    df_agrupado = primeras.merge(
        ultimas,
        on="inspector",
        how="left"
    )

    # ---------------------------------------------------
    # PUNTUALIDAD (usa SOLO la primera hora del día)
    # ---------------------------------------------------
    hora_oficial = datetime.time(7, 30)

    def mins_tarde(h):
        if h is None or pd.isna(h):
            return None
        if not isinstance(h, datetime.time):
            return None

        h1 = datetime.datetime.combine(datetime.date.today(), h)
        h2 = datetime.datetime.combine(datetime.date.today(), hora_oficial)
        return int((h1 - h2).total_seconds() / 60)

    df_agrupado["minutos_tarde"] = df_agrupado["hora_inicio"].apply(mins_tarde)

    # ---------------------------------------------------
    # ESTADO DE PUNTUALIDAD (ORIGINAL)
    # ---------------------------------------------------
    def estado(m):
        if m is None:
            return "SIN INICIO"
        if m <= 0:
            return "Puntual"
        if m <= 15:
            return "Tarde"
        return "Muy tarde"

    df_agrupado["estado"] = df_agrupado["minutos_tarde"].apply(estado)

    # ---------------------------------------------------
    # PRODUCCIÓN (MARCAR ÓRDENES EFECTIVAS)
    # ---------------------------------------------------
    valores_efectivos = [
        "INSPECCIONADA",
        "INSPECCIONADA CON DEFECTO NO CRITICO",
        "INSPECCIONADA CON DEFECTO CRITICO",
        "CERTIFICADA",
        "CERTIFICADA CON NOVEDAD"
    ]

    df2["efectiva"] = df2["cierre"].isin(valores_efectivos)

    total_ordenes = df2.shape[0]
    total_efectivas = df2["efectiva"].sum()

    porcentaje = (
        round((total_efectivas / total_ordenes) * 100, 1)
        if total_ordenes > 0 else 0
    )

    # ---------------------------------------------------
    # ÓRDENES EFECTIVAS CON TIEMPO VÁLIDO
    # ---------------------------------------------------
    df_eff = df2[
        (df2["efectiva"] == True) &
        (df2["tiempo_tarea_td"].notna())
    ]

    # ---------------------------------------------------
    # ✅ KPI: PROMEDIO HORA DE INICIO
    # (PRIMERA TAREA DEL DÍA POR INSPECTOR)
    # ---------------------------------------------------
    df_inicio_jornada = (
        df2[
            (df2["hora_inicio"] != "SIN HORA") &
            (df2["hora_inicio"].notna())
        ]
        .groupby("inspector", as_index=False)
        .agg({"hora_inicio": "min"})
    )

    df_inicio_jornada["ini_dec"] = (
        df_inicio_jornada["hora_inicio"]
        .apply(hora_to_decimal)
    )

    prom_ini = df_inicio_jornada["ini_dec"].mean()

    hora_prom_ini = (
        hora_to_string(decimal_to_hora(prom_ini))
        if pd.notna(prom_ini) else "—"
    )

    # ---------------------------------------------------
    # ✅ KPI: PROMEDIO HORA DE FIN
    # (ÚLTIMA TAREA DEL DÍA POR INSPECTOR)
    # ---------------------------------------------------
    df_fin_jornada = (
        df2[
            df2["hora_final"].notna()
        ]
        .groupby("inspector", as_index=False)
        .agg({"hora_final": "max"})
    )

    df_fin_jornada["fin_dec"] = (
        df_fin_jornada["hora_final"]
        .apply(hora_to_decimal)
    )

    prom_fin = df_fin_jornada["fin_dec"].mean()

    hora_prom_fin = (
        hora_to_string(decimal_to_hora(prom_fin))
        if pd.notna(prom_fin) else "—"
    )

    # ---------------------------------------------------
    # ✅ KPI: PROMEDIO TIEMPO POR TAREA (SOLO EFECTIVAS)
    # ---------------------------------------------------
    tiempo_prom_str = (
        td_to_str(df_eff["tiempo_tarea_td"].mean())
        if not df_eff.empty else "—"
    )

    # ---------------------------------------------------
    # KPIs EN PANTALLA (ORDEN ORIGINAL)
    # ---------------------------------------------------
    st.markdown("## ⭐ KPIs del día")

    c1, c2, c3 = st.columns(3)
    c1.metric("⏰ Promedio inicio", hora_prom_ini)
    c2.metric("🕒 Promedio fin", hora_prom_fin)
    c3.metric("🕓 Prom. tiempo por tarea", tiempo_prom_str)

    c4, c5, c6 = st.columns(3)
    c4.metric("📋 Total tareas", total_ordenes)
    c5.metric("✅ Efectivas", total_efectivas)
    c6.metric("📈 % Efectividad", f"{porcentaje}%")

    # ---------------------------------------------------
    # RESUMEN POR INSPECTOR (SOLO PARA CÁLCULO)
    # ---------------------------------------------------
    # ---------------------------------------------------
    # RESUMEN POR INSPECTOR
    # ---------------------------------------------------
    resumen = (
        df2.groupby("inspector")
        .apply(lambda x: pd.Series({
            "total_ordenes": x.shape[0],
            "ordenes_efectivas": x["efectiva"].sum(),
            "porcentaje_efectividad":
                round((x["efectiva"].sum() / x.shape[0]) * 100, 1)
                if x.shape[0] > 0 else 0,
            "promedio_tiempo_tarea":
                td_to_str(
                    x.loc[x["efectiva"], "tiempo_tarea_td"].mean()
                ),
            "ordenes_sin_recorrido": x["tiempo_recorrido_td"].isna().sum(),
            "promedio_tiempo_recorrido": td_to_str(x["tiempo_recorrido_td"].mean())
        }))
        .reset_index()
    )

    df_tabla = df_agrupado.merge(resumen, on="inspector", how="left")

    df_tabla = df_tabla.fillna({
        "hora_inicio": "—",
        "hora_final": "—",
        "localidad": "—",
        "estado": "SIN ACTIVIDAD",
        "total_ordenes": 0,
        "ordenes_efectivas": 0,
        "ordenes_sin_recorrido": 0,
        "porcentaje_efectividad": 0,
        "promedio_tiempo_tarea": "—",
        "promedio_tiempo_recorrido": "—"
    })

    columnas_tabla = [
        "inspector",
        "supervisor",
        "fecha",
        "hora_inicio",
        "hora_final",
        "localidad",
        "estado",
        "total_ordenes",
        "ordenes_efectivas",
        "ordenes_sin_recorrido",
        "porcentaje_efectividad",
        "promedio_tiempo_tarea",
        "promedio_tiempo_recorrido"
    ]

    # Filtrar solo las que existen para evitar errores
    columnas_disponibles = [c for c in columnas_tabla if c in df_tabla.columns]

    st.markdown("### 📋 Tabla de inspecciones del día")
    st.dataframe(
        df_tabla[columnas_disponibles],
        use_container_width=True,
        hide_index=True
    )

     # ===================================================
 # 🚨 INSPECTORES SIN ACTIVIDAD EN LA FECHA
    # ===================================================
    st.markdown("### 🚨 Inspectores sin actividad registrada")

    inspectores_con_actividad = set(df2["inspector"].str.upper().str.strip().unique())

    inspectores_del_filtro = [
        insp for insp in inspectores_lista
        if SUPERVISORES_DICT.get(insp.upper(), "SIN SUPERVISOR") in supervisores_sel
    ]

    inspectores_sin_actividad = [
        insp for insp in inspectores_del_filtro
        if insp.upper().strip() not in inspectores_con_actividad
    ]

    if inspectores_sin_actividad:
        df_sin_actividad = pd.DataFrame({
            "Inspector": inspectores_sin_actividad
        })
        df_sin_actividad["Supervisor"] = df_sin_actividad["Inspector"].apply(
            lambda x: SUPERVISORES_DICT.get(x.upper(), "SIN SUPERVISOR")
        )
        df_sin_actividad = df_sin_actividad.sort_values("Supervisor")

        st.error(f"🚨 {len(inspectores_sin_actividad)} inspector(es) sin actividad registrada para {fecha_sel}")
        st.dataframe(df_sin_actividad, use_container_width=True)
    else:
        st.success("✅ Todos los inspectores tienen actividad registrada para esta fecha.")

    # ===================================================
    # 📊 Producción por inspector (órdenes efectivas)
  
    # ===================================================
    st.markdown("## 📊 Producción por inspector (órdenes efectivas)")

    df_prod = (
        df2[df2["efectiva"] == True]
        .groupby("inspector")
        .size()
        .reset_index(name="Órdenes efectivas")
        .sort_values("Órdenes efectivas", ascending=True)
    )

    if df_prod.empty:
        st.info("⚠️ No hay órdenes efectivas para esta fecha.")
    else:
        # Colores según producción
        def color_por_produccion(valor):
            if valor <= 3:
                return "#dc3545"      # rojo
            elif valor <= 6:
                return "#f5b7b1"      # rosado
            elif valor <= 8:
                return "#f7dc6f"      # amarillo
            else:
                return "#28a745"      # verde

        df_prod["color"] = df_prod["Órdenes efectivas"].apply(color_por_produccion)

        fig_prod = px.bar(
            df_prod,
            y="inspector",
            x="Órdenes efectivas",
            orientation="h",
            text="Órdenes efectivas",
            title="Órdenes efectivas por inspector"
        )

        # Colores y barras más gruesas
        fig_prod.update_traces(
            marker_color=df_prod["color"],
            textposition="outside",
            textfont_size=28,
            cliponaxis=False
        )

        fig_prod.update_layout(
            bargap=0.15,              # barras más gruesas
            xaxis_title="Órdenes efectivas",
            yaxis_title="Inspector",
            font=dict(size=18),
            height=650
        )

        st.plotly_chart(fig_prod, use_container_width=True)
 

# ===================================================
# ===================================================
# ✅ TAB 3 — ADMINISTRACIÓN DE BITÁCORA (PROTEGIDO)
# Guarda / reemplaza BITACORA.xlsx en GitHub
# Guarda fecha y hora en BITACORA_INFO.json
# ===================================================
with tab3:
    st.subheader("🔐 Administración de Bitácora Compartida")

    # -------------------------------------------------
    # VALIDACIÓN DE ADMINISTRADOR
    # -------------------------------------------------
 #    clave_ingresada = st.text_input(
  #       "Contraseña de administrador",
#         type="password",
#         placeholder="Ingresa la clave para administrar la bitácora"
#     )
# 
#     clave_real = st.secrets["admin"]["password"]

 #    if clave_ingresada != clave_real:
#         st.warning(
#             "⛔ Acceso restringido.\n\n"
#             "Solo personal autorizado puede cargar o actualizar la bitácora."
#         )
 #        st.stop()

    # -------------------------------------------------
    # CONTENIDO SOLO PARA ADMIN
    # -------------------------------------------------
    st.success("✅ Acceso autorizado")

    st.info(
        "Desde aquí se sube la bitácora OFICIAL.\n\n"
        "Al cargar un nuevo archivo, este reemplazará el anterior y "
        "todos los usuarios verán la MISMA información en la pestaña "
        "🕒 Seguimiento Diario (TAB 2)."
    )

    archivo = st.file_uploader(
        "Sube el archivo BITACORA.xlsx",
        type=["xls", "xlsx"]
    )

    if archivo is not None:
        import base64
        import requests
        import json
        import datetime
        from zoneinfo import ZoneInfo

        # -----------------------------
        # ZONA HORARIA
        # -----------------------------
        TZ_UTC = ZoneInfo("UTC")

        # -----------------------------
        # LEER SECRETS DE GITHUB
        # -----------------------------
        token = st.secrets["github"]["token"]
        repo = st.secrets["github"]["repo"]
        branch = st.secrets["github"].get("branch", "main")

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }

        # =================================================
        # 1️⃣ GUARDAR / REEMPLAZAR BITACORA.xlsx
        # =================================================
        contenido_excel = archivo.read()
        contenido_excel_b64 = base64.b64encode(
            contenido_excel
        ).decode("utf-8")

        url_excel = f"https://api.github.com/repos/{repo}/contents/BITACORA.xlsx"

        r_excel = requests.get(url_excel, headers=headers)
        sha_excel = r_excel.json().get("sha") if r_excel.status_code == 200 else None

        payload_excel = {
            "message": "Actualización de BITACORA.xlsx desde Streamlit",
            "content": contenido_excel_b64,
            "branch": branch
        }

        if sha_excel:
            payload_excel["sha"] = sha_excel

        r_put_excel = requests.put(
            url_excel,
            headers=headers,
            json=payload_excel
        )

        if r_put_excel.status_code not in (200, 201):
            st.error("❌ Error al guardar BITACORA.xlsx en GitHub")
            st.json(r_put_excel.json())
            st.stop()

        # =================================================
        # 2️⃣ GUARDAR FECHA, HORA Y USUARIO (BITACORA_INFO.json)
        # =================================================
        info = {
            "ultima_actualizacion": datetime.datetime.now(TZ_UTC).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "usuario_actualizo": st.session_state.usuario
        }

        contenido_info_b64 = base64.b64encode(
            json.dumps(info, indent=2).encode("utf-8")
        ).decode("utf-8")

        url_info = f"https://api.github.com/repos/{repo}/contents/BITACORA_INFO.json"

        r_info = requests.get(url_info, headers=headers)
        sha_info = r_info.json().get("sha") if r_info.status_code == 200 else None

        payload_info = {
            "message": "Actualización de BITACORA_INFO.json",
            "content": contenido_info_b64,
            "branch": branch
        }

        if sha_info:
            payload_info["sha"] = sha_info

        requests.put(
            url_info,
            headers=headers,
            json=payload_info
        )

        st.cache_data.clear() # IMPORTANTÍSIMO: Limpiar caché al subir nueva bitácora
        # =================================================
        # ✅ CONFIRMACIÓN FINAL
        # =================================================
        st.success("✅ Bitácora actualizada correctamente")
        st.caption(f"🕓 Hora UTC guardada: {info['ultima_actualizacion']}")

  # =================================================
#PESTAÑA 4 SEGUIMIENTO AGENDAS
with tab4:
    # ======================================================
    # TÍTULO PRINCIPAL
    # ======================================================
    st.markdown("## 🗂️ Control agendas")

    # ======================================================
    # CARGAR BITÁCORA DESDE GITHUB (FORMA CORRECTA)
    # ======================================================
    archivo_bitacora = "BITACORA.xlsx"
    token = st.secrets["github"]["token"]
    repo = st.secrets["github"]["repo"]

    df, _ = fetch_github_excel(repo, archivo_bitacora, token)
    if not df.empty:
        # ======================================================
        # NORMALIZAR Y VALIDAR COLUMNAS
        # ======================================================
        df.columns = df.columns.str.strip().str.lower()

        columnas_req = [
            "grupo", "prioridad", "estado",
            "fecha de visita", "fecha de ejecucion",
            "inspector", "contrato", "direccion",
            "localidad", "detalle de tarea"
        ]

        # Verificar columnas antes de procesar
        faltantes = [c for c in columnas_req if c not in df.columns]
        if faltantes:
            st.error(f"❌ Faltan columnas requeridas en el archivo: {faltantes}")
        else:
            # ======================================================
            # FILTRO FIJO DE GRUPO
            # ======================================================
            df["grupo"] = df["grupo"].astype(str).str.upper().str.strip()
            grupos_validos = ["INSP-CALDAS", "INSP-RIS"]
            df = df[df["grupo"].isin(grupos_validos)].copy()

            # ======================================================
            # FECHAS Y ALERTAS
            # ======================================================
            df["fecha de visita"] = pd.to_datetime(df["fecha de visita"], errors="coerce")
            df["fecha de ejecucion"] = pd.to_datetime(df["fecha de ejecucion"], errors="coerce")

            ahora_colombia = datetime.datetime.now(ZoneInfo("America/Bogota")).replace(tzinfo=None)

            df["estado_alerta"] = df["fecha de visita"].apply(
                lambda x: "ALERTA" if pd.notna(x) and x <= ahora_colombia else "OK"
            )

            columnas_base = ["inspector", "contrato", "direccion", "estado", "fecha de visita", "localidad", "detalle de tarea", "estado_alerta"]

            t_fin, t_prox, t_pen = st.tabs(["✅ Finalizadas", "⏳ Próximas", "🚨 Pendientes"])

            with t_fin:
                st.markdown("### ✅ Agendas finalizadas")
                zonas_sel = []
                with st.expander("Seleccionar Zona"):
                    for z in grupos_validos:
                        if st.checkbox(z, value=True, key=f"fin_zona_{z}"):
                            zonas_sel.append(z)

                inicios_sel = []
                with st.expander("Filtrar por inicio de la tarea"):
                    for i in ["INICIO TARDE", "INICIO A TIEMPO"]:
                        if st.checkbox(i, value=True, key=f"fin_inicio_{i}"):
                            inicios_sel.append(i)

                df_final = df[df["estado"].str.upper() == "FINALIZADA"].copy()
                if zonas_sel:
                    df_final = df_final[df_final["grupo"].isin(zonas_sel)]

                def evaluar_inicio_tarde(row):
                    if pd.isna(row["fecha de ejecucion"]) or pd.isna(row["fecha de visita"]):
                        return "SIN DATO"
                    limite = row["fecha de visita"] + pd.Timedelta(minutes=15)
                    return "INICIO TARDE" if row["fecha de ejecucion"] > limite else "INICIO A TIEMPO"

                df_final["inicio_tarea"] = df_final.apply(evaluar_inicio_tarde, axis=1)
                if inicios_sel:
                    df_final = df_final[df_final["inicio_tarea"].isin(inicios_sel)]

                if df_final.empty:
                    st.info("✅ No hay agendas finalizadas con esos filtros.")
                else:
                    st.dataframe(df_final[columnas_base[:-1] + ["inicio_tarea"]].sort_values("fecha de visita"), use_container_width=True)

            with t_prox:
                st.markdown("### ⏳ Agendas próximas (no iniciadas)")
                df_prox = df[(df["estado"].str.upper() == "ASIGNADA") & (df["fecha de ejecucion"].isna()) & (df["fecha de visita"] > ahora_colombia)].copy()
                if df_prox.empty:
                    st.info("✅ No hay agendas próximas.")
                else:
                    st.dataframe(df_prox[columnas_base].sort_values("fecha de visita"), use_container_width=True)

            with t_pen:
                st.markdown("### 🚨 Agendas en ALERTA")
                df_alerta = df[(df["estado"].str.upper() == "ASIGNADA") & (df["prioridad"].str.upper() == "ALTA") & (df["estado_alerta"] == "ALERTA")].copy()
                if df_alerta.empty:
                    st.info("✅ No hay agendas en ALERTA.")
                else:
                    st.dataframe(df_alerta[columnas_base].sort_values("fecha de visita"), use_container_width=True)
                    st.error(f"🚨 TOTAL ALERTAS: {len(df_alerta)}")
    else:
        st.info("No se pudo cargar la bitácora desde GitHub para agendas.")

    # ======================================================
    # ⏳ PRÓXIMAS (NO INICIADAS)
    # ======================================================
    with t_prox:
        st.markdown("### ⏳ Agendas próximas (no iniciadas)")

        zonas_sel = []
        with st.expander("Seleccionar Zona"):
            for z in grupos_validos:
                if st.checkbox(z, value=True, key=f"prox_zona_{z}"):
                    zonas_sel.append(z)

        df_prox = df[
            (df["estado"].str.upper() == "ASIGNADA") &
            (df["fecha de ejecucion"].isna()) &
            (df["fecha de visita"] > ahora_colombia)
        ].copy()

        if zonas_sel:
            df_prox = df_prox[df_prox["grupo"].isin(zonas_sel)]

        if df_prox.empty:
            st.info("✅ No hay agendas próximas.")
        else:
            st.dataframe(
                df_prox[columnas_base].sort_values("fecha de visita"),
                use_container_width=True
            )

    # ======================================================
    # 🚨 PENDIENTES (ALERTAS REALES)
    # ======================================================
    with t_pen:
        st.markdown("### 🚨 Agendas en ALERTA")

        zonas_sel = []
        with st.expander("Seleccionar Zona"):
            for z in grupos_validos:
                if st.checkbox(z, value=True, key=f"pen_zona_{z}"):
                    zonas_sel.append(z)

        df_alerta = df[
            (df["estado"].str.upper() == "ASIGNADA") &
            (df["prioridad"].str.upper() == "ALTA") &
            (df["estado_alerta"] == "ALERTA")
        ].copy()

        if zonas_sel:
            df_alerta = df_alerta[df_alerta["grupo"].isin(zonas_sel)]

        if df_alerta.empty:
            st.info("✅ No hay agendas en ALERTA para la zona seleccionada.")
        else:
            st.dataframe(
                df_alerta[columnas_base].sort_values("fecha de visita"),
                use_container_width=True
            )
            st.error(f"🚨 TOTAL ALERTAS: {len(df_alerta)}")
with tab5:
    st.markdown("## 📌 Órdenes ASIGNADAS")

    # ===================================================
    # VALIDAR Y CARGAR BITÁCORA LOCAL
    # ===================================================
    archivo_bitacora = "BITACORA.xlsx"

    df = df_bitacora_base.copy()
    
    # ===================================================
    # ✅ FILTRAR SOLO GRUPOS PERMITIDOS
    # ===================================================
    if "grupo" in df.columns:
        df["grupo"] = df["grupo"].astype(str).str.upper().str.strip()

        grupos_permitidos = GRUPOS_OPERATIVOS
        df = df[df["grupo"].isin(grupos_permitidos)]

        # ===================================================
        # VALIDAR COLUMNAS NECESARIAS
    # ===================================================
    columnas_requeridas = ["inspector", "estado", "prioridad", "grupo"]
    for col in columnas_requeridas:
        if col not in df.columns:
            st.error(f"❌ Falta la columna requerida: {col}")

    # ===================================================
    # FILTRAR SOLO ÓRDENES ASIGNADAS
    # ===================================================
    df_asignadas = df[
        df["estado"]
        .astype(str)
        .str.contains("Asignad", case=False, na=False)
    ].copy()

    if df_asignadas.empty:
        st.info("✅ No hay órdenes ASIGNADAS en la bitácora.")

    # ===================================================
    # ================= FILTROS =================
    # ===================================================
    st.markdown("### 🔎 Filtros")

    # -------- FILTRO POR GRUPO --------
    grupos_disponibles = sorted(df_asignadas["grupo"].dropna().unique())
    grupos_sel = []

    with st.expander("Seleccionar Grupo", expanded=True):
        for g in grupos_disponibles:
            if st.checkbox(g, value=True, key=f"tab5_grupo_{g}"):
                grupos_sel.append(g)

    if grupos_sel:
        df_asignadas = df_asignadas[df_asignadas["grupo"].isin(grupos_sel)]

    # -------- FILTRO POR PRIORIDAD --------
    prioridades_disponibles = sorted(df_asignadas["prioridad"].dropna().unique())
    prioridades_sel = []

    with st.expander("Seleccionar Prioridad", expanded=True):
        for p in prioridades_disponibles:
            if st.checkbox(p, value=True, key=f"tab5_prio_{p}"):
                prioridades_sel.append(p)

    if prioridades_sel:
        df_asignadas = df_asignadas[df_asignadas["prioridad"].isin(prioridades_sel)]

    if df_asignadas.empty:
        st.warning("⚠️ No hay datos con los filtros seleccionados.")

    # ===================================================
    # AGRUPAR POR INSPECTOR Y PRIORIDAD (DATOS REALES)
    # ===================================================
    df_prio = (
        df_asignadas
        .groupby(["inspector", "prioridad"])
        .size()
        .reset_index(name="cantidad")
    )

    # Ordenar inspectores por carga total
    orden_inspectores = (
        df_prio.groupby("inspector")["cantidad"]
        .sum()
        .sort_values(ascending=False)
        .index
        .tolist()
    )

    # ===================================================
    # MAPA DE COLORES POR PRIORIDAD
    # ===================================================
    color_prioridad = {
        "Alta": "#dc3545",        # 🔴 rojo
        "Media": "#ffc107",       # 🟡 amarillo
        "Baja": "#7cd992",        # 🟢 verde claro
        "Critica": "#fd7e14",     # 🟠 naranja
        "Prioridad": "#6f4e37",    # 🟤 café
        
        "60 Meses": "#6f42c1",        # 🟣 morado
        "Segunda visita": "#ff8c00"   # 🟠 naranja

    }

    # ===================================================
    # GRÁFICA ACUMULADA
    # ===================================================
    fig = px.bar(
        df_prio,
        y="inspector",
        x="cantidad",
        color="prioridad",
        orientation="h",
        category_orders={"inspector": orden_inspectores},
        color_discrete_map=color_prioridad,
        text="cantidad",
        title="Órdenes ASIGNADAS por inspector (según filtros)"
    )

    fig.update_traces(
        textposition="inside",
        textfont_size=16
    )

    fig.update_layout(
        barmode="stack",
        xaxis_title="Cantidad de órdenes ASIGNADAS",
        yaxis_title="Inspector",
        legend_title="Prioridad",
        height=700
    )

    st.plotly_chart(fig, use_container_width=True)


    # ===================================================
    df_sst = df_bitacora_base.copy()


    # ---------------------------------------------------
    # ✅ TAB 6 — SST (Placeholder logic)
    # ---------------------------------------------------
with tab6:
    st.subheader("🦺 Seguridad y Salud en el Trabajo")
    st.info("Visualización de registros SST operativos.")
    # Filtro insensible a mayúsculas para asegurar que se encuentre la información
    df_sst_view = df_bitacora_base[df_bitacora_base["grupo"].astype(str).str.upper().str.contains("SST", na=False)]
    if not df_sst_view.empty:
        st.dataframe(df_sst_view, use_container_width=True, hide_index=True)
    else:
        st.warning("⚠️ No se encontraron registros con el grupo 'SST' en la bitácora.")

# ===================================================
# ✅ TAB_INV — INVENTARIO V2
# ===================================================
with tab_inv:
    st.markdown("# 🏭 Sistema de Gestión de Inventario V2")

    # --- 1. CONSTANTES Y CONFIGURACIÓN ---
    SEDES_INV = ["CALDAS", "RISARALDA"]
    RESPONSABLES_INV = ["CRISTIAN CHICA", "JANIER", "JENNY", "CAMILA", "ANDRES", "DANNY"]
    
    CATALOGO_DEFAULT = {
        "EPPs": {
            "Monogafas":  {"tallas": False},
            "Guantes":    {"tallas": False},
            "Piernera":   {"tallas": False},
        },
        "Dotación": {
            "Botas":    {"tallas": True, "opciones_talla": ["36","37","38","39","40","41","42","43","44","45","46"]},
            "Camisa":   {"tallas": True, "opciones_talla": ["XS","S","M","L","XL","XXL"]},
            "Pantalón": {"tallas": True, "opciones_talla": ["28","30","32","34","36","38","40"]},
            "Chaleco":  {"tallas": True, "opciones_talla": ["XS","S","M","L","XL","XXL"]},
        },
        "Papelería": {
            "Isométricos (paquete x200)": {"tallas": False},
            "Stickers":                   {"tallas": False},
            "Papelería general":          {"tallas": False},
        },
        "Herramientas": {
            "Cepo":           {"tallas": False},
            "Llaves de cepo": {"tallas": False},
        },
    }

    inv_token = st.secrets["github"]["token"]
    inv_repo  = st.secrets["github"]["repo"]
    inv_branch = st.secrets["github"].get("branch", "main")

    # --- 3. CÁLCULO DE STOCK DINÁMICO ---
    def obtener_stock_df(movs_list, sede_filtro):
        data_stock = {}
        relevant_movs = [m for m in movs_list if m.get("sede") == sede_filtro]
        
        for m in relevant_movs:
            key = (m["categoria"], m["item"], m.get("talla") or "N/A")
            if key not in data_stock:
                data_stock[key] = {"Entradas": 0, "Salidas": 0}
            
            if m["tipo"] == "ENTRADA":
                data_stock[key]["Entradas"] += m["cantidad"]
            else:
                data_stock[key]["Salidas"] += m["cantidad"]
        
        rows = []
        for (cat, item, talla), vals in data_stock.items():
            rows.append({
                "Categoría": cat,
                "Ítem": item,
                "Talla": talla,
                "Entradas": vals["Entradas"],
                "Salidas": vals["Salidas"],
                "Stock": vals["Entradas"] - vals["Salidas"]
            })
        return pd.DataFrame(rows)

    # --- 4. INTERFAZ DE USUARIO ---
    sub_tab1, sub_tab2, sub_tab3, sub_tab4 = st.tabs([
        "📊 Stock Actual", 
        "🔄 Registrar Movimiento", 
        "📜 Historial", 
        "⚙️ Configuración"
    ])

    with sub_tab1:
        sede_consulta = st.selectbox("Filtrar por Sede", SEDES_INV, key="inv_sede_stock")
        df_stock = obtener_stock_df(movimientos, sede_consulta)
        
        if not df_stock.empty:
            st.dataframe(df_stock.sort_values(["Categoría", "Ítem"]), use_container_width=True, hide_index=True)
            
            # Alertas de Stock Bajo
            bajo_stock = df_stock[df_stock["Stock"] <= 3]
            if not bajo_stock.empty:
                st.warning(f"⚠️ Hay {len(bajo_stock)} ítems con stock crítico (≤ 3 unidades)")
        else:
            st.info(f"No hay movimientos registrados para la sede {sede_consulta}.")

    with sub_tab2:
        st.subheader("Registrar Entrada o Salida")
        with st.form("form_movimiento_v2", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            m_tipo = c1.selectbox("Tipo de Movimiento", ["ENTRADA", "SALIDA"])
            m_sede = c2.selectbox("Sede", SEDES_INV)
            m_fecha = c3.date_input("Fecha Movimiento")
            
            c4, c5 = st.columns(2)
            m_resp = c4.selectbox("Responsable", RESPONSABLES_INV)
            m_insp = c5.selectbox("Inspector (Solo Salidas)", ["N/A"] + inspectores_lista)
            
            st.divider()
            c6, c7, c8, c9 = st.columns([2,2,1,1])
            cat_sel = c6.selectbox("Categoría", list(catalogo.keys()))
            item_sel = c7.selectbox("Ítem", list(catalogo[cat_sel].keys()))
            
            talla_sel = "N/A"
            if catalogo[cat_sel][item_sel]["tallas"]:
                talla_sel = c8.selectbox("Talla", catalogo[cat_sel][item_sel]["opciones_talla"])
            else:
                c8.text_input("Talla", "N/A", disabled=True)
                
            m_cant = c9.number_input("Cantidad", min_value=1, step=1)
            m_obs = st.text_input("Observaciones")
            
            if st.form_submit_button("💾 Guardar Movimiento", type="primary"):
                # Validaciones
                error = False
                if m_tipo == "SALIDA":
                    df_current = obtener_stock_df(movimientos, m_sede)
                    stock_actual = 0
                    if not df_current.empty:
                        match = df_current[(df_current["Categoría"] == cat_sel) & 
                                          (df_current["Ítem"] == item_sel) & 
                                          (df_current["Talla"] == talla_sel)]
                        if not match.empty:
                            stock_actual = match.iloc[0]["Stock"]
                    
                    if m_cant > stock_actual:
                        st.error(f"❌ Stock insuficiente. Disponible: {stock_actual}")
                        error = True
                
                if not error:
                    nuevo_mov = {
                        "tipo": m_tipo,
                        "fecha": str(m_fecha),
                        "timestamp": datetime.datetime.now(TZ_CO).strftime("%Y-%m-%d %H:%M:%S"),
                        "sede": m_sede,
                        "responsable": m_resp,
                        "categoria": cat_sel,
                        "item": item_sel,
                        "talla": talla_sel if talla_sel != "N/A" else None,
                        "cantidad": m_cant,
                        "observacion": m_obs,
                        "inspector": m_insp if m_insp != "N/A" else None
                    }
                    
                    movimientos.append(nuevo_mov)
                    resp = save_github_json(inv_repo, "MOVIMIENTOS.json", inv_token, movimientos, f"Nuevo movimiento: {m_tipo} {item_sel}", inv_branch)
                    
                    if resp.status_code in (200, 201):
                        st.success("✅ Movimiento registrado correctamente.")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("❌ Error al guardar en la base de datos de GitHub.")

    with sub_tab3:
        st.subheader("Historial de Movimientos")
        if movimientos:
            df_h = pd.DataFrame(movimientos)
            st.dataframe(df_h.sort_values("timestamp", ascending=False), use_container_width=True, hide_index=True)
        else:
            st.info("No hay movimientos registrados.")

    with sub_tab4:
        st.subheader("Configuración de Catálogo")
        
        with st.expander("Ver Catálogo Actual"):
            st.json(catalogo)
            
        st.markdown("### ➕ Agregar Nuevo Ítem")
        with st.form("form_config_cat", clear_on_submit=True):
            c1, c2 = st.columns(2)
            n_cat = c1.selectbox("Categoría Destino", list(catalogo.keys()))
            n_item = c2.text_input("Nombre del Ítem")
            n_tallas = st.checkbox("¿Maneja tallas?")
            n_opciones = st.text_input("Opciones de Talla (separadas por coma, ej: S,M,L)")
            
            if st.form_submit_button("Añadir al Catálogo"):
                if n_item:
                    catalogo[n_cat][n_item] = {
                        "tallas": n_tallas,
                        "opciones_talla": [x.strip() for x in n_opciones.split(",")] if n_tallas else []
                    }
                    save_github_json(inv_repo, "CATALOGO.json", inv_token, catalogo, f"Añadido {n_item} al catálogo", inv_branch)
                    st.success(f"Ítem {n_item} añadido correctamente.")
                    st.rerun()
                else:
                    st.error("El nombre del ítem es obligatorio.")

# ===================================================
# ✅ TAB 7 — SEGUIMIENTO ADICIONALESs
# ===================================================
with tab7:
    st.subheader("🏭 Seguimiento de Adicionales")

    # --- CONFIGURACIÓN DE PERSISTENCIA EN GITHUB ---
    token_ad = st.secrets["github"]["token"]
    repo_ad = st.secrets["github"]["repo"]
    branch_ad = st.secrets["github"].get("branch", "main")
    nombre_archivo_git = "PROGRAMACION.xlsx"

    # --- SECCIÓN PARA ACTUALIZAR EL ARCHIVO (Sincronizado con GitHub) ---
    with st.expander("⬆️ Actualizar Base de Datos de Programación"):
        archivo_nuevo = st.file_uploader(
            "Sube el nuevo archivo PROGRAMACION.xlsx para actualizar el dashboard global",
            type=["xlsx", "xls"],
            key="uploader_adicionales_github"
        )
        if st.button("🚀 Guardar y compartir con el equipo", key="btn_subir_adicionales"):
            if archivo_nuevo is not None:
                contenido_bin = archivo_nuevo.read()
                contenido_b64_ad = base64.b64encode(contenido_bin).decode("utf-8")
                
                url_ad = f"https://api.github.com/repos/{repo_ad}/contents/{nombre_archivo_git}"
                headers_ad = {"Authorization": f"Bearer {token_ad}", "Accept": "application/vnd.github+json"}
                
                # Obtener el SHA actual para permitir el reemplazo (evita conflictos de versión)
                resp_get = requests.get(url_ad, headers=headers_ad)
                sha_ad = resp_get.json().get("sha") if resp_get.status_code == 200 else None
                
                payload_ad = {
                    "message": "Actualización global de PROGRAMACION.xlsx desde Dashboard",
                    "content": contenido_b64_ad,
                    "branch": branch_ad
                }
                if sha_ad: payload_ad["sha"] = sha_ad
                
                resp_put = requests.put(url_ad, headers=headers_ad, json=payload_ad)
                if resp_put.status_code in (200, 201):
                    st.success("✅ Archivo guardado correctamente en la nube. Ahora todos los usuarios verán esta versión.")
                    st.cache_data.clear() # Limpiar caché para forzar la lectura del nuevo archivo
                    st.rerun()
                else:
                    st.error(f"❌ Error al sincronizar con GitHub: {resp_put.text}")
            else:
                st.warning("⚠️ Por favor selecciona un archivo antes de intentar guardar.")

    # --- CARGA DEL ARCHIVO DESDE GITHUB (Datos compartidos) ---
    df_p, _ = fetch_github_excel(repo_ad, nombre_archivo_git, token_ad, branch_ad)
    
    # Procesamiento cacheado para mayor velocidad
    df_p = process_adicionales_data(df_p)

    if not df_p.empty:
        # --- FILTRO DE SEDE (CARGUE) ---
        if "cargue" in df_p.columns:
            sedes_raw = sorted(df_p["cargue"].astype(str).unique().tolist())
            sedes_opciones = ["TODAS"] + sedes_raw
            sedes_sel = st.selectbox("📍 Seleccionar Sede (Cargue):", sedes_opciones, key="filtro_sede_adicionales")
            
            if sedes_sel != "TODAS":
                df_p = df_p[df_p["cargue"].astype(str) == sedes_sel]

        # Selección de columnas y visualización (Fuera del bloque 'if cargue' para mayor robustez)
        cols_req = ["contrato", "nombre_inspector", "direccion barrio", "codigo_tipo_trabajo", "cargue", "dias de asignacion"]
        cols_final = [c for c in cols_req if c in df_p.columns]
        
        def color_semaforo(row):
            # Verificación segura de la existencia de la columna calculada
            if "dias de asignacion" not in row:
                return [""] * len(row)
            dias = row["dias de asignacion"]
            if dias < 3:
                return ["background-color: #d4edda; color: #155724"] * len(row)  # Verde
            elif dias == 3:
                return ["background-color: #fff3cd; color: #856404"] * len(row)  # Amarillo
            else:
                return ["background-color: #f8d7da; color: #721c24"] * len(row)  # Rojo

        st.dataframe(df_p[cols_final].style.apply(color_semaforo, axis=1), use_container_width=True, hide_index=True)
    else:
        st.info("ℹ️ No hay un archivo de programación activo. Utiliza el panel superior para subir 'PROGRAMACION.xlsx'.")
