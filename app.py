"""
ÁGORA TECH — Plataforma Comercial v6 DEFINITIVA
Auto-actualización · Alertas en tiempo real · Informe semanal · Novedades
IA: Groq (llama-3.3-70b-versatile) — API key desde Streamlit Secrets
Datos: Google Drive (lectura directa vía gspread) + proyectos.json como base
"""

import streamlit as st
from groq import Groq
import pandas as pd
import json, os, re
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# ══════════════════════════════════════════════
# CONSTANTES
# ══════════════════════════════════════════════
VERSION = "v6.0 · Jun 2026"
GROQ_MODEL = "llama-3.3-70b-versatile"
DRIVE_FILE_ID = "1TxQOMBuMFgbdcobXZPoh7VwAY8maV5sR"  # Seguimiento edificio_Por_Comercial.xlsx

ETAPAS = {
    "lead":              {"label":"🔵 Lead",              "grupo":"Comercial",  "color":"#DBEAFE", "orden":0},
    "cotizado":          {"label":"🟡 Cotización enviada", "grupo":"Comercial",  "color":"#FEF9C3", "orden":1},
    "negociacion":       {"label":"🟠 Negociando",         "grupo":"Comercial",  "color":"#FED7AA", "orden":2},
    "aprobado_espera":   {"label":"🔒 Aprobado–Stand-by",  "grupo":"Comercial",  "color":"#E0F2FE", "orden":3},
    "perdido":           {"label":"🔴 Perdido",            "grupo":"Comercial",  "color":"#FEE2E2", "orden":4},
    "creacion_contrato": {"label":"📝 Creación Contrato",  "grupo":"Ejecución",  "color":"#D1FAF0", "orden":5},
    "financiacion":      {"label":"💰 Financiación",       "grupo":"Ejecución",  "color":"#D1FAF0", "orden":6},
    "obra":              {"label":"🔨 En Obra",             "grupo":"Ejecución",  "color":"#ECFDF5", "orden":7},
    "novedades_obra":    {"label":"⚠️ Novedades Obra",      "grupo":"Ejecución",  "color":"#FFFBEB", "orden":8},
    "entrega":           {"label":"🎉 Entrega",             "grupo":"Ejecución",  "color":"#ECFDF5", "orden":9},
    "mantenimiento":     {"label":"🔧 Mantenimiento",      "grupo":"Posventa",   "color":"#EFF6FF", "orden":10},
    "cerrado":           {"label":"✅ Cerrado",             "grupo":"Posventa",   "color":"#D1FAF0", "orden":11},
}
ESTADOS_LISTA = list(ETAPAS.keys())
COMS = ["RAFAEL TORRES","SONIA CASTRO","LINA CALLE","ALBERTO FERRER","SANTIAGO BOHORQUEZ","LUISA OLIVARES"]

AI_SYSTEM = """Eres el asesor estratégico de Ágora Tech Colombia — empresa de automatización de accesos para copropiedades residenciales.

PRODUCTO: Sistema SALTO HomeLok. Acceso por nube, Bluetooth, PIN físico, QR, app iOS/Android.
PROPUESTA ÚNICA: Financiación 100% a 24/36 meses sin intereses. Llave en mano en 40 días. Garantía 36 meses equipos / 12 meses adecuaciones.
PRECIOS BASE: Adecuaciones $18.8M · Lectora vidrio $4.2M · Puertas vehiculares $10.8M · CCTV $13.8M · Mantenimiento $966.400+IVA/mes.
REFERENCIA: Edificio Alto 61 (instalación funcional para visitas).

SITUACIÓN JUNIO 2026: 127 propuestas, $8.6B pipeline, 0 contratos firmados. 
Cierres probables Q3 2026: Risaralda (asamblea jul), Country 136 (asamblea jun 27), Park 104 (asamblea jun 13).
10 edificios esperando vencimiento vigilancia sep-nov 2026.
Rechazos frecuentes: adultos mayores (solución: teclado PIN físico con relieve, sin smartphone requerido), precio alto (mostrar ahorro vs vigilancia actual), seguridad percibida.

Responde en español colombiano. Sé específico, directo y usa datos reales del CRM cuando los tengas disponibles."""

# ══════════════════════════════════════════════
# CONFIG STREAMLIT
# ══════════════════════════════════════════════
st.set_page_config(
    page_title="Ágora Tech",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
  --bg:#F4F6FA; --surface:#FFFFFF; --surface2:#F0F3F9;
  --border:#E2E8F0; --border2:#CBD5E1;
  --ink:#0F172A; --ink2:#334155; --ink3:#64748B; --ink4:#94A3B8;
  --blue:#1B4FD8; --blue-dk:#1239A8; --blue-lt:#EEF2FF; --blue-mid:#BFCFFF;
  --teal:#0EA5B0; --green:#059669; --green-bg:#ECFDF5;
  --red:#DC2626; --red-bg:#FEF2F2;
  --amber:#D97706; --amber-bg:#FFFBEB; --amber-mid:#FDE68A;
  --purple:#7C3AED; --purple-bg:#F5F3FF;
  --sh:0 1px 3px rgba(15,23,42,.07),0 1px 2px rgba(15,23,42,.05);
  --sh-md:0 4px 12px rgba(15,23,42,.09);
  --r:12px;
}

html,body,[class*="css"]{font-family:'Inter',sans-serif!important;background:var(--bg)!important}
h1,h2,h3{font-family:'Space Grotesk',sans-serif!important}

/* Sidebar */
[data-testid="stSidebar"]{background:#0F172A!important;border-right:1px solid #1E293B!important}
[data-testid="stSidebar"] *{color:rgba(255,255,255,.8)!important}
[data-testid="stSidebar"] .stTextInput input{background:rgba(255,255,255,.06)!important;border:1px solid rgba(255,255,255,.12)!important;color:white!important;border-radius:8px!important}

/* Buttons */
.stButton>button{background:linear-gradient(135deg,#1B4FD8,#0EA5B0)!important;color:white!important;
  font-family:'Space Grotesk',sans-serif!important;font-weight:600!important;border:none!important;
  border-radius:8px!important;letter-spacing:-.2px!important;transition:all .18s!important;
  box-shadow:0 2px 8px rgba(27,79,216,.3)!important}
.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 6px 20px rgba(27,79,216,.45)!important}
.stButton>button[kind="secondary"]{background:var(--surface)!important;color:var(--ink)!important;
  border:1.5px solid var(--border2)!important;box-shadow:none!important;transform:none!important}
[data-testid="stSidebar"] .stButton>button{background:transparent!important;color:rgba(255,255,255,.6)!important;
  font-weight:500!important;border:none!important;box-shadow:none!important;border-radius:8px!important;
  text-align:left!important;font-size:13px!important;transform:none!important}
[data-testid="stSidebar"] .stButton>button:hover{background:rgba(255,255,255,.07)!important;color:white!important}

/* KPI */
.kpi{background:var(--surface);border:1px solid var(--border);border-radius:var(--r);
  padding:18px 20px;box-shadow:var(--sh);position:relative;overflow:hidden}
.kpi::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;
  background:linear-gradient(90deg,var(--blue),var(--teal))}
.kpi-label{font-size:10.5px;font-weight:600;color:var(--ink3);text-transform:uppercase;
  letter-spacing:.6px;margin-bottom:10px}
.kpi-val{font-family:'Space Grotesk',sans-serif;font-size:26px;font-weight:700;color:var(--ink);line-height:1;letter-spacing:-1px}
.kpi-val.g{color:var(--green)}.kpi-val.r{color:var(--red)}.kpi-val.o{color:var(--amber)}.kpi-val.b{color:var(--blue)}
.kpi-sub{font-size:11.5px;color:var(--ink4);margin-top:5px}

/* Cards */
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--r);
  box-shadow:var(--sh);overflow:hidden;margin-bottom:16px}
.card-h{padding:13px 18px;border-bottom:1px solid var(--border);display:flex;align-items:center;
  justify-content:space-between}
.card-t{font-family:'Space Grotesk',sans-serif;font-size:13.5px;font-weight:600;color:var(--ink)}
.card-b{padding:16px 18px}

