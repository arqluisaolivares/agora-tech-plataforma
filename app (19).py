"""
ÁGORA TECH — Plataforma Comercial v7
Dashboard interactivo · Novedades en tiempo real · Pagos · Informes socios
"""

import streamlit as st
from groq import Groq
import pandas as pd
import json, os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# ══════════════════════════════════════════════════════════════
# CONSTANTES
# ══════════════════════════════════════════════════════════════
VERSION   = "v7 · Jun 2026"
GROQ_MODEL = "llama-3.3-70b-versatile"

ETAPAS = {
    "lead":              {"label":"Lead nuevo",           "grupo":"Comercial", "color":"#DBEAFE", "dot":"#3B82F6"},
    "cotizado":          {"label":"Cotización enviada",   "grupo":"Comercial", "color":"#FEF9C3", "dot":"#F59E0B"},
    "negociacion":       {"label":"Negociando",           "grupo":"Comercial", "color":"#FED7AA", "dot":"#F97316"},
    "aprobado_espera":   {"label":"Aprobado–Stand-by",    "grupo":"Comercial", "color":"#E0F2FE", "dot":"#0EA5E9"},
    "perdido":           {"label":"Perdido",              "grupo":"Comercial", "color":"#FEE2E2", "dot":"#EF4444"},
    "creacion_contrato": {"label":"Creación Contrato",    "grupo":"Ejecución", "color":"#D1FAF0", "dot":"#10B981"},
    "financiacion":      {"label":"Financiación",         "grupo":"Ejecución", "color":"#D1FAF0", "dot":"#10B981"},
    "obra":              {"label":"En Obra",               "grupo":"Ejecución", "color":"#ECFDF5", "dot":"#059669"},
    "novedades_obra":    {"label":"Novedades Obra",        "grupo":"Ejecución", "color":"#FFFBEB", "dot":"#D97706"},
    "entrega":           {"label":"Entrega",               "grupo":"Ejecución", "color":"#ECFDF5", "dot":"#059669"},
    "mantenimiento":     {"label":"Mantenimiento",         "grupo":"Posventa",  "color":"#EFF6FF", "dot":"#6366F1"},
    "cerrado":           {"label":"Cerrado",               "grupo":"Posventa",  "color":"#D1FAF0", "dot":"#059669"},
}
ESTADOS_LISTA = list(ETAPAS.keys())
COMS = ["RAFAEL TORRES","SONIA CASTRO","LINA CALLE","ALBERTO FERRER","SANTIAGO BOHORQUEZ","LUISA OLIVARES"]

AI_SYSTEM = """Eres el asesor estratégico de Ágora Tech Colombia — automatización de accesos para copropiedades.
PRODUCTO: SALTO HomeLok. Financiación 100% 24/36 meses sin intereses. 40 días instalación.
SITUACIÓN: 127 propuestas, $8.6B pipeline, 0 contratos. Cierres probables jul-sep 2026.
Responde en español colombiano. Directo y accionable."""

# ══════════════════════════════════════════════════════════════
# STREAMLIT CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(page_title="Ágora Tech", page_icon="🔐", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

:root{
  --bg:#F1F5F9; --surface:#fff; --s2:#F8FAFC; --s3:#F1F5F9;
  --border:#E2E8F0; --b2:#CBD5E1;
  --ink:#0F172A; --ink2:#334155; --ink3:#64748B; --ink4:#94A3B8;
  --blue:#2563EB; --blue-lt:#EFF6FF; --blue-dk:#1D4ED8;
  --teal:#0D9488; --green:#059669; --green-lt:#ECFDF5;
  --red:#DC2626; --red-lt:#FEF2F2;
  --amber:#D97706; --amber-lt:#FFFBEB;
  --purple:#7C3AED; --purple-lt:#F5F3FF;
  --sh:0 1px 3px rgba(15,23,42,.08),0 1px 2px rgba(15,23,42,.05);
  --sh2:0 4px 16px rgba(15,23,42,.1);
  --r:12px; --r2:8px;
}

*{box-sizing:border-box}
html,body,[class*="css"]{font-family:'Inter',sans-serif!important;background:var(--bg)!important;color:var(--ink)!important}
h1,h2,h3,.sg{font-family:'Space Grotesk',sans-serif!important}

/* ── SIDEBAR premium ── */
[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#0F172A 0%,#1E293B 100%)!important;
  border-right:1px solid rgba(255,255,255,.05)!important;
  width:220px!important;
}
[data-testid="stSidebar"] section{padding:0!important}
[data-testid="stSidebar"] *{color:rgba(255,255,255,.7)!important}
[data-testid="stSidebar"] .stButton>button{
  background:transparent!important;color:rgba(255,255,255,.6)!important;
  border:none!important;box-shadow:none!important;border-radius:var(--r2)!important;
  text-align:left!important;font-size:12.5px!important;font-weight:500!important;
  padding:9px 12px!important;width:100%!important;margin:1px 0!important;
  transition:all .15s!important;letter-spacing:0!important;
}
[data-testid="stSidebar"] .stButton>button:hover{
  background:rgba(255,255,255,.07)!important;color:white!important;transform:none!important;
}

