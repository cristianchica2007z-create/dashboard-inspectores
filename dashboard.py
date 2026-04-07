import streamlit as st
import pandas as pd
import os
import plotly.express as px


# -------------------------------------------------
# -------------------------------------------------
# =======================
# LOGIN – BLOQUE ABSOLUTO
# =======================
import json
import os
import streamlit as st


# -------------------------------------------------
# ZONA HORARIA COLOMBIA
# -------------------------------------------------
from zoneinfo import ZoneInfo
import datetime

TZ_CO = ZoneInfo("America/Bogota")

def ahora_colombia():
    return datetime.datetime.now(TZ_CO)




if "usuario" not in st.session_state:
    st.session_state.usuario = None
    st.session_state.rol = None

def cargar_usuarios():
    if os.path.exists("USUARIOS.json"):
        with open("USUARIOS.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

if st.session_state.usuario is None:

    st.markdown("""
        <style>
        .login-card {
            max-width: 420px;
            margin: 4rem auto;
            padding: 2.5rem;
            border-radius: 18px;
            background-color: #ffffff;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }
        .login-title {
            text-align: center;
            font-size: 1.4rem;
            font-weight: 600;
            margin-bottom: 2rem;
            color: #0d3b66;
        }
        </style>
    """, unsafe_allow_html=True)

    st.image("logo.png", width=420)

    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">INICIAR SESIÓN</div>', unsafe_allow_html=True)

    usuarios = cargar_usuarios()

    usuario = st.text_input("Usuario")
    pin = st.text_input("PIN (4 dígitos)", type="password", max_chars=4)

    if st.button("🔐 INICIAR SESIÓN", use_container_width=True):
        if usuario in usuarios and pin == usuarios[usuario]["pin"]:
            st.session_state.usuario = usuario
            st.session_state.rol = usuarios[usuario]["rol"]
            st.rerun()
        else:
            st.error("❌ Usuario o PIN incorrectos")

    st.markdown("</div>", unsafe_allow_html=True)
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
    "CHAVARRIAGA JUAN MANUEL",
    "OSPINA RODRIGUEZ DANIEL ALBERTO",
    "OSPINA CASTELLANOS ANDERSON",
    "RUIZ DILON MARLON ANDREY",
    "RUIZ ARENAS JUAN CAMILO",
    "PATIÑO CIFUENTES RICARDO",
    "VARGAS FRANCO JHON EDISON",
    "CARDONA CANO NELSON",
    "GRISALES CUERVO JUAN DAVID",
    "LEON MARIN LEONARDO FABIO",
    "VELASQUEZ TAPASCO JHON DIEGO",
    "COBO HOYOS JUAN MANUEL",
    "NOREÑA GIRALDO GEOVANNY",
    "GALLEGO CADAVID NORBEY",
    "COGOLLO FIGUEROA RANDY",
    "ARIAS TORO YEISON",
    "MIRANDA FRANCO EFRAIN",
    "ARDILA MORA GUSTAVO ADOLFO",
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
])
# ---------------------------------------------------
# ✅ CONFIGURACIÓN GENERAL DEL DASHBOARD
# ---------------------------------------------------
st.set_page_config(      
    page_title="DASHBOARD INSPECTORES e&c",
       layout="wide"
)

# -------------------------------------------------
# HEADER CON LOGO A LA DERECHA (CORRECTO)
# -------------------------------------------------
col_titulo, col_logo = st.columns([8, 2])

with col_titulo:
    st.markdown(
        "<h1 style='margin-bottom: 0;'>📊 DASHBOARD INSPECTORES e&c</h1>",
        unsafe_allow_html=True
    )

with col_logo:
    st.image(
        "logo.png",
        use_container_width=True,
        caption=""
    )
# ---------------------------------------------------
# ✅ CREAR PESTAÑAS
# ---------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "📦 Inventario Papelería",
    "🕒 Seguimiento Diario",
    "📈 Subir Archivos"
])

# ===================================================
# ✅ TAB 1 — INVENTARIO DE PAPELERÍA (PARTE 1/4)
# Carga y preparación del inventario
# ===================================================
with tab1:
    st.subheader("📦 Control de entrega de papelería e inventario")

    archivo_inventario = "inventario.xlsx"

    # Crear archivo si no existe
    if not os.path.exists(archivo_inventario):
        df_inv = pd.DataFrame(columns=[
            "Fecha", "Sede", "Inspector",
            "Responsable", "Observación", "Ítems"
        ])
        df_inv.to_excel(
            archivo_inventario,
            index=False,
            engine="openpyxl"
        )
    else:
        df_inv = pd.read_excel(
            archivo_inventario,
            engine="openpyxl"
        )

    # Normalizar nombres de columnas
    df_inv.columns = df_inv.columns.str.strip()
    # ===================================================