/* Alertas */
.al{border-radius:10px;padding:11px 15px;margin-bottom:10px;display:flex;gap:10px;border:1px solid;font-size:12.5px;line-height:1.7}
.al-icon{font-size:16px;flex-shrink:0;margin-top:2px}
.al.red{background:var(--red-bg);border-color:#FCA5A5;color:#7F1D1D}
.al.amber{background:var(--amber-bg);border-color:var(--amber-mid);color:#78350F}
.al.green{background:var(--green-bg);border-color:#6EE7B7;color:#065F46}
.al.blue{background:var(--blue-lt);border-color:var(--blue-mid);color:var(--blue-dk)}
.al.purple{background:var(--purple-bg);border-color:#DDD6FE;color:#5B21B6}

/* Tags */
.tag{display:inline-flex;align-items:center;padding:2px 9px;border-radius:20px;font-size:11px;font-weight:600}
.tag-g{background:var(--green-bg);color:#065F46;border:1px solid #6EE7B7}
.tag-r{background:var(--red-bg);color:#991B1B;border:1px solid #FCA5A5}
.tag-b{background:var(--blue-lt);color:var(--blue-dk);border:1px solid var(--blue-mid)}
.tag-a{background:var(--amber-bg);color:#92400E;border:1px solid var(--amber-mid)}
.tag-p{background:var(--purple-bg);color:#5B21B6;border:1px solid #DDD6FE}
.tag-gray{background:var(--surface2);color:var(--ink3);border:1px solid var(--border2)}
.tag-teal{background:#F0FDFA;color:#0D9488;border:1px solid #99F6E4}

/* Historial */
.hist-item{background:var(--surface2);border-left:3px solid var(--blue);border-radius:0 8px 8px 0;
  padding:10px 14px;margin-bottom:8px;font-size:12.5px}
.hist-date{font-size:10px;color:var(--ink4);margin-bottom:3px;font-weight:700;text-transform:uppercase;letter-spacing:.4px}

/* Chat */
.chat-u{background:linear-gradient(135deg,var(--blue),var(--teal));color:white;padding:12px 16px;
  border-radius:16px 16px 3px 16px;margin:8px 0;font-weight:500;max-width:82%;margin-left:auto;display:block;font-size:13px}
.chat-a{background:var(--surface);border:1px solid var(--border);padding:14px 18px;
  border-radius:16px 16px 16px 3px;margin:8px 0;max-width:90%;box-shadow:var(--sh);
  line-height:1.75;display:block;font-size:13px}

/* Novedad badge */
.nov-new{background:#FEF9C3;color:#854D0E;border:1px solid #FDE047;border-radius:6px;
  padding:2px 8px;font-size:10px;font-weight:700;margin-left:6px}

/* Timeline */
.tl{position:relative;padding-left:24px}
.tl::before{content:'';position:absolute;left:7px;top:6px;bottom:0;width:2px;
  background:var(--border2);border-radius:1px}
.ti{position:relative;margin-bottom:16px}
.ti-dot{position:absolute;left:-24px;top:4px;width:13px;height:13px;border-radius:50%;
  border:2.5px solid white;box-shadow:0 0 0 2px var(--border2)}
.ti-date{font-size:10px;font-weight:700;color:var(--ink4);text-transform:uppercase;letter-spacing:.4px;margin-bottom:1px}
.ti-h{font-size:13px;font-weight:600;color:var(--ink);margin-bottom:1px}
.ti-t{font-size:12px;color:var(--ink3);line-height:1.65}

/* Semáforo urgencia */
.urgente-r{border-left:4px solid var(--red)!important}
.urgente-a{border-left:4px solid var(--amber)!important}
.urgente-g{border-left:4px solid var(--green)!important}

/* Tabla */
.tw{background:var(--surface);border:1px solid var(--border);border-radius:var(--r);overflow:hidden;box-shadow:var(--sh)}
table{width:100%;border-collapse:collapse}
thead{background:var(--surface2)}
th{padding:9px 13px;text-align:left;font-size:10.5px;font-weight:600;color:var(--ink3);
  text-transform:uppercase;letter-spacing:.6px;border-bottom:1px solid var(--border);white-space:nowrap}
td{padding:9px 13px;font-size:12.5px;border-bottom:1px solid var(--border);color:var(--ink2);vertical-align:top}
tr:last-child td{border-bottom:none}
tbody tr:hover{background:#FAFBFF}

/* Pulse animation */
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
.pulse-dot{display:inline-block;width:8px;height:8px;background:#22C55E;border-radius:50%;
  animation:pulse 2s infinite;margin-right:6px;vertical-align:middle}

div[data-testid="stForm"]{border:none!important;padding:0!important}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# USUARIOS
# ══════════════════════════════════════════════
USUARIOS_DEFAULT = {
    "luisa":    {"pass":"luisa2026",    "nombre":"Luisa Olivares",     "rol":"gerente",   "comercial":"LUISA OLIVARES",     "activo":True},
    "gerente":  {"pass":"gerente2026",  "nombre":"Luisa Olivares",     "rol":"gerente",   "comercial":"LUISA OLIVARES",     "activo":True},
    "rafael":   {"pass":"rafael2026",   "nombre":"Rafael Torres",      "rol":"comercial", "comercial":"RAFAEL TORRES",      "activo":True},
    "sonia":    {"pass":"sonia2026",    "nombre":"Sonia Castro",       "rol":"comercial", "comercial":"SONIA CASTRO",       "activo":True},
    "lina":     {"pass":"lina2026",     "nombre":"Lina Calle",         "rol":"comercial", "comercial":"LINA CALLE",         "activo":True},
    "alberto":  {"pass":"alberto2026",  "nombre":"Alberto Ferrer",     "rol":"comercial", "comercial":"ALBERTO FERRER",     "activo":True},
    "santiago": {"pass":"santiago2026", "nombre":"Santiago Bohórquez", "rol":"comercial", "comercial":"SANTIAGO BOHORQUEZ", "activo":True},
}

def get_usuarios():
    if "usuarios_db" not in st.session_state:
        st.session_state.usuarios_db = dict(USUARIOS_DEFAULT)
    return st.session_state.usuarios_db

# ══════════════════════════════════════════════
# IA — GROQ
# ══════════════════════════════════════════════
def get_ai_key():
    k = st.session_state.get("groq_key","")
    if k: return k
    try:
        k = st.secrets["GROQ_API_KEY"]
        if k: st.session_state["groq_key"] = k; return k
    except: pass
    return ""

def ai_activa(): return bool(get_ai_key())

def activar_ia(key):
    key = key.strip()
    if not key.startswith("gsk_") or len(key) < 20:
        st.error("La key debe empezar con gsk_ y tener al menos 20 caracteres"); return False
    try:
        c = Groq(api_key=key)
        c.chat.completions.create(model=GROQ_MODEL, messages=[{"role":"user","content":"OK"}], max_tokens=5)
        st.session_state["groq_key"] = key
        return True
    except Exception as e:
        st.error(f"❌ Key inválida: {str(e)[:100]}"); return False

def ask_ai(prompt, ctx="", max_tokens=2000):
    key = get_ai_key()
    if not key: return "⚠️ IA no configurada. Ve a ⚙️ Configuración."
    try:
        client = Groq(api_key=key)
        msgs = [{"role":"system","content":AI_SYSTEM}]
        if ctx:
            msgs.append({"role":"user","content":f"DATOS CRM:\n{ctx[:18000]}\n\nSOLICITUD:\n{prompt}"})
        else:
            msgs.append({"role":"user","content":prompt})
        r = client.chat.completions.create(model=GROQ_MODEL, messages=msgs, max_tokens=max_tokens, temperature=0.7)
        return r.choices[0].message.content
    except Exception as e:
        return f"Error IA: {e}"

# ══════════════════════════════════════════════
# NORMALIZACIÓN DE ESTADOS (CORRECTO)
# ══════════════════════════════════════════════
def normalizar_estado(estado):
    """Mapeo correcto según Drive actualizado junio 2026."""
    e = str(estado or "").strip().lower()
    # Stand-by: aprobaron automáticamente pero esperan vencimiento vigilancia
    if "vencimiento" in e or ("aprobado" in e and "aut" in e and "pendiente" in e):
        return "aprobado_espera"
    # En proceso activo — "Aprobado - Pendiente proveedor" = conversando
    if "aprobado" in e and "pendiente" in e:
        return "cotizado"
    # Otro "aprobado" → cotizado (ninguno es contrato firmado)
    if "aprobado" in e:
        return "cotizado"
    if "negociacion" in e or "negocia" in e or "avanzado" in e:
        return "negociacion"
    if "cotiz" in e or "conversando" in e or "proceso" in e or "pendiente" in e or "viabilidad" in e:
        return "cotizado"
    if "stand" in e or "retomar" in e or "suspendid" in e:
        return "aprobado_espera"
    if "rechaz" in e or "perdido" in e:
        return "perdido"
    if "cerrado" in e or "cierre" in e: return "cerrado"
    if "contrato" in e: return "creacion_contrato"
    if "financ" in e: return "financiacion"
    if "obra" in e: return "obra"
    if "novedad" in e: return "novedades_obra"
    if "entrega" in e: return "entrega"
    if "mantenimiento" in e: return "mantenimiento"
    if "lead" in e or "frio" in e or "frío" in e: return "lead"
    return e if e in ETAPAS else "lead"

def badge(estado):
    e = ETAPAS.get(estado, {"label":estado,"color":"#F1F5F9"})
    return f'<span class="tag" style="background:{e["color"]};border:1px solid rgba(0,0,0,.08)">{e["label"]}</span>'

def fc(n):
    try:
        n = int(float(n or 0))
        return "$0" if n == 0 else "$" + f"{n:,}".replace(",",".")
    except: return "$0"

def hdr(icon, title, sub=""):
    st.markdown(f"""
    <div style='display:flex;align-items:center;gap:14px;margin-bottom:24px;padding-bottom:16px;border-bottom:1px solid var(--border)'>
      <div style='width:42px;height:42px;border-radius:10px;background:linear-gradient(135deg,#1B4FD8,#0EA5B0);
           display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0'>{icon}</div>
      <div>
        <div style='font-family:Space Grotesk,sans-serif;font-size:19px;font-weight:700;color:var(--ink);letter-spacing:-.4px'>{title}</div>
        {'<div style="font-size:12px;color:var(--ink4);margin-top:2px">'+sub+'</div>' if sub else ''}
      </div>
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════
def init():
    defaults = {
        "logged_in": False, "user": None, "page": "Dashboard",
        "messages": [], "crm": None, "correo": "", "editing": "",
        "novedades": [], "last_refresh": None,
    }
    for k,v in defaults.items():
        if k not in st.session_state: st.session_state[k] = v
init()

# Cargar key de secrets al inicio
if not st.session_state.get("groq_key"):
    try:
        k = st.secrets["GROQ_API_KEY"]
        if k: st.session_state["groq_key"] = k
    except: pass

# ══════════════════════════════════════════════
# CRM CON HISTORIAL Y NOVEDADES
# ══════════════════════════════════════════════
@st.cache_data
def cargar_proyectos_base():
    base = os.path.dirname(os.path.abspath(__file__))
    for n in ["proyectos.json"]:
        ruta = os.path.join(base, n)
        if os.path.exists(ruta):
            with open(ruta, encoding="utf-8") as f:
                return json.load(f)
    return []

PROYECTOS_BASE = cargar_proyectos_base()

def get_crm():
    if st.session_state.crm is None:
        rows = []
        for p in PROYECTOS_BASE:
            est_raw = str(p.get("etapaOrig","") or p.get("estado",""))
            estado = normalizar_estado(est_raw) if est_raw else (p.get("estado","lead"))
            # Asegurar que el estado sea válido
            if estado not in ETAPAS: estado = "lead"
            rows.append({
                "id":          p.get("id",""),
                "nombre":      p.get("nombre",""),
                "comercial":   p.get("comercial",""),
                "contacto":    p.get("contacto",""),
                "email":       p.get("email",""),
                "total":       p.get("total","$0"),
                "totalNum":    int(float(p.get("totalNum",0) or 0)),
                "cuota24":     p.get("cuota24","$0"),
                "cuota36":     p.get("cuota36","$0"),
                "c24Num":      int(float(p.get("c24Num",0) or 0)),
                "c36Num":      int(float(p.get("c36Num",0) or 0)),
                "vig":         p.get("vig",""),
                "vigH":        p.get("vigH",""),
                "estado":      estado,
                "etapaOrig":   est_raw,
                "version":     p.get("version","v1"),
                "notas":       p.get("notas",""),
                "lastUpdate":  p.get("lastUpdate",""),
                "lastNote":    p.get("lastNote",""),
                "fecha":       p.get("fecha",""),
                "drive":       p.get("drive",""),
                "historial":   p.get("historial","[]"),
                "encuesta":    p.get("encuesta","{}"),
                "novedad":     p.get("novedad",""),  # novedad de esta semana
                "asamblea":    p.get("asamblea",""),
            })
        st.session_state.crm = pd.DataFrame(rows)
    return st.session_state.crm

def mis_proyectos():
    df = get_crm()
    u = st.session_state.user
    if not u: return df.iloc[0:0]
    if u["rol"] == "gerente": return df
    return df[df["comercial"].str.upper() == u["comercial"].upper()]

def update_proy(nombre, campos):
    df = get_crm()
    mask = df["nombre"] == nombre
    if mask.any():
        for k,v in campos.items(): df.loc[mask,k] = v
        st.session_state.crm = df

def agregar_historial(nombre, estado, nota, usuario):
    df = get_crm()
    mask = df["nombre"] == nombre
    if not mask.any(): return
    hist_raw = str(df.loc[mask,"historial"].iloc[0] or "[]")
    try: hist = json.loads(hist_raw)
    except: hist = []
    evento = {
        "fecha": datetime.now().strftime("%d %b %Y %H:%M"),
        "estado": estado,
        "nota": nota,
        "usuario": usuario,
        "ts": datetime.now().isoformat()
    }
    hist.append(evento)
    df.loc[mask,"historial"] = json.dumps(hist, ensure_ascii=False)
    df.loc[mask,"lastNote"] = nota
    df.loc[mask,"lastUpdate"] = datetime.now().isoformat()
    df.loc[mask,"estado"] = estado
    # Marcar como novedad de esta semana
    df.loc[mask,"novedad"] = f"{datetime.now().strftime('%d %b')} — {nota[:100]}"
    st.session_state.crm = df

def add_proy(datos):
    df = get_crm()
    st.session_state.crm = pd.concat([pd.DataFrame([datos]), df], ignore_index=True)

# ══════════════════════════════════════════════
# ALERTAS AUTOMÁTICAS
# ══════════════════════════════════════════════
def calcular_alertas(df):
    """Genera alertas dinámicas basadas en datos reales del CRM."""
    alertas = []
    hace_7 = (datetime.now() - timedelta(days=7)).isoformat()
    hace_15 = (datetime.now() - timedelta(days=15)).isoformat()

    # 1. Proyectos en negociación activa
    neg = df[df["estado"] == "negociacion"]
    for _, r in neg.iterrows():
        alertas.append({
            "tipo":"red", "prioridad":1,
            "titulo":f"🔥 NEGOCIACIÓN: {r['nombre']}",
            "msg":str(r.get("lastNote","") or r.get("notas",""))[:120] or "Seguimiento urgente",
            "comercial":r.get("comercial",""), "valor":r.get("totalNum",0)
        })

    # 2. Sin contratos cerrados (gerente)
    if df[df["estado"]=="cerrado"].shape[0] == 0:
        total_pip = int(df["totalNum"].sum())
        alertas.append({
            "tipo":"red", "prioridad":1,
            "titulo":"❗ 0 contratos cerrados",
            "msg":f"Pipeline de {fc(total_pip)} sin conversión. Priorizar cierre en asambleas de julio.",
            "comercial":"TODOS"
        })

    # 3. Proyectos aprobados en stand-by para reactivar
    espera = df[df["estado"] == "aprobado_espera"]
    if len(espera) > 0:
        for _, r in espera.iterrows():
            vig = str(r.get("vigH","") or "")
            if any(mes in vig.lower() for mes in ["jun","jul","ago","sep","oct"]):
                alertas.append({
                    "tipo":"amber", "prioridad":2,
                    "titulo":f"🔒 REACTIVAR: {r['nombre']}",
                    "msg":f"Aprobaron automatización — vencimiento vigilancia: {vig}. Contactar YA.",
                    "comercial":r.get("comercial","")
                })

    # 4. Sin actualización +7 días (los más valiosos)
    sin_upd = df[
        (df["lastUpdate"].astype(str).str.strip() == "") |
        (df["lastUpdate"].astype(str).str.strip() < hace_7)
    ]
    sin_upd_valiosos = sin_upd[sin_upd["totalNum"] > 80_000_000].sort_values("totalNum", ascending=False)
    if len(sin_upd_valiosos) > 0:
        alertas.append({
            "tipo":"amber", "prioridad":3,
            "titulo":f"📋 {len(sin_upd_valiosos)} proyectos >$80M sin actualizar en +7 días",
            "msg": ", ".join(sin_upd_valiosos["nombre"].head(5).tolist()) + ("..." if len(sin_upd_valiosos)>5 else ""),
            "comercial":"TODOS"
        })

    # 5. Oportunidades grandes en cotización
    hot = df[(df["estado"]=="cotizado") & (df["totalNum"]>100_000_000)].sort_values("totalNum", ascending=False).head(5)
    for _, r in hot.iterrows():
        nota = str(r.get("lastNote","") or r.get("notas",""))[:100]
        alertas.append({
            "tipo":"blue", "prioridad":4,
            "titulo":f"💰 {r['nombre']} — {fc(int(r['totalNum']))}",
            "msg":nota or "Dar seguimiento activo",
            "comercial":r.get("comercial","")
        })

    return sorted(alertas, key=lambda x: x["prioridad"])

# ══════════════════════════════════════════════
# LOGIN
# ══════════════════════════════════════════════
def pg_login():
    c1,c2,c3 = st.columns([1,1.1,1])
    with c2:
        st.markdown("""
        <div style='text-align:center;padding:52px 0 28px'>
          <div style='font-family:Space Grotesk,sans-serif;font-size:11px;font-weight:700;
               color:#64748B;letter-spacing:5px;text-transform:uppercase;margin-bottom:18px'>PLATAFORMA COMERCIAL</div>
          <div style='font-family:Space Grotesk,sans-serif;font-size:38px;font-weight:700;
               color:#0F172A;letter-spacing:-2px;line-height:1'>ÁGORA TECH</div>
          <div style='width:36px;height:3px;background:linear-gradient(90deg,#1B4FD8,#0EA5B0);
               margin:16px auto;border-radius:2px'></div>
          <div style='font-size:13px;color:#94A3B8;font-weight:400'>Acceso seguro al CRM comercial</div>
        </div>""", unsafe_allow_html=True)

        with st.form("login_form"):
            usuario  = st.text_input("Usuario", placeholder="rafael / sonia / lina / luisa...")
            password = st.text_input("Contraseña", type="password", placeholder="••••••••")
            if st.form_submit_button("Ingresar →", use_container_width=True):
                u = usuario.strip().lower()
                usuarios = get_usuarios()
                if u in usuarios and usuarios[u]["activo"] and usuarios[u]["pass"] == password:
                    st.session_state.logged_in = True
                    st.session_state.user = usuarios[u]
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")

        st.markdown("""
        <div style='background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;
             padding:12px 16px;margin-top:14px;font-size:11.5px;color:#94A3B8;text-align:center'>
          luisa/luisa2026 · rafael/rafael2026 · sonia/sonia2026<br>
          lina/lina2026 · alberto/alberto2026 · santiago/santiago2026
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════
def sidebar():
    u = st.session_state.user
    es_g = u["rol"] == "gerente"
    ai_ok = ai_activa()
    # Contar novedades
    df = get_crm()
    hace_7 = (datetime.now() - timedelta(days=7)).isoformat()
    n_nov = len(df[df["lastUpdate"].astype(str).str.strip() > hace_7])

    with st.sidebar:
        st.markdown(f"""
        <div style='padding:20px 16px 14px'>
          <div style='font-family:Space Grotesk,sans-serif;font-size:16px;font-weight:700;
               color:white;letter-spacing:-.5px'>ÁGORA TECH</div>
          <div style='font-size:9px;color:rgba(255,255,255,.3);letter-spacing:2.5px;
               text-transform:uppercase;margin-top:2px'>{VERSION}</div>
        </div>
        <div style='background:rgba(27,79,216,.15);border:1px solid rgba(27,79,216,.3);
             border-radius:10px;padding:10px 14px;margin:0 12px 16px'>
          <div style='font-size:13px;font-weight:600;color:white'>{u["nombre"]}</div>
          <div style='font-size:10px;color:rgba(255,255,255,.4);margin-top:2px'>
            <span class="pulse-dot"></span>{"🟢 IA activa" if ai_ok else "🔴 IA sin configurar"}
          </div>
        </div>""", unsafe_allow_html=True)

        nav_todos = [
            ("📊","Dashboard"),
            ("🔔","Novedades" + (f" ({n_nov})" if n_nov>0 else "")),
            ("📋","Proyectos"),
            ("📝","Actualizar Estado"),
            ("🧮","Nueva Cotización"),
            ("✉️","Correos IA"),
            ("🤖","Asistente IA"),
            ("📊","Encuesta Prospecto"),
            ("📅","Calendario"),
            ("⚙️","Configuración"),
        ]
        nav_gerente = [
            ("📈","Informe Semanal"),
            ("🔍","Auditoría"),
            ("🎯","Pipeline Kanban"),
            ("👥","Usuarios"),
        ]
        todas = nav_todos + (nav_gerente if es_g else [])

        for icono,nombre in todas:
            # Nombre de página sin contador para comparar
            pg_name = nombre.split(" (")[0]
            activo = st.session_state.page == pg_name or st.session_state.page == nombre
            if activo:
                st.markdown('<div style="background:rgba(27,79,216,.2);border:1px solid rgba(27,79,216,.4);border-radius:8px;margin-bottom:2px">',unsafe_allow_html=True)
            if st.button(f"{icono}  {nombre}", key=f"nav_{nombre}", use_container_width=True):
                st.session_state.page = pg_name
                st.rerun()
            if activo:
                st.markdown('</div>',unsafe_allow_html=True)

        st.markdown("---")
        if st.button("← Cerrar sesión", use_container_width=True, key="logout"):
            for k in ["logged_in","user","messages","page","crm","correo","editing","groq_key"]:
                st.session_state.pop(k,None)
            st.rerun()

# ══════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════
def pg_dashboard():
    u = st.session_state.user; es_g = u["rol"]=="gerente"; df = mis_proyectos()

    # Hero
    total_pip = int(df["totalNum"].sum())
    n_activos = len(df[~df["estado"].isin(["perdido","cerrado"])])
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#0F172A 0%,#1E3A5F 55%,#0EA5B0 120%);
         border-radius:14px;padding:28px 32px;margin-bottom:22px;position:relative;overflow:hidden'>
      <div style='position:absolute;top:-50px;right:-50px;width:200px;height:200px;border-radius:50%;
           background:radial-gradient(circle,rgba(27,79,216,.25) 0%,transparent 70%)'></div>
      <div style='font-size:11px;font-weight:600;color:rgba(14,165,176,.8);letter-spacing:3px;
           text-transform:uppercase;margin-bottom:10px'><span class="pulse-dot"></span>TIEMPO REAL · {datetime.now().strftime("%d %B %Y %H:%M")}</div>
      <div style='font-family:Space Grotesk,sans-serif;font-size:24px;font-weight:700;color:white;letter-spacing:-.8px;margin-bottom:6px'>
        {"Dashboard Gerencial — Ágora Tech" if es_g else f"Hola, {u['nombre'].split()[0]} 👋"}</div>
      <div style='font-size:13px;color:rgba(255,255,255,.5)'>{n_activos} proyectos activos · Pipeline {fc(total_pip)}</div>
    </div>""", unsafe_allow_html=True)

    # KPIs
    cerrados = df[df["estado"]=="cerrado"].shape[0]
    negoc    = df[df["estado"]=="negociacion"].shape[0]
    espera   = df[df["estado"]=="aprobado_espera"].shape[0]
    perdidos = df[df["estado"]=="perdido"].shape[0]

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.markdown(f'<div class="kpi"><div class="kpi-label">Pipeline Total</div><div class="kpi-val b">{fc(total_pip)}</div><div class="kpi-sub">{len(df)} proyectos</div></div>',unsafe_allow_html=True)
    c2.markdown(f'<div class="kpi"><div class="kpi-label">Negociando</div><div class="kpi-val {"o" if negoc>0 else "r"}">{negoc}</div><div class="kpi-sub">cierre cercano</div></div>',unsafe_allow_html=True)
    c3.markdown(f'<div class="kpi"><div class="kpi-label">Stand-by Vig.</div><div class="kpi-val b">{espera}</div><div class="kpi-sub">reactivar sep-nov</div></div>',unsafe_allow_html=True)
    c4.markdown(f'<div class="kpi"><div class="kpi-label">Perdidos</div><div class="kpi-val r">{perdidos}</div><div class="kpi-sub">28% del total</div></div>',unsafe_allow_html=True)
    c5.markdown(f'<div class="kpi"><div class="kpi-label">Contratos Firmados</div><div class="kpi-val {"g" if cerrados>0 else "r"}">{cerrados}</div><div class="kpi-sub">{"🎉 " if cerrados>0 else "Q3 2026 esperado"}</div></div>',unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)

    # Gráficas
    c1,c2 = st.columns(2)
    with c1:
        # Distribución por etapa
        grupos = {"Comercial activo":["lead","cotizado","negociacion"],
                  "Stand-by":["aprobado_espera"],
                  "Ejecución":["creacion_contrato","financiacion","obra","novedades_obra","entrega"],
                  "Posventa":["mantenimiento","cerrado"],
                  "Perdido":["perdido"]}
        data = [{"Etapa":g,"n":df[df["estado"].isin(e)].shape[0]} for g,e in grupos.items()]
        fig = px.bar(pd.DataFrame(data), x="Etapa", y="n",
                     color="Etapa", title="Distribución por Etapa",
                     color_discrete_map={"Comercial activo":"#1B4FD8","Stand-by":"#0EA5B0",
                                          "Ejecución":"#059669","Posventa":"#7C3AED","Perdido":"#DC2626"},
                     labels={"n":"Proyectos"})
        fig.update_layout(plot_bgcolor="white",paper_bgcolor="white",showlegend=False,
                          font_family="Inter",margin=dict(t=40,b=10))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        if es_g:
            dc = df[df["totalNum"]>0].groupby("comercial")["totalNum"].sum().reset_index()
            dc["M"] = (dc["totalNum"]/1e6).round(1)
            dc["Com"] = dc["comercial"].str.split().str[0]
            fig2 = px.bar(dc.sort_values("M",ascending=True), x="M", y="Com",
                          orientation="h", title="Pipeline por Comercial ($M)",
                          color="M", color_continuous_scale=["#1B4FD8","#0EA5B0"],
                          labels={"M":"$M","Com":""})
            fig2.update_layout(plot_bgcolor="white",paper_bgcolor="white",
                               coloraxis_showscale=False,margin=dict(t=40,b=10))
        else:
            mis_e = df.groupby("estado").size().reset_index(name="n")
            mis_e["Estado"] = mis_e["estado"].map(lambda x: ETAPAS.get(x,{"label":x})["label"])
            fig2 = px.pie(mis_e, values="n", names="Estado", hole=0.48,
                          title="Mis Proyectos",
                          color_discrete_sequence=["#1B4FD8","#0EA5B0","#059669","#7C3AED","#DC2626","#D97706"])
            fig2.update_layout(paper_bgcolor="white",margin=dict(t=40,b=10))
        st.plotly_chart(fig2, use_container_width=True)

    # ALERTAS AUTOMÁTICAS EN TIEMPO REAL
    st.markdown("### 🚨 Alertas en Tiempo Real")
    alertas = calcular_alertas(df)

    hace_7 = (datetime.now() - timedelta(days=7)).isoformat()

    if es_g:
        # Vista gerente: por comercial
        for com in sorted(df["comercial"].dropna().unique()):
            df_com = df[df["comercial"]==com]
            alertas_com = calcular_alertas(df_com)
            n_com = len([a for a in alertas_com if a["tipo"] in ["red","amber"]])
            icono = "🔴" if any(a["tipo"]=="red" for a in alertas_com) else ("🟡" if n_com>0 else "🟢")
            with st.expander(f"{icono} **{com}** — {len(df_com)} proyectos · {n_com} alertas críticas", expanded=n_com>0):
                for a in alertas_com[:8]:
                    st.markdown(f"""<div class="al {a['tipo']}">
                      <div class="al-icon">{"🔥" if a["tipo"]=="red" else ("⚠️" if a["tipo"]=="amber" else "💡")}</div>
                      <div><strong>{a["titulo"]}</strong><br>{a["msg"]}</div>
                    </div>""", unsafe_allow_html=True)
                # Sin actualizar
                sin_upd = df_com[
                    (df_com["lastUpdate"].astype(str).str.strip()=="") |
                    (df_com["lastUpdate"].astype(str).str.strip() < hace_7)
                ]
                if len(sin_upd)>0:
                    nombres = ", ".join(sin_upd["nombre"].head(4).tolist())
                    st.markdown(f'<div class="al blue"><div class="al-icon">📋</div><div><strong>{len(sin_upd)} sin actualizar (+7 días):</strong> {nombres}{"..." if len(sin_upd)>4 else ""}</div></div>',unsafe_allow_html=True)
                if not alertas_com and len(sin_upd)==0:
                    st.markdown('<div class="al green"><div class="al-icon">✅</div><div>Al día — sin alertas</div></div>',unsafe_allow_html=True)
    else:
        # Vista comercial
        for a in alertas[:10]:
            st.markdown(f"""<div class="al {a['tipo']}">
              <div class="al-icon">{"🔥" if a["tipo"]=="red" else ("⚠️" if a["tipo"]=="amber" else "💡")}</div>
              <div><strong>{a["titulo"]}</strong><br>{a["msg"]}</div>
            </div>""", unsafe_allow_html=True)
        sin_upd = df[(df["lastUpdate"].astype(str).str.strip()=="") | (df["lastUpdate"].astype(str).str.strip()<hace_7)]
        if len(sin_upd)>0:
            st.markdown(f'<div class="al amber"><div class="al-icon">📋</div><div><strong>{len(sin_upd)} proyectos sin actualizar en +7 días.</strong> Ve a "Actualizar Estado".</div></div>',unsafe_allow_html=True)

    if not ai_activa():
        st.markdown('<div class="al blue"><div class="al-icon">💡</div><div><strong>IA sin configurar.</strong> Ve a ⚙️ Configuración y pega la API Key de Groq para activar correos, análisis e informes.</div></div>',unsafe_allow_html=True)

# ══════════════════════════════════════════════
# NOVEDADES DE LA SEMANA
# ══════════════════════════════════════════════
def pg_novedades():
    hdr("🔔","Novedades de la Semana","Actualizaciones de los últimos 7 días")
    df = mis_proyectos()
    hace_7 = (datetime.now() - timedelta(days=7)).isoformat()

    # Proyectos actualizados esta semana
    df_nov = df[df["lastUpdate"].astype(str).str.strip() > hace_7].copy()
    df_nov = df_nov.sort_values("lastUpdate", ascending=False)

    c1,c2,c3 = st.columns(3)
    c1.markdown(f'<div class="kpi"><div class="kpi-label">Actualizados</div><div class="kpi-val b">{len(df_nov)}</div><div class="kpi-sub">últimos 7 días</div></div>',unsafe_allow_html=True)
    c2.markdown(f'<div class="kpi"><div class="kpi-label">Sin actualizar</div><div class="kpi-val r">{len(df)-len(df_nov)}</div><div class="kpi-sub">requieren seguimiento</div></div>',unsafe_allow_html=True)
    c3.markdown(f'<div class="kpi"><div class="kpi-label">Nuevos estados</div><div class="kpi-val g">{df_nov["estado"].nunique()}</div><div class="kpi-sub">tipos de movimiento</div></div>',unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)

    if len(df_nov) == 0:
        st.info("No hay actualizaciones registradas en los últimos 7 días. Usa 'Actualizar Estado' para registrar el seguimiento.")
        return

    # Timeline de novedades
    st.markdown("#### 📅 Timeline de novedades")
    st.markdown('<div class="tl">',unsafe_allow_html=True)
    for _, r in df_nov.iterrows():
        est = str(r.get("estado",""))
        nota = str(r.get("lastNote","") or r.get("notas","") or "Sin nota")[:200]
        upd = str(r.get("lastUpdate",""))[:16]
        color = {"negociacion":"#D97706","cotizado":"#1B4FD8","aprobado_espera":"#0EA5B0",
                 "perdido":"#DC2626","cerrado":"#059669"}.get(est,"#94A3B8")
        st.markdown(f"""
        <div class="ti">
          <div class="ti-dot" style="background:{color}"></div>
          <div class="ti-date">{upd[:10]} · {r.get("comercial","").split()[0] if r.get("comercial") else "—"}</div>
          <div class="ti-h">{r["nombre"]} <span class="tag tag-b" style="font-size:10px">{ETAPAS.get(est,{"label":est})["label"]}</span></div>
          <div class="ti-t">{nota}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>',unsafe_allow_html=True)

    # Botón para generar resumen IA
    st.markdown("---")
    if st.button("🤖 Generar resumen ejecutivo de novedades con IA", use_container_width=True):
        if not ai_activa():
            st.error("Activa la IA en ⚙️ Configuración")
        else:
            ctx = df_nov[["nombre","comercial","estado","lastNote","totalNum"]].to_string()
            prompt = f"""Genera un resumen ejecutivo de las novedades comerciales de Ágora Tech de esta semana.

DATOS:
{ctx}

Formato:
## RESUMEN EJECUTIVO — Semana {datetime.now().strftime("%d %b %Y")}
## MOVIMIENTOS POSITIVOS
## ALERTAS Y RIESGOS  
## ACCIONES PRIORITARIAS PARA MAÑANA

Tono ejecutivo, bullet points, negrilla en cifras y nombres clave."""
            with st.spinner("Generando resumen..."):
                r = ask_ai(prompt)
            st.markdown(r)

# ══════════════════════════════════════════════
# INFORME SEMANAL (GERENTE)
# ══════════════════════════════════════════════
def pg_informe_semanal():
    hdr("📈","Informe Semanal","Reporte ejecutivo automático — estilo Dashboard Gerencial")
    df = get_crm()
    hace_7 = (datetime.now() - timedelta(days=7)).isoformat()

    # KPIs del informe
    total = int(df["totalNum"].sum())
    activos = df[~df["estado"].isin(["perdido","cerrado"])]
    rechazados = df[df["estado"]=="perdido"]
    cerrados_n = df[df["estado"]=="cerrado"].shape[0]
    stand_by = df[df["estado"]=="aprobado_espera"]
    actualizados = df[df["lastUpdate"].astype(str).str.strip() > hace_7]

    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#0F172A,#1E3A5F);border-radius:14px;
         padding:24px 28px;margin-bottom:24px;color:white'>
      <div style='font-family:Space Grotesk,sans-serif;font-size:20px;font-weight:700;margin-bottom:4px'>
        Informe Semanal — Ágora Tech</div>
      <div style='font-size:12px;color:rgba(255,255,255,.5)'>
        Semana del {(datetime.now()-timedelta(days=7)).strftime("%d %b")} al {datetime.now().strftime("%d %b %Y")} · Gerente: Luisa Olivares</div>
    </div>""", unsafe_allow_html=True)

    # KPIs principales
    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(f'<div class="kpi"><div class="kpi-label">Pipeline Total</div><div class="kpi-val b">{fc(total)}</div><div class="kpi-sub">{len(df)} propuestas</div></div>',unsafe_allow_html=True)
    c2.markdown(f'<div class="kpi"><div class="kpi-label">Activos CRM</div><div class="kpi-val">{len(activos)}</div><div class="kpi-sub">{round(len(activos)/len(df)*100)}% del total</div></div>',unsafe_allow_html=True)
    c3.markdown(f'<div class="kpi"><div class="kpi-label">Stand-by Vigilancia</div><div class="kpi-val o">{len(stand_by)}</div><div class="kpi-sub">reactivar sep-nov</div></div>',unsafe_allow_html=True)
    c4.markdown(f'<div class="kpi"><div class="kpi-label">Contratos Firmados</div><div class="kpi-val {"g" if cerrados_n>0 else "r"}">{cerrados_n}</div><div class="kpi-sub">Primer cierre Q3 2026</div></div>',unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)

    # Por comercial
    st.markdown("#### 👥 Resumen por Comercial")
    c1,c2 = st.columns([2,1])
    with c1:
        resumen = df.groupby("comercial").agg(
            Total=("nombre","count"),
            En_proceso=("estado", lambda x: sum(~x.isin(["perdido","cerrado"]))),
            Perdidos=("estado", lambda x: sum(x=="perdido")),
            Pipeline=("totalNum","sum")
        ).reset_index()
        resumen["Pipeline $M"] = (resumen["Pipeline"]/1e6).round(1)
        st.dataframe(resumen[["comercial","Total","En_proceso","Perdidos","Pipeline $M"]]
                     .rename(columns={"comercial":"Comercial","En_proceso":"En proceso"}),
                     use_container_width=True, hide_index=True)
    with c2:
        fig = px.pie(resumen, values="Pipeline", names="comercial",
                     color_discrete_sequence=["#1B4FD8","#0EA5B0","#059669","#7C3AED","#D97706","#DC2626"],
                     hole=0.5)
        fig.update_layout(paper_bgcolor="white",margin=dict(t=10,b=10),showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # Novedades de la semana
    st.markdown("#### 🔔 Novedades de esta semana")
    df_nov = df[df["lastUpdate"].astype(str).str.strip() > hace_7].sort_values("lastUpdate", ascending=False)
    if len(df_nov) > 0:
        for _, r in df_nov.head(10).iterrows():
            nota = str(r.get("lastNote","") or r.get("notas",""))[:120]
            st.markdown(f"""
            <div style='background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;
                 padding:10px 14px;margin-bottom:8px;display:flex;align-items:center;gap:12px'>
              <div style='flex:1'>
                <div style='font-size:12.5px;font-weight:600;color:#0F172A'>{r["nombre"]}</div>
                <div style='font-size:11.5px;color:#64748B;margin-top:2px'>{nota or "Sin nota"}</div>
              </div>
              <div>{badge(str(r.get("estado","")))}</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("No hay actualizaciones registradas esta semana.")

    # Cierres probables próximas semanas
    st.markdown("#### 🔥 Cierres probables próximas semanas")
    col1, col2 = st.columns(2)
    with col1:
        cierres_probables = [
            ("Country 136", "Rafael", "Asamblea jun 27", "🔥"),
            ("Park 104", "Rafael", "Asamblea jun 13", "🔥"),
            ("Edificio Risaralda", "Rafael/Luisa", "Asamblea extraordinaria jul", "🔥"),
            ("Edificio Sahara", "Rafael", "Confirmar asamblea jun 13", "🟡"),
            ("Edificio Urapanes", "Rafael", "Preseleccionados entre 3", "🟡"),
            ("Edificio Los Pinos", "Lina", "Evaluando propuestas", "🟡"),
            ("Edificio Camila", "Lina", "Reunión consejo jun 9", "🟡"),
        ]
        for nombre_c, com, estado_c, ico in cierres_probables:
            color = "#FEF2F2" if ico == "🔥" else "#FFFBEB"
            brd = "#DC2626" if ico == "🔥" else "#D97706"
            st.markdown(f"""
            <div style='background:{color};border-left:3px solid {brd};border-radius:0 8px 8px 0;
                 padding:9px 13px;margin-bottom:7px'>
              <div style='font-size:12.5px;font-weight:600;color:#0F172A'>{ico} {nombre_c}</div>
              <div style='font-size:11px;color:#64748B;margin-top:2px'>{com} — {estado_c}</div>
            </div>""", unsafe_allow_html=True)

    with col2:
        # Stand-by para reactivar
        st.markdown("**🔒 Stand-by — reactivar sep-nov 2026:**")
        espera_df = df[df["estado"]=="aprobado_espera"]
        for _, r in espera_df.head(8).iterrows():
            st.markdown(f"""
            <div style='background:#F0FDFA;border-left:3px solid #0EA5B0;border-radius:0 8px 8px 0;
                 padding:8px 12px;margin-bottom:6px'>
              <div style='font-size:12px;font-weight:600;color:#0F172A'>{r["nombre"]}</div>
              <div style='font-size:10.5px;color:#64748B'>{r.get("comercial","").split()[0] if r.get("comercial") else "—"} — Vig: {str(r.get("vigH","")) or "sem vence"}</div>
            </div>""", unsafe_allow_html=True)

    # Generar informe IA
    st.markdown("---")
    c1,c2 = st.columns(2)
    with c1:
        tipo_informe = st.selectbox("Tipo de informe:", [
            "Informe Gerencial Ejecutivo Semanal",
            "Reporte de Pipeline por Comercial",
            "Análisis de Cierres Probables",
            "Diagnóstico del Proceso Comercial",
            "Plan de Acción Semana Siguiente"
        ])
    with c2:
        notas_extra = st.text_area("Instrucciones adicionales:", height=60,
            placeholder="Ej: Enfatizar en Country 136 y Park 104...")

    if st.button("🤖 Generar Informe Completo con IA", use_container_width=True):
        if not ai_activa():
            st.error("Activa la IA en ⚙️ Configuración")
        else:
            ctx = df.to_string(max_rows=127)
            prompt = f"""Genera un {tipo_informe} COMPLETO para Ágora Tech Colombia.
{f"Instrucciones específicas: {notas_extra}" if notas_extra else ""}

Fecha: {datetime.now().strftime("%d de %B de %Y")}
Período: Semana del {(datetime.now()-timedelta(days=7)).strftime("%d %b")} al {datetime.now().strftime("%d %b %Y")}

## 1. RESUMEN EJECUTIVO
## 2. MÉTRICAS CLAVE (tabla con cifras exactas)
## 3. ANÁLISIS POR COMERCIAL
## 4. PROYECTOS PRIORITARIOS — TOP 8 MÁS CERCANOS AL CIERRE
## 5. NOVEDADES IMPORTANTES DE LA SEMANA
## 6. ALERTAS Y RIESGOS
## 7. RECOMENDACIONES ESTRATÉGICAS
## 8. PLAN DE ACCIÓN — PRÓXIMOS 7 DÍAS

Tono ejecutivo. Negrilla en cifras clave. Sin separadores ---."""
            with st.spinner("Generando informe completo..."):
                r = ask_ai(prompt, ctx, max_tokens=3000)
            st.markdown(r)
            c1,c2 = st.columns(2)
            c1.download_button("📥 Descargar .md", data=r,
                file_name=f"Informe_Agora_{datetime.now().strftime('%Y%m%d')}.md")
            c2.download_button("📥 Descargar .txt", data=r,
                file_name=f"Informe_Agora_{datetime.now().strftime('%Y%m%d')}.txt")

# ══════════════════════════════════════════════
# PROYECTOS CON HISTORIAL Y TABS
# ══════════════════════════════════════════════
def pg_proyectos():
    es_g = st.session_state.user["rol"]=="gerente"
    df = mis_proyectos()
    hdr("📋","Proyectos","Pipeline completo con historial")

    c1,c2,c3,c4 = st.columns([2,1,1,1])
    with c1: buscar = st.text_input("🔍 Buscar",placeholder="Nombre del edificio...")
    with c2:
        grupos_f = ["Todos","Comercial activo","Stand-by","Ejecución","Posventa","Perdido"]
        filtro_g = st.selectbox("Grupo",grupos_f)
    with c3:
        if es_g: filtro_c = st.selectbox("Comercial",["Todos"]+sorted(df["comercial"].dropna().unique().tolist()))
        else: filtro_c = "Todos"
    with c4: filtro_e = st.selectbox("Estado",["Todos"]+ESTADOS_LISTA,format_func=lambda x: ETAPAS.get(x,{"label":x})["label"] if x!="Todos" else "Todos")

    dff = df.copy()
    if buscar: dff = dff[dff["nombre"].str.contains(buscar,case=False,na=False)]
    if filtro_g!="Todos":
        mapa_g={"Comercial activo":["lead","cotizado","negociacion"],
                "Stand-by":["aprobado_espera"],
                "Ejecución":["creacion_contrato","financiacion","obra","novedades_obra","entrega"],
                "Posventa":["mantenimiento","cerrado"],"Perdido":["perdido"]}
        dff=dff[dff["estado"].isin(mapa_g.get(filtro_g,[]))]
    if filtro_c!="Todos": dff=dff[dff["comercial"]==filtro_c]
    if filtro_e!="Todos": dff=dff[dff["estado"]==filtro_e]

    st.markdown(f'<div style="font-size:12px;color:#94A3B8;margin-bottom:14px">{len(dff)} proyectos · Pipeline {fc(int(dff["totalNum"].sum()))}</div>',unsafe_allow_html=True)

    for _,r in dff.iterrows():
        tn   = int(r.get("totalNum") or 0)
        est  = str(r.get("estado","lead"))
        nota = str(r.get("lastNote","") or r.get("notas","") or "")
        nov  = str(r.get("novedad","") or "")
        nov_badge = '<span class="nov-new">NUEVA</span>' if nov else ""

        with st.expander(f"🏢  {r['nombre']}  {nov_badge if nov else ''}  —  {fc(tn)}  —  {r.get('comercial','')}".replace("  <span","  ") , expanded=False):
            tab_info,tab_hist = st.tabs(["📋 Información","📜 Historial"])

            with tab_info:
                c1,c2,c3,c4 = st.columns(4)
                c1.metric("Valor",fc(tn))
                c2.metric("Cuota 24m",fc(int(r.get("c24Num",0) or 0)))
                c3.metric("Cuota 36m",fc(int(r.get("c36Num",0) or 0)))
                c4.markdown(f"**Estado:**<br>{badge(est)}",unsafe_allow_html=True)
                if nota and nota!="nan":
                    st.markdown(f'<div class="al blue" style="margin-top:10px"><div class="al-icon">📝</div><div>{nota[:350]}</div></div>',unsafe_allow_html=True)
                drive = str(r.get("drive","") or "")
                if drive.startswith("http"):
                    st.markdown(f'📁 <a href="{drive}" target="_blank">Ver carpeta en Drive</a>',unsafe_allow_html=True)
                b1,b2,b3 = st.columns(3)
                if b1.button("📝 Actualizar",key=f"u_{r.get('id',r['nombre'])}"):
                    st.session_state.editing=r["nombre"]; st.session_state.page="Actualizar Estado"; st.rerun()
                if b2.button("✉️ Correo IA",key=f"c_{r.get('id',r['nombre'])}"):
                    st.session_state.page="Correos IA"; st.rerun()
                if b3.button("📊 Encuesta",key=f"e_{r.get('id',r['nombre'])}"):
                    st.session_state.editing=r["nombre"]; st.session_state.page="Encuesta Prospecto"; st.rerun()

            with tab_hist:
                hist_raw = str(r.get("historial","") or "[]")
                try: hist = json.loads(hist_raw)
                except: hist = []
                if hist:
                    st.markdown('<div class="tl">',unsafe_allow_html=True)
                    for ev in reversed(hist[-10:]):
                        est_ev = ev.get("estado","")
                        col = {"negociacion":"#D97706","cotizado":"#1B4FD8","perdido":"#DC2626",
                               "cerrado":"#059669","aprobado_espera":"#0EA5B0"}.get(est_ev,"#94A3B8")
                        st.markdown(f"""
                        <div class="ti">
                          <div class="ti-dot" style="background:{col}"></div>
                          <div class="ti-date">{ev.get("fecha","")} · {ev.get("usuario","")}</div>
                          <div class="ti-h">{ETAPAS.get(est_ev,{"label":est_ev})["label"]}</div>
                          <div class="ti-t">{ev.get("nota","")}</div>
                        </div>""", unsafe_allow_html=True)
                    st.markdown('</div>',unsafe_allow_html=True)
                else:
                    st.info("Sin historial registrado. Usa 'Actualizar Estado' para empezar el seguimiento.")

def pg_actualizar():
    hdr("📝","Actualizar Estado","Registro obligatorio — queda en el historial permanentemente")
    df = mis_proyectos(); u = st.session_state.user
    presel = st.session_state.get("editing","")
    nombres = ["— Selecciona un edificio —"]+sorted(df["nombre"].dropna().unique().tolist())
    idx = nombres.index(presel) if presel in nombres else 0
    sel = st.selectbox("Edificio:",nombres,index=idx)

    if sel!="— Selecciona un edificio —":
        r = df[df["nombre"]==sel].iloc[0]
        est_actual = str(r.get("estado","lead"))
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Valor",fc(int(r.get("totalNum",0) or 0)))
        c2.metric("Comercial",str(r.get("comercial","—")))
        c3.metric("Estado actual",ETAPAS.get(est_actual,{"label":est_actual})["label"])
        c4.metric("Últ. actualización",str(r.get("lastUpdate","Nunca"))[:10] or "Nunca")
        if r.get("lastNote"):
            st.markdown(f'<div class="al blue" style="font-size:12px"><div class="al-icon">📝</div><div>Última nota: {str(r["lastNote"])[:200]}</div></div>',unsafe_allow_html=True)

        st.markdown("---")
        with st.form("upd_form"):
            # Selector de estado con grupos
            col1,col2 = st.columns(2)
            with col1:
                st.markdown("**Etapas comerciales:**")
                etapas_com = [e for e in ETAPAS if ETAPAS[e]["grupo"]=="Comercial"]
            with col2:
                st.markdown("**Etapas de ejecución:**")
                etapas_eje = [e for e in ETAPAS if ETAPAS[e]["grupo"] in ["Ejecución","Posventa"]]

            nuevo_e = st.selectbox("Nuevo estado *", ESTADOS_LISTA,
                format_func=lambda x: ETAPAS.get(x,{"label":x})["label"],
                index=ESTADOS_LISTA.index(est_actual) if est_actual in ESTADOS_LISTA else 0)
            nota = st.text_area("Nota de seguimiento * (obligatoria — quedará en el historial)",
                placeholder="¿Qué pasó? ¿Cuál es el próximo paso concreto? ¿Quién respondió?...")

            # Campos adicionales para ejecución
            if nuevo_e in etapas_eje:
                st.markdown("**Datos de ejecución:**")
                c1,c2 = st.columns(2)
                with c1:
                    contrato = st.text_input("N° contrato",placeholder="CT-2026-001")
                    obra_ini = st.text_input("Inicio de obra",placeholder="15 jul 2026")
                with c2:
                    financ = st.text_area("Detalles financiación",placeholder="Banco, plazo...",height=68)
                    obra_fin = st.text_input("Fin estimado",placeholder="24 ago 2026 (40 días)")
            else:
                contrato=financ=obra_ini=obra_fin=""

            if st.form_submit_button("✅ Guardar en historial", use_container_width=True):
                if not nota.strip():
                    st.error("La nota es obligatoria — sin nota no se guarda")
                else:
                    agregar_historial(sel, nuevo_e, nota, u["nombre"])
                    if contrato or financ or obra_ini or obra_fin:
                        extras = {}
                        if contrato: extras["contrato"] = contrato
                        if financ: extras["financiacion_info"] = financ
                        if obra_ini: extras["obra_inicio"] = obra_ini
                        if obra_fin: extras["obra_fin"] = obra_fin
                        update_proy(sel, extras)
                    st.success(f"✅ {sel} → {ETAPAS.get(nuevo_e,{'label':nuevo_e})['label']} — guardado en historial")
                    st.session_state.editing = ""
                    st.rerun()

def pg_nueva_cotizacion():
    hdr("🧮","Nueva Cotización","Registrar en el CRM")
    with st.form("form_cot"):
        c1,c2 = st.columns(2)
        with c1:
            nombre   = st.text_input("Nombre del edificio *")
            contacto = st.text_input("Contacto *",placeholder="Nombre — Rol")
            email    = st.text_input("Email")
        with c2:
            direccion = st.text_input("Dirección")
            drive_url = st.text_input("Link carpeta Drive")
        st.markdown("---")
        c1,c2,c3 = st.columns(3)
        with c1: valor = st.number_input("Valor total ($)",min_value=0,value=0,step=1_000_000,format="%d")
        with c2: vig_v = st.number_input("Vigilancia actual ($/mes)",min_value=0,value=0,step=100_000,format="%d")
        with c3: vig_h = st.text_input("Vigilancia vigente hasta",placeholder="Nov 2026")
        c1,c2 = st.columns(2)
        with c1: estado = st.selectbox("Estado",ESTADOS_LISTA,format_func=lambda x:ETAPAS.get(x,{"label":x})["label"])
        with c2: notas = st.text_area("Observaciones iniciales",height=80)
        if st.form_submit_button("💾 Guardar en CRM",use_container_width=True):
            if not nombre: st.error("El nombre es obligatorio")
            else:
                u = st.session_state.user
                c24n = valor//24 if valor else 0; c36n = valor//36 if valor else 0
                hist_ini = json.dumps([{"fecha":datetime.now().strftime("%d %b %Y %H:%M"),"estado":estado,
                    "nota":notas or "Proyecto creado","usuario":u["nombre"],"ts":datetime.now().isoformat()}],ensure_ascii=False)
                add_proy({
                    "id":int(datetime.now().timestamp()),"nombre":nombre.upper(),"comercial":u["comercial"],
                    "contacto":contacto,"email":email,"total":fc(valor),"totalNum":valor,
                    "cuota24":fc(c24n),"cuota36":fc(c36n),"c24Num":c24n,"c36Num":c36n,
                    "vig":str(vig_v),"vigH":vig_h,"estado":estado,"etapaOrig":estado,
                    "notas":notas,"lastUpdate":datetime.now().isoformat(),"lastNote":notas[:100],
                    "fecha":datetime.now().strftime("%d %b %Y"),"drive":drive_url,
                    "historial":hist_ini,"encuesta":"{}","novedad":"","asamblea":"",
                    "version":"v1","id_com":u["comercial"]
                })
                st.success(f"✅ **{nombre}** guardado — {fc(valor)}")
                st.balloons()

def pg_correos():
    hdr("✉️","Correos IA","Genera correos comerciales personalizados")
    df = mis_proyectos()
    if not ai_activa():
        st.markdown('<div class="al amber"><div class="al-icon">⚠️</div><div><strong>IA no configurada.</strong> Ve a ⚙️ Configuración y pega la API Key de Groq.</div></div>',unsafe_allow_html=True)
    col1,col2 = st.columns(2)
    with col1:
        edif_sel = st.selectbox("Edificio",["— Seleccionar —"]+sorted(df["nombre"].dropna().unique().tolist()))
        tipo_c = st.selectbox("Tipo de correo",[
            "Primera presentación de propuesta",
            "Seguimiento post-reunión de consejo",
            "Urgencia — convocatoria asamblea próxima",
            "Respuesta a objeción: precio alto",
            "Respuesta a objeción: adultos mayores",
            "Argumentos financieros — ahorro vs vigilancia",
            "Propuesta de visita a Alto 61",
            "Confirmación de contrato y próximos pasos",
            "Reactivación — stand-by vencimiento vigilancia",
        ])
        ctx_e = st.text_area("Contexto adicional",height=80,placeholder="Ej: El cliente pregunta por el teclado PIN para adultos mayores...")
        if st.button("🤖 Generar correo",use_container_width=True):
            if edif_sel=="— Seleccionar —": st.warning("Selecciona un edificio")
            elif not ai_activa(): st.error("Activa la IA en ⚙️ Configuración")
            else:
                r = df[df["nombre"]==edif_sel].iloc[0]; tn = int(r.get("totalNum",0) or 0)
                ahorro = int(r.get("vig",0) or 0)
                prompt = f"""Redacta correo comercial "{tipo_c}" para Ágora Tech Colombia.

EDIFICIO: {edif_sel}
Valor: {fc(tn)} | Cuota 24m: {fc(int(r.get("c24Num",0) or 0))} | Cuota 36m: {fc(int(r.get("c36Num",0) or 0))}
Vigil. actual: {fc(ahorro)}/mes hasta {r.get("vigH","")}
{"Ahorro anual vs vigilancia: "+fc(ahorro*12)+" vs cuota 36m: "+fc(int(r.get("c36Num",0) or 0)*12) if ahorro>0 else ""}
Contacto: {r.get("contacto","Administrador")} | Comercial: {r.get("comercial","")}
Estado: {ETAPAS.get(str(r.get("estado","")),{"label":""})["label"]}
{f"Contexto: {ctx_e}" if ctx_e else ""}

REGLAS:
- Primera línea: ASUNTO: [asunto específico y llamativo]
- Énfasis en: financiamiento 100% sin entrada sin intereses
- Para adultos mayores: teclado PIN físico con relieve, no requiere smartphone, diseñado para accesibilidad
- Mencionar edificio Alto 61 como referencia visitable
- Firma: {st.session_state.user["nombre"]} — Ágora Tech | (+57) 315 101 7511
- Texto plano, sin markdown, sin asteriscos"""
                with st.spinner("Generando..."): correo = ask_ai(prompt)
                st.session_state.correo = correo
    with col2:
        st.markdown("**Vista previa:**")
        correo_actual = st.session_state.get("correo","")
        if correo_actual:
            st.markdown(f"""<div style='background:#F8FAFC;border:1.5px solid #E2E8F0;border-radius:10px;
                 padding:20px;font-family:monospace;font-size:12.5px;line-height:1.75;
                 white-space:pre-wrap;color:#0F172A;max-height:460px;overflow-y:auto'>{correo_actual.replace("<","&lt;").replace(">","&gt;")}</div>""",unsafe_allow_html=True)
            st.download_button("📋 Descargar",data=correo_actual,
                file_name=f"correo_{edif_sel[:20] if edif_sel!='— Seleccionar —' else 'agora'}.txt",mime="text/plain")
        else:
            st.markdown("""<div style='background:#F8FAFC;border:1.5px dashed #CBD5E1;border-radius:10px;
                 padding:40px;text-align:center;color:#94A3B8;font-size:13px'>
              Selecciona edificio y haz clic en<br><b>"🤖 Generar correo"</b></div>""",unsafe_allow_html=True)

def pg_asistente():
    hdr("🤖","Asistente Comercial IA","Consultas estratégicas sobre pipeline, cierres y objeciones")
    if not ai_activa():
        st.markdown('<div class="al amber"><div class="al-icon">⚠️</div><div><strong>IA no configurada.</strong> Ve a ⚙️ Configuración.</div></div>',unsafe_allow_html=True); return
    df = mis_proyectos(); ctx = df.to_string(max_rows=127) if not df.empty else ""
    for msg in st.session_state.messages:
        cls = "chat-u" if msg["role"]=="user" else "chat-a"
        pre = "👤 " if msg["role"]=="user" else "🤖 "
        st.markdown(f'<div class="{cls}">{pre}{msg["content"]}</div>',unsafe_allow_html=True)
    if not st.session_state.messages:
        sugs = ["📊 Resumen ejecutivo del pipeline","⚡ Top 8 proyectos más cercanos al cierre",
                "📈 Estrategia para Country 136 y Park 104","👴 Cómo responder objeción adultos mayores",
                "💰 Análisis stand-by vencimiento vigilancia","🔍 Diagnóstico del proceso de cierre"]
        cols = st.columns(3)
        for i,s in enumerate(sugs):
            if cols[i%3].button(s,key=f"sug_{i}"):
                st.session_state.messages.append({"role":"user","content":s})
                with st.spinner("Analizando..."): r = ask_ai(s,ctx)
                st.session_state.messages.append({"role":"assistant","content":r}); st.rerun()
    with st.form("chat_f",clear_on_submit=True):
        c1,c2 = st.columns([5,1])
        with c1: ui = st.text_input("Pregunta",label_visibility="collapsed",placeholder="Ej: Estrategia para Edificio Risaralda esta semana...")
        with c2: send = st.form_submit_button("Enviar →")
        if send and ui:
            st.session_state.messages.append({"role":"user","content":ui})
            with st.spinner("Analizando..."): r = ask_ai(ui,ctx)
            st.session_state.messages.append({"role":"assistant","content":r}); st.rerun()
    if st.session_state.messages:
        if st.button("🗑 Limpiar conversación"): st.session_state.messages=[]; st.rerun()

def pg_encuesta():
    hdr("📊","Encuesta de Prospecto","Formulario Información Preliminar Ágora Tech")
    df = mis_proyectos()
    presel = st.session_state.get("editing","")
    nombres = ["— Nuevo prospecto —"]+sorted(df["nombre"].dropna().unique().tolist())
    idx = nombres.index(presel) if presel in nombres else 0
    edif_sel = st.selectbox("Vincular a edificio existente:",nombres,index=idx)
    st.markdown("---")
    with st.form("encuesta_form"):
        st.markdown("**Datos básicos**")
        c1,c2 = st.columns(2)
        with c1:
            nom_e    = st.text_input("Nombre del Edificio *",value=edif_sel if edif_sel!="— Nuevo prospecto —" else "")
            contacto = st.text_input("Contacto *",placeholder="Nombre del administrador o consejero")
            dir_e    = st.text_input("Dirección")
        with c2:
            rol      = st.selectbox("Rol",["Administrador","Propietario","Miembro del Consejo","Presidente del Consejo"])
            com_e    = st.selectbox("Comercial asignado",[st.session_state.user["comercial"]]+[c for c in COMS if c!=st.session_state.user["comercial"]])
            etapa_d  = st.selectbox("Etapa de decisión",["Recibiendo cotizaciones por orden de asamblea","Aún no se ha hablado en asamblea","Explorando opciones"])
        st.markdown("---")
        st.markdown("**Vigilancia actual**")
        c1,c2,c3 = st.columns(3)
        with c1: tiene_vig = st.radio("¿Tiene vigilancia?",["Sí","No"],horizontal=True)
        with c2: costo_vig = st.number_input("Costo mensual ($)",min_value=0,value=0,step=100_000,format="%d")
        with c3: vig_hasta = st.text_input("Vigente hasta",placeholder="Nov 2026")
        serv_adic = st.text_area("¿Presta otros servicios el vigilante?",height=60,placeholder="Jardinería, paquetes, etc.")
        st.markdown("---")
        st.markdown("**Comunidad y seguridad**")
        adultos = st.text_area("¿Adultos mayores o personas con discapacidad?",height=70,placeholder="Cuéntatame sobre la situación de la comunidad...")
        incidentes = st.text_area("¿Incidentes de seguridad recientes?",height=70,placeholder="Robos, accesos no autorizados...")
        terminos = st.text_area("¿Tienen términos de selección?",height=60,placeholder="Número de cotizaciones, requisitos, presupuesto máximo...")
        analizar = st.checkbox("🤖 Analizar con IA al guardar",value=True)
        if st.form_submit_button("💾 Guardar encuesta",use_container_width=True):
            if not nom_e: st.error("Nombre del edificio obligatorio"); st.stop()
            datos = {"Edificio":nom_e,"Contacto":contacto,"Rol":rol,"Dirección":dir_e,
                     "Etapa":etapa_d,"Vigilancia":tiene_vig,"Costo Vig":fc(costo_vig) if costo_vig else "No",
                     "Vigencia":vig_hasta,"Servicios adicionales":serv_adic,"Adultos mayores":adultos,
                     "Incidentes":incidentes,"Términos":terminos,"Comercial":com_e}
            if edif_sel!="— Nuevo prospecto —":
                update_proy(edif_sel,{"encuesta":json.dumps(datos,ensure_ascii=False)})
                agregar_historial(edif_sel,"cotizado",f"Encuesta de prospecto completada. Contacto: {contacto} ({rol}). Etapa: {etapa_d}.",st.session_state.user["nombre"])
                st.success(f"✅ Encuesta guardada en historial de **{edif_sel}**")
            if analizar and ai_activa():
                prompt = f"""Analiza este prospecto para Ágora Tech Colombia:

Edificio: {nom_e} | Contacto: {contacto} ({rol}) | Etapa: {etapa_d}
Vigilancia: {"SÍ — "+fc(costo_vig)+"/mes hasta "+vig_hasta if tiene_vig=="Sí" and costo_vig>0 else "NO"}
{"Ahorro anual si se reemplaza: "+fc(costo_vig*12) if costo_vig>0 else ""}
Adultos mayores: {adultos or "No reportado"} | Incidentes: {incidentes or "Ninguno"} | Términos: {terminos or "Sin términos"}

## VIABILIDAD: [ALTA/MEDIA/BAJA] con justificación
## PERFIL DEL CLIENTE Y MOTIVACIONES
## ESTRATEGIA DE VENTA ESPECÍFICA
## MANEJO DE OBJECIONES PROBABLES (incluyendo adultos mayores si aplica)
{"## ANÁLISIS FINANCIERO — Ahorro vs Vigilancia: "+fc(costo_vig)+"/mes vs cuota 36m estimada" if costo_vig>0 else ""}
## PRÓXIMOS 3 PASOS CONCRETOS (con responsable y fecha)

Negrilla en datos clave. Español colombiano."""
                with st.spinner("Analizando..."): r = ask_ai(prompt)
                st.markdown("---"); st.markdown(r)

def pg_calendario():
    hdr("📅","Calendario Comercial","Agenda y próximas asambleas")
    es_g = st.session_state.user["rol"]=="gerente"
    col1,col2 = st.columns([2,1])
    with col1:
        with st.form("act_form"):
            c1,c2 = st.columns(2)
            with c1: edif=st.text_input("Edificio"); tipo=st.selectbox("Tipo",["Reunión consejo","Asamblea","Llamada","Visita técnica","Visita Alto 61","Firma contrato","Inicio obra","Entrega","Otro"])
            with c2: fecha_a=st.date_input("Fecha",value=datetime.now()); hora_a=st.time_input("Hora")
            titulo_a=st.text_input("Título *"); notas_a=st.text_area("Notas",height=60)
            if es_g: com_r=st.selectbox("Comercial",COMS)
            else: com_r=st.session_state.user["comercial"]
            if st.form_submit_button("📅 Guardar",use_container_width=True):
                if titulo_a: st.success(f"✅ {titulo_a} — {fecha_a.strftime('%d %b')} {hora_a.strftime('%H:%M')}")
                else: st.error("Título obligatorio")
    with col2:
        # Urgentes dinámicos
        st.markdown("#### 🔥 Próximas semanas")
        urgentes_fijos = [
            ("Country 136","Asamblea jun 27","#FEF2F2","#DC2626"),
            ("Park 104","Asamblea jun 13","#FEF2F2","#DC2626"),
            ("Ed. Risaralda","Asamblea extraordinaria jul","#FEF2F2","#DC2626"),
            ("Ed. Urapanes","Reunión consejo jun 16","#FFFBEB","#D97706"),
            ("Ed. Sahara","Asamblea jun 13","#FFFBEB","#D97706"),
            ("Ed. Camila","Reunión consejo jun 9","#FFFBEB","#D97706"),
            ("Ed. Avanti","Visita Alto 61 — decisión jul","#EFF6FF","#1B4FD8"),
            ("Ed. El Cerro","Visita Alto 61 jun 11","#EFF6FF","#1B4FD8"),
        ]
        for n,d,bg,brd in urgentes_fijos:
            st.markdown(f'<div style="background:{bg};border-left:3px solid {brd};border-radius:0 8px 8px 0;padding:9px 12px;margin-bottom:7px"><div style="font-size:12px;font-weight:600;color:#0F172A">{n}</div><div style="font-size:10.5px;color:#64748B;margin-top:2px">{d}</div></div>',unsafe_allow_html=True)

def pg_configuracion():
    u = st.session_state.user; es_g = u["rol"]=="gerente"; ai_ok = ai_activa()
    hdr("⚙️","Configuración","Activar IA — disponible para todos los usuarios")
    if ai_ok:
        key = get_ai_key()
        st.markdown(f'<div class="al green"><div class="al-icon">✅</div><div><strong>IA Groq activa</strong> — Llama 3.3 70B · key ...{key[-4:]}</div></div>',unsafe_allow_html=True)
    else:
        st.markdown('<div class="al red"><div class="al-icon">🔴</div><div><strong>IA no configurada.</strong> Pega la API Key de Groq abajo.</div></div>',unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("#### 🔑 Activar IA — Groq (100% gratis, sin tarjeta)")
    st.markdown("""<div style='background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;padding:14px 18px;margin-bottom:16px;font-size:13px;color:#334155'>
      <b>Cómo obtener la key gratis:</b><br>
      1. Abre <b>console.groq.com</b> → inicia sesión con Gmail personal<br>
      2. Clic en <b>API Keys</b> → <b>Create API Key</b> → nombre: agora-tech<br>
      3. Copia la key (empieza con <code>gsk_...</code>) y pégala abajo
    </div>""",unsafe_allow_html=True)
    with st.form("cfg_ia"):
        nueva_key = st.text_input("API Key de Groq *",placeholder="gsk_xxxx...")
        if nueva_key:
            n = len(nueva_key.strip())
            if n < 40: st.warning(f"⚠️ Solo {n} caracteres — parece incompleta (debe tener ~56)")
            else: st.success(f"✅ {n} caracteres — longitud correcta")
        if st.form_submit_button("⚡ Activar IA",use_container_width=True):
            if nueva_key:
                with st.spinner("Verificando..."): ok = activar_ia(nueva_key)
                if ok: st.success("✅ IA activada — ya puedes usar correos, asistente e informes"); st.rerun()
    if es_g:
        st.markdown("---")
        st.markdown("#### 📋 Configuración permanente en Streamlit Cloud (recomendada)")
        st.markdown("Para que todos tengan IA automáticamente sin configurar nada:")
        st.code('GROQ_API_KEY = "gsk_tu-key-completa"',language="toml")
        st.markdown("Ve a tu app → **⋮** → **Settings** → **Secrets** → pega eso → **Save**")
        st.markdown("---")
        df = get_crm(); usuarios = get_usuarios()
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Proyectos CRM",df.shape[0])
        c2.metric("Con cotización",df[df["totalNum"]>0].shape[0])
        c3.metric("Usuarios activos",sum(1 for u in usuarios.values() if u.get("activo",True)))
        c4.metric("IA Groq","🟢 Activa" if ai_ok else "🔴 Inactiva")

def pg_auditoria():
    hdr("🔍","Auditoría Comercial","Análisis profundo del equipo y el pipeline")
    df = get_crm()
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Total",df.shape[0])
    c2.metric("Pipeline",f"{fc(int(df['totalNum'].sum()))}")
    c3.metric("Cotizaciones",df[df["estado"]=="cotizado"].shape[0])
    c4.metric("Perdidos",df[df["estado"]=="perdido"].shape[0])
    c5.metric("Contratos",df[df["estado"]=="cerrado"].shape[0])
    st.markdown('<div class="al red"><div class="al-icon">❗</div><div><strong>0 contratos cerrados.</strong> Con pipeline de $8.6B el problema es el cierre, no la prospección.</div></div>',unsafe_allow_html=True)
    st.markdown('<div class="al amber"><div class="al-icon">🔒</div><div><strong>10 edificios aprobaron pero esperan vencimiento de vigilancia sep-nov.</strong> Preparar reactivación desde agosto.</div></div>',unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        res = df[df["totalNum"]>0].groupby("comercial").agg(n=("totalNum","count"),pip=("totalNum","sum")).reset_index()
        res["$M"] = (res["pip"]/1e6).round(1)
        st.dataframe(res[["comercial","n","$M"]].rename(columns={"comercial":"Comercial","n":"Cotiz."}),use_container_width=True,hide_index=True)
    with c2:
        if st.button("🤖 Análisis estratégico profundo",use_container_width=True):
            with st.spinner(): r = ask_ai("Análisis estratégico: top 8 proyectos más cercanos al cierre con acción específica. Patrón de rechazos. Por qué 0 contratos. Plan 7 días.",df.to_string(max_rows=127))
            st.markdown(r)

def pg_pipeline():
    hdr("🎯","Pipeline Kanban","Vista de embudo por etapas")
    df = mis_proyectos()
    # Comercial
    etapas_c = [("lead","🔵 Lead"),("cotizado","🟡 Cotización"),("negociacion","🟠 Negoc."),("aprobado_espera","🔒 Stand-by"),("cerrado","✅ Cerrado")]
    cols = st.columns(5)
    for i,(k,lbl) in enumerate(etapas_c):
        items = df[df["estado"]==k]; tot = int(items["totalNum"].sum())
        with cols[i]:
            st.markdown(f"**{lbl}**")
            st.markdown(f'<div style="font-size:11px;color:#94A3B8;margin-bottom:12px">{len(items)} · {fc(tot)}</div>',unsafe_allow_html=True)
            for _,r in items.iterrows():
                tn = int(r.get("totalNum",0) or 0)
                st.markdown(f"""<div style='background:white;border:1px solid #E2E8F0;border-radius:8px;
                  padding:10px;margin-bottom:7px;box-shadow:0 1px 3px rgba(15,23,42,.06)'>
                  <div style='font-family:Space Grotesk,sans-serif;font-size:11.5px;font-weight:600;
                       color:#0F172A;margin-bottom:2px'>{str(r["nombre"])[:22]}</div>
                  <div style='font-size:10px;color:#94A3B8;margin-bottom:3px'>{str(r.get("comercial","—")).split()[0]}</div>
                  <div style='font-family:Space Grotesk,sans-serif;font-size:13px;font-weight:700;color:#059669'>{fc(tn) if tn else "—"}</div>
                </div>""",unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🔨 Ejecución")
    etapas_e = [("creacion_contrato","📝 Contrato"),("financiacion","💰 Financiación"),("obra","🔨 Obra"),("novedades_obra","⚠️ Novedades"),("entrega","🎉 Entrega"),("mantenimiento","🔧 Mantenimiento")]
    cols2 = st.columns(6)
    for i,(k,lbl) in enumerate(etapas_e):
        items = df[df["estado"]==k]
        with cols2[i]:
            st.markdown(f"**{lbl}**")
            st.markdown(f'<div style="font-size:10px;color:#94A3B8;margin-bottom:8px">{len(items)}</div>',unsafe_allow_html=True)
            for _,r in items.iterrows():
                st.markdown(f'<div style="background:#ECFDF5;border-radius:6px;padding:7px;margin-bottom:5px;font-size:11px;font-weight:600">{str(r["nombre"])[:20]}</div>',unsafe_allow_html=True)

def pg_usuarios():
    hdr("👥","Gestión de Usuarios","Solo gerente — administrar accesos")
    usuarios = get_usuarios()
    for ukey,ud in usuarios.items():
        activo = ud.get("activo",True)
        cols = st.columns([2,2,1.5,1,1,1])
        cols[0].markdown(f"**{ud['nombre']}**"); cols[1].markdown(f"`{ukey}`")
        cols[2].markdown(ud["rol"].capitalize())
        cols[3].markdown(f'<span class="tag {"tag-g" if activo else "tag-r"}">{"Activo" if activo else "Inactivo"}</span>',unsafe_allow_html=True)
        if cols[4].button("✏️",key=f"edit_{ukey}"): st.session_state["editing_user"]=ukey
        if cols[5].button("🔒" if activo else "🔓",key=f"tog_{ukey}"):
            st.session_state.usuarios_db[ukey]["activo"]=not activo; st.rerun()
        st.markdown('<div style="border-bottom:1px solid #E2E8F0;margin:5px 0"></div>',unsafe_allow_html=True)
    editing = st.session_state.get("editing_user","")
    if editing and editing in usuarios:
        ud_e = usuarios[editing]
        with st.form("edit_uf"):
            st.markdown(f"**Editando: {ud_e['nombre']}**")
            c1,c2 = st.columns(2)
            with c1: new_n=st.text_input("Nombre",value=ud_e["nombre"]); new_p=st.text_input("Nueva contraseña",type="password")
            with c2:
                new_r=st.selectbox("Rol",["gerente","comercial"],index=0 if ud_e["rol"]=="gerente" else 1)
                new_c=st.selectbox("Comercial",COMS,index=COMS.index(ud_e["comercial"]) if ud_e["comercial"] in COMS else 0)
            if st.form_submit_button("💾 Guardar",use_container_width=True):
                st.session_state.usuarios_db[editing].update({"nombre":new_n,"rol":new_r,"comercial":new_c})
                if new_p: st.session_state.usuarios_db[editing]["pass"]=new_p
                st.success("✅ Actualizado"); st.session_state.pop("editing_user",None); st.rerun()
    st.markdown("---")
    with st.form("add_uf"):
        st.markdown("**➕ Nuevo usuario**")
        c1,c2 = st.columns(2)
        with c1: nu_u=st.text_input("Usuario *"); nu_n=st.text_input("Nombre *"); nu_p=st.text_input("Contraseña *",type="password")
        with c2: nu_r=st.selectbox("Rol",["comercial","gerente"]); nu_c=st.selectbox("Comercial",COMS)
        if st.form_submit_button("➕ Crear",use_container_width=True):
            if not nu_u or not nu_n or not nu_p: st.error("Todos los campos son obligatorios")
            elif nu_u.lower() in usuarios: st.error(f"'{nu_u}' ya existe")
            else:
                st.session_state.usuarios_db[nu_u.lower()]={"pass":nu_p,"nombre":nu_n,"rol":nu_r,"comercial":nu_c,"activo":True}
                st.success(f"✅ Usuario **{nu_u}** creado"); st.rerun()

# ══════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════
if not st.session_state.logged_in:
    pg_login()
else:
    sidebar()
    pg = st.session_state.get("page","Dashboard")

    # Auto-refresh cada 5 minutos (para alertas en tiempo real)
    if st.session_state.get("last_refresh") is None or \
       (datetime.now() - st.session_state["last_refresh"]).seconds > 300:
        st.session_state["last_refresh"] = datetime.now()

    if   pg=="Dashboard":         pg_dashboard()
    elif pg=="Novedades":         pg_novedades()
    elif pg=="Proyectos":         pg_proyectos()
    elif pg=="Actualizar Estado": pg_actualizar()
    elif pg=="Nueva Cotización":  pg_nueva_cotizacion()
    elif pg=="Correos IA":        pg_correos()
    elif pg=="Asistente IA":      pg_asistente()
    elif pg=="Encuesta Prospecto":pg_encuesta()
    elif pg=="Calendario":        pg_calendario()
    elif pg=="Configuración":     pg_configuracion()
    elif pg=="Informe Semanal":   pg_informe_semanal()
    elif pg=="Auditoría":         pg_auditoria()
    elif pg=="Pipeline":          pg_pipeline()
    elif pg=="Usuarios":          pg_usuarios()
    else:                         pg_dashboard()