/* ── BOTONES principales ── */
.stButton>button{
  background:linear-gradient(135deg,#2563EB,#0D9488)!important;color:white!important;
  font-family:'Space Grotesk',sans-serif!important;font-weight:600!important;
  border:none!important;border-radius:var(--r2)!important;letter-spacing:-.1px!important;
  transition:all .18s!important;box-shadow:0 2px 8px rgba(37,99,235,.3)!important;
}
.stButton>button:hover{transform:translateY(-1px)!important;box-shadow:0 5px 18px rgba(37,99,235,.4)!important}
.stButton>button[kind="secondary"]{
  background:var(--surface)!important;color:var(--ink)!important;
  border:1.5px solid var(--b2)!important;box-shadow:none!important;transform:none!important;
}

/* ── KPI CARDS ── */
.kpi-card{
  background:var(--surface);border:1px solid var(--border);border-radius:var(--r);
  padding:18px 20px;box-shadow:var(--sh);cursor:pointer;
  transition:all .2s;position:relative;overflow:hidden;
}
.kpi-card:hover{transform:translateY(-3px);box-shadow:var(--sh2);border-color:var(--b2)}
.kpi-card::after{content:'';position:absolute;bottom:0;left:0;right:0;height:2px}
.kpi-card.blue::after{background:var(--blue)}
.kpi-card.green::after{background:var(--green)}
.kpi-card.amber::after{background:var(--amber)}
.kpi-card.red::after{background:var(--red)}
.kpi-card.teal::after{background:var(--teal)}
.kpi-label{font-size:10px;font-weight:700;color:var(--ink4);text-transform:uppercase;letter-spacing:.8px;margin-bottom:8px}
.kpi-val{font-family:'Space Grotesk',sans-serif;font-size:28px;font-weight:700;line-height:1;letter-spacing:-1px}
.kpi-val.blue{color:var(--blue)}.kpi-val.green{color:var(--green)}.kpi-val.amber{color:var(--amber)}
.kpi-val.red{color:var(--red)}.kpi-val.teal{color:var(--teal)}
.kpi-sub{font-size:11px;color:var(--ink4);margin-top:5px}
.kpi-hint{font-size:10px;color:var(--blue);margin-top:6px;font-weight:600}

/* ── ALERTAS ── */
.al{border-radius:10px;padding:11px 14px;margin-bottom:8px;display:flex;gap:10px;
  border:1px solid;font-size:12.5px;line-height:1.7;transition:all .15s;cursor:default}
.al:hover{transform:translateX(2px)}
.al-ic{font-size:16px;flex-shrink:0;margin-top:1px}
.al.red{background:var(--red-lt);border-color:#FCA5A5;color:#7F1D1D}
.al.amber{background:var(--amber-lt);border-color:#FDE68A;color:#78350F}
.al.green{background:var(--green-lt);border-color:#6EE7B7;color:#065F46}
.al.blue{background:var(--blue-lt);border-color:#BFDBFE;color:#1E3A8A}
.al.teal{background:#F0FDFA;border-color:#99F6E4;color:#134E4A}

/* ── CARDS ── */
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--r);
  box-shadow:var(--sh);overflow:hidden;margin-bottom:14px}
.card-h{padding:13px 18px;border-bottom:1px solid var(--border);display:flex;
  align-items:center;justify-content:space-between}
.card-title{font-family:'Space Grotesk',sans-serif;font-size:13px;font-weight:600;color:var(--ink)}
.card-b{padding:16px 18px}

/* ── EDIFICIO ROWS interactivos ── */
.edif-row{background:var(--surface);border:1px solid var(--border);border-radius:var(--r2);
  padding:13px 16px;margin-bottom:7px;cursor:pointer;transition:all .15s;
  display:flex;align-items:center;gap:12px}
.edif-row:hover{border-color:var(--blue);box-shadow:var(--sh2);transform:translateX(2px)}
.edif-name{font-weight:600;font-size:13px;color:var(--ink);flex:1}
.edif-com{font-size:11px;color:var(--ink4);margin-top:1px}
.edif-val{font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:13px;color:var(--green)}
.edif-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0}

/* ── TAGS ── */
.tag{display:inline-flex;align-items:center;padding:2px 9px;border-radius:20px;
  font-size:10.5px;font-weight:600;white-space:nowrap}
.tag-g{background:var(--green-lt);color:#065F46;border:1px solid #6EE7B7}
.tag-r{background:var(--red-lt);color:#991B1B;border:1px solid #FCA5A5}
.tag-b{background:var(--blue-lt);color:#1E3A8A;border:1px solid #BFDBFE}
.tag-a{background:var(--amber-lt);color:#92400E;border:1px solid #FDE68A}
.tag-p{background:var(--purple-lt);color:#5B21B6;border:1px solid #DDD6FE}
.tag-t{background:#F0FDFA;color:#134E4A;border:1px solid #99F6E4}
.tag-gray{background:var(--s3);color:var(--ink3);border:1px solid var(--b2)}

/* ── TIMELINE ── */
.tl{position:relative;padding-left:24px}
.tl::before{content:'';position:absolute;left:7px;top:8px;bottom:0;width:2px;
  background:var(--border);border-radius:1px}
.ti{position:relative;margin-bottom:14px}
.ti-dot{position:absolute;left:-24px;top:4px;width:12px;height:12px;border-radius:50%;
  border:2px solid white;box-shadow:0 0 0 2px var(--b2)}
.ti-date{font-size:10px;font-weight:700;color:var(--ink4);text-transform:uppercase;letter-spacing:.4px}
.ti-h{font-size:13px;font-weight:600;color:var(--ink);margin:1px 0}
.ti-t{font-size:12px;color:var(--ink3);line-height:1.6}

/* ── NOVEDAD ITEM ── */
.nov-item{background:var(--surface);border:1px solid var(--border);border-radius:var(--r2);
  padding:12px 16px;margin-bottom:8px;transition:all .15s;cursor:pointer;
  border-left:3px solid var(--blue)}
.nov-item:hover{box-shadow:var(--sh2);transform:translateX(2px)}
.nov-item.red{border-left-color:var(--red)}
.nov-item.green{border-left-color:var(--green)}
.nov-item.amber{border-left-color:var(--amber)}
.nov-title{font-weight:600;font-size:13px;color:var(--ink)}
.nov-meta{font-size:11px;color:var(--ink4);margin-top:2px}
.nov-text{font-size:12.5px;color:var(--ink3);margin-top:5px;line-height:1.6}

/* ── PAGO ITEM ── */
.pago-row{background:var(--surface);border:1px solid var(--border);border-radius:var(--r2);
  padding:11px 16px;margin-bottom:6px;display:flex;align-items:center;gap:12px}
.pago-name{font-size:12.5px;font-weight:600;color:var(--ink);flex:1}
.pago-cat{font-size:10.5px;color:var(--ink4)}
.pago-val{font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:14px}
.pago-val.gasto{color:var(--red)}.pago-val.ingreso{color:var(--green)}

/* ── CHAT ── */
.chat-u{background:linear-gradient(135deg,#2563EB,#0D9488);color:white;padding:11px 15px;
  border-radius:16px 16px 3px 16px;margin:7px 0;font-weight:500;max-width:80%;
  margin-left:auto;display:block;font-size:13px}
.chat-a{background:var(--surface);border:1px solid var(--border);padding:13px 17px;
  border-radius:16px 16px 16px 3px;margin:7px 0;max-width:90%;
  box-shadow:var(--sh);line-height:1.75;display:block;font-size:13px}

/* ── PULSE ── */
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.35}}
.dot-live{display:inline-block;width:7px;height:7px;background:#22C55E;border-radius:50%;
  animation:pulse 2s infinite;margin-right:5px;vertical-align:middle}

/* ── HERO ── */
.hero{background:linear-gradient(135deg,#0F172A 0%,#1E3A5F 60%,#0D9488 130%);
  border-radius:14px;padding:24px 28px;margin-bottom:22px;position:relative;overflow:hidden;color:white}
.hero::before{content:'';position:absolute;top:-60px;right:-60px;width:220px;height:220px;
  border-radius:50%;background:radial-gradient(circle,rgba(37,99,235,.2) 0%,transparent 70%)}

/* Fix form */
div[data-testid="stForm"]{border:none!important;padding:0!important}

/* Metricas Streamlit */
[data-testid="metric-container"]{
  background:var(--surface);border:1px solid var(--border);border-radius:var(--r);
  padding:14px!important;box-shadow:var(--sh)}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# USUARIOS
# ══════════════════════════════════════════════════════════════
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

# ══════════════════════════════════════════════════════════════
# IA — GROQ
# ══════════════════════════════════════════════════════════════
def get_ai_key():
    k = st.session_state.get("groq_key","")
    if k: return k
    try:
        k = st.secrets["GROQ_API_KEY"]
        if k: st.session_state["groq_key"]=k; return k
    except: pass
    return ""

def ai_activa(): return bool(get_ai_key())

def activar_ia(key):
    key = key.strip()
    if not key.startswith("gsk_") or len(key)<20:
        st.error("La key debe empezar con gsk_"); return False
    try:
        Groq(api_key=key).chat.completions.create(model=GROQ_MODEL,messages=[{"role":"user","content":"OK"}],max_tokens=5)
        st.session_state["groq_key"]=key; return True
    except Exception as e:
        st.error(f"Key inválida: {str(e)[:80]}"); return False

def ask_ai(prompt, ctx="", max_tokens=2000):
    key = get_ai_key()
    if not key: return "⚠️ IA no configurada. Ve a ⚙️ Configuración."
    try:
        msgs = [{"role":"system","content":AI_SYSTEM}]
        msgs.append({"role":"user","content":f"DATOS CRM:\n{ctx[:18000]}\n\nSOLICITUD:\n{prompt}" if ctx else prompt})
        r = Groq(api_key=key).chat.completions.create(model=GROQ_MODEL,messages=msgs,max_tokens=max_tokens,temperature=0.7)
        return r.choices[0].message.content
    except Exception as e: return f"Error IA: {e}"

# ══════════════════════════════════════════════════════════════
# CRM
# ══════════════════════════════════════════════════════════════
def normalizar(estado):
    e = str(estado or "").strip().lower()
    if "vencimiento" in e or ("aprobado" in e and "aut" in e): return "aprobado_espera"
    if "aprobado" in e and "pendiente" in e: return "cotizado"
    if "aprobado" in e: return "cotizado"
    if "negoci" in e or "avanzado" in e: return "negociacion"
    if "cotiz" in e or "conversando" in e or "proceso" in e or "pendiente" in e: return "cotizado"
    if "stand" in e or "retomar" in e or "suspendid" in e: return "aprobado_espera"
    if "rechaz" in e or "perdido" in e: return "perdido"
    if "cerrado" in e: return "cerrado"
    if "contrato" in e: return "creacion_contrato"
    if "financ" in e: return "financiacion"
    if "obra" in e: return "obra"
    if "novedad" in e: return "novedades_obra"
    if "entrega" in e: return "entrega"
    if "mantenimiento" in e: return "mantenimiento"
    return e if e in ETAPAS else "lead"

@st.cache_data
def cargar_base():
    base = os.path.dirname(os.path.abspath(__file__))
    ruta = os.path.join(base,"proyectos.json")
    if os.path.exists(ruta):
        with open(ruta,encoding="utf-8") as f: return json.load(f)
    return []

PROYECTOS_BASE = cargar_base()

def get_crm():
    if st.session_state.get("crm") is None:
        rows=[]
        for p in PROYECTOS_BASE:
            est_raw = str(p.get("etapaOrig","") or p.get("estado",""))
            estado = normalizar(est_raw)
            if estado not in ETAPAS: estado="lead"
            rows.append({
                "id":p.get("id",""), "nombre":p.get("nombre",""), "comercial":p.get("comercial",""),
                "contacto":p.get("contacto",""), "email":p.get("email",""),
                "totalNum":int(float(p.get("totalNum",0) or 0)),
                "c24Num":int(float(p.get("c24Num",0) or 0)),
                "c36Num":int(float(p.get("c36Num",0) or 0)),
                "vig":p.get("vig",""), "vigH":p.get("vigH",""),
                "estado":estado, "etapaOrig":est_raw,
                "notas":p.get("notas",""), "lastUpdate":p.get("lastUpdate",""),
                "lastNote":p.get("lastNote",""), "fecha":p.get("fecha",""),
                "drive":p.get("drive",""),
                "historial":p.get("historial","[]"),
                "encuesta":p.get("encuesta","{}"),
                "novedad":p.get("novedad",""),
            })
        st.session_state.crm = pd.DataFrame(rows)
    return st.session_state.crm

def mis_proyectos():
    df=get_crm(); u=st.session_state.get("user")
    if not u: return df.iloc[0:0]
    if u["rol"]=="gerente": return df
    return df[df["comercial"].str.upper()==u["comercial"].upper()]

def update_proy(nombre,campos):
    df=get_crm()
    mask=df["nombre"]==nombre
    if mask.any():
        for k,v in campos.items(): df.loc[mask,k]=v
        st.session_state.crm=df

def agregar_historial(nombre,estado,nota,usuario):
    df=get_crm(); mask=df["nombre"]==nombre
    if not mask.any(): return
    try: hist=json.loads(str(df.loc[mask,"historial"].iloc[0] or "[]"))
    except: hist=[]
    hist.append({"fecha":datetime.now().strftime("%d %b %Y %H:%M"),"estado":estado,"nota":nota,"usuario":usuario,"ts":datetime.now().isoformat()})
    df.loc[mask,"historial"]=json.dumps(hist,ensure_ascii=False)
    df.loc[mask,"lastNote"]=nota
    df.loc[mask,"lastUpdate"]=datetime.now().isoformat()
    df.loc[mask,"estado"]=estado
    df.loc[mask,"novedad"]=f"{datetime.now().strftime('%d %b')} — {nota[:100]}"
    st.session_state.crm=df

def add_proy(datos):
    df=get_crm()
    st.session_state.crm=pd.concat([pd.DataFrame([datos]),df],ignore_index=True)

def fc(n):
    try:
        n=int(float(n or 0))
        return "$0" if n==0 else "$"+f"{n:,}".replace(",",".")
    except: return "$0"

def badge(estado):
    e=ETAPAS.get(estado,{"label":estado,"dot":"#94A3B8"})
    return f'<span class="tag" style="background:{ETAPAS.get(estado,{}).get("color","#F1F5F9")};border:1px solid rgba(0,0,0,.07);color:#0F172A">{e["label"]}</span>'

def hdr(icon,title,sub=""):
    st.markdown(f"""<div style='display:flex;align-items:center;gap:14px;margin-bottom:22px;padding-bottom:14px;border-bottom:1px solid var(--border)'>
      <div style='width:40px;height:40px;border-radius:9px;background:linear-gradient(135deg,#2563EB,#0D9488);display:flex;align-items:center;justify-content:center;font-size:19px;flex-shrink:0'>{icon}</div>
      <div><div style='font-family:Space Grotesk,sans-serif;font-size:18px;font-weight:700;color:var(--ink);letter-spacing:-.4px'>{title}</div>
      {'<div style="font-size:11.5px;color:var(--ink4);margin-top:1px">'+sub+'</div>' if sub else ''}</div>
    </div>""",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════
def init():
    for k,v in {"logged_in":False,"user":None,"page":"Dashboard","messages":[],
                "crm":None,"correo":"","editing":"","vista_estado":None}.items():
        if k not in st.session_state: st.session_state[k]=v
init()

if not st.session_state.get("groq_key"):
    try:
        k=st.secrets["GROQ_API_KEY"]
        if k: st.session_state["groq_key"]=k
    except: pass

# ══════════════════════════════════════════════════════════════
# LOGIN
# ══════════════════════════════════════════════════════════════
def pg_login():
    c1,c2,c3=st.columns([1,1.1,1])
    with c2:
        st.markdown("""<div style='text-align:center;padding:52px 0 28px'>
          <div style='font-family:Space Grotesk,sans-serif;font-size:10px;font-weight:700;color:#64748B;letter-spacing:5px;text-transform:uppercase;margin-bottom:18px'>PLATAFORMA COMERCIAL</div>
          <div style='font-family:Space Grotesk,sans-serif;font-size:40px;font-weight:700;color:#0F172A;letter-spacing:-2px'>ÁGORA TECH</div>
          <div style='width:32px;height:3px;background:linear-gradient(90deg,#2563EB,#0D9488);margin:16px auto;border-radius:2px'></div>
          <div style='font-size:13px;color:#94A3B8'>Gestión Comercial</div>
        </div>""",unsafe_allow_html=True)
        with st.form("lf"):
            u=st.text_input("Usuario",placeholder="rafael / sonia / lina / luisa...")
            p=st.text_input("Contraseña",type="password",placeholder="••••••••")
            if st.form_submit_button("Ingresar →",use_container_width=True):
                un=u.strip().lower(); users=get_usuarios()
                if un in users and users[un]["activo"] and users[un]["pass"]==p:
                    st.session_state.logged_in=True; st.session_state.user=users[un]; st.rerun()
                else: st.error("Usuario o contraseña incorrectos")
        st.markdown("""<div style='background:#F8FAFC;border:1px solid #E2E8F0;border-radius:9px;padding:11px;margin-top:12px;font-size:11px;color:#94A3B8;text-align:center'>
          luisa/luisa2026 · rafael/rafael2026 · sonia/sonia2026<br>lina/lina2026 · alberto/alberto2026 · santiago/santiago2026
        </div>""",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
def sidebar():
    u=st.session_state.user; es_g=u["rol"]=="gerente"; ai_ok=ai_activa()
    df=mis_proyectos()
    hace_7=(datetime.now()-timedelta(days=7)).isoformat()
    n_nov=len(df[df["lastUpdate"].astype(str).str.strip()>hace_7])

    with st.sidebar:
        # Logo
        st.markdown(f"""<div style='padding:20px 16px 8px'>
          <div style='font-family:Space Grotesk,sans-serif;font-size:17px;font-weight:700;color:white;letter-spacing:-.5px'>Ágora Tech</div>
          <div style='font-size:9px;color:rgba(255,255,255,.25);letter-spacing:2px;text-transform:uppercase;margin-top:1px'>{VERSION}</div>
        </div>
        <div style='background:rgba(37,99,235,.15);border:1px solid rgba(37,99,235,.3);border-radius:9px;padding:10px 13px;margin:6px 12px 16px'>
          <div style='font-size:12.5px;font-weight:600;color:white'>{u["nombre"]}</div>
          <div style='font-size:10px;color:rgba(255,255,255,.4);margin-top:2px'>
            <span class="dot-live"></span>{"IA activa" if ai_ok else "IA sin configurar"}</div>
        </div>""",unsafe_allow_html=True)

        # Secciones del menú
        secciones = [
            ("PRINCIPAL",[("📊","Dashboard"),("🔔",f"Novedades{' ('+str(n_nov)+')' if n_nov>0 else ''}")]),
            ("COMERCIAL",[("📋","Proyectos"),("📝","Actualizar Estado"),("🧮","Nueva Cotización"),("📊","Encuesta Prospecto"),("📅","Calendario")]),
            ("IA",[("✉️","Correos IA"),("🤖","Asistente IA")]),
        ]
        if es_g:
            secciones += [
                ("GERENCIA",[("📈","Informe Semanal"),("💰","Pagos y Finanzas"),("🔍","Auditoría"),("🎯","Pipeline")]),
                ("ADMIN",[("👥","Usuarios"),("⚙️","Configuración")]),
            ]
        else:
            secciones += [("CONFIG",[("⚙️","Configuración")])]

        for sec_title, items in secciones:
            st.markdown(f'<div style="font-size:9px;font-weight:700;color:rgba(255,255,255,.25);letter-spacing:2px;text-transform:uppercase;padding:10px 12px 4px">{sec_title}</div>',unsafe_allow_html=True)
            for icono,nombre in items:
                pg_name = nombre.split(" (")[0]
                activo = st.session_state.page == pg_name
                if activo:
                    st.markdown('<div style="background:rgba(37,99,235,.25);border-radius:8px;margin:0 8px 2px">',unsafe_allow_html=True)
                    if st.button(f"{icono}  {nombre}",key=f"nav_{nombre}",use_container_width=True):
                        st.session_state.page=pg_name; st.rerun()
                    st.markdown('</div>',unsafe_allow_html=True)
                else:
                    if st.button(f"{icono}  {nombre}",key=f"nav_{nombre}",use_container_width=True):
                        st.session_state.page=pg_name; st.rerun()

        st.markdown('<div style="margin:12px 12px 0;border-top:1px solid rgba(255,255,255,.07);padding-top:10px">',unsafe_allow_html=True)
        if st.button("← Salir",use_container_width=True,key="logout"):
            for k in ["logged_in","user","messages","page","crm","correo","editing","groq_key","vista_estado"]:
                st.session_state.pop(k,None)
            st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# DASHBOARD — INTERACTIVO
# ══════════════════════════════════════════════════════════════
def pg_dashboard():
    u=st.session_state.user; es_g=u["rol"]=="gerente"; df=mis_proyectos()

    # Si hay un estado seleccionado, mostrar lista filtrada
    if st.session_state.get("vista_estado"):
        est=st.session_state.vista_estado
        lbl=ETAPAS.get(est,{"label":est})["label"]
        col1,col2=st.columns([4,1])
        with col1: hdr("📋",f"Proyectos — {lbl}",f"Clic en un edificio para ver el detalle")
        with col2:
            if st.button("← Volver al Dashboard"):
                st.session_state.vista_estado=None; st.rerun()
        df_f=df[df["estado"]==est]
        for _,r in df_f.iterrows():
            tn=int(r.get("totalNum",0) or 0)
            nota=str(r.get("lastNote","") or r.get("notas","") or "")[:120]
            dot=ETAPAS.get(est,{"dot":"#94A3B8"})["dot"]
            upd=str(r.get("lastUpdate",""))[:10] or "Sin actualizar"
            with st.expander(f"🏢 {r['nombre']}  ·  {fc(tn)}  ·  {str(r.get('comercial','')).split()[0] if r.get('comercial') else '—'}"):
                c1,c2,c3=st.columns(3)
                c1.metric("Valor total",fc(tn))
                c2.metric("Cuota 36m",fc(int(r.get("c36Num",0) or 0)))
                c3.metric("Última actualización",upd)
                if nota and nota!="nan":
                    st.markdown(f'<div class="al blue"><div class="al-ic">📝</div><div>{nota}</div></div>',unsafe_allow_html=True)
                # Historial
                try: hist=json.loads(str(r.get("historial","[]") or "[]"))
                except: hist=[]
                if hist:
                    st.markdown("**Historial:**")
                    st.markdown('<div class="tl">',unsafe_allow_html=True)
                    for ev in reversed(hist[-5:]):
                        dc=ETAPAS.get(ev.get("estado",""),{"dot":"#94A3B8"})["dot"]
                        st.markdown(f'<div class="ti"><div class="ti-dot" style="background:{dc}"></div><div class="ti-date">{ev.get("fecha","")} · {ev.get("usuario","")}</div><div class="ti-h">{ETAPAS.get(ev.get("estado",""),{"label":ev.get("estado","")})["label"]}</div><div class="ti-t">{ev.get("nota","")}</div></div>',unsafe_allow_html=True)
                    st.markdown('</div>',unsafe_allow_html=True)
                b1,b2=st.columns(2)
                if b1.button("📝 Actualizar estado",key=f"du_{r['nombre']}"):
                    st.session_state.editing=r["nombre"]; st.session_state.page="Actualizar Estado"; st.session_state.vista_estado=None; st.rerun()
                if b2.button("✉️ Generar correo IA",key=f"dc_{r['nombre']}"):
                    st.session_state.page="Correos IA"; st.session_state.vista_estado=None; st.rerun()
        return

    # ── HERO ──
    total_pip=int(df["totalNum"].sum()); n_activos=len(df[~df["estado"].isin(["perdido","cerrado"])])
    st.markdown(f"""<div class="hero">
      <div style='font-size:10px;font-weight:700;color:rgba(13,148,136,.9);letter-spacing:3px;text-transform:uppercase;margin-bottom:10px'><span class="dot-live"></span>EN VIVO · {datetime.now().strftime("%d %B %Y %H:%M")}</div>
      <div style='font-family:Space Grotesk,sans-serif;font-size:22px;font-weight:700;color:white;letter-spacing:-.6px;margin-bottom:5px'>{"Dashboard Gerencial" if es_g else f"Hola, {u['nombre'].split()[0]} 👋"}</div>
      <div style='font-size:13px;color:rgba(255,255,255,.45)'>{n_activos} proyectos activos · Pipeline {fc(total_pip)}</div>
    </div>""",unsafe_allow_html=True)

    # ── KPIs INTERACTIVOS ──
    st.markdown("#### Resumen del pipeline — *clic en cualquier tarjeta para ver los edificios*")

    total_n=len(df)
    activos_n=len(df[~df["estado"].isin(["perdido","cerrado"])])
    standby_n=len(df[df["estado"]=="aprobado_espera"])
    rechazados_n=len(df[df["estado"]=="perdido"])
    cerrados_n=len(df[df["estado"]=="cerrado"])
    neg_n=len(df[df["estado"]=="negociacion"])
    cotiz_n=len(df[df["estado"]=="cotizado"])

    c1,c2,c3,c4,c5 = st.columns(5)

    with c1:
        st.markdown(f'<div class="kpi-card blue"><div class="kpi-label">Presentadas</div><div class="kpi-val blue">{total_n}</div><div class="kpi-sub">Ene–Jun 2026</div></div>',unsafe_allow_html=True)

    with c2:
        st.markdown(f'<div class="kpi-card amber"><div class="kpi-label">En seguimiento</div><div class="kpi-val amber">{cotiz_n}</div><div class="kpi-sub">cotizaciones activas</div><div class="kpi-hint">▸ Ver lista</div></div>',unsafe_allow_html=True)
        if st.button("Ver activos →",key="k_activos",use_container_width=True):
            st.session_state.vista_estado="cotizado"; st.rerun()

    with c3:
        st.markdown(f'<div class="kpi-card teal"><div class="kpi-label">Stand-by Vig.</div><div class="kpi-val teal">{standby_n}</div><div class="kpi-sub">reactivar sep-nov</div><div class="kpi-hint">▸ Ver lista</div></div>',unsafe_allow_html=True)
        if st.button("Ver stand-by →",key="k_standby",use_container_width=True):
            st.session_state.vista_estado="aprobado_espera"; st.rerun()

    with c4:
        st.markdown(f'<div class="kpi-card red"><div class="kpi-label">Rechazados</div><div class="kpi-val red">{rechazados_n}</div><div class="kpi-sub">28% del total</div><div class="kpi-hint">▸ Ver lista</div></div>',unsafe_allow_html=True)
        if st.button("Ver rechazados →",key="k_rechaz",use_container_width=True):
            st.session_state.vista_estado="perdido"; st.rerun()

    with c5:
        st.markdown(f'<div class="kpi-card green"><div class="kpi-label">Contratos</div><div class="kpi-val {"green" if cerrados_n>0 else "red"}">{cerrados_n}</div><div class="kpi-sub">{"🎉 Primer cierre!" if cerrados_n>0 else "Q3 2026 esperado"}</div></div>',unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)

    # ── NEGOCIANDO — urgente ──
    neg_df=df[df["estado"]=="negociacion"]
    if len(neg_df)>0:
        st.markdown("#### 🔥 Negociando ahora — acción inmediata")
        for _,r in neg_df.iterrows():
            nota=str(r.get("lastNote","") or r.get("notas","") or "Seguimiento urgente")[:150]
            st.markdown(f'<div class="al red"><div class="al-ic">🔥</div><div><strong>{r["nombre"]}</strong> · {str(r.get("comercial","")).split()[0] if r.get("comercial") else "—"} · {fc(int(r.get("totalNum",0) or 0))}<br>{nota}</div></div>',unsafe_allow_html=True)

    # ── GRÁFICAS ──
    c1,c2=st.columns(2)
    with c1:
        data=[{"Etapa":"Cotización","n":cotiz_n},{"Etapa":"Stand-by","n":standby_n},
              {"Etapa":"Negociando","n":neg_n},{"Etapa":"Perdido","n":rechazados_n},{"Etapa":"Cerrado","n":cerrados_n}]
        fig=px.bar(pd.DataFrame(data),x="Etapa",y="n",title="Proyectos por etapa",
                   color="Etapa",color_discrete_map={"Cotización":"#2563EB","Stand-by":"#0D9488",
                    "Negociando":"#F97316","Perdido":"#EF4444","Cerrado":"#059669"},labels={"n":""})
        fig.update_layout(plot_bgcolor="white",paper_bgcolor="white",showlegend=False,
                          font_family="Inter",title_font_family="Space Grotesk",margin=dict(t=36,b=8,l=0,r=0))
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        if es_g:
            dc=df[df["totalNum"]>0].groupby("comercial")["totalNum"].sum().reset_index()
            dc["M"]=(dc["totalNum"]/1e6).round(1); dc["Com"]=dc["comercial"].str.split().str[0]
            fig2=px.bar(dc.sort_values("M",ascending=True),x="M",y="Com",orientation="h",
                        title="Pipeline por comercial ($M)",color="M",
                        color_continuous_scale=["#2563EB","#0D9488"],labels={"M":"$M","Com":""})
            fig2.update_layout(plot_bgcolor="white",paper_bgcolor="white",coloraxis_showscale=False,
                               font_family="Inter",title_font_family="Space Grotesk",margin=dict(t=36,b=8))
        else:
            mis_e=df.groupby("estado").size().reset_index(name="n")
            mis_e["Estado"]=mis_e["estado"].map(lambda x:ETAPAS.get(x,{"label":x})["label"])
            fig2=px.pie(mis_e,values="n",names="Estado",hole=0.48,title="Mis proyectos",
                        color_discrete_sequence=["#2563EB","#F59E0B","#F97316","#EF4444","#059669","#0D9488"])
            fig2.update_layout(paper_bgcolor="white",font_family="Inter",title_font_family="Space Grotesk",margin=dict(t=36,b=8))
        st.plotly_chart(fig2,use_container_width=True)

    # ── ALERTAS automáticas ──
    st.markdown("#### 🚨 Alertas")
    hace_7=(datetime.now()-timedelta(days=7)).isoformat()
    if es_g:
        for com in sorted(df["comercial"].dropna().unique()):
            dc=df[df["comercial"]==com]
            neg_c=dc[dc["estado"]=="negociacion"]
            esp_c=dc[dc["estado"]=="aprobado_espera"]
            sin_c=dc[(dc["lastUpdate"].astype(str).str.strip()=="")|(dc["lastUpdate"].astype(str).str.strip()<hace_7)]
            n_al=len(neg_c)+len(esp_c)+(1 if len(sin_c)>0 else 0)
            ico="🔴" if len(neg_c)>0 else ("🟡" if n_al>0 else "🟢")
            with st.expander(f"{ico} {com} — {len(dc)} proyectos · {n_al} alertas",expanded=n_al>0):
                for _,r in neg_c.iterrows():
                    nota=str(r.get("lastNote","") or r.get("notas",""))[:100]
                    st.markdown(f'<div class="al red"><div class="al-ic">🔥</div><div><strong>{r["nombre"]}</strong><br>{nota or "Seguimiento urgente"}</div></div>',unsafe_allow_html=True)
                for _,r in esp_c.iterrows():
                    vig=str(r.get("vigH",""))
                    if any(m in vig.lower() for m in ["jun","jul","ago","sep","oct","nov"]):
                        st.markdown(f'<div class="al teal"><div class="al-ic">🔒</div><div><strong>Reactivar: {r["nombre"]}</strong> — Vencimiento vigilancia: {vig}</div></div>',unsafe_allow_html=True)
                if len(sin_c)>0:
                    ns=", ".join(sin_c["nombre"].head(4).tolist())
                    st.markdown(f'<div class="al amber"><div class="al-ic">📋</div><div><strong>{len(sin_c)} sin actualizar (+7 días):</strong> {ns}{"..." if len(sin_c)>4 else ""}</div></div>',unsafe_allow_html=True)
                if n_al==0:
                    st.markdown('<div class="al green"><div class="al-ic">✅</div><div>Al día</div></div>',unsafe_allow_html=True)
    else:
        mi_df=df
        neg_m=mi_df[mi_df["estado"]=="negociacion"]
        sin_m=mi_df[(mi_df["lastUpdate"].astype(str).str.strip()=="")|(mi_df["lastUpdate"].astype(str).str.strip()<hace_7)]
        for _,r in neg_m.iterrows():
            nota=str(r.get("lastNote","") or r.get("notas",""))[:150]
            st.markdown(f'<div class="al red"><div class="al-ic">🔥</div><div><strong>NEGOCIACIÓN: {r["nombre"]}</strong><br>{nota}</div></div>',unsafe_allow_html=True)
        if len(sin_m)>0:
            st.markdown(f'<div class="al amber"><div class="al-ic">📋</div><div><strong>{len(sin_m)} proyectos sin actualizar en +7 días.</strong> Ve a "Actualizar Estado".</div></div>',unsafe_allow_html=True)
        if len(neg_m)==0 and len(sin_m)==0:
            st.markdown('<div class="al green"><div class="al-ic">✅</div><div>Todo al día — sin alertas pendientes</div></div>',unsafe_allow_html=True)
    if not ai_activa():
        st.markdown('<div class="al blue"><div class="al-ic">💡</div><div><strong>IA sin configurar.</strong> Ve a ⚙️ Configuración.</div></div>',unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# NOVEDADES — INTERACTIVAS
# ══════════════════════════════════════════════════════════════
def pg_novedades():
    hdr("🔔","Novedades","Actualizaciones de los últimos 7 días — clic para ver el detalle")
    df=mis_proyectos()
    hace_7=(datetime.now()-timedelta(days=7)).isoformat()
    df_nov=df[df["lastUpdate"].astype(str).str.strip()>hace_7].sort_values("lastUpdate",ascending=False)
    df_sin=df[~(df["lastUpdate"].astype(str).str.strip()>hace_7)]

    c1,c2,c3=st.columns(3)
    c1.markdown(f'<div class="kpi-card green"><div class="kpi-label">Actualizados</div><div class="kpi-val green">{len(df_nov)}</div><div class="kpi-sub">últimos 7 días</div></div>',unsafe_allow_html=True)
    c2.markdown(f'<div class="kpi-card red"><div class="kpi-label">Sin actualizar</div><div class="kpi-val red">{len(df_sin)}</div><div class="kpi-sub">requieren seguimiento</div></div>',unsafe_allow_html=True)
    c3.markdown(f'<div class="kpi-card blue"><div class="kpi-label">Pipeline movido</div><div class="kpi-val blue">{fc(int(df_nov["totalNum"].sum()))}</div><div class="kpi-sub">en proyectos activos</div></div>',unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)

    if len(df_nov)==0:
        st.info("No hay actualizaciones esta semana. Usa 'Actualizar Estado' para registrar seguimiento.")
    else:
        st.markdown("#### ✅ Actualizados esta semana")
        for _,r in df_nov.iterrows():
            est=str(r.get("estado",""))
            nota=str(r.get("lastNote","") or r.get("notas","") or "")[:180]
            dot=ETAPAS.get(est,{"dot":"#94A3B8"})["dot"]
            upd=str(r.get("lastUpdate",""))[:10]
            col_class={"negociacion":"red","cotizado":"blue","perdido":"red","cerrado":"green","aprobado_espera":"amber"}.get(est,"blue")

            with st.expander(f"🏢 {r['nombre']}  ·  {ETAPAS.get(est,{'label':est})['label']}  ·  {upd}"):
                c1,c2,c3=st.columns(3)
                c1.metric("Valor",fc(int(r.get("totalNum",0) or 0)))
                c2.metric("Comercial",str(r.get("comercial","—")).split()[0] if r.get("comercial") else "—")
                c3.metric("Estado",ETAPAS.get(est,{"label":est})["label"])
                if nota and nota!="nan":
                    st.markdown(f'<div class="al blue"><div class="al-ic">📝</div><div>{nota}</div></div>',unsafe_allow_html=True)
                try: hist=json.loads(str(r.get("historial","[]") or "[]"))
                except: hist=[]
                if hist:
                    st.markdown("**Historial reciente:**")
                    st.markdown('<div class="tl">',unsafe_allow_html=True)
                    for ev in reversed(hist[-4:]):
                        dc=ETAPAS.get(ev.get("estado",""),{"dot":"#94A3B8"})["dot"]
                        st.markdown(f'<div class="ti"><div class="ti-dot" style="background:{dc}"></div><div class="ti-date">{ev.get("fecha","")} · {ev.get("usuario","")}</div><div class="ti-h">{ETAPAS.get(ev.get("estado",""),{"label":ev.get("estado","")})["label"]}</div><div class="ti-t">{ev.get("nota","")}</div></div>',unsafe_allow_html=True)
                    st.markdown('</div>',unsafe_allow_html=True)
                if st.button("📝 Actualizar ahora",key=f"n_upd_{r['nombre']}"):
                    st.session_state.editing=r["nombre"]; st.session_state.page="Actualizar Estado"; st.rerun()

    if len(df_sin)>0:
        st.markdown("---")
        st.markdown("#### ⚠️ Sin actualizar esta semana")
        df_sin_sorted=df_sin[df_sin["totalNum"]>0].sort_values("totalNum",ascending=False)
        for _,r in df_sin_sorted.head(15).iterrows():
            est=str(r.get("estado",""))
            upd=str(r.get("lastUpdate",""))[:10] or "Nunca"
            col=st.columns([3,1.5,1.5,1])
            col[0].markdown(f"**{r['nombre']}**")
            col[1].markdown(f"<small style='color:#94A3B8'>{str(r.get('comercial','')).split()[0] if r.get('comercial') else '—'}</small>",unsafe_allow_html=True)
            col[2].markdown(f"<small style='color:#94A3B8'>{upd}</small>",unsafe_allow_html=True)
            if col[3].button("📝",key=f"ns_{r['nombre']}",help="Actualizar"):
                st.session_state.editing=r["nombre"]; st.session_state.page="Actualizar Estado"; st.rerun()

    st.markdown("---")
    if st.button("🤖 Generar resumen ejecutivo de novedades con IA",use_container_width=True):
        if not ai_activa(): st.error("Activa la IA en ⚙️ Configuración")
        else:
            ctx=df_nov[["nombre","comercial","estado","lastNote","totalNum"]].to_string() if len(df_nov)>0 else "Sin novedades esta semana"
            with st.spinner("Generando..."): r=ask_ai(f"Resumen ejecutivo de novedades comerciales semana {datetime.now().strftime('%d %b')}. ## MOVIMIENTOS POSITIVOS ## ALERTAS ## ACCIONES PRIORITARIAS MAÑANA. Bullet points, negrilla en nombres.",ctx)
            st.markdown(r)

# ══════════════════════════════════════════════════════════════
# INFORME SEMANAL (GERENTE)
# ══════════════════════════════════════════════════════════════
def pg_informe_semanal():
    hdr("📈","Informe Semanal","Para socios y equipo directivo — generado automáticamente")
    df=get_crm(); hace_7=(datetime.now()-timedelta(days=7)).isoformat()

    # Banner
    st.markdown(f"""<div style='background:linear-gradient(135deg,#0F172A,#1E3A5F);border-radius:12px;padding:20px 24px;margin-bottom:22px;color:white'>
      <div style='font-family:Space Grotesk,sans-serif;font-size:18px;font-weight:700'>Informe Gerencial — Ágora Tech</div>
      <div style='font-size:11.5px;color:rgba(255,255,255,.45);margin-top:3px'>
        Semana {(datetime.now()-timedelta(days=7)).strftime("%d %b")} – {datetime.now().strftime("%d %b %Y")} · Gerente: Luisa Olivares · {len(df)} propuestas totales</div>
    </div>""",unsafe_allow_html=True)

    # KPIs
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Pipeline activo",fc(int(df[~df["estado"].isin(["perdido","cerrado"])]["totalNum"].sum())))
    c2.metric("Propuestas totales",f"{len(df)}")
    c3.metric("Stand-by reactivar",f"{len(df[df['estado']=='aprobado_espera'])}")
    c4.metric("Contratos firmados",f"{len(df[df['estado']=='cerrado'])}")

    # Por comercial
    st.markdown("#### 👥 Por comercial")
    res=df.groupby("comercial").agg(Total=("nombre","count"),Activos=("estado",lambda x:sum(~x.isin(["perdido","cerrado"]))),Pipeline=("totalNum","sum")).reset_index()
    res["$M"]=(res["Pipeline"]/1e6).round(1)
    st.dataframe(res[["comercial","Total","Activos","$M"]].rename(columns={"comercial":"Comercial"}),use_container_width=True,hide_index=True)

    # Novedades
    df_nov=df[df["lastUpdate"].astype(str).str.strip()>hace_7].sort_values("lastUpdate",ascending=False)
    st.markdown(f"#### 🔔 Novedades de la semana — {len(df_nov)} actualizaciones")
    for _,r in df_nov.head(8).iterrows():
        nota=str(r.get("lastNote","") or r.get("notas",""))[:100]
        st.markdown(f"""<div style='background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;padding:9px 13px;margin-bottom:6px;display:flex;align-items:center;gap:12px'>
          <div style='flex:1'><div style='font-size:12.5px;font-weight:600;color:#0F172A'>{r["nombre"]}</div>
          <div style='font-size:11.5px;color:#64748B;margin-top:2px'>{nota or "Sin nota"}</div></div>
          {badge(str(r.get("estado","")))}
        </div>""",unsafe_allow_html=True)

    # Cierres próximos
    st.markdown("#### 🔥 Cierres probables jul 2026")
    cierres=[("Country 136","Rafael","Asamblea jun 27","red"),("Park 104","Rafael","Asamblea jun 13","red"),("Ed. Risaralda","Rafael/Luisa","Asamblea extraordinaria jul","red"),("Ed. Camila","Lina","Reunión consejo jun 9","amber"),("Ed. Los Pinos","Lina","Evaluando propuestas","amber"),("Ed. El Cerro","Rafael","Visita Alto 61 jun 11","blue")]
    for n,c,s,col in cierres:
        icon={"red":"🔥","amber":"🟡","blue":"💡"}[col]
        st.markdown(f'<div class="al {col}"><div class="al-ic">{icon}</div><div><strong>{n}</strong> ({c})<br>{s}</div></div>',unsafe_allow_html=True)

    # Generar informe
    st.markdown("---")
    c1,c2=st.columns(2)
    with c1: tipo=st.selectbox("Tipo de informe:",["Informe Gerencial Ejecutivo","Reporte Pipeline por Comercial","Análisis Cierres Probables","Diagnóstico del Proceso","Plan de Acción Semana Siguiente"])
    with c2: notas_i=st.text_area("Instrucciones:",height=68,placeholder="Ej: Enfatizar Country 136...")
    if st.button("🤖 Generar informe completo",use_container_width=True):
        if not ai_activa(): st.error("Activa IA en ⚙️ Configuración")
        else:
            prompt=f"""Genera {tipo} para Ágora Tech Colombia.
{f"Instrucciones: {notas_i}" if notas_i else ""}
Fecha: {datetime.now().strftime("%d de %B de %Y")}
## 1. RESUMEN EJECUTIVO ## 2. MÉTRICAS ## 3. ANÁLISIS POR COMERCIAL ## 4. TOP 8 MÁS CERCANOS AL CIERRE ## 5. NOVEDADES SEMANA ## 6. ALERTAS ## 7. RECOMENDACIONES ## 8. PLAN 7 DÍAS
Tono ejecutivo. Sin ---."""
            with st.spinner("Generando..."): r=ask_ai(prompt,df.to_string(max_rows=127),max_tokens=3000)
            st.markdown(r)
            c1,c2=st.columns(2)
            c1.download_button("📥 .md",data=r,file_name=f"Informe_Agora_{datetime.now().strftime('%Y%m%d')}.md")
            c2.download_button("📥 .txt",data=r,file_name=f"Informe_Agora_{datetime.now().strftime('%Y%m%d')}.txt")

# ══════════════════════════════════════════════════════════════
# PAGOS Y FINANZAS (GERENTE)
# ══════════════════════════════════════════════════════════════
def pg_pagos():
    hdr("💰","Pagos y Finanzas","Control de costos y proyección de rentabilidad")

    # Estructura de costos fijos julio 2026
    GASTOS_FIJOS = [
        {"nombre":"Luisa Olivares — Coordinadora","tipo":"Nómina","valor":7_000_000,"variante":"fijo","detalle":"Salario $7M + prestaciones"},
        {"nombre":"Comercial nuevo (julio)","tipo":"Nómina","valor":3_000_000,"variante":"fijo","detalle":"Salario $3M + prestaciones ~$1M"},
        {"nombre":"Leads / Publicidad (Meta Ads)","tipo":"Marketing","valor":1_500_000,"variante":"fijo","detalle":"$1.5M mensual"},
        {"nombre":"Diseñador — cotizaciones","tipo":"Variable","valor":0,"variante":"variable","detalle":"$50.000 por presentación enviada"},
    ]

    st.markdown("#### 📊 Estructura de costos mensual — Julio 2026")
    c1,c2,c3,c4=st.columns(4)
    total_fijo=sum(g["valor"] for g in GASTOS_FIJOS if g["variante"]=="fijo")

    c1.markdown(f'<div class="kpi-card red"><div class="kpi-label">Costos fijos/mes</div><div class="kpi-val red">{fc(total_fijo)}</div><div class="kpi-sub">sin prestaciones</div></div>',unsafe_allow_html=True)
    c2.markdown(f'<div class="kpi-card amber"><div class="kpi-label">Costo diseñador</div><div class="kpi-val amber">$50K</div><div class="kpi-sub">por presentación</div></div>',unsafe_allow_html=True)
    c3.markdown(f'<div class="kpi-card blue"><div class="kpi-label">Primer contrato</div><div class="kpi-val blue">~$83M</div><div class="kpi-sub">ticket promedio CRM</div></div>',unsafe_allow_html=True)
    c4.markdown(f'<div class="kpi-card green"><div class="kpi-label">ROI primer cierre</div><div class="kpi-val green">~10x</div><div class="kpi-sub">vs costo mensual</div></div>',unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)

    # Tabla de costos
    st.markdown("#### 💸 Detalle de costos")
    for g in GASTOS_FIJOS:
        color="red" if g["variante"]=="fijo" else "amber"
        val_str=fc(g["valor"]) if g["valor"]>0 else "Variable"
        st.markdown(f"""<div class="pago-row">
          <div style='width:10px;height:10px;border-radius:50%;background:{"#EF4444" if color=="red" else "#F59E0B"};flex-shrink:0'></div>
          <div style='flex:1'>
            <div class="pago-name">{g["nombre"]}</div>
            <div class="pago-cat">{g["tipo"]} · {g["detalle"]}</div>
          </div>
          <div class="pago-val {"gasto" if g["valor"]>0 else ""}">{val_str}/mes</div>
        </div>""",unsafe_allow_html=True)

    # Simulador de presentaciones
    st.markdown("---")
    st.markdown("#### 🧮 Simulador — ¿cuánto cuesta conseguir un contrato?")
    c1,c2=st.columns(2)
    with c1:
        n_pres=st.slider("Presentaciones enviadas en el mes",10,80,51,help="En abril enviaron 51")
        tasa_cierre=st.slider("Tasa de cierre esperada (%)",1,30,5,help="Sector: 5-15% en ciclo de 6-12 meses")
        valor_contrato=st.number_input("Valor promedio por contrato ($)",value=83_000_000,step=5_000_000,format="%d")
    with c2:
        costo_diseno=n_pres*50_000
        costo_total_mes=total_fijo+costo_diseno
        contratos_esp=n_pres*(tasa_cierre/100)
        ingreso_esp=contratos_esp*valor_contrato
        utilidad=ingreso_esp-costo_total_mes

        st.markdown(f"""
        <div style='background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;padding:16px 18px'>
          <div style='font-family:Space Grotesk,sans-serif;font-size:13px;font-weight:600;color:#0F172A;margin-bottom:12px'>Proyección mensual</div>
          <div style='display:grid;gap:8px'>
            <div style='display:flex;justify-content:space-between'><span style='color:#64748B;font-size:12.5px'>Costo diseñador ({n_pres} pres.)</span><span style='font-weight:600;color:#EF4444'>{fc(costo_diseno)}</span></div>
            <div style='display:flex;justify-content:space-between'><span style='color:#64748B;font-size:12.5px'>Costo total del mes</span><span style='font-weight:600;color:#EF4444'>{fc(costo_total_mes)}</span></div>
            <div style='display:flex;justify-content:space-between'><span style='color:#64748B;font-size:12.5px'>Contratos esperados</span><span style='font-weight:600;color:#2563EB'>{contratos_esp:.1f}</span></div>
            <div style='display:flex;justify-content:space-between'><span style='color:#64748B;font-size:12.5px'>Ingreso esperado</span><span style='font-weight:600;color:#059669'>{fc(int(ingreso_esp))}</span></div>
            <div style='border-top:1px solid #E2E8F0;margin-top:4px;padding-top:8px;display:flex;justify-content:space-between'>
              <span style='font-weight:700;color:#0F172A'>Utilidad estimada</span>
              <span style='font-family:Space Grotesk,sans-serif;font-size:16px;font-weight:700;color:{"#059669" if utilidad>0 else "#EF4444"}'>{fc(int(utilidad))}</span>
            </div>
          </div>
        </div>""",unsafe_allow_html=True)

    # Registro de pagos manuales
    st.markdown("---")
    st.markdown("#### ➕ Registrar pago o gasto")
    if "pagos_log" not in st.session_state: st.session_state.pagos_log=[]
    with st.form("pago_form"):
        c1,c2,c3=st.columns(3)
        with c1: concepto=st.text_input("Concepto *",placeholder="Ej: Pago diseñador mayo")
        with c2:
            tipo_p=st.selectbox("Tipo",["Nómina","Marketing","Diseño","Operativo","Otro"])
            monto=st.number_input("Monto ($)",min_value=0,value=0,step=50_000,format="%d")
        with c3:
            fecha_p=st.date_input("Fecha",value=datetime.now())
            estado_p=st.selectbox("Estado",["Pagado","Pendiente","Aprobado"])
        notas_p=st.text_input("Notas",placeholder="Referencia, proveedor...")
        if st.form_submit_button("💾 Registrar",use_container_width=True):
            if concepto and monto>0:
                st.session_state.pagos_log.append({"fecha":str(fecha_p),"concepto":concepto,"tipo":tipo_p,"monto":monto,"estado":estado_p,"notas":notas_p})
                st.success(f"✅ Registrado: {concepto} — {fc(monto)}")
            else: st.error("Concepto y monto son obligatorios")

    if st.session_state.pagos_log:
        st.markdown("#### 📋 Pagos registrados esta sesión")
        df_p=pd.DataFrame(st.session_state.pagos_log)
        df_p["Monto"]=df_p["monto"].apply(fc)
        st.dataframe(df_p[["fecha","concepto","tipo","Monto","estado","notas"]],use_container_width=True,hide_index=True)
        total_reg=sum(p["monto"] for p in st.session_state.pagos_log)
        st.markdown(f'<div class="al red"><div class="al-ic">💸</div><div><strong>Total registrado esta sesión: {fc(total_reg)}</strong></div></div>',unsafe_allow_html=True)

    # Análisis IA
    st.markdown("---")
    if st.button("🤖 Análisis financiero con IA",use_container_width=True):
        if not ai_activa(): st.error("Activa IA en ⚙️ Configuración")
        else:
            df_crm=get_crm()
            prompt=f"""Analiza la situación financiera de Ágora Tech Colombia:

COSTOS MENSUALES JULIO 2026:
- Luisa Olivares (coordinadora): $7M + prestaciones
- Comercial nuevo: $3M + prestaciones ~$1M
- Marketing/Leads: $1.5M/mes  
- Diseñador: $50.000 por presentación (variable)
- Total fijo estimado: ~$12.5M/mes

CRM: {len(df_crm)} propuestas, Pipeline {fc(int(df_crm["totalNum"].sum()))}, 0 contratos cerrados
Ticket promedio: ~$83M por contrato
Presentaciones promedio: 51/mes (abril)
Inversión acumulada leads Feb-Jun: ~$17M

## 1. DIAGNÓSTICO FINANCIERO ACTUAL
## 2. PUNTO DE EQUILIBRIO (¿cuántos contratos necesitan al mes?)
## 3. PROYECCIÓN Jul-Dic 2026 con escenarios
## 4. RECOMENDACIONES PARA OPTIMIZAR COSTOS
## 5. ALERTA: ¿Cuánto tiempo pueden operar sin cierres?

Sé directo y usa cifras concretas."""
            with st.spinner("Analizando..."): r=ask_ai(prompt)
            st.markdown(r)

# ══════════════════════════════════════════════════════════════
# PROYECTOS
# ══════════════════════════════════════════════════════════════
def pg_proyectos():
    es_g=st.session_state.user["rol"]=="gerente"; df=mis_proyectos()
    hdr("📋","Proyectos","Pipeline completo con historial")
    c1,c2,c3=st.columns([2,1,1])
    with c1: buscar=st.text_input("🔍 Buscar edificio",placeholder="Nombre...")
    with c2: filtro_e=st.selectbox("Estado",["Todos"]+ESTADOS_LISTA,format_func=lambda x:ETAPAS.get(x,{"label":x})["label"] if x!="Todos" else "Todos")
    with c3:
        if es_g: filtro_c=st.selectbox("Comercial",["Todos"]+sorted(df["comercial"].dropna().unique().tolist()))
        else: filtro_c="Todos"
    dff=df.copy()
    if buscar: dff=dff[dff["nombre"].str.contains(buscar,case=False,na=False)]
    if filtro_e!="Todos": dff=dff[dff["estado"]==filtro_e]
    if filtro_c!="Todos": dff=dff[dff["comercial"]==filtro_c]
    st.markdown(f'<div style="font-size:12px;color:#94A3B8;margin-bottom:12px">{len(dff)} proyectos · {fc(int(dff["totalNum"].sum()))}</div>',unsafe_allow_html=True)
    for _,r in dff.iterrows():
        tn=int(r.get("totalNum",0) or 0); est=str(r.get("estado","lead"))
        nota=str(r.get("lastNote","") or r.get("notas","") or "")
        lbl=f"🏢 {r['nombre']}  ·  {fc(tn)}  ·  {ETAPAS.get(est,{'label':est})['label']}"
        with st.expander(lbl):
            ti,th=st.tabs(["📋 Info","📜 Historial"])
            with ti:
                c1,c2,c3,c4=st.columns(4)
                c1.metric("Valor",fc(tn)); c2.metric("Cuota 24m",fc(int(r.get("c24Num",0) or 0)))
                c3.metric("Cuota 36m",fc(int(r.get("c36Num",0) or 0))); c4.metric("Estado",ETAPAS.get(est,{"label":est})["label"])
                if nota and nota!="nan": st.markdown(f'<div class="al blue"><div class="al-ic">📝</div><div>{nota[:300]}</div></div>',unsafe_allow_html=True)
                b1,b2=st.columns(2)
                if b1.button("📝 Actualizar",key=f"pu_{r.get('id',r['nombre'])}"):
                    st.session_state.editing=r["nombre"]; st.session_state.page="Actualizar Estado"; st.rerun()
                if b2.button("✉️ Correo IA",key=f"pc_{r.get('id',r['nombre'])}"):
                    st.session_state.page="Correos IA"; st.rerun()
            with th:
                try: hist=json.loads(str(r.get("historial","[]") or "[]"))
                except: hist=[]
                if hist:
                    st.markdown('<div class="tl">',unsafe_allow_html=True)
                    for ev in reversed(hist[-8:]):
                        dc=ETAPAS.get(ev.get("estado",""),{"dot":"#94A3B8"})["dot"]
                        st.markdown(f'<div class="ti"><div class="ti-dot" style="background:{dc}"></div><div class="ti-date">{ev.get("fecha","")} · {ev.get("usuario","")}</div><div class="ti-h">{ETAPAS.get(ev.get("estado",""),{"label":ev.get("estado","")})["label"]}</div><div class="ti-t">{ev.get("nota","")}</div></div>',unsafe_allow_html=True)
                    st.markdown('</div>',unsafe_allow_html=True)
                else: st.info("Sin historial. Usa 'Actualizar Estado' para empezar.")

def pg_actualizar():
    hdr("📝","Actualizar Estado","Se guarda en el historial permanentemente")
    df=mis_proyectos(); u=st.session_state.user
    presel=st.session_state.get("editing","")
    nombres=["— Selecciona —"]+sorted(df["nombre"].dropna().unique().tolist())
    idx=nombres.index(presel) if presel in nombres else 0
    sel=st.selectbox("Edificio:",nombres,index=idx)
    if sel!="— Selecciona —":
        r=df[df["nombre"]==sel].iloc[0]; est=str(r.get("estado","lead"))
        c1,c2,c3=st.columns(3)
        c1.metric("Valor",fc(int(r.get("totalNum",0) or 0)))
        c2.metric("Estado actual",ETAPAS.get(est,{"label":est})["label"])
        c3.metric("Última actualización",str(r.get("lastUpdate","Nunca"))[:10] or "Nunca")
        if r.get("lastNote"): st.markdown(f'<div class="al blue"><div class="al-ic">📝</div><div>Última nota: {str(r["lastNote"])[:200]}</div></div>',unsafe_allow_html=True)
        with st.form("uf"):
            nuevo_e=st.selectbox("Nuevo estado *",ESTADOS_LISTA,format_func=lambda x:ETAPAS.get(x,{"label":x})["label"],index=ESTADOS_LISTA.index(est) if est in ESTADOS_LISTA else 0)
            nota=st.text_area("Nota de seguimiento * (obligatoria)",placeholder="¿Qué pasó? ¿Próximo paso? ¿Quién respondió?...")
            if nuevo_e in ["creacion_contrato","financiacion","obra","novedades_obra","entrega","mantenimiento","cerrado"]:
                c1,c2=st.columns(2)
                with c1: contrato=st.text_input("N° contrato",placeholder="CT-2026-001"); obra_ini=st.text_input("Inicio obra",placeholder="15 jul 2026")
                with c2: financ=st.text_area("Detalles financiación",height=68); obra_fin=st.text_input("Fin estimado",placeholder="24 ago 2026")
            else: contrato=financ=obra_ini=obra_fin=""
            if st.form_submit_button("✅ Guardar en historial",use_container_width=True):
                if not nota.strip(): st.error("La nota es obligatoria")
                else:
                    agregar_historial(sel,nuevo_e,nota,u["nombre"])
                    ext={k:v for k,v in {"contrato":contrato,"financiacion_info":financ,"obra_inicio":obra_ini,"obra_fin":obra_fin}.items() if v}
                    if ext: update_proy(sel,ext)
                    st.success(f"✅ {sel} → {ETAPAS.get(nuevo_e,{'label':nuevo_e})['label']}"); st.session_state.editing=""; st.rerun()

def pg_nueva_cotizacion():
    hdr("🧮","Nueva Cotización","Registrar en el CRM")
    with st.form("nc"):
        c1,c2=st.columns(2)
        with c1: nombre=st.text_input("Nombre del edificio *"); contacto=st.text_input("Contacto *"); email=st.text_input("Email")
        with c2: direccion=st.text_input("Dirección"); drive_url=st.text_input("Link Drive")
        c1,c2,c3=st.columns(3)
        with c1: valor=st.number_input("Valor ($)",min_value=0,value=0,step=1_000_000,format="%d")
        with c2: vig_v=st.number_input("Vigilancia ($/mes)",min_value=0,value=0,step=100_000,format="%d")
        with c3: vig_h=st.text_input("Vigente hasta",placeholder="Nov 2026")
        c1,c2=st.columns(2)
        with c1: estado=st.selectbox("Estado",ESTADOS_LISTA,format_func=lambda x:ETAPAS.get(x,{"label":x})["label"])
        with c2: notas=st.text_area("Observaciones",height=80)
        if st.form_submit_button("💾 Guardar",use_container_width=True):
            if not nombre: st.error("Nombre obligatorio")
            else:
                u=st.session_state.user; c24n=valor//24 if valor else 0; c36n=valor//36 if valor else 0
                hist_ini=json.dumps([{"fecha":datetime.now().strftime("%d %b %Y %H:%M"),"estado":estado,"nota":notas or "Creado","usuario":u["nombre"],"ts":datetime.now().isoformat()}],ensure_ascii=False)
                add_proy({"id":int(datetime.now().timestamp()),"nombre":nombre.upper(),"comercial":u["comercial"],"contacto":contacto,"email":email,"totalNum":valor,"c24Num":c24n,"c36Num":c36n,"vig":str(vig_v),"vigH":vig_h,"estado":estado,"etapaOrig":estado,"notas":notas,"lastUpdate":datetime.now().isoformat(),"lastNote":notas[:100],"fecha":datetime.now().strftime("%d %b %Y"),"drive":drive_url,"historial":hist_ini,"encuesta":"{}","novedad":""})
                st.success(f"✅ **{nombre}** guardado — {fc(valor)}"); st.balloons()

def pg_correos():
    hdr("✉️","Correos IA","Genera correos comerciales personalizados")
    df=mis_proyectos()
    if not ai_activa(): st.markdown('<div class="al amber"><div class="al-ic">⚠️</div><div><strong>IA no configurada.</strong> Ve a ⚙️ Configuración.</div></div>',unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        edif=st.selectbox("Edificio",["— Seleccionar —"]+sorted(df["nombre"].dropna().unique().tolist()))
        tipo=st.selectbox("Tipo de correo",["Primera presentación","Seguimiento post-reunión","Urgencia — asamblea próxima","Objeción: precio alto","Objeción: adultos mayores","Reactivación — stand-by vigilancia","Propuesta visita Alto 61","Confirmación contrato"])
        ctx_e=st.text_area("Contexto",height=80,placeholder="Ej: El cliente pregunta por adultos mayores...")
        if st.button("🤖 Generar correo",use_container_width=True):
            if edif=="— Seleccionar —": st.warning("Selecciona un edificio")
            elif not ai_activa(): st.error("Activa IA en ⚙️ Configuración")
            else:
                r=df[df["nombre"]==edif].iloc[0]; tn=int(r.get("totalNum",0) or 0); vig=int(r.get("vig",0) or 0)
                prompt=f"""Correo "{tipo}" para Ágora Tech Colombia.
Edificio: {edif} | Valor: {fc(tn)} | Cuota 36m: {fc(int(r.get("c36Num",0) or 0))} | Vigilancia: {fc(vig)}/mes hasta {r.get("vigH","")}
{"Ahorro anual: "+fc(vig*12)+" vs cuota 36m: "+fc(int(r.get("c36Num",0) or 0)*12) if vig>0 else ""}
{f"Contexto: {ctx_e}" if ctx_e else ""}
Primera línea: ASUNTO: [asunto llamativo]. Financiamiento 100% sin entrada. PIN físico con relieve para adultos mayores. Referencia: Alto 61.
Firma: {st.session_state.user["nombre"]} — Ágora Tech | (+57) 315 101 7511. Texto plano."""
                with st.spinner("..."): correo=ask_ai(prompt)
                st.session_state.correo=correo
    with c2:
        st.markdown("**Vista previa:**")
        correo=st.session_state.get("correo","")
        if correo:
            st.markdown(f'<div style="background:#F8FAFC;border:1.5px solid #E2E8F0;border-radius:10px;padding:18px;font-family:monospace;font-size:12.5px;line-height:1.75;white-space:pre-wrap;color:#0F172A;max-height:420px;overflow-y:auto">{correo.replace("<","&lt;").replace(">","&gt;")}</div>',unsafe_allow_html=True)
            st.download_button("📋 Descargar",data=correo,file_name=f"correo_{edif[:20]}.txt",mime="text/plain")
        else:
            st.markdown('<div style="background:#F8FAFC;border:1.5px dashed #CBD5E1;border-radius:10px;padding:40px;text-align:center;color:#94A3B8;font-size:13px">Selecciona edificio y genera el correo</div>',unsafe_allow_html=True)

def pg_asistente():
    hdr("🤖","Asistente IA","Pipeline, cierres, objeciones")
    if not ai_activa(): st.markdown('<div class="al amber"><div class="al-ic">⚠️</div><div>IA no configurada. Ve a ⚙️.</div></div>',unsafe_allow_html=True); return
    df=mis_proyectos(); ctx=df.to_string(max_rows=127) if not df.empty else ""
    for msg in st.session_state.messages:
        st.markdown(f'<div class="{"chat-u" if msg["role"]=="user" else "chat-a"}">{"👤 " if msg["role"]=="user" else "🤖 "}{msg["content"]}</div>',unsafe_allow_html=True)
    if not st.session_state.messages:
        sugs=["📊 Resumen ejecutivo del pipeline","⚡ Top 8 proyectos más cercanos al cierre","📈 Estrategia para Country 136 y Park 104","👴 Responder objeción adultos mayores","💰 Edificios stand-by: plan de reactivación","🔍 Diagnóstico: por qué 0 contratos en 6 meses"]
        cols=st.columns(3)
        for i,s in enumerate(sugs):
            if cols[i%3].button(s,key=f"s_{i}"):
                st.session_state.messages.append({"role":"user","content":s})
                with st.spinner("..."): r=ask_ai(s,ctx)
                st.session_state.messages.append({"role":"assistant","content":r}); st.rerun()
    with st.form("cf",clear_on_submit=True):
        c1,c2=st.columns([5,1])
        with c1: ui=st.text_input("",label_visibility="collapsed",placeholder="Pregunta sobre el pipeline...")
        with c2: send=st.form_submit_button("→")
        if send and ui:
            st.session_state.messages.append({"role":"user","content":ui})
            with st.spinner("..."): r=ask_ai(ui,ctx)
            st.session_state.messages.append({"role":"assistant","content":r}); st.rerun()
    if st.session_state.messages and st.button("🗑 Limpiar"): st.session_state.messages=[]; st.rerun()

def pg_encuesta():
    hdr("📊","Encuesta de Prospecto","Formulario Información Preliminar")
    df=mis_proyectos(); presel=st.session_state.get("editing","")
    nombres=["— Nuevo —"]+sorted(df["nombre"].dropna().unique().tolist())
    idx=nombres.index(presel) if presel in nombres else 0
    edif_sel=st.selectbox("Vincular a edificio:",nombres,index=idx)
    with st.form("ef"):
        c1,c2=st.columns(2)
        with c1: nom_e=st.text_input("Edificio *",value=edif_sel if edif_sel!="— Nuevo —" else ""); contacto=st.text_input("Contacto *"); dir_e=st.text_input("Dirección")
        with c2: rol=st.selectbox("Rol",["Administrador","Propietario","Miembro Consejo","Presidente Consejo"]); etapa_d=st.selectbox("Etapa decisión",["Recibiendo cotizaciones por orden asamblea","No se ha hablado en asamblea","Explorando opciones"])
        c1,c2,c3=st.columns(3)
        with c1: vig=st.radio("¿Tiene vigilancia?",["Sí","No"],horizontal=True)
        with c2: costo_v=st.number_input("Costo/mes ($)",min_value=0,value=0,step=100_000,format="%d")
        with c3: vig_h=st.text_input("Hasta cuándo",placeholder="Nov 2026")
        adultos=st.text_area("Adultos mayores / Discapacidad",height=70)
        incidentes=st.text_area("Incidentes de seguridad",height=70)
        terminos=st.text_area("Términos de selección",height=60)
        analizar=st.checkbox("🤖 Analizar con IA",value=True)
        if st.form_submit_button("💾 Guardar encuesta",use_container_width=True):
            if not nom_e: st.error("Nombre obligatorio"); st.stop()
            datos={"Edificio":nom_e,"Contacto":contacto,"Rol":rol,"Vigilancia":vig,"Costo Vig":fc(costo_v) if costo_v else "No","Vigencia":vig_h,"Adultos":adultos,"Incidentes":incidentes,"Términos":terminos}
            if edif_sel!="— Nuevo —":
                update_proy(edif_sel,{"encuesta":json.dumps(datos,ensure_ascii=False)})
                agregar_historial(edif_sel,"cotizado",f"Encuesta completada. {rol}: {contacto}. Etapa: {etapa_d}.",st.session_state.user["nombre"])
                st.success(f"✅ Encuesta guardada en {edif_sel}")
            if analizar and ai_activa():
                prompt=f"""Analiza prospecto Ágora Tech:
Edificio: {nom_e} | {rol}: {contacto} | Etapa: {etapa_d}
Vigilancia: {"SÍ "+fc(costo_v)+"/mes hasta "+vig_h if vig=="Sí" and costo_v>0 else "NO"}
Adultos: {adultos or "No reportado"} | Incidentes: {incidentes or "Ninguno"}
## VIABILIDAD ## ESTRATEGIA ## OBJECIONES ## {"AHORRO: "+fc(costo_v)+" vigilancia vs "+fc(costo_v)+" cuota si la cuota fuera similar" if costo_v>0 else ""} ## PRÓXIMOS 3 PASOS
Negrilla en datos clave."""
                with st.spinner("..."): r=ask_ai(prompt)
                st.markdown("---"); st.markdown(r)

def pg_calendario():
    hdr("📅","Calendario","Agenda y asambleas próximas")
    c1,c2=st.columns([2,1])
    with c1:
        with st.form("cal_f"):
            c1i,c2i=st.columns(2)
            with c1i: edif=st.text_input("Edificio"); tipo=st.selectbox("Tipo",["Reunión consejo","Asamblea","Llamada","Visita técnica","Visita Alto 61","Firma contrato","Inicio obra","Entrega","Otro"])
            with c2i: fecha_a=st.date_input("Fecha",value=datetime.now()); hora_a=st.time_input("Hora")
            titulo_a=st.text_input("Título *"); notas_a=st.text_area("Notas",height=60)
            if st.form_submit_button("📅 Guardar",use_container_width=True):
                if titulo_a: st.success(f"✅ {titulo_a} — {fecha_a.strftime('%d %b')}")
                else: st.error("Título obligatorio")
    with c2:
        st.markdown("#### 🔥 Próximas semanas")
        urgentes=[("Country 136","Asamblea jun 27","red"),("Park 104","Asamblea jun 13","red"),("Ed. Risaralda","Asamblea extraordinaria jul","red"),("Ed. Camila","Reunión consejo jun 9","amber"),("Ed. Urapanes","Reunión consejo jun 16","amber"),("Ed. El Cerro","Visita Alto 61 jun 11","blue"),("Ed. Avanti","Decisión julio","blue")]
        for n,d,c in urgentes:
            ic={"red":"🔥","amber":"🟡","blue":"💡"}[c]
            st.markdown(f'<div class="al {c}" style="padding:9px 12px;margin-bottom:6px"><div class="al-ic" style="font-size:14px">{ic}</div><div><strong style="font-size:12px">{n}</strong><div style="font-size:10.5px">{d}</div></div></div>',unsafe_allow_html=True)

def pg_configuracion():
    u=st.session_state.user; es_g=u["rol"]=="gerente"; ai_ok=ai_activa()
    hdr("⚙️","Configuración","Activar IA — para todos los usuarios")
    if ai_ok:
        k=get_ai_key()
        st.markdown(f'<div class="al green"><div class="al-ic">✅</div><div><strong>IA Groq activa</strong> — Llama 3.3 70B · ...{k[-4:]}</div></div>',unsafe_allow_html=True)
    else:
        st.markdown('<div class="al red"><div class="al-ic">🔴</div><div><strong>IA no configurada.</strong></div></div>',unsafe_allow_html=True)
    with st.form("cfg"):
        nueva_key=st.text_input("API Key de Groq",placeholder="gsk_...",type="password")
        if nueva_key:
            n=len(nueva_key.strip())
            if n<40: st.warning(f"⚠️ {n} caracteres — parece incompleta")
            else: st.success(f"✅ {n} caracteres OK")
        if st.form_submit_button("⚡ Activar IA",use_container_width=True):
            if nueva_key:
                with st.spinner("Verificando..."): ok=activar_ia(nueva_key)
                if ok: st.success("✅ IA activada"); st.rerun()
    if es_g:
        st.markdown("---")
        st.markdown("Configuración permanente en **Streamlit Cloud → ⋮ → Settings → Secrets**:")
        st.code('GROQ_API_KEY = "gsk_tu-key"',language="toml")
        df=get_crm(); usuarios=get_usuarios()
        c1,c2,c3,c4=st.columns(4)
        c1.metric("Proyectos",df.shape[0]); c2.metric("Con cotización",df[df["totalNum"]>0].shape[0])
        c3.metric("Usuarios",sum(1 for uu in usuarios.values() if uu.get("activo",True)))
        c4.metric("IA","🟢 Activa" if ai_ok else "🔴 Inactiva")

def pg_auditoria():
    hdr("🔍","Auditoría","Análisis profundo del equipo")
    df=get_crm()
    c1,c2,c3,c4,c5=st.columns(5)
    c1.metric("Total",df.shape[0]); c2.metric("Pipeline",fc(int(df["totalNum"].sum())))
    c3.metric("Cotizaciones",df[df["estado"]=="cotizado"].shape[0])
    c4.metric("Perdidos",df[df["estado"]=="perdido"].shape[0]); c5.metric("Contratos",df[df["estado"]=="cerrado"].shape[0])
    st.markdown('<div class="al red"><div class="al-ic">❗</div><div><strong>0 contratos cerrados.</strong> El cuello de botella está en el cierre en asamblea, no en la prospección.</div></div>',unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        res=df[df["totalNum"]>0].groupby("comercial").agg(n=("totalNum","count"),pip=("totalNum","sum")).reset_index()
        res["$M"]=(res["pip"]/1e6).round(1)
        st.dataframe(res[["comercial","n","$M"]].rename(columns={"comercial":"Comercial","n":"Cotiz."}),use_container_width=True,hide_index=True)
    with c2:
        if st.button("🤖 Diagnóstico estratégico",use_container_width=True):
            with st.spinner(): r=ask_ai("Top 8 proyectos más cercanos al cierre con acción concreta. Por qué 0 contratos. Plan 7 días.",df.to_string(max_rows=127))
            st.markdown(r)

def pg_pipeline():
    hdr("🎯","Pipeline Kanban","Embudo por etapas")
    df=mis_proyectos()
    etapas_k=[("lead","🔵 Lead"),("cotizado","🟡 Cotización"),("negociacion","🟠 Negociando"),("aprobado_espera","🔒 Stand-by"),("cerrado","✅ Cerrado")]
    cols=st.columns(5)
    for i,(k,lbl) in enumerate(etapas_k):
        items=df[df["estado"]==k]; tot=int(items["totalNum"].sum())
        with cols[i]:
            st.markdown(f"**{lbl}**")
            st.markdown(f'<div style="font-size:10.5px;color:#94A3B8;margin-bottom:10px">{len(items)} · {fc(tot)}</div>',unsafe_allow_html=True)
            for _,r in items.iterrows():
                tn=int(r.get("totalNum",0) or 0)
                st.markdown(f'<div style="background:white;border:1px solid #E2E8F0;border-radius:7px;padding:9px;margin-bottom:6px"><div style="font-family:Space Grotesk,sans-serif;font-size:11.5px;font-weight:600;color:#0F172A;margin-bottom:1px">{str(r["nombre"])[:22]}</div><div style="font-size:10px;color:#94A3B8;margin-bottom:3px">{str(r.get("comercial","—")).split()[0]}</div><div style="font-family:Space Grotesk,sans-serif;font-size:12.5px;font-weight:700;color:#059669">{fc(tn) if tn else "—"}</div></div>',unsafe_allow_html=True)

def pg_usuarios():
    hdr("👥","Usuarios","Administrar accesos")
    usuarios=get_usuarios()
    for uk,ud in usuarios.items():
        activo=ud.get("activo",True)
        cols=st.columns([2,2,1.5,1,1,1])
        cols[0].markdown(f"**{ud['nombre']}**"); cols[1].markdown(f"`{uk}`")
        cols[2].markdown(ud["rol"].capitalize())
        cols[3].markdown(f'<span class="tag {"tag-g" if activo else "tag-r"}">{"Activo" if activo else "Inactivo"}</span>',unsafe_allow_html=True)
        if cols[4].button("✏️",key=f"e_{uk}"): st.session_state["eu"]=uk
        if cols[5].button("🔒" if activo else "🔓",key=f"t_{uk}"):
            st.session_state.usuarios_db[uk]["activo"]=not activo; st.rerun()
        st.markdown('<div style="border-bottom:1px solid #E2E8F0;margin:4px 0"></div>',unsafe_allow_html=True)
    eu=st.session_state.get("eu","")
    if eu and eu in usuarios:
        ud_e=usuarios[eu]
        with st.form("eu_f"):
            st.markdown(f"**Editando: {ud_e['nombre']}**")
            c1,c2=st.columns(2)
            with c1: nn=st.text_input("Nombre",value=ud_e["nombre"]); np=st.text_input("Nueva contraseña",type="password")
            with c2:
                nr=st.selectbox("Rol",["gerente","comercial"],index=0 if ud_e["rol"]=="gerente" else 1)
                nc=st.selectbox("Comercial",COMS,index=COMS.index(ud_e["comercial"]) if ud_e["comercial"] in COMS else 0)
            if st.form_submit_button("💾 Guardar",use_container_width=True):
                st.session_state.usuarios_db[eu].update({"nombre":nn,"rol":nr,"comercial":nc})
                if np: st.session_state.usuarios_db[eu]["pass"]=np
                st.success("✅ Actualizado"); st.session_state.pop("eu",None); st.rerun()
    st.markdown("---")
    with st.form("au_f"):
        st.markdown("**➕ Nuevo usuario**")
        c1,c2=st.columns(2)
        with c1: nu=st.text_input("Usuario *"); nn2=st.text_input("Nombre *"); np2=st.text_input("Contraseña *",type="password")
        with c2: nr2=st.selectbox("Rol",["comercial","gerente"]); nc2=st.selectbox("Comercial",COMS)
        if st.form_submit_button("➕ Crear",use_container_width=True):
            if not nu or not nn2 or not np2: st.error("Todos los campos obligatorios")
            elif nu.lower() in usuarios: st.error(f"'{nu}' ya existe")
            else:
                st.session_state.usuarios_db[nu.lower()]={"pass":np2,"nombre":nn2,"rol":nr2,"comercial":nc2,"activo":True}
                st.success(f"✅ {nu} creado"); st.rerun()

# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    pg_login()
else:
    sidebar()
    pg=st.session_state.get("page","Dashboard")
    pages={
        "Dashboard":pg_dashboard, "Novedades":pg_novedades,
        "Proyectos":pg_proyectos, "Actualizar Estado":pg_actualizar,
        "Nueva Cotización":pg_nueva_cotizacion, "Correos IA":pg_correos,
        "Asistente IA":pg_asistente, "Encuesta Prospecto":pg_encuesta,
        "Calendario":pg_calendario, "Configuración":pg_configuracion,
        "Informe Semanal":pg_informe_semanal, "Pagos y Finanzas":pg_pagos,
        "Auditoría":pg_auditoria, "Pipeline":pg_pipeline, "Usuarios":pg_usuarios,
    }
    pages.get(pg, pg_dashboard)()
