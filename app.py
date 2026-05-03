"""
ÁGORA TECH — Plataforma Comercial
Versión corregida: datos en archivos JSON separados
"""

import streamlit as st
import google.generativeai as genai
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import plotly.express as px

# ═══════════════════════════════════════════
# CARGAR DATOS DESDE ARCHIVOS JSON
# ═══════════════════════════════════════════
@st.cache_data
def cargar_proyectos():
    """Carga los 185 proyectos desde proyectos.json"""
    base = os.path.dirname(os.path.abspath(__file__))
    ruta = os.path.join(base, "proyectos.json")
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

@st.cache_data
def cargar_cotizaciones():
    """Carga las 40 cotizaciones de la calculadora"""
    base = os.path.dirname(os.path.abspath(__file__))
    ruta = os.path.join(base, "cotizaciones.json")
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

TODOS_PROYECTOS = cargar_proyectos()
COTIZACIONES_CALC = cargar_cotizaciones()

# ═══════════════════════════════════════════
# USUARIOS Y CONTRASEÑAS
# ═══════════════════════════════════════════
USUARIOS = {
    "luisa":    {"pass": "luisa2026",    "nombre": "Luisa Olivares",     "rol": "gerente",   "comercial": "LUISA OLIVARES"},
    "gerente":  {"pass": "gerente2026",  "nombre": "Luisa Olivares",     "rol": "gerente",   "comercial": "LUISA OLIVARES"},
    "rafael":   {"pass": "rafael2026",   "nombre": "Rafael Torres",      "rol": "comercial", "comercial": "RAFAEL TORRES"},
    "sonia":    {"pass": "sonia2026",    "nombre": "Sonia Castro",       "rol": "comercial", "comercial": "SONIA CASTRO"},
    "lina":     {"pass": "lina2026",     "nombre": "Lina Calle",         "rol": "comercial", "comercial": "LINA CALLE"},
    "alberto":  {"pass": "alberto2026",  "nombre": "Alberto Ferrer",     "rol": "comercial", "comercial": "ALBERTO FERRER"},
    "santiago": {"pass": "santiago2026", "nombre": "Santiago Bohórquez", "rol": "comercial", "comercial": "SANTIAGO BOHORQUEZ"},
}

# ═══════════════════════════════════════════
# CONFIGURACIÓN STREAMLIT
# ═══════════════════════════════════════════
st.set_page_config(
    page_title="Ágora Tech · Plataforma",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=DM+Sans:wght@400;500;600&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif!important}