# ✅ TAB 1 — PARTE 2/4
# Formulario de registro de entrega
# ===================================================
    with st.form("form_entrega", clear_on_submit=True):
        st.markdown("### Registrar entrega")

        col1, col2, col3 = st.columns(3)

        with col1:
            sede = st.selectbox(
                "Sede",
                ["CALDAS", "RISARALDA"],
                key="inv_sede"
            )

        with col2:
            inspector = st.selectbox(
                "Inspector",
                inspectores_lista,
                key="inv_inspector"
            )

        with col3:
            fecha = st.date_input(
                "Fecha",
                key="inv_fecha"
            )

        col4, col5 = st.columns([1, 2])

        with col4:
            responsable = st.selectbox(
                "Responsable",
                [
                    "JUAN DIEGO SANCHEZ",
                    "CRISTIAN CHICA",
                    "ANDRES ARROYAVE",
                    "MARIA CAMILA",
                    "JANIER",
                    "DANNY DE LA CRUZ"
                ],
                key="inv_responsable"
            )

        with col5:
            observacion = st.text_input(
                "Observación (opcional)",
                key="inv_obs"
            )

        # ---------- ÍTEMS ----------
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
                marcar = cols[c_idx].checkbox(
                    item,
                    key=f"item_chk_{f_idx}_{c_idx}"
                )
                cantidad = cols[c_idx].number_input(
                    "Cantidad",
                    min_value=0,
                    step=1,
                    label_visibility="collapsed",
                    key=f"item_qty_{f_idx}_{c_idx}"
                )

                if marcar and cantidad > 0:
                    items_seleccionados.append(
                        f"{item} x{cantidad}"
                    )

        submitted = st.form_submit_button("✅ Guardar entrega")
        # ===================================================
# ✅ TAB 1 — PARTE 3/4
# Guardado y historial
# ===================================================
    if submitted:
        if not items_seleccionados:
            st.warning(
                "⚠️ Debes seleccionar al menos un ítem con cantidad."
            )
        else:
            nueva_fila = pd.DataFrame([{
                "Fecha": fecha.strftime("%Y-%m-%d"),
                "Sede": sede,
                "Inspector": inspector,
                "Responsable": responsable,
                "Observación": observacion,
                "Ítems": ", ".join(items_seleccionados)
            }])

            df_inv = pd.concat(
                [df_inv, nueva_fila],
                ignore_index=True
            )

            df_inv.to_excel(
                archivo_inventario,
                index=False,
                engine="openpyxl"
            )

            st.success("✅ Entrega registrada correctamente")

    # ---------- HISTORIAL ----------
    st.markdown("### 📋 Historial de entregas")

    filtro_inspector = st.selectbox(
        "Filtrar por inspector",
        ["TODOS"] + inspectores_lista,
        key="inv_filtro_inspector"
    )

    df_hist = df_inv.copy()
    if filtro_inspector != "TODOS":
        df_hist = df_hist[
            df_hist["Inspector"] == filtro_inspector
        ]

    st.dataframe(df_hist, use_container_width=True)

    if st.button(
        "💾 Guardar cambios del historial",
        key="inv_guardar_hist"
    ):
        df_inv.to_excel(
            archivo_inventario,
            index=False,
            engine="openpyxl"
        )
        st.success("✅ Cambios del historial guardados")
        # ===================================================
# ✅ TAB 1 — PARTE 4/4
# Consumo mensual consolidado por ítem
# ===================================================
    st.markdown("## 📊 Consumo mensual consolidado por ítem")

    df_cons = df_inv.copy()
    df_cons["Fecha"] = pd.to_datetime(
        df_cons["Fecha"],
        errors="coerce"
    )
    df_cons["Mes"] = (
        df_cons["Fecha"]
        .dt.to_period("M")
        .astype(str)
    )

    registros = []

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
# ✅ TAB 2 — PARTE 1 / 4
# Carga + funciones + normalización
# LEE BITACORA.xlsx DESDE EL REPOSITORIO
# ===================================================
with tab2:
    st.subheader("🕒 Control Operativo e&c")
    st.subheader("Eje Cafetero")
    # -------------------------------------------------
    # VALIDAR QUE EXISTA BITÁCORA COMPARTIDA
    # -------------------------------------------------
    archivo_bitacora = "BITACORA.xlsx"

    if not os.path.exists(archivo_bitacora):
        st.warning(
            "⚠️ No hay una bitácora cargada.\n\n"
            "Un administrador debe subir el archivo en la pestaña "
            "📂 Administración de Bitácora."
        )
        st.stop()

    # -------------------------------------------------
    # CARGAR BITÁCORA COMPARTIDA
    # -------------------------------------------------
    df_bitacora = pd.read_excel(archivo_bitacora)

    # -------------------------------------------------
    # MOSTRAR FECHA Y HORA DE LA ÚLTIMA ACTUALIZACIÓN
    # (FORMA SEGURA – NO ROMPE TAB 2)
    # -------------------------------------------------
    import json

    info_path = "BITACORA_INFO.json"
    ultima_actualizacion = "—"

    try:
        if os.path.exists(info_path):
            with open(info_path, "r", encoding="utc-5") as f:
                info = json.load(f)
                ultima_actualizacion = info.get(
                    "ultima_actualizacion", "—"
                )
    except Exception:
        ultima_actualizacion = "—"

    st.caption(
        f"🕓 Última actualización de la bitácora: "
        f"{ultima_actualizacion}"
    )
    # -------------------------------------------------
    # FUNCIONES UTILITARIAS
    # -------------------------------------------------
    import datetime

    def parse_hora(valor):
        try:
            return pd.to_datetime(valor, format="%H:%M").time()
        except:
            try:
                return pd.to_datetime(str(valor)).time()
            except:
                return None

    def parse_tiempo_tarea(valor):
        try:
            return pd.to_timedelta(str(valor))
        except:
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

    # -------------------------------------------------
    # NORMALIZAR COLUMNAS
    # -------------------------------------------------
    df_bitacora.columns = df_bitacora.columns.str.strip().str.lower()

    columnas_necesarias = [
        "fecha de ejecucion", "hora inicio", "hora final",
        "inspector", "localidad", "cierre", "tiempo de tarea"
    ]

    for col in columnas_necesarias:
        if col not in df_bitacora.columns:
            st.error(f"❌ Falta la columna requerida: {col}")
            st.stop()

    # -------------------------------------------------
    # NORMALIZAR TEXTO
    # -------------------------------------------------
    df_bitacora["inspector"] = (
        df_bitacora["inspector"]
        .astype(str)
        .str.upper()
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

    df_bitacora["localidad"] = (
        df_bitacora["localidad"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    # -------------------------------------------------
    # CONVERTIR FECHAS Y HORAS
    # -------------------------------------------------
    df_bitacora["fecha"] = pd.to_datetime(
        df_bitacora["fecha de ejecucion"], errors="coerce"
    ).dt.date

    df_bitacora["hora_inicio"] = df_bitacora["hora inicio"].apply(parse_hora)
    df_bitacora["hora_final"] = df_bitacora["hora final"].apply(parse_hora)

    df_bitacora["tiempo_tarea_td"] = (
        df_bitacora["tiempo de tarea"].apply(parse_tiempo_tarea)
    )

    # Mantener registros sin hora (SIN HORA)
    df_bitacora["hora_inicio"] = df_bitacora["hora_inicio"].apply(
        lambda x: x if pd.notna(x) else "SIN HORA"
    )
    # ===================================================
    # ✅ TAB 2 — PARTE 2 / 4
    # Supervisores y filtros
    # ===================================================
    supervisores_dict = {k.upper(): v for k, v in {
      "ARIZA MARIN SERGIO": "ANDRES ARROYAVE",
        "ANDRES ARROYAVE": "ANDRES ARROYAVE",
        "BEDOYA DIEGO ALEJANDRO": "DANNY DE LA CRUZ",
        "DANNY DE LA CRUZ": "DANNY DE LA CRUZ",
        "CARVAJAL RESTREPO JUAN DAVID": "JANIER MARIN",
        "JANIER MARIN": "JANIER MARIN",
        "CHAVARRIAGA JUAN MANUEL": "CRISTIAN CHICA",
        "CRISTIAN CHICA": "CRISTIAN CHICA",
        "ECHEVERRY CARDONA JHON STIVEN": "JANIER MARIN",
        "GALLEGO CADAVID NORBEY": "DANNY DE LA CRUZ",
        "GIRALDO GARCIA SIGIFREDO": "ANDRES ARROYAVE",
        "LOPEZ PINEDA CESAR AUGUSTO": "JANIER MARIN",
        "NOREÑA GIRALDO GEOVANNY": "ANDRES ARROYAVE",
        "OSPINA CASTELLANOS ANDERSON": "CRISTIAN CHICA",
        "OSPINA RODRIGUEZ DANIEL ALBERTO": "ANDRES ARROYAVE",
        "RUIZ DILON MARLON ANDREY": "ANDRES ARROYAVE",
        "LARGO OSORIO JOSE OMAR": "ANDRES ARROYAVE",
        "PULGARIN QUINTERO JULIAN ANDRES": "DANNY DE LA CRUZ",
        "TAYACK TRUJILLO DEIVER EVELIO": "ANDRES ARROYAVE",
        "RUIZ ARENAS JUAN CAMILO": "CRISTIAN CHICA",
        "PATIÑO CIFUENTES RICARDO": "JANIER MARIN",
        "VARGAS FRANCO JHON EDISON": "CRISTIAN CHICA",
        "CARDONA CANO NELSON": "CRISTIAN CHICA",
        "CARDONA OROZCO JULIAN ANDRES": "ANDRES ARROYAVE",
        "GRISALES CUERVO JUAN DAVID": "JANIER MARIN",
        "LEON MARIN LEONARDO FABIO": "JANIER MARIN",
        "VELASQUEZ TAPASCO JHON DIEGO": "ANDRES ARROYAVE",
        "CARDONA CASTANO DIDIER ORLANDO": "CRISTIAN CHICA",
        "TORRES HERNANDEZ JOHN JAMES": "ANDRES ARROYAVE",
        "COBO HOYOS JUAN MANUEL": "CRISTIAN CHICA",
        "OSPINA NARANJO BERNARDO": "CRISTIAN CHICA",
        "COGOLLO FIGUEROA RANDY": "DANNY DE LA CRUZ",
        "ARIAS TORO YEISON": "DANNY DE LA CRUZ",
        "MIRANDA FRANCO EFRAIN": "DANNY DE LA CRUZ",
        "ARDILA MORA GUSTAVO ADOLFO": "DANNY DE LA CRUZ",
        "LOPEZ VELEZ ESTEBAN": "JANIER MARIN",
        "GALEANO GRISALEZ RICARDO": "DANNY DE LA CRUZ",
        "CAICEDO ESCOBAR JUNIOR SANTIAGO": "JANIER MARIN",
        "OTERO CAICEDO ANYEMBER": "DANNY DE LA CRUZ",
        "BUITRAGO RAMIREZ LEONARD": "CRISTIAN CHICA",
        "BORJAS WILLY ALEXANDER": "ANDRES ARROYAVE",
        "MARIN LEON JAISSON JOAQUIN": "CRISTIAN CHICA",
        "AMAYA HINCAPIE JUAN CARLOS": "CRISTIAN CHICA",
        "BEDOYA SANCHEZ CRISTIAN DAVID": "ANDRES ARROYAVE",
        "RAMIREZ WILSON ENRIQUE": "CRISTIAN CHICA",
        "CANO MORALES JIMY ALFREDO": "ANDRES ARROYAVE",
        "CASTRO CASTAÑO JUAN DAVID": "CRISTIAN CHICA",
        "LOAIZA GAMBA JHON ALEXANDER": "ANDRES ARROYAVE",
        "VILLA LOAIZA JHEISON ESTIBEN": "CRISTIAN CHICA",
        "CÁRDENAS GALIANO HAROLD MAURICIO": "JANIER MARIN",
        "VARGAS CORREA VICTOR ALFONSO": "DANNY DE LA CRUZ",
        "VILLA MERA CHRISTIAN DAVID": "JANIER MARIN",
        "AVENDAÑO GARCIA JUAN NEPOMUCENO": "ANDRES ARROYAVE",
        "PELAEZ TATIS GABRIEL ESTEBAN": "CRISTIAN CHICA",
    }.items()}

    df_bitacora["supervisor"] = (
        df_bitacora["inspector"]
        .map(supervisores_dict)
        .fillna("SIN SUPERVISOR")
    )

    fechas_validas = sorted(df_bitacora["fecha"].dropna().unique())
    fecha_sel = st.selectbox("Selecciona fecha:", fechas_validas)
    df2 = df_bitacora[df_bitacora["fecha"] == fecha_sel]

    supervisor_sel = st.selectbox(
        "Selecciona supervisor:",
        sorted(df2["supervisor"].unique())
    )
    df2 = df2[df2["supervisor"] == supervisor_sel]

    inspectores_sel = st.multiselect(
        "Selecciona inspectores:",
        sorted(df2["inspector"].unique()),
        default=sorted(df2["inspector"].unique())
    )
    df2 = df2[df2["inspector"].isin(inspectores_sel)]
# ===================================================
# ===================================================
    # ✅ TAB 2 — PARTE 3 / 4
    # Agrupación diaria, puntualidad, producción y KPIs
    # ===================================================

    # ---------------------------------------------------
    # AGRUPACIÓN DIARIA (solo para puntualidad y tabla)
    # ---------------------------------------------------
    primeras = (
        df2.sort_values("hora_inicio")
           .groupby(["inspector", "fecha"], as_index=False)
           .first()[["inspector", "supervisor", "fecha", "hora_inicio", "localidad"]]
    )

    ultimas = (
        df2.sort_values("hora_final")
           .groupby(["inspector", "fecha"], as_index=False)
           .last()[["inspector", "fecha", "hora_final"]]
    )

    df_agrupado = primeras.merge(
        ultimas,
        on=["inspector", "fecha"],
        how="left"
    )

    # ---------------------------------------------------
    # PUNTUALIDAD (usa SOLO la primera hora del día)
    # ---------------------------------------------------
    hora_oficial = datetime.time(7, 30)

    def mins_tarde(h):
        if h == "SIN HORA" or h is None:
            return None
        h1 = datetime.datetime.combine(datetime.date.today(), h)
        h2 = datetime.datetime.combine(datetime.date.today(), hora_oficial)
        return int((h1 - h2).total_seconds() / 60)

    df_agrupado["minutos_tarde"] = df_agrupado["hora_inicio"].apply(mins_tarde)

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
    # ✅ KPI: PROMEDIO HORA DE INICIO (TODAS LAS ÓRDENES)
    # ---------------------------------------------------
    df_ini = df2[
        (df2["hora_inicio"] != "SIN HORA") &
        (df2["hora_inicio"].notna())
    ]

    prom_ini = df_ini["hora_inicio"].apply(hora_to_decimal).mean()
    hora_prom_ini = (
        hora_to_string(decimal_to_hora(prom_ini))
        if pd.notna(prom_ini) else "—"
    )

    # ---------------------------------------------------
    # ✅ KPI: PROMEDIO HORA DE FIN (TODAS LAS ÓRDENES)
    # ---------------------------------------------------
    df_fin = df2[df2["hora_final"].notna()]

    prom_fin = df_fin["hora_final"].apply(hora_to_decimal).mean()
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
                   )
           }))
           .reset_index()
    )

    # ---------------------------------------------------
    # TABLA CONSOLIDADA DEL DÍA (UNA SOLA)
    # ---------------------------------------------------
    df_tabla = df_agrupado.merge(
        resumen,
        on="inspector",
        how="left"
    )

    df_tabla = df_tabla.fillna({
        "hora_inicio": "—",
        "hora_final": "—",
        "localidad": "—",
        "estado": "SIN ACTIVIDAD",
        "total_ordenes": 0,
        "ordenes_efectivas": 0,
        "porcentaje_efectividad": 0,
        "promedio_tiempo_tarea": "—"
    })

    st.markdown("### 📋 Tabla de inspecciones del día")

    st.dataframe(
        df_tabla[
            [
                "inspector",
                "supervisor",
                "fecha",
                "hora_inicio",
                "hora_final",
                "localidad",
                "estado",
                "total_ordenes",
                "ordenes_efectivas",
                "porcentaje_efectividad",
                "promedio_tiempo_tarea"
            ]
        ],
        use_container_width=True
    )


  # ===================================================
    # ✅ TAB 2 — PARTE 4 / 4
    # Gráficas finales
    # ===================================================

    # ---------------------------------------------------
    # PRODUCCIÓN POR INSPECTOR
    # ---------------------------------------------------
    st.markdown("## 📊 Producción por inspector")

    df_prod = (
        df2.groupby("inspector")
           .apply(lambda x: pd.Series({
               "Efectivas": x["efectiva"].sum(),
               "No efectivas": (~x["efectiva"]).sum()
           }))
           .reset_index()
    )

    fig_prod = px.bar(
        df_prod,
        y="inspector",
        x=["Efectivas", "No efectivas"],
        orientation="h",
        barmode="group",
        color_discrete_map={
            "Efectivas": "green",
            "No efectivas": "red"
        }
    )

    fig_prod.update_traces(texttemplate="%{x}", textposition="outside")
    st.plotly_chart(fig_prod, use_container_width=True)

    # ---------------------------------------------------
    # TOP 5 EFECTIVIDAD (USA 'resumen' DE PARTE 3)
    # ---------------------------------------------------
    st.markdown("## 🏆 TOP 5 Inspectores por efectividad")

    df_rank = (
        resumen.sort_values("porcentaje_efectividad", ascending=False)
               .head(5)
    )

    fig_rank = px.bar(
        df_rank,
        x="porcentaje_efectividad",
        y="inspector",
        orientation="h",
        text="porcentaje_efectividad",
        color="porcentaje_efectividad"
    )

    fig_rank.update_traces(texttemplate="%{x}%")
    st.plotly_chart(fig_rank, use_container_width=True)

    # ---------------------------------------------------
    # PRODUCTIVIDAD POR HORA (EFECTIVAS)
    # ---------------------------------------------------
    st.markdown("## ⏱️ Productividad por hora (tareas efectivas)")

    df_horas = df2[df2["efectiva"] == True]

    if df_horas.empty:
        st.info("⚠️ No hay tareas efectivas para esta fecha.")
    else:
        df_horas = df_horas.copy()
        df_horas["hora_str"] = df_horas["hora_inicio"].astype(str)

        horas_prod = (
            df_horas.groupby("hora_str")
                    .size()
                    .reset_index(name="cantidad")
        )

        fig_horas = px.bar(
            horas_prod,
            x="hora_str",
            y="cantidad",
            text="cantidad",
            color="cantidad"
        )

        fig_horas.update_traces(textposition="outside")
        st.plotly_chart(fig_horas, use_container_width=True)