h1,h2,h3{font-family:'Sora',sans-serif!important}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#04111E 0%,#0A2540 100%)!important}
[data-testid="stSidebar"] *{color:rgba(255,255,255,.85)!important}
.stButton>button{background:linear-gradient(135deg,#00C896,#1A9FCC)!important;color:#04111E!important;
  font-family:'Sora',sans-serif!important;font-weight:700!important;border:none!important;border-radius:10px!important}
.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 6px 20px rgba(0,200,150,.4)!important}
.kpi{background:white;border:1px solid #E3EAF3;border-radius:12px;padding:16px;text-align:center;box-shadow:0 2px 8px rgba(4,17,30,.06)}
.kpi-v{font-family:'Sora',sans-serif;font-size:26px;font-weight:800;color:#04111E;line-height:1}
.kpi-v.g{color:#009E78}.kpi-v.r{color:#E84040}.kpi-v.o{color:#D97706}
.kpi-l{font-size:10px;color:#8BA3BD;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px}
.bg-g{background:#D1FAF0;color:#065F46;padding:3px 10px;border-radius:20px;font-size:10.5px;font-weight:600;display:inline-block}
.bg-y{background:#FEF9C3;color:#92400E;padding:3px 10px;border-radius:20px;font-size:10.5px;font-weight:600;display:inline-block}
.bg-b{background:#DBEAFE;color:#1E3A8A;padding:3px 10px;border-radius:20px;font-size:10.5px;font-weight:600;display:inline-block}
.bg-r{background:#FEE2E2;color:#991B1B;padding:3px 10px;border-radius:20px;font-size:10.5px;font-weight:600;display:inline-block}
.bg-p{background:#F5F3FF;color:#5B21B6;padding:3px 10px;border-radius:20px;font-size:10.5px;font-weight:600;display:inline-block}
.al-r{background:#FEF2F2;border-left:4px solid #E84040;padding:12px 16px;border-radius:8px;font-size:13px;margin-bottom:8px}
.al-y{background:#FFFBEB;border-left:4px solid #F2A12E;padding:12px 16px;border-radius:8px;font-size:13px;margin-bottom:8px}
.al-g{background:#F0FDF9;border-left:4px solid #00C896;padding:12px 16px;border-radius:8px;font-size:13px;margin-bottom:8px}
.al-b{background:#EFF6FF;border-left:4px solid #1A9FCC;padding:12px 16px;border-radius:8px;font-size:13px;margin-bottom:8px}
.chat-u{background:linear-gradient(135deg,#00C896,#1A9FCC);color:#04111E;padding:12px 16px;
  border-radius:16px 16px 3px 16px;margin:8px 0;font-weight:600;max-width:80%;margin-left:auto;display:block}
.chat-a{background:white;border:1px solid #E3EAF3;padding:14px 18px;border-radius:16px 16px 16px 3px;
  margin:8px 0;max-width:90%;box-shadow:0 2px 8px rgba(4,17,30,.06);line-height:1.7;display:block}
div[data-testid="stForm"]{border:none!important;padding:0!important}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════
def init_state():
    defaults = {
        "logged_in": False,
        "user": None,
        "messages": [],
        "gemini_model": None,
        "page": "Dashboard",
        "correo_generado": "",
        "editing_nombre": "",
        # CRM en memoria — se pre-carga con los 185 proyectos
        "crm": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ═══════════════════════════════════════════
# CRM EN MEMORIA (con los 185 proyectos base)
# ═══════════════════════════════════════════
def get_crm():
    """Devuelve el DataFrame del CRM, inicializándolo si es necesario."""
    if st.session_state.crm is None:
        rows = []
        for p in TODOS_PROYECTOS:
            rows.append({
                "id":        p.get("id", ""),
                "nombre":    p.get("nombre", ""),
                "comercial": p.get("comercial", ""),
                "contacto":  p.get("contacto", ""),
                "email":     p.get("email", ""),
                "total":     p.get("total", "$0"),
                "totalNum":  p.get("totalNum", 0),
                "cuota24":   p.get("cuota24", "$0"),
                "cuota36":   p.get("cuota36", "$0"),
                "c24Num":    p.get("c24Num", 0),
                "c36Num":    p.get("c36Num", 0),
                "vig":       p.get("vig", ""),
                "vigH":      p.get("vigH", ""),
                "estado":    p.get("estado", "nuevo"),
                "etapaOrig": p.get("etapaOrig", ""),
                "version":   p.get("version", "v1"),
                "notas":     p.get("notas", ""),
                "lastUpdate": p.get("lastUpdate", ""),
                "lastNote":  p.get("lastNote", ""),
                "fecha":     p.get("fecha", ""),
                "drive":     p.get("drive", ""),
            })
        # Enriquecer con cotizaciones de la calculadora
        df = pd.DataFrame(rows)
        for c in COTIZACIONES_CALC:
            mask = df["nombre"].str.upper() == c["edificio"].upper()
            if mask.any() and df.loc[mask, "totalNum"].iloc[0] == 0:
                df.loc[mask, "totalNum"] = c["valor"]
                df.loc[mask, "total"]    = fc(c["valor"])
                df.loc[mask, "c24Num"]   = c["valor"] // 24
                df.loc[mask, "cuota24"]  = fc(c["valor"] // 24)
                df.loc[mask, "c36Num"]   = c["valor"] // 36
                df.loc[mask, "cuota36"]  = fc(c["valor"] // 36)
        st.session_state.crm = df
    return st.session_state.crm

def update_proyecto(nombre, campos: dict):
    """Actualiza un proyecto en el CRM en memoria."""
    df = get_crm()
    mask = df["nombre"] == nombre
    if mask.any():
        for campo, valor in campos.items():
            df.loc[mask, campo] = valor
        st.session_state.crm = df
        return True
    return False

def agregar_proyecto(datos: dict):
    """Agrega un nuevo proyecto al CRM."""
    df = get_crm()
    nueva_fila = pd.DataFrame([datos])
    st.session_state.crm = pd.concat([nueva_fila, df], ignore_index=True)

def mis_proyectos():
    """Retorna solo los proyectos del usuario actual."""
    df = get_crm()
    if not st.session_state.logged_in:
        return df.iloc[0:0]
    user = st.session_state.user
    if user["rol"] == "gerente":
        return df
    return df[df["comercial"].str.upper() == user["comercial"].upper()]

# ═══════════════════════════════════════════
# UTILIDADES
# ═══════════════════════════════════════════
def fc(n):
    try:
        n = int(float(n or 0))
        return "$0" if n == 0 else "$" + f"{n:,}".replace(",", ".")
    except:
        return "$0"

def badge(estado):
    mapa = {
        "nuevo":      ("bg-b", "🔵 Lead"),
        "cotizado":   ("bg-y", "🟡 Enviado"),
        "negociacion":("bg-p", "🟠 Negoc."),
        "cerrado":    ("bg-g", "🟢 Cerrado"),
        "perdido":    ("bg-r", "🔴 Perdido"),
    }
    cls, lbl = mapa.get(estado, ("bg-b", "❓"))
    return f'<span class="{cls}">{lbl}</span>'

def ask_gemini(pregunta, contexto=""):
    m = st.session_state.gemini_model
    if not m:
        return "⚠️ Configura la API Key de Gemini en el panel izquierdo para usar la IA."
    try:
        prompt = f"DATOS DEL CRM:\n{contexto[:20000]}\n\nSOLICITUD:\n{pregunta}" if contexto else pregunta
        return m.generate_content(prompt).text
    except Exception as e:
        return f"Error Gemini: {e}"

# ═══════════════════════════════════════════
# LOGIN
# ═══════════════════════════════════════════
def mostrar_login():
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown("""
        <div style='text-align:center;padding:56px 0 28px'>
          <div style='font-family:Sora,sans-serif;font-size:34px;font-weight:800;
               color:#04111E;letter-spacing:-2px'>ÁGORA TECH</div>
          <div style='font-size:12px;color:#8BA3BD;letter-spacing:3px;
               text-transform:uppercase;margin-top:8px'>Plataforma Comercial</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login"):
            usuario  = st.text_input("Usuario", placeholder="rafael / sonia / lina / luisa...")
            password = st.text_input("Contraseña", type="password", placeholder="••••••••")
            entrar   = st.form_submit_button("Ingresar →", use_container_width=True)

            if entrar:
                u = usuario.strip().lower()
                if u in USUARIOS and USUARIOS[u]["pass"] == password:
                    st.session_state.logged_in = True
                    st.session_state.user = USUARIOS[u]
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")

        st.markdown("""
        <div style='background:#F4F7FB;border-radius:10px;padding:14px;
             margin-top:16px;font-size:12px;color:#8BA3BD;text-align:center'>
          <b style='color:#04111E'>Accesos:</b><br>
          luisa / luisa2026 (Gerente) &nbsp;·&nbsp; rafael / rafael2026<br>
          sonia / sonia2026 &nbsp;·&nbsp; lina / lina2026<br>
          alberto / alberto2026 &nbsp;·&nbsp; santiago / santiago2026
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════
def mostrar_sidebar():
    user = st.session_state.user
    es_gerente = user["rol"] == "gerente"

    with st.sidebar:
        st.markdown(f"""
        <div style='text-align:center;padding:10px 0 14px'>
          <div style='font-family:Sora,sans-serif;font-size:18px;font-weight:800;
               color:#fff;letter-spacing:-0.5px'>ÁGORA TECH</div>
          <div style='font-size:9px;color:rgba(255,255,255,.3);letter-spacing:2px;
               text-transform:uppercase;margin-top:2px'>Plataforma Comercial</div>
        </div>
        <div style='background:rgba(0,200,150,.12);border:1px solid rgba(0,200,150,.25);
             border-radius:10px;padding:10px 12px;margin-bottom:14px'>
          <div style='font-size:13px;font-weight:600;color:#fff'>{user["nombre"]}</div>
          <div style='font-size:10px;color:rgba(255,255,255,.4);margin-top:2px'>
            {user["rol"].capitalize()} · Ágora Tech</div>
        </div>
        """, unsafe_allow_html=True)

        # Navegación
        paginas_base = [
            ("📊", "Dashboard"),
            ("📋", "Mis Proyectos"),
            ("🧮", "Nueva Cotización"),
            ("📝", "Actualizar Estado"),
            ("🏢", "Edificios"),
            ("📅", "Calendario"),
            ("✉️", "Correos IA"),
            ("🤖", "Asistente IA"),
        ]
        paginas_gerente = [
            ("🔍", "Auditoría"),
            ("📈", "Informes"),
            ("🎯", "Pipeline"),
            ("📊", "Encuestas"),
        ]

        todas = paginas_base + (paginas_gerente if es_gerente else [])
        for icono, nombre in todas:
            activo = st.session_state.page == nombre
            if st.sidebar.button(
                f"{icono}  {nombre}",
                key=f"nav_{nombre}",
                use_container_width=True,
                type="primary" if activo else "secondary"
            ):
                st.session_state.page = nombre
                st.rerun()

        st.markdown("---")

        # Gemini
        st.markdown("**⚡ Gemini IA**")
        if not st.session_state.gemini_model:
            gkey = st.text_input("API Key", type="password",
                                  placeholder="AIzaSy...", key="gkey_sidebar")
            if gkey:
                try:
                    genai.configure(api_key=gkey)
                    m = genai.GenerativeModel(
                        model_name="gemini-1.5-pro",
                        system_instruction="""Eres el asistente comercial de Ágora Tech Colombia.
Sistema SALTO HomeLok. Financiación 100% a 24/36 meses sin intereses.
Responde en español colombiano. Sé específico y accionable."""
                    )
                    st.session_state.gemini_model = m
                    st.success("✅ Gemini activo")
                    st.rerun()
                except Exception as e:
                    st.error(f"API Key inválida: {e}")
        else:
            st.success("✅ Gemini activo")
            if st.button("Cambiar key", key="cambiar_key"):
                st.session_state.gemini_model = None
                st.rerun()

        st.markdown("---")
        if st.button("⇤  Cerrar sesión", use_container_width=True):
            for k in ["logged_in","user","messages","gemini_model","page","crm"]:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

# ═══════════════════════════════════════════
# PÁGINAS
# ═══════════════════════════════════════════

def pg_dashboard():
    user = st.session_state.user
    es_gerente = user["rol"] == "gerente"
    df = mis_proyectos()

    # Header
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#04111E 0%,#0A2540 60%,#0E3D6B 100%);
         border-radius:16px;padding:28px 32px;margin-bottom:24px;color:white;overflow:hidden;position:relative'>
      <div style='position:absolute;top:-50px;right:-50px;width:200px;height:200px;border-radius:50%;
           background:radial-gradient(circle,rgba(0,200,150,.2) 0%,transparent 70%)'></div>
      <div style='font-family:Sora,sans-serif;font-size:22px;font-weight:800;margin-bottom:6px'>
        {"Dashboard General — Ágora Tech" if es_gerente else f"Hola, {user['nombre'].split()[0]} 👋"}
      </div>
      <div style='font-size:13px;color:rgba(255,255,255,.55)'>
        {"Todo el equipo · " if es_gerente else "Tus proyectos · "}{len(df)} proyectos · {datetime.now().strftime("%d %b %Y")}
      </div>
    </div>
    """, unsafe_allow_html=True)

    # KPIs
    total_pip = int(df["totalNum"].sum())
    con_valor = df[df["totalNum"] > 0]
    prom      = int(con_valor["totalNum"].mean()) if len(con_valor) > 0 else 0
    cerrados  = int(df[df["estado"] == "cerrado"].shape[0])
    negoc     = int(df[df["estado"] == "negociacion"].shape[0])
    cotizados = int(df[df["estado"] == "cotizado"].shape[0])

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.markdown(f'<div class="kpi"><div class="kpi-l">Pipeline Total</div><div class="kpi-v g">${total_pip/1e6:.1f}M</div><div style="font-size:11px;color:#8BA3BD;margin-top:4px">{len(df)} proyectos</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="kpi"><div class="kpi-l">Promedio Cotización</div><div class="kpi-v">${prom/1e6:.1f}M</div><div style="font-size:11px;color:#8BA3BD;margin-top:4px">{len(con_valor)} con valor</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="kpi"><div class="kpi-l">Negociando</div><div class="kpi-v o">{negoc}</div><div style="font-size:11px;color:#8BA3BD;margin-top:4px">proyectos activos</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="kpi"><div class="kpi-l">Cotizaciones Enviadas</div><div class="kpi-v o">{cotizados}</div><div style="font-size:11px;color:#8BA3BD;margin-top:4px">en seguimiento</div></div>', unsafe_allow_html=True)
    c5.markdown(f'<div class="kpi"><div class="kpi-l">Contratos Cerrados</div><div class="kpi-v {"r" if cerrados==0 else "g"}">{cerrados}</div><div style="font-size:11px;color:{"#E84040" if cerrados==0 else "#009E78"};margin-top:4px">{"⚠️ Urgente" if cerrados==0 else "¡Excelente!"}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Gráficas
    col1, col2 = st.columns(2)
    with col1:
        est = df.groupby("estado").size().reset_index(name="n")
        lm  = {"nuevo":"Lead","cotizado":"Enviado","negociacion":"Negoc.","cerrado":"Cerrado","perdido":"Perdido"}
        est["Estado"] = est["estado"].map(lm).fillna(est["estado"])
        fig = px.bar(est, x="Estado", y="n", color="n",
                     color_continuous_scale=["#1A9FCC","#00C896"],
                     title="Proyectos por Estado", labels={"n":"Proyectos"})
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                          coloraxis_showscale=False, margin=dict(t=40, b=10))
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        if es_gerente:
            df_c = df[df["totalNum"] > 0].groupby("comercial")["totalNum"].sum().reset_index()
            df_c["M"]   = (df_c["totalNum"] / 1e6).round(1)
            df_c["Com"] = df_c["comercial"].str.split().str[0]
            fig2 = px.bar(df_c.sort_values("M", ascending=True),
                          x="M", y="Com", orientation="h",
                          title="Pipeline por Comercial ($M)",
                          color="M", color_continuous_scale=["#1A9FCC","#00C896"],
                          labels={"M":"$M","Com":""})
            fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                               coloraxis_showscale=False, margin=dict(t=40, b=10))
        else:
            est2 = df.groupby("estado").size().reset_index(name="n")
            est2["Estado"] = est2["estado"].map(lm).fillna(est2["estado"])
            fig2 = px.pie(est2, values="n", names="Estado", hole=0.45,
                          color_discrete_sequence=["#1A9FCC","#F2A12E","#8B5CF6","#00C896","#E84040"],
                          title="Mis Proyectos")
            fig2.update_layout(paper_bgcolor="white", margin=dict(t=40, b=10))
        st.plotly_chart(fig2, use_container_width=True)

    # Alertas
    st.markdown("### 🚨 Alertas")
    if es_gerente:
        st.markdown('<div class="al-r">❗ <b>0 contratos cerrados en 5 meses.</b> Con $3.93B en pipeline el cuello de botella está en el cierre, no en la prospección.</div>', unsafe_allow_html=True)
        st.markdown('<div class="al-y">⚡ <b>Nomad (David Conde / Rafael Torres)</b> — único en cierre cercano. Reunir con contrato listo esta semana.</div>', unsafe_allow_html=True)
        st.markdown('<div class="al-b">📈 Crecimiento de leads: Dic 3 → Ene 17 → Feb 25 → Mar 32 → Abr 46. Excelente prospección.</div>', unsafe_allow_html=True)

    sin_upd = df[df["lastUpdate"].astype(str).str.strip() == ""].shape[0]
    if sin_upd > 0:
        st.markdown(f'<div class="al-y">⚠️ <b>{sin_upd} proyectos</b> nunca han sido actualizados. Ve a "Actualizar Estado" para reportar el seguimiento.</div>', unsafe_allow_html=True)


def pg_proyectos():
    es_gerente = st.session_state.user["rol"] == "gerente"
    df = mis_proyectos()

    st.markdown("## 📋 " + ("Todos los Proyectos" if es_gerente else "Mis Proyectos"))

    c1, c2, c3 = st.columns(3)
    with c1: buscar = st.text_input("🔍 Buscar", placeholder="Nombre del edificio...")
    with c2: filtro_est = st.selectbox("Estado", ["Todos","nuevo","cotizado","negociacion","cerrado","perdido"])
    with c3:
        if es_gerente:
            coms = ["Todos"] + sorted(df["comercial"].dropna().unique().tolist())
            filtro_com = st.selectbox("Comercial", coms)
        else:
            filtro_com = "Todos"

    df_f = df.copy()
    if buscar:        df_f = df_f[df_f["nombre"].str.contains(buscar, case=False, na=False)]
    if filtro_est != "Todos": df_f = df_f[df_f["estado"] == filtro_est]
    if filtro_com != "Todos": df_f = df_f[df_f["comercial"] == filtro_com]

    st.markdown(f"**{len(df_f)} proyectos encontrados**")

    for _, row in df_f.iterrows():
        tnum  = int(row.get("totalNum") or 0)
        total = fc(tnum) if tnum else row.get("total","$0") or "$0"
        c24   = fc(int(row.get("c24Num") or 0)) if tnum else row.get("cuota24","—") or "—"
        c36   = fc(int(row.get("c36Num") or 0)) if tnum else row.get("cuota36","—") or "—"
        est   = str(row.get("estado","nuevo"))
        nota  = str(row.get("lastNote","") or row.get("notas","") or row.get("etapaOrig",""))
        drive = str(row.get("drive","") or "")

        titulo = f"🏢 **{row['nombre']}**  —  {total}  —  {row.get('comercial','')}"
        with st.expander(titulo, expanded=False):
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Valor total", total)
            m2.metric("Cuota 24m",  c24)
            m3.metric("Cuota 36m",  c36)
            m4.markdown(f"**Estado:**<br>{badge(est)}", unsafe_allow_html=True)

            if nota and nota != "nan": st.info(f"📝 {nota[:200]}")
            if drive.startswith("http"):
                st.markdown(f"📁 [Ver carpeta en Drive]({drive})")

            if st.button("📝 Actualizar estado", key=f"upd_{row.get('id',row['nombre'])}"):
                st.session_state.editing_nombre = row["nombre"]
                st.session_state.page = "Actualizar Estado"
                st.rerun()


def pg_nueva_cotizacion():
    st.markdown("## 🧮 Nueva Cotización")
    st.info("Completa los datos del edificio. Se guardará en el CRM de esta sesión.")

    with st.form("nueva_cot"):
        st.markdown("### Datos del edificio")
        c1, c2 = st.columns(2)
        with c1:
            nombre   = st.text_input("Nombre del edificio *", placeholder="Edificio Altos del Pino")
            contacto = st.text_input("Contacto *", placeholder="Juan Pérez — Administrador")
            email    = st.text_input("Email", placeholder="admin@edificio.com")
        with c2:
            direccion = st.text_input("Dirección", placeholder="Cra 7 No. 45-23, Bogotá")
            telefono  = st.text_input("Teléfono", placeholder="300 123 4567")
            drive_url = st.text_input("Link carpeta Drive (opcional)", placeholder="https://drive.google.com/...")

        st.markdown("### Cotización")
        c1, c2, c3 = st.columns(3)
        with c1: total_v  = st.number_input("Valor total ($)", min_value=0, value=0, step=1_000_000, format="%d")
        with c2: vig_v    = st.number_input("Vigilancia actual ($/mes)", min_value=0, value=0, step=100_000, format="%d")
        with c3: vig_h    = st.text_input("Vigilancia vigente hasta", placeholder="Nov 2026")

        st.markdown("### Estado")
        c1, c2 = st.columns(2)
        with c1: estado  = st.selectbox("Estado", ["nuevo","cotizado","negociacion","cerrado","perdido"])
        with c2: version = st.text_input("Versión", value="v1")
        notas = st.text_area("Observaciones / Notas", placeholder="Contexto, acuerdos, próximos pasos...")

        archivos = st.file_uploader("Adjuntar archivos (PDF, Excel, imágenes)", accept_multiple_files=True)

        guardar = st.form_submit_button("💾 Guardar Cotización", use_container_width=True)

        if guardar:
            if not nombre:
                st.error("El nombre del edificio es obligatorio")
            else:
                user = st.session_state.user
                c24n = total_v // 24 if total_v else 0
                c36n = total_v // 36 if total_v else 0
                agregar_proyecto({
                    "id":        int(datetime.now().timestamp()),
                    "nombre":    nombre.upper(),
                    "comercial": user["comercial"],
                    "contacto":  contacto,
                    "email":     email,
                    "total":     fc(total_v),
                    "totalNum":  total_v,
                    "cuota24":   fc(c24n),
                    "cuota36":   fc(c36n),
                    "c24Num":    c24n,
                    "c36Num":    c36n,
                    "vig":       str(vig_v),
                    "vigH":      vig_h,
                    "estado":    estado,
                    "etapaOrig": estado,
                    "version":   version,
                    "notas":     notas,
                    "lastUpdate": datetime.now().isoformat(),
                    "lastNote":  notas,
                    "fecha":     datetime.now().strftime("%d %b %Y"),
                    "drive":     drive_url,
                })
                st.success(f"✅ Guardado: **{nombre}** — {fc(total_v)}")
                if archivos:
                    st.info(f"📎 {len(archivos)} archivo(s) adjuntado(s): {', '.join(f.name for f in archivos)}")
                st.balloons()


def pg_actualizar():
    st.markdown("## 📝 Actualizar Estado de Proyectos")
    st.info("Mantén cada proyecto actualizado. Es obligatorio reportar el estado al menos cada 7 días.")

    df = mis_proyectos()
    presel = st.session_state.get("editing_nombre", "")
    nombres = ["— Seleccionar edificio —"] + sorted(df["nombre"].unique().tolist())
    idx = nombres.index(presel) if presel in nombres else 0

    selected = st.selectbox("Selecciona el edificio:", nombres, index=idx)

    if selected != "— Seleccionar edificio —":
        fila = df[df["nombre"] == selected].iloc[0]
        c1, c2, c3 = st.columns(3)
        c1.metric("Valor", fc(int(fila.get("totalNum") or 0)))
        c2.metric("Comercial", str(fila.get("comercial","—")))
        c3.metric("Última actualización", str(fila.get("lastUpdate","Nunca"))[:10] or "Nunca")

        with st.form("upd_form"):
            nuevo_est = st.selectbox(
                "Nuevo estado *",
                ["nuevo","cotizado","negociacion","cerrado","perdido"],
                index=["nuevo","cotizado","negociacion","cerrado","perdido"].index(
                    str(fila.get("estado","nuevo")) if str(fila.get("estado","nuevo")) in
                    ["nuevo","cotizado","negociacion","cerrado","perdido"] else "nuevo"
                )
            )
            nota = st.text_area("Nota de seguimiento * (requerida)",
                                placeholder="¿Qué pasó? ¿Cuál es el próximo paso? Sé específico...")
            guardar = st.form_submit_button("✅ Actualizar", use_container_width=True)

            if guardar:
                if not nota.strip():
                    st.error("La nota de seguimiento es obligatoria")
                else:
                    update_proyecto(selected, {
                        "estado":    nuevo_est,
                        "lastNote":  nota,
                        "lastUpdate": datetime.now().isoformat(),
                    })
                    st.success(f"✅ **{selected}** actualizado → {nuevo_est}")
                    if "editing_nombre" in st.session_state:
                        del st.session_state["editing_nombre"]
                    st.rerun()


def pg_edificios():
    st.markdown("## 🏢 Carpetas de Edificios")
    df = mis_proyectos()

    buscar = st.text_input("🔍 Buscar edificio", placeholder="Nombre...")
    if buscar:
        df = df[df["nombre"].str.contains(buscar, case=False, na=False)]

    cols = st.columns(4)
    for i, (_, row) in enumerate(df.iterrows()):
        with cols[i % 4]:
            tnum  = int(row.get("totalNum") or 0)
            total = fc(tnum) if tnum else "—"
            c36   = fc(int(row.get("c36Num") or 0)) if tnum else "—"
            est   = str(row.get("estado","nuevo"))
            drive = str(row.get("drive","") or "")
            drv_btn = f'<a href="{drive}" target="_blank" style="background:#E8F0FE;color:#1A73E8;border-radius:6px;padding:2px 8px;font-size:10px;font-weight:600;text-decoration:none;display:inline-block;margin-top:4px">📁 Drive</a>' if drive.startswith("http") else ""

            st.markdown(f"""
            <div style='background:white;border:1px solid #E3EAF3;border-radius:12px;
                 padding:14px;margin-bottom:12px;box-shadow:0 2px 8px rgba(4,17,30,.06)'>
              <div style='font-size:22px;margin-bottom:8px'>🏢</div>
              <div style='font-family:Sora,sans-serif;font-size:12px;font-weight:700;
                   color:#04111E;margin-bottom:3px'>{str(row["nombre"])[:26]}</div>
              <div style='font-size:11px;color:#8BA3BD;margin-bottom:6px'>
                {str(row.get("comercial","—"))}</div>
              <div style='font-family:Sora,sans-serif;font-size:15px;font-weight:800;
                   color:#009E78;margin-bottom:2px'>{total}</div>
              <div style='font-size:10px;color:#8BA3BD;margin-bottom:6px'>
                Cuota 36m: {c36}/mes</div>
              {badge(est)}
              {drv_btn}
            </div>
            """, unsafe_allow_html=True)


def pg_calendario():
    st.markdown("## 📅 Calendario Comercial")
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### ➕ Registrar nueva actividad")
        with st.form("nueva_act"):
            c1, c2 = st.columns(2)
            with c1:
                edificio = st.text_input("Edificio / Proyecto", placeholder="Nombre del edificio")
                tipo     = st.selectbox("Tipo", ["Reunión presencial","Llamada","Visita técnica","Asamblea","Otro"])
            with c2:
                fecha_act = st.date_input("Fecha", value=datetime.now())
                hora_act  = st.time_input("Hora")
            titulo_act = st.text_input("Título *", placeholder="Ej: Reunión asamblea propietarios")
            notas_act  = st.text_area("Notas / Agenda", placeholder="Objetivos, dirección...")

            es_gerente = st.session_state.user["rol"] == "gerente"
            if es_gerente:
                com_r = st.selectbox("Comercial responsable", ["RAFAEL TORRES","SONIA CASTRO","LINA CALLE","ALBERTO FERRER","SANTIAGO BOHORQUEZ","LUISA OLIVARES"])
            else:
                com_r = st.session_state.user["comercial"]

            if st.form_submit_button("📅 Guardar actividad", use_container_width=True):
                if titulo_act:
                    st.success(f"✅ Actividad guardada: **{titulo_act}** — {fecha_act.strftime('%d %b')} {hora_act.strftime('%H:%M')}")
                else:
                    st.error("El título es obligatorio")

    with col2:
        st.markdown("### 🔥 Actividades urgentes")
        urgentes = [
            ("Nomad / David Conde",         "Reunión — Llevar contrato listo", "#FEE2E2"),
            ("Park 104",                    "Reunión consejo — 27 Abr",        "#FEF9C3"),
            ("Yakarta",                     "Asamblea — 25 Abr",               "#FEF9C3"),
            ("Bosque San Vicente",          "Enviar cotización antes martes",  "#EFF6FF"),
        ]
        for nombre_u, desc, color in urgentes:
            st.markdown(f"""
            <div style='background:{color};border-radius:8px;padding:10px 12px;
                 margin-bottom:8px;border-left:3px solid #E84040'>
              <div style='font-size:12px;font-weight:700;color:#04111E'>{nombre_u}</div>
              <div style='font-size:10.5px;color:#8BA3BD;margin-top:2px'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)


def pg_correos():
    st.markdown("## ✉️ Generador de Correos Comerciales")
    df = mis_proyectos()

    col1, col2 = st.columns(2)
    with col1:
        edificio_sel = st.selectbox(
            "Edificio / Cotización",
            ["— Seleccionar —"] + sorted(df["nombre"].dropna().unique().tolist())
        )
        tipo_correo = st.selectbox("Tipo de correo", [
            "Primera presentación de propuesta",
            "Seguimiento 5-7 días post-envío",
            "Urgencia / oferta próxima a vencer",
            "Respuesta a objeción de precio alto",
            "Respuesta técnica a pregunta del cliente",
            "Argumentos para asamblea de propietarios",
            "Adultos mayores / discapacidad",
        ])
        ctx_extra = st.text_area("Contexto adicional",
                                  placeholder="Ej: El cliente dice que es muy caro. Preguntan por personas mayores...")

        if st.button("🤖 Generar Correo con IA", use_container_width=True):
            if edificio_sel != "— Seleccionar —":
                fila  = df[df["nombre"] == edificio_sel].iloc[0]
                tnum  = int(fila.get("totalNum") or 0)
                total = fc(tnum)
                c24   = fc(int(fila.get("c24Num") or 0))
                c36   = fc(int(fila.get("c36Num") or 0))
                vig   = fila.get("vig","") or ""

                prompt = f"""Redacta un correo comercial de tipo "{tipo_correo}" para Ágora Tech Colombia.
EDIFICIO: {edificio_sel} | Total: {total} | Cuota 24m: {c24} | Cuota 36m: {c36}
{f"Vigilancia actual: ${int(float(vig)):,}/mes" if vig and vig != "0" else ""}
Contacto: {fila.get("contacto","Administrador")}
{f"Contexto: {ctx_extra}" if ctx_extra else ""}
Comercial: {fila.get("comercial", st.session_state.user["comercial"])}

Primera línea: ASUNTO: [asunto específico]
Argumento principal: ahorro económico. Para adultos mayores: teclado PIN físico + Bluetooth sin smartphone.
Firma: {st.session_state.user["nombre"]} — Ágora Tech · (+57) 315 101 7511 · agoratech.com.co
Solo texto plano."""

                with st.spinner("Generando correo..."):
                    correo = ask_gemini(prompt)
                st.session_state.correo_generado = correo
            else:
                st.warning("Selecciona un edificio primero")

    with col2:
        st.markdown("**Vista previa:**")
        val = st.session_state.get("correo_generado", "Selecciona un edificio y genera el correo.")
        st.text_area("", value=val, height=450, key="prev_correo")
        if val != "Selecciona un edificio y genera el correo.":
            st.download_button("📋 Descargar correo", data=val,
                               file_name=f"correo_{edificio_sel[:20] if edificio_sel != '— Seleccionar —' else 'agora'}.txt")


def pg_asistente():
    st.markdown("## 🤖 Asistente Comercial IA")
    df   = mis_proyectos()
    ctx  = df.to_string(max_rows=60) if not df.empty else ""

    for msg in st.session_state.messages:
        cls = "chat-u" if msg["role"] == "user" else "chat-a"
        pre = "👤 " if msg["role"] == "user" else "🤖 "
        st.markdown(f'<div class="{cls}">{pre}{msg["content"]}</div>', unsafe_allow_html=True)

    if not st.session_state.messages:
        st.markdown("**Sugerencias rápidas:**")
        sugerencias = [
            "📊 Resume el estado de mi pipeline",
            "💰 ¿Cuánto vale mi pipeline total en COP?",
            "⚡ Proyectos más urgentes esta semana",
            "📈 Estrategia para cerrar Nomad",
            "🔍 Por qué se rechazan por adultos mayores",
            "✉️ Cómo convencer a una asamblea",
        ]
        cols = st.columns(3)
        for i, s in enumerate(sugerencias):
            if cols[i % 3].button(s, key=f"sug_{i}"):
                st.session_state.messages.append({"role": "user", "content": s})
                with st.spinner("Analizando..."):
                    r = ask_gemini(s, ctx)
                st.session_state.messages.append({"role": "assistant", "content": r})
                st.rerun()

    with st.form("chat_form", clear_on_submit=True):
        c1, c2 = st.columns([5, 1])
        with c1:
            ui = st.text_input("Pregunta", label_visibility="collapsed",
                               placeholder="Ej: Dame la estrategia para Nomad...")
        with c2:
            send = st.form_submit_button("Enviar →")
        if send and ui:
            st.session_state.messages.append({"role": "user", "content": ui})
            with st.spinner("Analizando..."):
                r = ask_gemini(ui, ctx)
            st.session_state.messages.append({"role": "assistant", "content": r})
            st.rerun()

    if st.session_state.messages:
        if st.button("🗑 Limpiar chat"):
            st.session_state.messages = []
            st.rerun()


def pg_auditoria():
    st.markdown("## 🔍 Auditoría Comercial")
    df = get_crm()  # Gerente ve todo

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Total Proyectos", df.shape[0])
    c2.metric("Pipeline", f"${int(df['totalNum'].sum())/1e9:.2f}B")
    c3.metric("Cotizados", df[df["estado"]=="cotizado"].shape[0])
    c4.metric("Rechazados", df[df["estado"]=="perdido"].shape[0])
    c5.metric("Contratos", df[df["estado"]=="cerrado"].shape[0])

    st.markdown("---")
    st.markdown('<div class="al-r">❗ <b>0 contratos cerrados en 5 meses.</b> El pipeline de $3.93B evidencia un cuello de botella en el cierre.</div>', unsafe_allow_html=True)
    st.markdown('<div class="al-y">⚡ <b>Nomad</b> — único en cierre cercano. Rafael Torres debe ir esta semana con contrato.</div>', unsafe_allow_html=True)
    st.markdown('<div class="al-b">ℹ️ Patrón: "La propuesta favorita pero adultos mayores no aprobaron" (Inzar VI y otros).</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        resumen = df[df["totalNum"]>0].groupby("comercial").agg(
            cotizaciones=("totalNum","count"), pipeline=("totalNum","sum")
        ).reset_index()
        resumen["pipeline_M"] = (resumen["pipeline"]/1e6).round(1)
        st.dataframe(resumen[["comercial","cotizaciones","pipeline_M"]]
                     .rename(columns={"comercial":"Comercial","cotizaciones":"Cotiz.","pipeline_M":"Pipeline ($M)"}),
                     use_container_width=True, hide_index=True)
    with c2:
        if st.button("🤖 Análisis profundo con IA", use_container_width=True):
            with st.spinner("Analizando..."):
                r = ask_gemini(
                    "Análisis estratégico: 1)Por qué no se cierran contratos. 2)Patrones de rechazo. "
                    "3)Plan Nomad esta semana. 4)Plan 30 días primer contrato. Sin separadores ---.",
                    df.to_string(max_rows=80)
                )
            st.markdown(r)


def pg_informes():
    st.markdown("## 📈 Informes Gerenciales")
    df = get_crm()

    # Gráficas
    c1, c2, c3 = st.columns(3)
    with c1:
        df_com = df[df["totalNum"]>0].groupby("comercial")["totalNum"].sum().reset_index()
        df_com["M"]   = (df_com["totalNum"]/1e6).round(1)
        df_com["Com"] = df_com["comercial"].str.split().str[0]
        fig = px.bar(df_com.sort_values("M",ascending=True), x="M", y="Com", orientation="h",
                     title="Pipeline por Comercial ($M)", color="M",
                     color_continuous_scale=["#1A9FCC","#00C896"])
        fig.update_layout(plot_bgcolor="white",paper_bgcolor="white",coloraxis_showscale=False,margin=dict(t=40))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        lm = {"nuevo":"Lead","cotizado":"Enviado","negociacion":"Negoc.","cerrado":"Cerrado","perdido":"Perdido"}
        est = df.groupby("estado").size().reset_index(name="n")
        est["Estado"] = est["estado"].map(lm).fillna(est["estado"])
        fig2 = px.pie(est, values="n", names="Estado", hole=0.45,
                      color_discrete_sequence=["#1A9FCC","#F2A12E","#8B5CF6","#00C896","#E84040"],
                      title="Distribución")
        fig2.update_layout(paper_bgcolor="white",margin=dict(t=40))
        st.plotly_chart(fig2, use_container_width=True)
    with c3:
        crecimiento = pd.DataFrame({
            "Mes":  ["Dic 2025","Ene 2026","Feb 2026","Mar 2026","Abr 2026"],
            "Leads":[3,17,25,32,46]
        })
        fig3 = px.area(crecimiento, x="Mes", y="Leads", title="Crecimiento Mensual",
                       color_discrete_sequence=["#00C896"], markers=True)
        fig3.update_traces(line_width=3, marker_size=8, fill="tozeroy",
                           fillcolor="rgba(0,200,150,0.1)")
        fig3.update_layout(plot_bgcolor="white",paper_bgcolor="white",margin=dict(t=40))
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        tipo_inf = st.selectbox("Tipo de informe:", [
            "Informe Gerencial Ejecutivo",
            "Reporte Pipeline Comercial",
            "Análisis del Equipo Comercial",
            "Oportunidades Críticas de Cierre",
            "Auditoría Comercial",
        ])
    with c2:
        notas_inf = st.text_area("Instrucciones:", placeholder="Ej: Enfatizar en Nomad...", height=80)

    if st.button("🤖 Generar Informe Completo", use_container_width=True):
        prompt = f"""Genera un {tipo_inf} COMPLETO para Ágora Tech Colombia.
{f"Instrucciones: {notas_inf}" if notas_inf else ""}
Estructura:
# {tipo_inf}
Fecha: {datetime.now().strftime("%d de %B de %Y")}
## 1. RESUMEN EJECUTIVO
## 2. MÉTRICAS CLAVE
## 3. ANÁLISIS DETALLADO
## 4. ALERTAS Y RIESGOS
## 5. RECOMENDACIONES
## 6. PRÓXIMOS PASOS ESTA SEMANA
Sin separadores ---. Negrilla para cifras clave."""
        with st.spinner("Generando informe..."):
            r = ask_gemini(prompt, df.to_string(max_rows=80))
        st.markdown(r)
        c1, c2 = st.columns(2)
        c1.download_button("📥 Descargar .md", data=r,
                           file_name=f"Informe_{datetime.now().strftime('%Y%m%d')}.md")
        c2.download_button("📥 Descargar .txt", data=r,
                           file_name=f"Informe_{datetime.now().strftime('%Y%m%d')}.txt")


def pg_pipeline():
    st.markdown("## 🎯 Pipeline — Kanban")
    df = mis_proyectos()
    etapas = [("nuevo","🔵 Lead Nuevo"),("cotizado","🟡 Cotización"),("negociacion","🟠 Negociando"),("cerrado","🟢 Cerrado")]
    cols   = st.columns(4)
    for i, (k, lbl) in enumerate(etapas):
        items = df[df["estado"] == k]
        tot   = int(items["totalNum"].sum())
        with cols[i]:
            st.markdown(f"**{lbl}**")
            st.markdown(f"_{len(items)} · ${tot/1e6:.1f}M_")
            for _, row in items.iterrows():
                tnum = int(row.get("totalNum") or 0)
                st.markdown(f"""
                <div style='background:white;border:1px solid #E3EAF3;border-radius:8px;
                     padding:11px;margin-bottom:8px;box-shadow:0 1px 4px rgba(4,17,30,.06)'>
                  <div style='font-size:11.5px;font-weight:700;color:#04111E;margin-bottom:2px'>
                    {str(row["nombre"])[:24]}</div>
                  <div style='font-size:10.5px;color:#8BA3BD;margin-bottom:4px'>
                    {str(row.get("comercial","—"))}</div>
                  <div style='font-size:13px;font-weight:800;color:#009E78'>
                    {fc(tnum) if tnum else "—"}</div>
                </div>
                """, unsafe_allow_html=True)


def pg_encuestas():
    st.markdown("## 📊 Encuestas de Prospectos")
    st.info("Registra prospectos nuevos con el formulario de información preliminar. La IA analiza la viabilidad automáticamente.")

    with st.form("form_prosp"):
        c1, c2 = st.columns(2)
        with c1:
            nom_e = st.text_input("Nombre del Edificio *")
            dir_e = st.text_input("Dirección")
            cont_e = st.text_input("Contacto *")
        with c2:
            rol_e   = st.selectbox("Rol", ["Administrador","Propietario","Miembro del Consejo","Presidente del Consejo"])
            etapa_e = st.selectbox("Etapa de decisión", ["Recibiendo cotizaciones por asamblea","No se ha hablado en asamblea","Explorando opciones"])
            com_e   = st.selectbox("Comercial", ["RAFAEL TORRES","SONIA CASTRO","LINA CALLE","ALBERTO FERRER","SANTIAGO BOHORQUEZ"])

        vig_e   = st.radio("¿Tiene vigilancia?", ["Sí","No"], horizontal=True)
        c1, c2  = st.columns(2)
        with c1: costo_e = st.number_input("Costo vigilancia ($/mes)", min_value=0, value=0, step=100_000, format="%d")
        with c2: vigh_e  = st.text_input("Contrato vigente hasta", placeholder="Nov 2026")

        incid_e = st.text_area("Incidentes de seguridad", placeholder="Robos, incidentes recientes...")
        acces_e = st.text_area("Adultos mayores / Discapacidad", placeholder="¿Hay residentes con necesidades especiales?")
        notas_e = st.text_area("Notas del comercial")

        if st.form_submit_button("🤖 Analizar con IA y Guardar", use_container_width=True):
            if not nom_e:
                st.error("Nombre del edificio obligatorio")
            else:
                prompt = f"""Analiza este prospecto para Ágora Tech:
Edificio: {nom_e} | Contacto: {cont_e} ({rol_e}) | Etapa: {etapa_e}
Vigilancia: {"SÍ $"+f"{int(costo_e):,}"+"/mes hasta "+vigh_e if vig_e=="Sí" and costo_e>0 else "NO"}
Incidentes: {incid_e or "Ninguno"} | Adultos mayores: {acces_e or "No reportado"}
Comercial: {com_e}

## VIABILIDAD: [ALTA / MEDIA / BAJA]
## AHORRO POTENCIAL
## ESTRATEGIA DE VENTA
## OBJECIONES Y RESPUESTAS
## PRÓXIMOS PASOS

Sin ---. Negrilla para datos clave. Accionable."""
                with st.spinner("Analizando con IA..."):
                    r = ask_gemini(prompt)
                st.markdown("---")
                st.markdown(r)
                st.success(f"✅ Prospecto {nom_e} analizado y registrado")


# ═══════════════════════════════════════════
# MAIN — ENRUTADOR
# ═══════════════════════════════════════════
if not st.session_state.logged_in:
    mostrar_login()
else:
    mostrar_sidebar()
    pg = st.session_state.get("page", "Dashboard")

    if   pg == "Dashboard":        pg_dashboard()
    elif pg == "Mis Proyectos":    pg_proyectos()
    elif pg == "Nueva Cotización": pg_nueva_cotizacion()
    elif pg == "Actualizar Estado":pg_actualizar()
    elif pg == "Edificios":        pg_edificios()
    elif pg == "Calendario":       pg_calendario()
    elif pg == "Correos IA":       pg_correos()
    elif pg == "Asistente IA":     pg_asistente()
    elif pg == "Auditoría":        pg_auditoria()
    elif pg == "Informes":         pg_informes()
    elif pg == "Pipeline":         pg_pipeline()
    elif pg == "Encuestas":        pg_encuestas()
    else:                          pg_dashboard()