# ---------------------------------------------------
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
    clave_ingresada = st.text_input(
        "Contraseña de administrador",
        type="password",
        placeholder="Ingresa la clave para administrar la bitácora"
    )

    clave_real = st.secrets["admin"]["password"]

    if clave_ingresada != clave_real:
        st.warning(
            "⛔ Acceso restringido.\n\n"
            "Solo personal autorizado puede cargar o actualizar la bitácora."
        )
        st.stop()

    # -------------------------------------------------
    # CONTENIDO SOLO PARA ADMIN
    # -------------------------------------------------
    st.success("✅ Acceso autorizado")

    st.info(
        "Desde aquí se sube la bitácora OFICIAL.\n\n"
        "Al cargar un nuevo archivo, este reemplazará el anterior y "
        "todos los usuarios verán la MISMA información en la pestaña "
        "🕒 Seguimiento Diario (TAB 2), sin volver a cargar archivos."
    )

    archivo = st.file_uploader(
        "Sube el archivo BITACORA.xlsx",
        type=["xls", "xlsx"]
    )

    if archivo is not None:
        import base64
        import requests
        import json
        from datetime import datetime

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
        sha_excel = None
        if r_excel.status_code == 200:
            sha_excel = r_excel.json().get("sha")

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
        # 2️⃣ GUARDAR FECHA Y HORA (BITACORA_INFO.json)
        # =================================================
        info = {
            "ultima_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        contenido_info_b64 = base64.b64encode(
            json.dumps(info, indent=2).encode("utf-8")
        ).decode("utf-8")

        url_info = f"https://api.github.com/repos/{repo}/contents/BITACORA_INFO.json"

        r_info = requests.get(url_info, headers=headers)
        sha_info = None
        if r_info.status_code == 200:
            sha_info = r_info.json().get("sha")

        payload_info = {
            "message": "Actualización de fecha y hora de BITACORA",
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

        # =================================================
        # ✅ CONFIRMACIÓN FINAL
        # =================================================
        st.success("✅ Bitácora actualizada correctamente")
        st.caption(
            f"🕓 Última actualización: {info['ultima_actualizacion']}"
        )
        st.info(
            "La pestaña 🕒 Seguimiento Diario se actualizará automáticamente "
            "para todos los usuarios."
        )
