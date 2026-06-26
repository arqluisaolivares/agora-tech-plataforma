"""
ÁGORA TECH — Plataforma Comercial v8
VINCULADA AL GOOGLE SHEET EN TIEMPO REAL
Sheet ID: 1GyvYB7__4XKZicXAUU-nSHIFRVCJNs8oMgNWVpYEaTE
Lee directamente del Sheet vía URL pública (sin service account).
Los cambios se guardan en session_state + proyectos.json como respaldo.
"""

import streamlit as st
import pandas as pd
import json, os
from datetime import datetime, timedelta
from groq import Groq
import plotly.express as px
import plotly.graph_objects as go
import urllib.request, io
import streamlit.components.v1

# ══════════════════════════════════════════
# CONFIGURACIÓN
# ══════════════════════════════════════════
VERSION    = "v8 · Jun 2026"
GROQ_MODEL = "llama-3.3-70b-versatile"
SHEET_ID   = "1GyvYB7__4XKZicXAUU-nSHIFRVCJNs8oMgNWVpYEaTE"
SHEET_URL  = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

ETAPAS = {
    "lead":              {"label":"Lead nuevo",              "color":"#DBEAFE","dot":"#3B82F6","grupo":"Comercial"},
    "cotizado":          {"label":"Contacto frío",           "color":"#FEF9C3","dot":"#F59E0B","grupo":"Comercial"},
    "evaluacion_consejo":{"label":"En evaluación / Consejo", "color":"#FDE68A","dot":"#D97706","grupo":"Comercial"},
    "negociacion":       {"label":"Negociando",              "color":"#FED7AA","dot":"#F97316","grupo":"Comercial"},
    "aprobado_espera":   {"label":"Aprobado–Stand-by Vig.",  "color":"#E0F2FE","dot":"#0EA5E9","grupo":"Comercial"},
    "perdido":           {"label":"Perdido",                 "color":"#FEE2E2","dot":"#EF4444","grupo":"Comercial"},
    "creacion_contrato": {"label":"Creación Contrato",       "color":"#D1FAF0","dot":"#10B981","grupo":"Ejecución"},
    "financiacion":      {"label":"Financiación",            "color":"#D1FAF0","dot":"#10B981","grupo":"Ejecución"},
    "obra":              {"label":"En Obra",                 "color":"#ECFDF5","dot":"#059669","grupo":"Ejecución"},
    "novedades_obra":    {"label":"Novedades Obra",          "color":"#FFFBEB","dot":"#D97706","grupo":"Ejecución"},
    "entrega":           {"label":"Entrega",                 "color":"#ECFDF5","dot":"#059669","grupo":"Ejecución"},
    "mantenimiento":     {"label":"Mantenimiento",           "color":"#EFF6FF","dot":"#6366F1","grupo":"Posventa"},
    "cerrado":           {"label":"✅ Cerrado",               "color":"#D1FAF0","dot":"#059669","grupo":"Posventa"},
}
ESTADOS_LISTA = list(ETAPAS.keys())
COMS = ["RAFAEL TORRES","SONIA CASTRO","LINA CALLE","ALBERTO FERRER","SANTIAGO BOHORQUEZ","LUISA OLIVARES"]

AI_SYSTEM = """Eres el asesor estratégico de Ágora Tech Colombia — automatización de accesos para copropiedades residenciales con sistema SALTO HomeLok. Financiación 100% a 24/36 meses sin intereses. Instalación en 40 días. 140 propuestas activas, $4.2B pipeline, 0 contratos cerrados a jun 2026. Responde en español colombiano. Sé directo y accionable."""

# ══════════════════════════════════════════
# STREAMLIT CONFIG
# ══════════════════════════════════════════
st.set_page_config(page_title="Ágora Tech CRM", page_icon="🔐", layout="wide", initial_sidebar_state="expanded")

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
:root{--bg:#F1F5F9;--s:#fff;--s2:#F8FAFC;--border:#E2E8F0;--b2:#CBD5E1;
  --ink:#0F172A;--ink2:#334155;--ink3:#64748B;--ink4:#94A3B8;
  --blue:#2563EB;--blu-lt:#EFF6FF;--teal:#0D9488;--green:#059669;--g-lt:#ECFDF5;
  --red:#DC2626;--r-lt:#FEF2F2;--amber:#D97706;--a-lt:#FFFBEB;
  --sh:0 1px 3px rgba(15,23,42,.08);--sh2:0 4px 16px rgba(15,23,42,.1);--r:12px;--r2:8px;}
html,body,[class*="css"]{font-family:'Inter',sans-serif!important;background:var(--bg)!important}
h1,h2,h3{font-family:'Space Grotesk',sans-serif!important}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"],section[data-testid="stSidebar"]>div,[data-testid="stSidebar"]{background:#0B1629!important;border-right:1px solid #1a2744!important}
[data-testid="stSidebar"] .stButton>button{
  all:unset!important;display:block!important;width:100%!important;
  padding:8px 14px!important;font-size:12.5px!important;font-weight:500!important;
  color:rgba(255,255,255,.65)!important;border-radius:6px!important;cursor:pointer!important;
  transition:background .14s,color .14s!important;text-align:left!important;
  box-sizing:border-box!important;margin:1px 0!important;}
[data-testid="stSidebar"] .stButton>button:hover{background:rgba(255,255,255,.09)!important;color:white!important;}
[data-testid="stSidebar"] .stButton>button *{color:inherit!important;background:transparent!important;text-align:left!important;}

/* BOTONES */
.stButton>button{background:linear-gradient(135deg,#2563EB,#0D9488)!important;color:white!important;
  font-family:'Space Grotesk',sans-serif!important;font-weight:600!important;border:none!important;
  border-radius:var(--r2)!important;transition:all .18s!important;box-shadow:0 2px 8px rgba(37,99,235,.28)!important}
.stButton>button:hover{transform:translateY(-1px)!important;box-shadow:0 5px 18px rgba(37,99,235,.38)!important}
.stButton>button[kind="secondary"]{background:var(--s)!important;color:var(--ink)!important;
  border:1.5px solid var(--b2)!important;box-shadow:none!important;transform:none!important}

/* KPI CLICKEABLE */
.kpi{background:var(--s);border:1px solid var(--border);border-radius:var(--r);
  padding:16px 18px;box-shadow:var(--sh);cursor:pointer;transition:all .2s;position:relative;overflow:hidden}
.kpi:hover{transform:translateY(-3px);box-shadow:var(--sh2);border-color:var(--b2)}
.kpi-lbl{font-size:10px;font-weight:700;color:var(--ink4);text-transform:uppercase;letter-spacing:.8px;margin-bottom:7px}
.kpi-val{font-family:'Space Grotesk',sans-serif;font-size:26px;font-weight:700;line-height:1;letter-spacing:-1px}
.kpi-sub{font-size:11px;color:var(--ink4);margin-top:4px}
.kpi-hint{font-size:10px;color:var(--blue);margin-top:5px;font-weight:600}
.kpi.blue .kpi-val{color:var(--blue)}.kpi.amber .kpi-val{color:var(--amber)}
.kpi.teal .kpi-val{color:var(--teal)}.kpi.red .kpi-val{color:var(--red)}
.kpi.green .kpi-val{color:var(--green)}

/* ALERTAS */
.al{border-radius:9px;padding:10px 13px;margin-bottom:7px;display:flex;gap:9px;border:1px solid;font-size:12.5px;line-height:1.7}
.al.red{background:var(--r-lt);border-color:#FCA5A5;color:#7F1D1D}
.al.amber{background:var(--a-lt);border-color:#FDE68A;color:#78350F}
.al.green{background:var(--g-lt);border-color:#6EE7B7;color:#065F46}
.al.blue{background:var(--blu-lt);border-color:#BFDBFE;color:#1E3A8A}
.al.teal{background:#F0FDFA;border-color:#99F6E4;color:#134E4A}

/* CARDS */
.card{background:var(--s);border:1px solid var(--border);border-radius:var(--r);box-shadow:var(--sh);overflow:hidden;margin-bottom:14px}
.card-h{padding:12px 16px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between}
.card-t{font-family:'Space Grotesk',sans-serif;font-size:13px;font-weight:600;color:var(--ink)}

/* TAGS */
.tag{display:inline-flex;align-items:center;padding:2px 8px;border-radius:20px;font-size:10.5px;font-weight:600}
.tag-g{background:var(--g-lt);color:#065F46;border:1px solid #6EE7B7}
.tag-r{background:var(--r-lt);color:#991B1B;border:1px solid #FCA5A5}
.tag-b{background:var(--blu-lt);color:#1E3A8A;border:1px solid #BFDBFE}
.tag-a{background:var(--a-lt);color:#92400E;border:1px solid #FDE68A}
.tag-t{background:#F0FDFA;color:#134E4A;border:1px solid #99F6E4}

/* TIMELINE */
.tl{position:relative;padding-left:22px}
.tl::before{content:'';position:absolute;left:6px;top:8px;bottom:0;width:2px;background:var(--border);border-radius:1px}
.ti{position:relative;margin-bottom:13px}
.ti-dot{position:absolute;left:-22px;top:4px;width:11px;height:11px;border-radius:50%;border:2px solid white;box-shadow:0 0 0 2px var(--b2)}
.ti-date{font-size:10px;font-weight:700;color:var(--ink4);text-transform:uppercase;letter-spacing:.4px}
.ti-h{font-size:12.5px;font-weight:600;color:var(--ink);margin:1px 0}
.ti-t{font-size:11.5px;color:var(--ink3);line-height:1.6}

/* CHAT */
.chat-u{background:linear-gradient(135deg,#2563EB,#0D9488);color:white;padding:10px 14px;border-radius:14px 14px 3px 14px;margin:6px 0;font-weight:500;max-width:80%;margin-left:auto;display:block;font-size:13px}
.chat-a{background:var(--s);border:1px solid var(--border);padding:12px 16px;border-radius:14px 14px 14px 3px;margin:6px 0;max-width:90%;box-shadow:var(--sh);line-height:1.75;display:block;font-size:13px}

/* PULSE */
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.35}}
.dot-live{display:inline-block;width:7px;height:7px;background:#22C55E;border-radius:50%;animation:pulse 2s infinite;margin-right:5px;vertical-align:middle}

/* HERO */
.hero{background:linear-gradient(135deg,#0F172A 0%,#1E3A5F 55%,#0D9488 130%);border-radius:13px;padding:22px 26px;margin-bottom:20px;color:white;position:relative;overflow:hidden}
.hero::before{content:'';position:absolute;top:-50px;right:-50px;width:180px;height:180px;border-radius:50%;background:radial-gradient(circle,rgba(37,99,235,.2) 0%,transparent 70%)}

/* PAGO */
.pago-row{background:var(--s);border:1px solid var(--border);border-radius:var(--r2);padding:10px 14px;margin-bottom:6px;display:flex;align-items:center;gap:10px}

div[data-testid="stForm"]{border:none!important;padding:0!important}
/* Sidebar: hacer botones de nav invisibles pero clickeables sobre el HTML */
[data-testid="stSidebar"] .stButton>button:has(> div > p:empty),
[data-testid="stSidebar"] .stButton>button{
  position:relative!important;
  margin-top:-38px!important;
  height:38px!important;
  width:100%!important;
  background:transparent!important;
  background-color:transparent!important;
  border:none!important;
  box-shadow:none!important;
  color:transparent!important;
  font-size:0px!important;
  opacity:.01!important;
  cursor:pointer!important;
  z-index:10!important;
  border-radius:0!important;
  transform:none!important;
}

/* Sidebar: los st.button quedan invisibles, el HTML de arriba es la UI real */
[data-testid="stSidebar"] .stButton>button>div,
[data-testid="stSidebar"] .stButton>button p{
  visibility:hidden!important;height:0!important;margin:0!important;padding:0!important;
}
[data-testid="stSidebar"] .element-container:has(.stButton){
  position:relative!important;
}

</style>""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# USUARIOS
# ══════════════════════════════════════════
USUARIOS_BASE = {
    "luisa":    {"pass":"luisa2026",    "nombre":"Luisa Olivares",     "rol":"gerente",   "comercial":"LUISA OLIVARES",     "activo":True},
    "gerente":  {"pass":"gerente2026",  "nombre":"Luisa Olivares",     "rol":"gerente",   "comercial":"LUISA OLIVARES",     "activo":True},
    "rafael":   {"pass":"rafael2026",   "nombre":"Rafael Torres",      "rol":"comercial", "comercial":"RAFAEL TORRES",      "activo":True},
    "sonia":    {"pass":"sonia2026",    "nombre":"Sonia Castro",       "rol":"comercial", "comercial":"SONIA CASTRO",       "activo":True},
    "lina":     {"pass":"lina2026",     "nombre":"Lina Calle",         "rol":"comercial", "comercial":"LINA CALLE",         "activo":True},
    "alberto":  {"pass":"alberto2026",  "nombre":"Alberto Ferrer",     "rol":"comercial", "comercial":"ALBERTO FERRER",     "activo":True},
    "santiago": {"pass":"santiago2026", "nombre":"Santiago Bohórquez", "rol":"comercial", "comercial":"SANTIAGO BOHORQUEZ", "activo":True},
    "ctorres":  {"pass":"socio2026", "nombre":"Carlos Torres",  "rol":"socio", "comercial":"", "activo":True},
    "cmendez":  {"pass":"socio2026", "nombre":"Carlos Méndez",  "rol":"socio", "comercial":"", "activo":True},
}
def get_usuarios():
    if "usuarios_db" not in st.session_state:
        st.session_state.usuarios_db = dict(USUARIOS_BASE)
    return st.session_state.usuarios_db

# ══════════════════════════════════════════
# IA — GROQ
# ══════════════════════════════════════════
def get_key():
    k = st.session_state.get("groq_key","")
    if k: return k
    try:
        k = st.secrets.get("GROQ_API_KEY","")
        if k: st.session_state["groq_key"]=k; return k
    except: pass
    return ""

def ai_ok(): return bool(get_key())

def activar_ia(key):
    key=key.strip()
    if not key.startswith("gsk_") or len(key)<20: st.error("Key debe empezar con gsk_"); return False
    try:
        Groq(api_key=key).chat.completions.create(model=GROQ_MODEL,messages=[{"role":"user","content":"OK"}],max_tokens=5)
        st.session_state["groq_key"]=key; return True
    except Exception as e: st.error(f"Key inválida: {str(e)[:80]}"); return False

def ask_ai(prompt, ctx="", max_tokens=2000):
    key=get_key()
    if not key: return "⚠️ IA no configurada. Ve a ⚙️ Configuración."
    try:
        msgs=[{"role":"system","content":AI_SYSTEM}]
        msgs.append({"role":"user","content":f"DATOS CRM:\n{ctx[:18000]}\n\nSOLICITUD:\n{prompt}" if ctx else prompt})
        r=Groq(api_key=key).chat.completions.create(model=GROQ_MODEL,messages=msgs,max_tokens=max_tokens,temperature=0.7)
        return r.choices[0].message.content
    except Exception as e: return f"Error IA: {e}"

# ══════════════════════════════════════════
# CARGA DE DATOS: SHEET → JSON → session_state
# ══════════════════════════════════════════
def normalizar(estado_raw, etapa_orig):
    e = str(etapa_orig or "").strip().lower()
    er = str(estado_raw or "").strip().lower()
    if er=="perdido" or "rechaz" in e: return "perdido"
    if er=="cerrado": return "cerrado"
    if er=="lead" or e=="lead nuevo": return "lead"
    for et in ["creacion_contrato","financiacion","obra","novedades_obra","entrega","mantenimiento"]:
        if er==et: return et
    if "aprobado aut" in e or "vencimiento" in e: return "aprobado_espera"
    if "seguimiento activo" in e or "pendiente decisión" in e or "en evaluación" in e: return "evaluacion_consejo"
    if "contacto frío" in e or "frio" in e: return "cotizado"
    if "negociac" in er: return "negociacion"
    if er=="cotizado": return "cotizado"
    if er=="aprobado": return "evaluacion_consejo"
    return "cotizado"

def limpiar_num(val):
    if val is None: return 0
    s=str(val).replace("$","").replace(".","").replace(",","").replace("#","").strip()
    try: return int(float(s))
    except: return 0

def cop(n):
    try:
        n=int(float(n or 0))
        if n==0: return "$0"
        return "$"+f"{n:,}".replace(",",".")
    except: return "$0"

@st.cache_data(ttl=300)  # Cache 5 minutos — se actualiza automáticamente
def cargar_desde_sheet():
    """Carga los datos del Google Sheet (CSV público). TTL=5min para auto-actualización."""
    try:
        req = urllib.request.Request(SHEET_URL, headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        df_raw = pd.read_csv(io.StringIO(raw), dtype=str, on_bad_lines="skip")
        df_raw.columns = [c.strip() for c in df_raw.columns]
        rows = []
        for _, r in df_raw.iterrows():
            nombre = str(r.get("nombre","")).strip()
            if not nombre or nombre=="nan": continue
            estado_raw = str(r.get("estado","")).strip().lower()
            etapa_orig = str(r.get("etapaOrig","")).strip()
            estado = normalizar(estado_raw, etapa_orig)
            tn = limpiar_num(r.get("totalNum") or r.get("total_num") or r.get("valorTotal") or 0)
            c24 = limpiar_num(r.get("c24Num") or r.get("cuota24Num") or 0) or (tn//24 if tn else 0)
            c36 = limpiar_num(r.get("c36Num") or r.get("cuota36Num") or 0) or (tn//36 if tn else 0)
            rows.append({
                "id":          str(r.get("id","")).strip(),
                "nombre":      nombre,
                "comercial":   str(r.get("comercial","")).strip(),
                "contacto":    str(r.get("contacto","")).strip(),
                "email":       str(r.get("email","")).strip(),
                "totalNum":    tn, "c24Num": c24, "c36Num": c36,
                "total":       cop(tn), "cuota24": cop(c24), "cuota36": cop(c36),
                "vig":         str(r.get("vig","")).strip(),
                "vigH":        str(r.get("vigH","")).strip(),
                "estado":      estado,
                "etapaOrig":   etapa_orig,
                "notas":       str(r.get("notas","")).strip(),
                "lastNote":    str(r.get("lastNote","")).strip(),
                "lastUpdate":  str(r.get("lastUpdate","")).strip()[:10],
                "fecha":       str(r.get("fecha","")).strip()[:10],
                "drive":       str(r.get("drive","")).strip(),
                "historial":   str(r.get("historial","[]")).strip(),
                "encuesta":    str(r.get("encuesta","{}")).strip(),
                "novedad":     str(r.get("novedad","")).strip(),
            })
        return pd.DataFrame(rows), f"✅ Sheet sincronizado — {len(rows)} proyectos · {datetime.now().strftime('%H:%M:%S')}", True
    except Exception as ex:
        return None, f"⚠️ No se pudo conectar al Sheet: {ex}", False

@st.cache_data
def cargar_json_base():
    """Fallback: proyectos.json local (140 proyectos del Sheet descargados)."""
    base = os.path.dirname(os.path.abspath(__file__))
    ruta = os.path.join(base, "proyectos.json")
    if os.path.exists(ruta):
        with open(ruta, encoding="utf-8") as f:
            data = json.load(f)
        rows = []
        for p in data:
            er = str(p.get("etapaOrig","") or p.get("estado",""))
            estado = normalizar(p.get("estado",""), er)
            tn = int(float(p.get("totalNum",0) or 0))
            c24 = int(float(p.get("c24Num",0) or 0)) or (tn//24 if tn else 0)
            c36 = int(float(p.get("c36Num",0) or 0)) or (tn//36 if tn else 0)
            rows.append({**p, "estado":estado, "totalNum":tn, "c24Num":c24, "c36Num":c36,
                         "total":cop(tn), "cuota24":cop(c24), "cuota36":cop(c36)})
        return pd.DataFrame(rows)
    return pd.DataFrame()

def get_crm():
    """Devuelve el DataFrame del CRM. Prioriza Sheet, luego session_state con cambios locales, luego JSON."""
    if st.session_state.get("crm") is not None:
        return st.session_state.crm
    df_sheet, msg, ok = cargar_desde_sheet()
    if ok and df_sheet is not None and len(df_sheet)>0:
        st.session_state["sheet_status"] = msg
        st.session_state["sheet_ok"] = True
        st.session_state.crm = df_sheet
        return df_sheet
    else:
        st.session_state["sheet_status"] = msg
        st.session_state["sheet_ok"] = False
        df_json = cargar_json_base()
        if len(df_json)>0:
            st.session_state.crm = df_json
            return df_json
    return pd.DataFrame()

def refrescar_sheet():
    """Fuerza recarga desde el Sheet."""
    cargar_desde_sheet.clear()
    st.session_state.pop("crm", None)
    st.session_state.pop("sheet_status", None)

def mis_proyectos():
    df=get_crm(); u=st.session_state.get("user")
    if not u: return df.iloc[0:0]
    if u["rol"]=="gerente": return df
    return df[df["comercial"].str.upper()==u["comercial"].upper()]

def update_proy(nombre, campos):
    df=get_crm()
    mask=df["nombre"]==nombre
    if mask.any():
        for k,v in campos.items(): df.loc[mask,k]=v
        st.session_state.crm=df

def agregar_historial(nombre, estado, nota, usuario):
    df=get_crm(); mask=df["nombre"]==nombre
    if not mask.any(): return
    try: hist=json.loads(str(df.loc[mask,"historial"].iloc[0] or "[]"))
    except: hist=[]
    hist.append({"fecha":datetime.now().strftime("%d %b %Y %H:%M"),"estado":estado,"nota":nota,"usuario":usuario,"ts":datetime.now().isoformat()})
    df.loc[mask,"historial"]=json.dumps(hist,ensure_ascii=False)
    df.loc[mask,"lastNote"]=nota
    df.loc[mask,"lastUpdate"]=datetime.now().isoformat()[:10]
    df.loc[mask,"estado"]=estado
    df.loc[mask,"novedad"]=f"{datetime.now().strftime('%d %b')} — {nota[:100]}"
    st.session_state.crm=df

def add_proy(datos):
    df=get_crm()
    st.session_state.crm=pd.concat([pd.DataFrame([datos]),df],ignore_index=True)

def badge(estado):
    e=ETAPAS.get(estado,{"label":estado,"color":"#F1F5F9"})
    return f'<span class="tag" style="background:{e["color"]};border:1px solid rgba(0,0,0,.07);color:#0F172A;white-space:nowrap">{e["label"]}</span>'

def hdr(icon,title,sub=""):
    st.markdown(f"""<div style='display:flex;align-items:center;gap:12px;margin-bottom:20px;padding-bottom:13px;border-bottom:1px solid var(--border)'>
      <div style='width:38px;height:38px;border-radius:9px;background:linear-gradient(135deg,#2563EB,#0D9488);display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0'>{icon}</div>
      <div><div style='font-family:Space Grotesk,sans-serif;font-size:17px;font-weight:700;color:var(--ink);letter-spacing:-.4px'>{title}</div>
      {'<div style="font-size:11.5px;color:var(--ink4);margin-top:1px">'+sub+'</div>' if sub else ''}</div>
    </div>""",unsafe_allow_html=True)

# ══════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════
for k,v in {"logged_in":False,"user":None,"page":"Dashboard","messages":[],"crm":None,
            "correo":"","editing":"","vista_estado":None,"sheet_ok":False,"sheet_status":""}.items():
    if k not in st.session_state: st.session_state[k]=v

if not st.session_state.get("groq_key"):
    try:
        k=st.secrets.get("GROQ_API_KEY","")
        if k: st.session_state["groq_key"]=k
    except: pass

# ══════════════════════════════════════════
# LOGIN
# ══════════════════════════════════════════
def pg_login():
    c1,c2,c3=st.columns([1,1.1,1])
    with c2:
        st.markdown("""<div style='text-align:center;padding:50px 0 26px'>
          <div style='font-family:Space Grotesk,sans-serif;font-size:10px;font-weight:700;color:#64748B;letter-spacing:5px;text-transform:uppercase;margin-bottom:16px'>PLATAFORMA COMERCIAL</div>
          <div style='font-family:Space Grotesk,sans-serif;font-size:38px;font-weight:700;color:#0F172A;letter-spacing:-2px'>ÁGORA TECH</div>
          <div style='width:30px;height:3px;background:linear-gradient(90deg,#2563EB,#0D9488);margin:14px auto;border-radius:2px'></div>
          <div style='font-size:13px;color:#94A3B8'>Gestión Comercial · 140 proyectos · $4.2B pipeline</div>
        </div>""",unsafe_allow_html=True)
        with st.form("lf"):
            u=st.text_input("Usuario",placeholder="luisa / rafael / sonia...")
            p=st.text_input("Contraseña",type="password",placeholder="••••••••")
            if st.form_submit_button("Ingresar →",use_container_width=True):
                un=u.strip().lower(); users=get_usuarios()
                if un in users and users[un]["activo"] and users[un]["pass"]==p:
                    st.session_state.logged_in=True; st.session_state.user=users[un]; st.rerun()
                else: st.error("Usuario o contraseña incorrectos")
        st.markdown("""<div style='background:#F8FAFC;border:1px solid #E2E8F0;border-radius:9px;padding:10px;margin-top:12px;font-size:11px;color:#94A3B8;text-align:center'>
          luisa/luisa2026 · rafael/rafael2026 · sonia/sonia2026<br>lina/lina2026 · alberto/alberto2026 · santiago/santiago2026<br><span style='color:#A78BFA'>Socios: ctorres/socio2026 · cmendez/socio2026</span>
        </div>""",unsafe_allow_html=True)

# ══════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════
def sidebar():
    u=st.session_state.user; es_g=u["rol"] in ["gerente","socio"]
    df=mis_proyectos(); hace_7=(datetime.now()-timedelta(days=7)).isoformat()[:10]
    n_nov=len(df[df["lastUpdate"].astype(str).str.strip()>hace_7])
    sheet_ok=st.session_state.get("sheet_ok",False)
    pg_actual=st.session_state.get("page","Dashboard")

    with st.sidebar:
        st.markdown(f"""<div style='padding:20px 14px 8px'>
          <div style='font-family:Space Grotesk,sans-serif;font-size:17px;font-weight:700;color:white;letter-spacing:-.5px'>Ágora Tech</div>
          <div style='font-size:9px;color:rgba(255,255,255,.22);letter-spacing:2.5px;text-transform:uppercase;margin-top:2px'>{VERSION}</div>
        </div>""", unsafe_allow_html=True)
        st.markdown(f"""<div style='background:rgba(37,99,235,.18);border:1px solid rgba(37,99,235,.3);border-radius:8px;padding:9px 13px;margin:0 10px 12px'>
          <div style='font-size:13px;font-weight:600;color:white'>{u["nombre"]}</div>
          <div style='font-size:10px;color:rgba(255,255,255,.38);margin-top:3px'>
            <span class="dot-live"></span>{"IA activa" if ai_ok() else "Sin IA"} · {"Sheet ✓" if sheet_ok else "Local"}
          </div>
        </div>""", unsafe_allow_html=True)

        def sec(t):
            st.markdown(f'<div style="font-size:9px;font-weight:700;color:rgba(255,255,255,.22);letter-spacing:2.5px;text-transform:uppercase;padding:10px 14px 3px">{t}</div>',unsafe_allow_html=True)

        def item(label, page, key):
            activo = pg_actual==page
            bg     = "#1B3A6B" if activo else "transparent"
            bord   = "border-left:3px solid #3B82F6;" if activo else "border-left:3px solid transparent;"
            color  = "#FFFFFF" if activo else "#94A3B8"
            fw     = "600" if activo else "400"
            # Mostrar el div decorativo
            st.markdown(f"""<div style='background:{bg};{bord}padding:9px 16px;
                margin:1px 0;display:flex;align-items:center;gap:8px'>
              <span style='font-size:11px;font-weight:{fw};color:{color};
                   letter-spacing:.5px;text-transform:uppercase;
                   font-family:Inter,sans-serif'>{label}</span>
            </div>""", unsafe_allow_html=True)
            # Botón con CSS que lo hace transparente e invisible encima del div
            if st.button(" ", key=f"ni_{key}", use_container_width=True):
                st.session_state.page=page; st.rerun()

        sec("PRINCIPAL")
        item("📊  Dashboard",       "Dashboard",          "dash")
        item(f"🔔  Novedades{' ('+str(n_nov)+')' if n_nov else ''}","Novedades","nov")
        sec("COMERCIAL")
        item("📲  Leads WA",         "Leads WhatsApp",     "leads")
        item("📋  Proyectos",        "Proyectos",          "proy")
        item("📝  Actualizar Estado","Actualizar Estado",  "act")
        item("🧮  Nueva Cotización", "Nueva Cotización",   "cot")
        item("📊  Encuesta",         "Encuesta Prospecto", "enc")
        item("📅  Calendario",       "Calendario",         "cal")
        item("🗺️  Mapa",             "Mapa de Proyectos",  "mapa")
        sec("IA")
        item("✉️  Correos IA",       "Correos IA",         "cor")
        item("🤖  Asistente IA",     "Asistente IA",       "asi")
        if es_g:
            sec("GERENCIA")
            item("📈  Informe Semanal",  "Informe Semanal",   "inf")
            item("💰  Pagos y Finanzas", "Pagos y Finanzas",  "pag")
            item("🔍  Auditoría",        "Auditoría",         "aud")
            item("🎯  Pipeline",         "Pipeline",          "pip")
            sec("ADMIN")
            item("👥  Usuarios",         "Usuarios",          "usr")
            item("⚙️  Configuración",    "Configuración",     "cfg")
        else:
            sec("CONFIG")
            item("⚙️  Configuración",    "Configuración",     "cfg2")

        st.markdown("<hr style='border-color:rgba(255,255,255,.08);margin:10px 0'>", unsafe_allow_html=True)
        if st.button("🔄  Sincronizar Sheet", use_container_width=True, key="sb_sync"):
            refrescar_sheet(); st.rerun()
        if st.button("← Salir", use_container_width=True, key="sb_logout"):
            for k in list(st.session_state.keys()): st.session_state.pop(k,None)
            st.rerun()
        status=st.session_state.get("sheet_status","")
        if status:
            col="#22C55E" if sheet_ok else "#F59E0B"
            st.markdown(f'<div style="padding:5px 12px;font-size:9.5px;color:{col}">{status}</div>',unsafe_allow_html=True)


# ══════════════════════════════════════════
# DASHBOARD INTERACTIVO
# ══════════════════════════════════════════
def pg_dashboard():
    u=st.session_state.user; es_g=u["rol"]=="gerente"; df=mis_proyectos()
    if df.empty: st.warning("Cargando datos..."); return

    # Banner de conexión
    sheet_ok=st.session_state.get("sheet_ok",False)
    if not sheet_ok:
        st.markdown('<div class="al amber"><div>⚠️</div><div><strong>Usando datos locales.</strong> El Sheet no está accesible. Haz clic en "🔄 Sincronizar Sheet" en la barra lateral.</div></div>',unsafe_allow_html=True)

    # Alertas críticas banner
    hace_14=(datetime.now()-timedelta(days=14)).isoformat()[:10]
    neg_al=df[df["estado"]=="negociacion"]
    sin_14=df[(df["estado"]=="evaluacion_consejo")&(df["lastUpdate"].astype(str).str.strip()<hace_14)]
    if len(neg_al)>0 or len(sin_14)>0:
        with st.expander(f"🚨 ALERTAS CRÍTICAS ({len(neg_al)} negociaciones · {len(sin_14)} sin actualizar)",expanded=True):
            for _,r in neg_al.iterrows():
                nota=str(r.get("lastNote","") or r.get("notas",""))[:100]
                st.markdown(f'<div class="al red"><div>🔥</div><div><strong>NEGOCIACIÓN: {r["nombre"]}</strong><br><small>{nota}</small></div></div>',unsafe_allow_html=True)
            if len(sin_14)>0:
                ns=", ".join(sin_14["nombre"].head(5).tolist())
                st.markdown(f'<div class="al amber"><div>⏰</div><div><strong>{len(sin_14)} en evaluación sin actualizar +14 días:</strong> {ns}{"..." if len(sin_14)>5 else ""}</div></div>',unsafe_allow_html=True)

    # Vista filtrada (clic en KPI)
    if st.session_state.get("vista_estado"):
        est=st.session_state.vista_estado
        lbl=ETAPAS.get(est,{"label":est})["label"]
        col_r,col_b=st.columns([4,1])
        with col_r: hdr("📋",f"{lbl}",f"{len(df[df['estado']==est])} proyectos — clic para ver detalle")
        with col_b:
            if st.button("← Volver"): st.session_state.vista_estado=None; st.rerun()
        df_f=df[df["estado"]==est]
        for _,r in df_f.iterrows():
            tn=int(r.get("totalNum",0) or 0)
            nota=str(r.get("lastNote","") or r.get("notas","") or "")[:200]
            upd=str(r.get("lastUpdate",""))[:10] or "—"
            dot=ETAPAS.get(est,{"dot":"#94A3B8"})["dot"]
            with st.expander(f"🏢 {r['nombre']}  ·  {cop(tn)}  ·  {str(r.get('comercial','')).split()[0] if r.get('comercial') else '—'}"):
                c1,c2,c3=st.columns(3)
                c1.metric("Valor total",cop(tn))
                c2.metric("Cuota 36m",cop(int(r.get("c36Num",0) or 0)))
                c3.metric("Actualizado",upd)
                if nota and nota!="nan":
                    st.markdown(f'<div class="al blue"><div>📝</div><div>{nota}</div></div>',unsafe_allow_html=True)
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
                if b1.button("📝 Actualizar",key=f"v_{r['nombre']}"):
                    st.session_state.editing=r["nombre"]; st.session_state.page="Actualizar Estado"; st.session_state.vista_estado=None; st.rerun()
        return

    # HERO
    pip=int(df["totalNum"].sum()); n_act=len(df[~df["estado"].isin(["perdido","cerrado"])])
    st.markdown(f"""<div class="hero">
      <div style='font-size:10px;font-weight:700;color:rgba(13,148,136,.9);letter-spacing:3px;text-transform:uppercase;margin-bottom:8px'><span class="dot-live"></span>EN VIVO · {datetime.now().strftime("%d %B %Y %H:%M")} · {'Sheet ✓' if sheet_ok else 'Local'}</div>
      <div style='font-family:Space Grotesk,sans-serif;font-size:21px;font-weight:700;color:white;letter-spacing:-.5px;margin-bottom:4px'>{"Dashboard Gerencial" if es_g else f"Hola, {u['nombre'].split()[0]} 👋"}</div>
      <div style='font-size:12.5px;color:rgba(255,255,255,.45)'>{len(df)} proyectos totales · {n_act} activos · Pipeline {cop(pip)}</div>
    </div>""",unsafe_allow_html=True)

    # KPIs INTERACTIVOS
    eval_n  = len(df[df["estado"]=="evaluacion_consejo"])
    cotiz_n = len(df[df["estado"]=="cotizado"])
    standb  = len(df[df["estado"]=="aprobado_espera"])
    perd_n  = len(df[df["estado"]=="perdido"])
    cerra_n = len(df[df["estado"]=="cerrado"])
    neg_n   = len(df[df["estado"]=="negociacion"])

    st.markdown("#### Resumen — *clic en cualquier tarjeta para ver los edificios*")
    c1,c2,c3,c4,c5,c6=st.columns(6)

    with c1:
        st.markdown(f'<div class="kpi blue"><div class="kpi-lbl">Total presentadas</div><div class="kpi-val blue">{len(df)}</div><div class="kpi-sub">Ene–Jun 2026</div></div>',unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="kpi" style="border-bottom:2px solid #D97706"><div class="kpi-lbl">En evaluación</div><div class="kpi-val amber">{eval_n}</div><div class="kpi-sub">reuniones consejo</div><div class="kpi-hint">▸ Ver lista</div></div>',unsafe_allow_html=True)
        if st.button("Ver →",key="ke",use_container_width=True): st.session_state.vista_estado="evaluacion_consejo"; st.rerun()
    with c3:
        st.markdown(f'<div class="kpi" style="border-bottom:2px solid #F59E0B"><div class="kpi-lbl">Contacto frío</div><div class="kpi-val" style="color:#F59E0B">{cotiz_n}</div><div class="kpi-sub">sin respuesta activa</div><div class="kpi-hint">▸ Ver lista</div></div>',unsafe_allow_html=True)
        if st.button("Ver →",key="kc",use_container_width=True): st.session_state.vista_estado="cotizado"; st.rerun()
    with c4:
        st.markdown(f'<div class="kpi" style="border-bottom:2px solid #0EA5E9"><div class="kpi-lbl">Stand-by Vigilancia</div><div class="kpi-val teal">{standb}</div><div class="kpi-sub">reactivar sep–nov</div><div class="kpi-hint">▸ Ver lista</div></div>',unsafe_allow_html=True)
        if st.button("Ver →",key="ks",use_container_width=True): st.session_state.vista_estado="aprobado_espera"; st.rerun()
    with c5:
        st.markdown(f'<div class="kpi" style="border-bottom:2px solid #EF4444"><div class="kpi-lbl">Rechazados</div><div class="kpi-val red">{perd_n}</div><div class="kpi-sub">{round(perd_n/len(df)*100) if len(df) else 0}% del total</div><div class="kpi-hint">▸ Ver lista</div></div>',unsafe_allow_html=True)
        if st.button("Ver →",key="kr",use_container_width=True): st.session_state.vista_estado="perdido"; st.rerun()
    with c6:
        st.markdown(f'<div class="kpi" style="border-bottom:2px solid {"#059669" if cerra_n>0 else "#EF4444"}"><div class="kpi-lbl">Contratos</div><div class="kpi-val {"green" if cerra_n>0 else "red"}">{cerra_n}</div><div class="kpi-sub">{"🎉 ¡Primer cierre!" if cerra_n>0 else "Q3 2026 esperado"}</div></div>',unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)

    # Negociando — urgente
    neg_df=df[df["estado"]=="negociacion"]
    if len(neg_df)>0:
        st.markdown("#### 🔥 Negociando — acción inmediata")
        for _,r in neg_df.iterrows():
            nota=str(r.get("lastNote","") or r.get("notas","") or "Seguimiento urgente")[:150]
            st.markdown(f'<div class="al red"><div>🔥</div><div><strong>{r["nombre"]}</strong> · {str(r.get("comercial","")).split()[0] if r.get("comercial") else "—"} · {cop(int(r.get("totalNum",0) or 0))}<br>{nota}</div></div>',unsafe_allow_html=True)

    # ── TIEMPOS POR ETAPA + EMBUDO
    st.markdown("---")
    col_t, col_f = st.columns(2)
    with col_t:
        st.markdown("#### ⏱ Tiempo promedio por etapa")
        hoy_dt=datetime.now()
        for est,lbl,maxd in [
            ("cotizado","Contacto frío",60),
            ("evaluacion_consejo","En evaluación / Consejo",180),
            ("negociacion","Negociando",60),
            ("aprobado_espera","Stand-by Vigilancia",300),
        ]:
            sub=df[(df["estado"]==est)&(df["fecha"].astype(str).str.strip()>"2020")]
            if len(sub)==0: continue
            dias_list=[]
            for _,r in sub.iterrows():
                try:
                    f=str(r.get("fecha",""))[:10]
                    d=(hoy_dt-datetime.fromisoformat(f)).days
                    if 0<=d<730: dias_list.append(d)
                except: pass
            if not dias_list: continue
            prom=int(sum(dias_list)/len(dias_list))
            pct=min(prom/maxd,1.0)
            color="#059669" if pct<0.5 else ("#D97706" if pct<0.85 else "#EF4444")
            st.markdown(f"""<div style='margin-bottom:11px'>
              <div style='display:flex;justify-content:space-between;margin-bottom:4px'>
                <span style='font-size:12px;color:#334155;font-weight:500'>{lbl}</span>
                <span style='font-size:11px;color:{color};font-weight:700'>{prom} días · {len(sub)} proy.</span>
              </div>
              <div style='background:#F1F5F9;border-radius:4px;height:7px'>
                <div style='background:{color};height:7px;border-radius:4px;width:{pct*100:.0f}%'></div>
              </div>
            </div>""",unsafe_allow_html=True)
        st.markdown('<div style="font-size:10.5px;color:#94A3B8;margin-top:4px">La etapa de Evaluación/Consejo es el cuello de botella — es el ciclo más largo.</div>',unsafe_allow_html=True)
    with col_f:
        etapas_f=[("Propuestas totales",len(df)),("Sin rechazar",len(df[~df["estado"].isin(["perdido"])])),("En evaluación",eval_n),("Negociando",max(neg_n,0)),("Contratos",cerra_n)]
        fig2=go.Figure(go.Funnel(
            y=[e[0] for e in etapas_f],x=[e[1] for e in etapas_f],
            textinfo="value+percent initial",textfont=dict(size=12,family="Space Grotesk"),
            marker=dict(color=["#2563EB","#7C3AED","#D97706","#F97316","#059669"],line=dict(width=1,color="white")),
            connector=dict(line=dict(color="#E2E8F0",width=1)),
        ))
        fig2.update_layout(title="Embudo de conversión",paper_bgcolor="white",plot_bgcolor="white",
            font_family="Inter",title_font_family="Space Grotesk",
            margin=dict(t=38,b=8,l=8,r=8),showlegend=False,height=310)
        st.plotly_chart(fig2,use_container_width=True)

    # Alertas
    st.markdown("#### 🚨 Alertas automáticas")
    hace_7=(datetime.now()-timedelta(days=7)).isoformat()[:10]
    if es_g:
        for com in sorted(df["comercial"].dropna().unique()):
            dc=df[df["comercial"]==com]
            neg_c=dc[dc["estado"]=="negociacion"]
            eval_c=dc[dc["estado"]=="evaluacion_consejo"]
            esp_c=dc[dc["estado"]=="aprobado_espera"]
            sin_c=dc[dc["lastUpdate"].astype(str).str.strip()<hace_7]
            n_al=len(neg_c)+(1 if len(esp_c)>0 else 0)+(1 if len(sin_c)>5 else 0)
            ico="🔴" if len(neg_c)>0 else ("🟡" if n_al>0 else "🟢")
            with st.expander(f"{ico} {com} — {len(dc)} proy · {len(eval_c)} en evaluación · {len(esp_c)} stand-by",expanded=len(neg_c)>0):
                for _,r in neg_c.iterrows():
                    nota=str(r.get("lastNote","") or r.get("notas",""))[:100]
                    st.markdown(f'<div class="al red"><div>🔥</div><div><strong>NEGOCIACIÓN: {r["nombre"]}</strong><br>{nota}</div></div>',unsafe_allow_html=True)
                for _,r in esp_c.iterrows():
                    vig=str(r.get("vigH",""))
                    if any(m in vig.lower() for m in ["jun","jul","ago","sep","oct","nov"]):
                        st.markdown(f'<div class="al teal"><div>🔒</div><div><strong>Reactivar: {r["nombre"]}</strong> — Vigilancia vence: {vig}</div></div>',unsafe_allow_html=True)
                if len(eval_c)>0:
                    nombres=", ".join(eval_c["nombre"].head(4).tolist())
                    st.markdown(f'<div class="al amber"><div>📋</div><div><strong>{len(eval_c)} en evaluación/consejo:</strong> {nombres}{"..." if len(eval_c)>4 else ""}</div></div>',unsafe_allow_html=True)
                if len(sin_c)>5:
                    st.markdown(f'<div class="al blue"><div>⏰</div><div><strong>{len(sin_c)} sin actualizar en +7 días</strong></div></div>',unsafe_allow_html=True)
                if n_al==0:
                    st.markdown('<div class="al green"><div>✅</div><div>Al día</div></div>',unsafe_allow_html=True)
    else:
        mi=df
        for _,r in mi[mi["estado"]=="negociacion"].iterrows():
            st.markdown(f'<div class="al red"><div>🔥</div><div><strong>NEGOCIACIÓN: {r["nombre"]}</strong><br>{str(r.get("lastNote",""))[:150]}</div></div>',unsafe_allow_html=True)
        sin=mi[mi["lastUpdate"].astype(str).str.strip()<hace_7]
        if len(sin)>0:
            st.markdown(f'<div class="al amber"><div>📋</div><div><strong>{len(sin)} proyectos sin actualizar en +7 días.</strong> Usa Actualizar Estado.</div></div>',unsafe_allow_html=True)
    if not ai_ok():
        st.markdown('<div class="al blue"><div>💡</div><div><strong>IA no configurada.</strong> Ve a ⚙️ Configuración → pega tu API Key de Groq.</div></div>',unsafe_allow_html=True)

# ══════════════════════════════════════════
# NOVEDADES
# ══════════════════════════════════════════
def pg_novedades():
    hdr("🔔","Novedades","Actualizaciones de los últimos 7 días — clic para ver detalle")
    df=mis_proyectos()
    hace_7=(datetime.now()-timedelta(days=7)).isoformat()[:10]
    df_nov=df[df["lastUpdate"].astype(str).str.strip()>hace_7].sort_values("lastUpdate",ascending=False)
    df_sin=df[~(df["lastUpdate"].astype(str).str.strip()>hace_7)]

    c1,c2,c3=st.columns(3)
    c1.markdown(f'<div class="kpi" style="border-bottom:2px solid #059669"><div class="kpi-lbl">Actualizados</div><div class="kpi-val green">{len(df_nov)}</div><div class="kpi-sub">últimos 7 días</div></div>',unsafe_allow_html=True)
    c2.markdown(f'<div class="kpi" style="border-bottom:2px solid #EF4444"><div class="kpi-lbl">Sin actualizar</div><div class="kpi-val red">{len(df_sin)}</div><div class="kpi-sub">requieren seguimiento</div></div>',unsafe_allow_html=True)
    c3.markdown(f'<div class="kpi" style="border-bottom:2px solid #2563EB"><div class="kpi-lbl">Pipeline movido</div><div class="kpi-val blue">{cop(int(df_nov["totalNum"].sum()))}</div><div class="kpi-sub">en proyectos activos</div></div>',unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)

    if len(df_nov)==0:
        st.info("No hay actualizaciones esta semana. Usa 'Actualizar Estado' para registrar seguimiento.")
    else:
        st.markdown(f"#### ✅ Actualizados ({len(df_nov)})")
        for _,r in df_nov.iterrows():
            est=str(r.get("estado",""))
            nota=str(r.get("lastNote","") or r.get("notas","") or "")[:200]
            upd=str(r.get("lastUpdate",""))[:10]
            with st.expander(f"🏢 {r['nombre']}  ·  {ETAPAS.get(est,{'label':est})['label']}  ·  {upd}"):
                c1,c2,c3=st.columns(3)
                c1.metric("Valor",cop(int(r.get("totalNum",0) or 0)))
                c2.metric("Comercial",str(r.get("comercial","—")).split()[0] if r.get("comercial") else "—")
                c3.metric("Estado",ETAPAS.get(est,{"label":est})["label"])
                if nota and nota!="nan":
                    st.markdown(f'<div class="al blue"><div>📝</div><div>{nota}</div></div>',unsafe_allow_html=True)
                try: hist=json.loads(str(r.get("historial","[]") or "[]"))
                except: hist=[]
                if hist:
                    st.markdown("**Historial:**")
                    st.markdown('<div class="tl">',unsafe_allow_html=True)
                    for ev in reversed(hist[-4:]):
                        dc=ETAPAS.get(ev.get("estado",""),{"dot":"#94A3B8"})["dot"]
                        st.markdown(f'<div class="ti"><div class="ti-dot" style="background:{dc}"></div><div class="ti-date">{ev.get("fecha","")} · {ev.get("usuario","")}</div><div class="ti-h">{ETAPAS.get(ev.get("estado",""),{"label":ev.get("estado","")})["label"]}</div><div class="ti-t">{ev.get("nota","")}</div></div>',unsafe_allow_html=True)
                    st.markdown('</div>',unsafe_allow_html=True)
                if st.button("📝 Actualizar ahora",key=f"nu_{r['nombre']}"):
                    st.session_state.editing=r["nombre"]; st.session_state.page="Actualizar Estado"; st.rerun()

    if len(df_sin)>0:
        st.markdown("---")
        st.markdown(f"#### ⚠️ Sin actualizar ({len(df_sin)})")
        df_sin_v=df_sin[df_sin["totalNum"]>0].sort_values("totalNum",ascending=False)
        for _,r in df_sin_v.head(20).iterrows():
            cols=st.columns([3,1.5,1.5,1])
            cols[0].markdown(f"**{r['nombre']}**  <span style='font-size:11px;color:#94A3B8'>{ETAPAS.get(str(r.get('estado','')),{'label':''})['label']}</span>",unsafe_allow_html=True)
            cols[1].markdown(f"<small style='color:#94A3B8'>{str(r.get('comercial','')).split()[0] if r.get('comercial') else '—'}</small>",unsafe_allow_html=True)
            cols[2].markdown(f"<small style='color:#94A3B8'>{str(r.get('lastUpdate','Nunca'))[:10]}</small>",unsafe_allow_html=True)
            if cols[3].button("📝",key=f"ns_{r['nombre']}"):
                st.session_state.editing=r["nombre"]; st.session_state.page="Actualizar Estado"; st.rerun()

    st.markdown("---")
    if st.button("🤖 Generar resumen ejecutivo con IA",use_container_width=True):
        if not ai_ok(): st.error("Activa IA en ⚙️ Configuración")
        else:
            ctx=df_nov[["nombre","comercial","estado","lastNote","totalNum"]].to_string() if len(df_nov)>0 else "Sin novedades esta semana"
            with st.spinner("..."): r=ask_ai(f"Resumen ejecutivo de novedades comerciales semana {datetime.now().strftime('%d %b')}. ## MOVIMIENTOS POSITIVOS ## ALERTAS ## ACCIONES PRIORITARIAS MAÑANA. Bullet points, negrilla en nombres.",ctx)
            st.markdown(r)

# ══════════════════════════════════════════
# INFORME SEMANAL
# ══════════════════════════════════════════
def pg_informe_semanal():
    hdr("📈","Informe Semanal","Para socios y equipo directivo")
    df=get_crm(); hace_7=(datetime.now()-timedelta(days=7)).isoformat()[:10]
    st.markdown(f"""<div style='background:linear-gradient(135deg,#0F172A,#1E3A5F);border-radius:12px;padding:18px 22px;margin-bottom:20px;color:white'>
      <div style='font-family:Space Grotesk,sans-serif;font-size:17px;font-weight:700'>Informe Gerencial — Ágora Tech</div>
      <div style='font-size:11px;color:rgba(255,255,255,.4);margin-top:3px'>Semana {(datetime.now()-timedelta(days=7)).strftime("%d %b")} – {datetime.now().strftime("%d %b %Y")} · {len(df)} propuestas totales</div>
    </div>""",unsafe_allow_html=True)

    c1,c2,c3,c4=st.columns(4)
    c1.metric("Pipeline activo",cop(int(df[~df["estado"].isin(["perdido","cerrado"])]["totalNum"].sum())))
    c2.metric("En evaluación",str(len(df[df["estado"]=="evaluacion_consejo"])))
    c3.metric("Stand-by Vig.",str(len(df[df["estado"]=="aprobado_espera"])))
    c4.metric("Contratos firmados",str(len(df[df["estado"]=="cerrado"])))

    st.markdown("#### 👥 Por comercial")
    res=df.groupby("comercial").agg(Total=("nombre","count"),Evaluacion=("estado",lambda x:sum(x=="evaluacion_consejo")),Perdidos=("estado",lambda x:sum(x=="perdido")),Pipeline=("totalNum","sum")).reset_index()
    res["$M"]=(res["Pipeline"]/1e6).round(1)
    st.dataframe(res[["comercial","Total","Evaluacion","Perdidos","$M"]].rename(columns={"comercial":"Comercial","Evaluacion":"En evaluación"}),use_container_width=True,hide_index=True)

    df_nov=df[df["lastUpdate"].astype(str).str.strip()>hace_7].sort_values("lastUpdate",ascending=False)
    st.markdown(f"#### 🔔 Novedades ({len(df_nov)})")
    for _,r in df_nov.head(8).iterrows():
        nota=str(r.get("lastNote","") or r.get("notas",""))[:100]
        st.markdown(f"""<div style='background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;padding:8px 12px;margin-bottom:5px;display:flex;align-items:center;gap:10px'>
          <div style='flex:1'><div style='font-size:12.5px;font-weight:600;color:#0F172A'>{r["nombre"]}</div>
          <div style='font-size:11px;color:#64748B;margin-top:1px'>{nota or "Sin nota"}</div></div>
          {badge(str(r.get("estado","")))}
        </div>""",unsafe_allow_html=True)

    st.markdown("#### 🔥 Cierres probables jul 2026")
    cierres=[("Country 136","Rafael","Asamblea jun 27","red"),("Park 104","Rafael","Asamblea jun 13","red"),("Ed. Risaralda","Rafael/Luisa","Asamblea extraordinaria jul","red"),("Ed. Camila","Lina","Reunión consejo jun 9","amber"),("Ed. Los Pinos","Lina","Asamblea tentativa jul 16","amber"),("Ed. Cesanne","Rafael","Asamblea jul 16","amber")]
    for n,c,s,col in cierres:
        st.markdown(f'<div class="al {col}"><div>{"🔥" if col=="red" else "🟡"}</div><div><strong>{n}</strong> ({c}) — {s}</div></div>',unsafe_allow_html=True)

    st.markdown("---")
    c1,c2=st.columns(2)
    with c1: tipo=st.selectbox("Tipo:",["Informe Gerencial Ejecutivo","Pipeline por Comercial","Análisis Cierres Probables","Diagnóstico del Proceso","Plan de Acción Semana Siguiente"])
    with c2: notas_i=st.text_area("Instrucciones:",height=60,placeholder="Ej: Enfatizar Country 136...")
    if st.button("🤖 Generar informe completo",use_container_width=True):
        if not ai_ok(): st.error("Activa IA en ⚙️ Configuración")
        else:
            with st.spinner("Generando..."): r=ask_ai(f"""Genera {tipo} para Ágora Tech Colombia. {f"Instrucciones: {notas_i}" if notas_i else ""}
Fecha: {datetime.now().strftime("%d de %B de %Y")}
## 1. RESUMEN EJECUTIVO ## 2. MÉTRICAS ## 3. POR COMERCIAL ## 4. TOP 8 CIERRES ## 5. NOVEDADES ## 6. ALERTAS ## 7. RECOMENDACIONES ## 8. PLAN 7 DÍAS
Tono ejecutivo. Sin ---.""",df.to_string(max_rows=140),max_tokens=3000)
            st.markdown(r)
            c1,c2=st.columns(2)
            c1.download_button("📥 .md",data=r,file_name=f"Informe_{datetime.now().strftime('%Y%m%d')}.md")
            c2.download_button("📥 .txt",data=r,file_name=f"Informe_{datetime.now().strftime('%Y%m%d')}.txt")

# ══════════════════════════════════════════
# PAGOS Y FINANZAS
# ══════════════════════════════════════════
def pg_pagos():
    hdr("💰","Pagos y Finanzas","Control de costos · Simulador de rentabilidad")
    COSTOS=[
        {"nombre":"Luisa Olivares — Coordinadora","tipo":"Nómina","valor":7_000_000,"nota":"$7M salario + prestaciones ~$2.3M"},
        {"nombre":"Comercial nuevo (julio 2026)","tipo":"Nómina","valor":3_000_000,"nota":"$3M salario + prestaciones ~$1M"},
        {"nombre":"Leads / Publicidad (Meta Ads)","tipo":"Marketing","valor":1_500_000,"nota":"$1.5M/mes"},
        {"nombre":"Diseñador — presentaciones","tipo":"Variable","valor":0,"nota":"$50.000 por presentación enviada"},
    ]
    total_fijo=sum(c["valor"] for c in COSTOS)

    c1,c2,c3,c4=st.columns(4)
    c1.markdown(f'<div class="kpi" style="border-bottom:2px solid #EF4444"><div class="kpi-lbl">Costos fijos/mes</div><div class="kpi-val red">{cop(total_fijo)}</div><div class="kpi-sub">sin prestaciones</div></div>',unsafe_allow_html=True)
    c2.markdown(f'<div class="kpi" style="border-bottom:2px solid #D97706"><div class="kpi-lbl">Diseñador</div><div class="kpi-val amber">$50K</div><div class="kpi-sub">por presentación</div></div>',unsafe_allow_html=True)
    c3.markdown(f'<div class="kpi" style="border-bottom:2px solid #2563EB"><div class="kpi-lbl">Ticket promedio</div><div class="kpi-val blue">~$83M</div><div class="kpi-sub">COP por contrato</div></div>',unsafe_allow_html=True)
    c4.markdown(f'<div class="kpi" style="border-bottom:2px solid #059669"><div class="kpi-lbl">1 contrato =</div><div class="kpi-val green">~7x</div><div class="kpi-sub">vs costo mensual</div></div>',unsafe_allow_html=True)

    st.markdown("<br>")
    st.markdown("#### 💸 Detalle de costos")
    for c in COSTOS:
        val=cop(c["valor"]) if c["valor"]>0 else "Variable"
        color="#EF4444" if c["valor"]>0 else "#D97706"
        st.markdown(f"""<div class="pago-row">
          <div style='width:9px;height:9px;border-radius:50%;background:{color};flex-shrink:0'></div>
          <div style='flex:1'><div style='font-size:12.5px;font-weight:600;color:#0F172A'>{c["nombre"]}</div>
          <div style='font-size:11px;color:#64748B'>{c["tipo"]} · {c["nota"]}</div></div>
          <div style='font-family:Space Grotesk,sans-serif;font-weight:700;font-size:13px;color:{color}'>{val}/mes</div>
        </div>""",unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🧮 Simulador — ¿Cuánto cuesta conseguir un contrato?")
    c1,c2=st.columns(2)
    with c1:
        n_pres=st.slider("Presentaciones enviadas/mes",10,80,51,help="En abril enviaron 51")
        tasa=st.slider("Tasa de cierre esperada (%)",1,25,5)
        val_con=st.number_input("Valor promedio por contrato ($)",value=83_000_000,step=5_000_000,format="%d")
    with c2:
        dis=n_pres*50_000; total=total_fijo+dis
        cont_esp=n_pres*(tasa/100); ing=cont_esp*val_con; util=ing-total
        st.markdown(f"""<div style='background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;padding:14px 16px'>
          <div style='font-family:Space Grotesk,sans-serif;font-size:13px;font-weight:600;color:#0F172A;margin-bottom:10px'>Proyección mensual</div>
          <div style='display:grid;gap:7px'>
            <div style='display:flex;justify-content:space-between'><span style='color:#64748B;font-size:12px'>Diseñador ({n_pres} presentaciones)</span><span style='font-weight:600;color:#EF4444'>{cop(dis)}</span></div>
            <div style='display:flex;justify-content:space-between'><span style='color:#64748B;font-size:12px'>Costo total del mes</span><span style='font-weight:600;color:#EF4444'>{cop(total)}</span></div>
            <div style='display:flex;justify-content:space-between'><span style='color:#64748B;font-size:12px'>Contratos esperados</span><span style='font-weight:600;color:#2563EB'>{cont_esp:.1f}</span></div>
            <div style='display:flex;justify-content:space-between'><span style='color:#64748B;font-size:12px'>Ingreso esperado</span><span style='font-weight:600;color:#059669'>{cop(int(ing))}</span></div>
            <div style='border-top:1px solid #E2E8F0;margin-top:4px;padding-top:7px;display:flex;justify-content:space-between'>
              <span style='font-weight:700;color:#0F172A'>Utilidad estimada</span>
              <span style='font-family:Space Grotesk,sans-serif;font-size:15px;font-weight:700;color:{"#059669" if util>0 else "#EF4444"}'>{cop(int(util))}</span>
            </div>
          </div>
        </div>""",unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### ➕ Registrar gasto")
    if "pagos_log" not in st.session_state: st.session_state.pagos_log=[]
    with st.form("pf"):
        c1,c2,c3=st.columns(3)
        with c1: concepto=st.text_input("Concepto *"); tipo_p=st.selectbox("Tipo",["Nómina","Marketing","Diseño","Operativo","Otro"])
        with c2: monto=st.number_input("Monto ($)",min_value=0,value=0,step=50_000,format="%d"); fecha_p=st.date_input("Fecha",value=datetime.now())
        with c3: estado_p=st.selectbox("Estado",["Pagado","Pendiente","Aprobado"]); notas_p=st.text_input("Notas")
        if st.form_submit_button("💾 Registrar",use_container_width=True):
            if concepto and monto>0:
                st.session_state.pagos_log.append({"fecha":str(fecha_p),"concepto":concepto,"tipo":tipo_p,"monto":monto,"estado":estado_p,"notas":notas_p})
                st.success(f"✅ {concepto} — {cop(monto)}")
            else: st.error("Concepto y monto obligatorios")
    if st.session_state.pagos_log:
        st.markdown("**Pagos registrados esta sesión:**")
        df_p=pd.DataFrame(st.session_state.pagos_log)
        df_p["Monto"]=df_p["monto"].apply(cop)
        st.dataframe(df_p[["fecha","concepto","tipo","Monto","estado"]],use_container_width=True,hide_index=True)
        st.markdown(f'<div class="al red"><div>💸</div><div><strong>Total sesión: {cop(sum(p["monto"] for p in st.session_state.pagos_log))}</strong></div></div>',unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🤖 Análisis financiero con IA",use_container_width=True):
        if not ai_ok(): st.error("Activa IA en ⚙️ Configuración")
        else:
            with st.spinner("..."): r=ask_ai(f"""Analiza situación financiera Ágora Tech Colombia:
COSTOS JULIO 2026: Luisa $7M + prestaciones · Comercial nuevo $3M + prestaciones · Marketing $1.5M · Diseñador $50K/presentación
CRM: 140 propuestas, pipeline $4.2B, 0 contratos, ticket promedio ~$83M, 51 presentaciones/mes en abril.
## 1. DIAGNÓSTICO FINANCIERO ## 2. PUNTO DE EQUILIBRIO ## 3. PROYECCIÓN Jul-Dic 2026 ## 4. OPTIMIZACIÓN COSTOS ## 5. RIESGO DE LIQUIDEZ
Cifras concretas. Español colombiano.""")
            st.markdown(r)

# ══════════════════════════════════════════
# PROYECTOS
# ══════════════════════════════════════════
def pg_proyectos():
    es_g=st.session_state.user["rol"]=="gerente"; df=mis_proyectos()
    hdr("📋","Proyectos",f"{len(df)} en el CRM")
    c1,c2,c3=st.columns([2,1,1])
    with c1: buscar=st.text_input("🔍 Buscar",placeholder="Nombre del edificio...")
    with c2: filtro_e=st.selectbox("Estado",["Todos"]+ESTADOS_LISTA,format_func=lambda x:ETAPAS.get(x,{"label":x})["label"] if x!="Todos" else "Todos")
    with c3:
        if es_g: filtro_c=st.selectbox("Comercial",["Todos"]+sorted(df["comercial"].dropna().unique().tolist()))
        else: filtro_c="Todos"
    dff=df.copy()
    if buscar: dff=dff[dff["nombre"].str.contains(buscar,case=False,na=False)]
    if filtro_e!="Todos": dff=dff[dff["estado"]==filtro_e]
    if filtro_c!="Todos": dff=dff[dff["comercial"]==filtro_c]
    st.markdown(f'<div style="font-size:12px;color:#94A3B8;margin-bottom:10px">{len(dff)} proyectos · {cop(int(dff["totalNum"].sum()))}</div>',unsafe_allow_html=True)
    for _,r in dff.iterrows():
        tn=int(r.get("totalNum",0) or 0); est=str(r.get("estado","lead"))
        nota=str(r.get("lastNote","") or r.get("notas","") or "")
        with st.expander(f"🏢 {r['nombre']}  ·  {cop(tn)}  ·  {ETAPAS.get(est,{'label':est})['label']}"):
            ti,th=st.tabs(["📋 Info","📜 Historial"])
            with ti:
                c1,c2,c3,c4=st.columns(4)
                c1.metric("Valor",cop(tn)); c2.metric("Cuota 24m",cop(int(r.get("c24Num",0) or 0)))
                c3.metric("Cuota 36m",cop(int(r.get("c36Num",0) or 0))); c4.metric("Actualizado",str(r.get("lastUpdate","—"))[:10])
                if nota and nota!="nan":
                    st.markdown(f'<div class="al blue"><div>📝</div><div>{nota[:300]}</div></div>',unsafe_allow_html=True)
                b1,b2=st.columns(2)
                if b1.button("📝 Actualizar",key=f"pu_{r['nombre']}"):
                    st.session_state.editing=r["nombre"]; st.session_state.page="Actualizar Estado"; st.rerun()
                if b2.button("✉️ Correo IA",key=f"pc_{r['nombre']}"):
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
    hdr("📝","Actualizar Estado e Información","Historial permanente + datos del proyecto")
    df  = mis_proyectos()
    u   = st.session_state.user
    presel  = st.session_state.get("editing","")
    nombres = ["— Selecciona un edificio —"] + sorted(df["nombre"].dropna().unique().tolist())
    idx_sel = nombres.index(presel) if presel in nombres else 0
    sel     = st.selectbox("🏢 Edificio:", nombres, index=idx_sel)

    if sel == "— Selecciona un edificio —":
        st.info("Selecciona un edificio para actualizar su estado e información.")
        return

    r   = df[df["nombre"]==sel].iloc[0]
    est = str(r.get("estado","lead"))

    # ── Tabs: Actualizar estado | Editar información
    tab_est, tab_info = st.tabs(["📋 Actualizar estado","🏗️ Editar información del proyecto"])

    # ════════════════════════════════
    # TAB 1 — ACTUALIZAR ESTADO
    # ════════════════════════════════
    with tab_est:
        # Resumen actual
        tn  = int(r.get("totalNum",0) or 0)
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Valor total",    cop(tn))
        c2.metric("Cuota 36m",      cop(int(r.get("c36Num",0) or 0)))
        c3.metric("Estado actual",  ETAPAS.get(est,{"label":est})["label"])
        c4.metric("Actualizado",    str(r.get("lastUpdate","Nunca"))[:10] or "Nunca")

        nota_actual = str(r.get("lastNote","") or r.get("notas",""))
        if nota_actual and nota_actual not in ["nan",""]:
            st.markdown(
                f'<div class="al blue"><div>📝</div><div><strong>Última nota:</strong> {nota_actual[:250]}</div></div>',
                unsafe_allow_html=True)

        # Historial rápido
        try:
            hist = json.loads(str(r.get("historial","[]") or "[]"))
        except:
            hist = []
        if hist:
            with st.expander(f"📜 Ver historial ({len(hist)} entradas)"):
                st.markdown('<div class="tl">', unsafe_allow_html=True)
                for ev in reversed(hist[-6:]):
                    dc = ETAPAS.get(ev.get("estado",""),{"dot":"#94A3B8"})["dot"]
                    st.markdown(
                        f'<div class="ti"><div class="ti-dot" style="background:{dc}"></div>' +
                        f'<div class="ti-date">{ev.get("fecha","")} · {ev.get("usuario","")}</div>' +
                        f'<div class="ti-h">{ETAPAS.get(ev.get("estado",""),{"label":ev.get("estado","")})["label"]}</div>' +
                        f'<div class="ti-t">{ev.get("nota","")}</div></div>',
                        unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        with st.form("uf_estado"):
            nuevo_e = st.selectbox(
                "Nuevo estado *", ESTADOS_LISTA,
                format_func=lambda x: ETAPAS.get(x,{"label":x})["label"],
                index=ESTADOS_LISTA.index(est) if est in ESTADOS_LISTA else 0)
            nota = st.text_area(
                "Nota * (obligatoria — qué pasó, próximo paso, quién respondió)",
                height=100,
                placeholder="Ej: Hablé con el administrador Juan Pérez. La asamblea es el 16 de julio. Piden cotización actualizada antes del viernes.")

            # Campos adicionales para etapas de ejecución
            if nuevo_e in ["creacion_contrato","financiacion","obra","novedades_obra","entrega","mantenimiento","cerrado"]:
                st.markdown("**Datos de ejecución:**")
                c1,c2 = st.columns(2)
                with c1:
                    contrato  = st.text_input("N° contrato", placeholder="CT-2026-001")
                    obra_ini  = st.text_input("Inicio de obra", placeholder="dd/mm/yyyy")
                with c2:
                    financ    = st.text_area("Detalles de financiación", height=60)
                    obra_fin  = st.text_input("Fin estimado obra", placeholder="dd/mm/yyyy")
            else:
                contrato = financ = obra_ini = obra_fin = ""

            if st.form_submit_button("✅ Guardar en historial", use_container_width=True):
                if not nota.strip():
                    st.error("La nota es obligatoria — describe qué pasó y cuál es el próximo paso.")
                else:
                    agregar_historial(sel, nuevo_e, nota, u["nombre"])
                    ext = {k:v for k,v in {"contrato":contrato,"financiacion_info":financ,
                                            "obra_inicio":obra_ini,"obra_fin":obra_fin}.items() if v}
                    if ext: update_proy(sel, ext)
                    st.success(f"✅ **{sel}** → {ETAPAS.get(nuevo_e,{'label':nuevo_e})['label']}")
                    st.session_state.editing = ""
                    st.rerun()

    # ════════════════════════════════
    # TAB 2 — EDITAR INFORMACIÓN
    # ════════════════════════════════
    with tab_info:
        st.markdown(
            '<div class="al blue"><div>💡</div><div>Actualiza aquí la información base del proyecto. '            'Los cambios se guardan en el CRM local. Para que queden en el Sheet de Google, '            'agrega los datos directamente allí también.</div></div>',
            unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # Valores actuales
        tn_act  = int(r.get("totalNum",0)  or 0)
        c24_act = int(r.get("c24Num",0)    or 0)
        c36_act = int(r.get("c36Num",0)    or 0)

        with st.form("uf_info"):
            st.markdown("#### 🏢 Identificación")
            ci1, ci2 = st.columns(2)
            with ci1:
                nuevo_nombre  = st.text_input("Nombre del edificio",
                    value=str(r.get("nombre","")).strip())
                nueva_dir     = st.text_input("Dirección completa",
                    value=str(r.get("direccion","") or "").strip(),
                    placeholder="Ej: Calle 94 No 23-17, Chapinero, Bogotá")
                nuevo_ctc     = st.text_input("Contacto principal",
                    value=str(r.get("contacto","") or "").strip(),
                    placeholder="Nombre del administrador o presidente de consejo")
            with ci2:
                nuevo_email   = st.text_input("Email de contacto",
                    value=str(r.get("email","") or "").strip(),
                    placeholder="admin@edificio.com")
                nuevo_tel     = st.text_input("Teléfono / WhatsApp",
                    value=str(r.get("telefono","") or "").strip(),
                    placeholder="+57 300 000 0000")
                if u["rol"] in ["gerente","socio"]:
                    nuevo_com = st.selectbox("Comercial responsable", COMS,
                        index=COMS.index(str(r.get("comercial","")).strip())
                        if str(r.get("comercial","")).strip() in COMS else 0)
                else:
                    nuevo_com = str(r.get("comercial","")).strip()

            st.markdown("#### 💰 Valor y financiación")
            cv1, cv2, cv3 = st.columns(3)
            with cv1:
                nuevo_val  = st.number_input("Valor total del proyecto ($)",
                    value=tn_act, step=1_000_000, format="%d",
                    help="Valor total de la propuesta en pesos COP")
            with cv2:
                nuevo_c24  = st.number_input("Cuota 24 meses ($)",
                    value=c24_act if c24_act>0 else (tn_act//24 if tn_act>0 else 0),
                    step=100_000, format="%d")
            with cv3:
                nuevo_c36  = st.number_input("Cuota 36 meses ($)",
                    value=c36_act if c36_act>0 else (tn_act//36 if tn_act>0 else 0),
                    step=100_000, format="%d")

            # Auto-calcular si el usuario cambia el total y deja cuotas en 0
            if nuevo_val > 0 and nuevo_c24 == 0:
                nuevo_c24 = nuevo_val // 24
            if nuevo_val > 0 and nuevo_c36 == 0:
                nuevo_c36 = nuevo_val // 36

            st.markdown("#### 🔒 Vigilancia actual")
            cv1, cv2 = st.columns(2)
            with cv1:
                nuevo_vig  = st.text_input("Costo mensual vigilancia ($)",
                    value=str(r.get("vig","") or "").strip(),
                    placeholder="Ej: 4500000")
            with cv2:
                nuevo_vigh = st.text_input("Vigente hasta",
                    value=str(r.get("vigH","") or "").strip(),
                    placeholder="Ej: Noviembre 2026")

            st.markdown("#### 📝 Observaciones generales")
            nuevo_drive = st.text_input("Link carpeta Drive",
                value=str(r.get("drive","") or "").strip(),
                placeholder="https://drive.google.com/...")
            nuevas_notas = st.text_area("Notas generales del proyecto",
                value=str(r.get("notas","") or "").strip(),
                height=100,
                placeholder="Información general del edificio, particularidades, histórico...")

            st.markdown("<br>", unsafe_allow_html=True)
            ga, gb = st.columns(2)
            with ga:
                guardar_info = st.form_submit_button("💾 Guardar información", use_container_width=True)
            with gb:
                cancelar_info = st.form_submit_button("✕ Cancelar", use_container_width=True)

            if guardar_info:
                cambios = {
                    "nombre":    nuevo_nombre.strip().upper(),
                    "contacto":  nuevo_ctc.strip(),
                    "email":     nuevo_email.strip(),
                    "telefono":  nuevo_tel.strip(),
                    "direccion": nueva_dir.strip(),
                    "comercial": nuevo_com,
                    "totalNum":  nuevo_val,
                    "c24Num":    nuevo_c24,
                    "c36Num":    nuevo_c36,
                    "total":     cop(nuevo_val),
                    "cuota24":   cop(nuevo_c24),
                    "cuota36":   cop(nuevo_c36),
                    "vig":       nuevo_vig.strip(),
                    "vigH":      nuevo_vigh.strip(),
                    "drive":     nuevo_drive.strip(),
                    "notas":     nuevas_notas.strip(),
                    "lastUpdate": datetime.now().isoformat()[:10],
                }
                # Filtrar vacíos para no sobrescribir con nada
                cambios = {k:v for k,v in cambios.items() if v not in [None,""]}
                update_proy(sel, cambios)

                # Registrar en historial que se actualizó info
                campos_cambiados = []
                if nuevo_val != tn_act and nuevo_val > 0:
                    campos_cambiados.append(f"Valor: {cop(nuevo_val)}")
                if nueva_dir.strip() and nueva_dir.strip() != str(r.get("direccion","")).strip():
                    campos_cambiados.append(f"Dirección: {nueva_dir.strip()}")
                if nuevo_ctc.strip() and nuevo_ctc.strip() != str(r.get("contacto","")).strip():
                    campos_cambiados.append(f"Contacto: {nuevo_ctc.strip()}")
                if campos_cambiados:
                    agregar_historial(sel, est,
                        f"Información actualizada — {', '.join(campos_cambiados)}",
                        u["nombre"])

                st.success(f"✅ Información de **{nuevo_nombre or sel}** actualizada correctamente")
                st.rerun()

            if cancelar_info:
                st.session_state.editing = ""
                st.rerun()


def pg_nueva_cotizacion():
    hdr("🧮","Nueva Cotización","Registrar en el CRM")
    with st.form("nc"):
        c1,c2=st.columns(2)
        with c1: nombre=st.text_input("Edificio *"); contacto=st.text_input("Contacto *"); email=st.text_input("Email")
        with c2: direccion=st.text_input("Dirección *",placeholder="Ej: Calle 94 No 23-17, Bogotá"); drive_url=st.text_input("Link Drive")
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
                add_proy({"id":int(datetime.now().timestamp()),"nombre":nombre.upper(),"comercial":u["comercial"],"contacto":contacto,"email":email,"totalNum":valor,"c24Num":c24n,"c36Num":c36n,"total":cop(valor),"cuota24":cop(c24n),"cuota36":cop(c36n),"vig":str(vig_v),"vigH":vig_h,"estado":estado,"etapaOrig":estado,"notas":notas,"lastNote":notas[:100],"lastUpdate":datetime.now().isoformat()[:10],"fecha":datetime.now().strftime("%Y-%m-%d"),"drive":drive_url,"direccion":direccion,"historial":hist_ini,"encuesta":"{}","novedad":""})
                st.success(f"✅ **{nombre}** guardado — {cop(valor)}"); st.balloons()

def pg_correos():
    hdr("✉️","Correos IA","Personalizados por edificio")
    df=mis_proyectos()
    if not ai_ok(): st.markdown('<div class="al amber"><div>⚠️</div><div><strong>IA no configurada.</strong> Ve a ⚙️ Configuración.</div></div>',unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        edif=st.selectbox("Edificio",["— Seleccionar —"]+sorted(df["nombre"].dropna().unique().tolist()))
        tipo=st.selectbox("Tipo",["Primera presentación","Seguimiento post-reunión","Urgencia — asamblea próxima","Objeción: precio alto","Objeción: adultos mayores","Reactivación — stand-by vigilancia","Propuesta visita Alto 61","Confirmación contrato"])
        ctx_e=st.text_area("Contexto",height=70,placeholder="Ej: El cliente pregunta por adultos mayores...")
        if st.button("🤖 Generar",use_container_width=True):
            if edif=="— Seleccionar —": st.warning("Selecciona un edificio")
            elif not ai_ok(): st.error("Activa IA en ⚙️ Configuración")
            else:
                r=df[df["nombre"]==edif].iloc[0]; tn=int(r.get("totalNum",0) or 0); vig=int(r.get("vig",0) or 0)
                with st.spinner("..."): correo=ask_ai(f"""Correo "{tipo}" para Ágora Tech Colombia.
Edificio: {edif} | Valor: {cop(tn)} | Cuota 36m: {cop(int(r.get("c36Num",0) or 0))} | Vigilancia: {cop(vig)}/mes hasta {r.get("vigH","")}
{"Ahorro anual: "+cop(vig*12)+" vs cuota anual 36m: "+cop(int(r.get("c36Num",0) or 0)*12) if vig>0 else ""}
{f"Contexto: {ctx_e}" if ctx_e else ""}
Primera línea: ASUNTO: [asunto llamativo]. Financiamiento 100% sin entrada sin intereses. PIN físico con relieve para adultos mayores. Referencia: edificio Alto 61.
Firma: {st.session_state.user["nombre"]} — Ágora Tech | (+57) 315 101 7511. Texto plano.""")
                st.session_state.correo=correo
    with c2:
        st.markdown("**Vista previa:**")
        correo=st.session_state.get("correo","")
        if correo:
            st.markdown(f'<div style="background:#F8FAFC;border:1.5px solid #E2E8F0;border-radius:10px;padding:16px;font-family:monospace;font-size:12px;line-height:1.75;white-space:pre-wrap;color:#0F172A;max-height:400px;overflow-y:auto">{correo.replace("<","&lt;").replace(">","&gt;")}</div>',unsafe_allow_html=True)
            st.download_button("📋 Descargar",data=correo,file_name=f"correo_{edif[:20]}.txt",mime="text/plain")
        else:
            st.markdown('<div style="background:#F8FAFC;border:1.5px dashed #CBD5E1;border-radius:10px;padding:40px;text-align:center;color:#94A3B8;font-size:13px">Selecciona edificio y genera el correo</div>',unsafe_allow_html=True)

def pg_asistente():
    hdr("🤖","Asistente IA","Pipeline, cierres, objeciones")
    if not ai_ok(): st.markdown('<div class="al amber"><div>⚠️</div><div>IA no configurada. Ve a ⚙️.</div></div>',unsafe_allow_html=True); return
    df=mis_proyectos(); ctx=df.to_string(max_rows=140) if not df.empty else ""
    for msg in st.session_state.messages:
        st.markdown(f'<div class="{"chat-u" if msg["role"]=="user" else "chat-a"}">{"👤 " if msg["role"]=="user" else "🤖 "}{msg["content"]}</div>',unsafe_allow_html=True)
    if not st.session_state.messages:
        sugs=["📊 Resumen ejecutivo del pipeline","⚡ Top 8 proyectos más cercanos al cierre","📈 Estrategia Country 136 y Park 104","👴 Responder objeción adultos mayores","💰 Plan reactivación stand-by vigilancia sep","🔍 Diagnóstico: por qué 0 contratos en 6 meses"]
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
        adultos=st.text_area("Adultos mayores / Discapacidad",height=60)
        incidentes=st.text_area("Incidentes de seguridad",height=60)
        analizar=st.checkbox("🤖 Analizar con IA",value=True)
        if st.form_submit_button("💾 Guardar",use_container_width=True):
            if not nom_e: st.error("Nombre obligatorio"); st.stop()
            if edif_sel!="— Nuevo —":
                datos={"Edificio":nom_e,"Contacto":contacto,"Rol":rol,"Vigilancia":vig,"Costo Vig":cop(costo_v),"Vigencia":vig_h,"Adultos":adultos,"Incidentes":incidentes}
                update_proy(edif_sel,{"encuesta":json.dumps(datos,ensure_ascii=False)})
                agregar_historial(edif_sel,"evaluacion_consejo",f"Encuesta completada. {rol}: {contacto}. Etapa: {etapa_d}.",st.session_state.user["nombre"])
                st.success(f"✅ Encuesta guardada en {edif_sel}")
            if analizar and ai_ok():
                with st.spinner("..."): r=ask_ai(f"""Analiza prospecto Ágora Tech:
Edificio: {nom_e} | {rol}: {contacto} | Etapa: {etapa_d}
Vigilancia: {"SÍ "+cop(costo_v)+"/mes hasta "+vig_h if vig=="Sí" and costo_v>0 else "NO"}
Adultos: {adultos or "No reportado"} | Incidentes: {incidentes or "Ninguno"}
## VIABILIDAD ## ESTRATEGIA ## OBJECIONES PROBABLES ## PRÓXIMOS 3 PASOS""")
                st.markdown("---"); st.markdown(r)

def pg_calendario():
    hdr("📅","Calendario Comercial","Agenda semanal · Asambleas · Seguimiento de edificios")

    # ── Inicializar eventos base
    if "eventos_cal" not in st.session_state:
        st.session_state.eventos_cal = [
            # Comité de gerencia — todos los martes 4:00–5:30pm (recurrente)
            {"titulo":"Comité de Gerencia","tipo":"Comité","fecha":"2026-06-30","hora":"16:00","fin":"17:30","notas":"Socios: Carlos Torres y Carlos Méndez","color":"#7C3AED","icono":"🏢"},
            {"titulo":"Comité de Gerencia","tipo":"Comité","fecha":"2026-07-07","hora":"16:00","fin":"17:30","notas":"Socios: Carlos Torres y Carlos Méndez","color":"#7C3AED","icono":"🏢"},
            {"titulo":"Comité de Gerencia","tipo":"Comité","fecha":"2026-07-14","hora":"16:00","fin":"17:30","notas":"Socios: Carlos Torres y Carlos Méndez","color":"#7C3AED","icono":"🏢"},
            {"titulo":"Comité de Gerencia","tipo":"Comité","fecha":"2026-07-21","hora":"16:00","fin":"17:30","notas":"Socios: Carlos Torres y Carlos Méndez","color":"#7C3AED","icono":"🏢"},
            {"titulo":"Comité de Gerencia","tipo":"Comité","fecha":"2026-07-28","hora":"16:00","fin":"17:30","notas":"Socios: Carlos Torres y Carlos Méndez","color":"#7C3AED","icono":"🏢"},
            # Asambleas críticas
            {"titulo":"Asamblea Country 136","tipo":"Asamblea","fecha":"2026-06-27","hora":"18:00","fin":"20:00","notas":"🔥 CRÍTICA — Gestiona Luisa. Cierre probable.","color":"#EF4444","icono":"🔥"},
            {"titulo":"Asamblea Park 104","tipo":"Asamblea","fecha":"2026-06-13","hora":"18:00","fin":"20:00","notas":"🔥 Rafael — Confirmar nueva admón.","color":"#EF4444","icono":"🔥"},
            {"titulo":"Asamblea Edificio Sahara","tipo":"Asamblea","fecha":"2026-06-13","hora":"17:00","fin":"19:00","notas":"Rafael — Confirmar si va propuesta Ágora","color":"#EF4444","icono":"🔥"},
            {"titulo":"Reunión consejo Camila","tipo":"Reunión consejo","fecha":"2026-06-09","hora":"18:00","fin":"19:30","notas":"Lina — Decidirán proveedor","color":"#D97706","icono":"📋"},
            {"titulo":"Visita Alto 61 — Ed. El Cerro","tipo":"Visita Alto 61","fecha":"2026-06-11","hora":"10:00","fin":"11:30","notas":"Rafael — Consejo visita edificio modelo","color":"#0D9488","icono":"⭐"},
            {"titulo":"Reunión consejo Urapanes","tipo":"Reunión consejo","fecha":"2026-06-16","hora":"18:00","fin":"19:30","notas":"Rafael — Preseleccionados entre 3","color":"#D97706","icono":"📋"},
            {"titulo":"Asamblea Ed. Cesanne","tipo":"Asamblea","fecha":"2026-07-16","hora":"18:00","fin":"20:00","notas":"Rafael — Germán González impulsa","color":"#D97706","icono":"🟡"},
            {"titulo":"Asamblea Ed. Los Pinos","tipo":"Asamblea","fecha":"2026-07-16","hora":"19:30","fin":"21:00","notas":"Lina — Asamblea extraordinaria nocturna","color":"#D97706","icono":"🟡"},
            {"titulo":"Asamblea Ed. Altos del Retiro","tipo":"Asamblea","fecha":"2026-07-16","hora":"20:00","fin":"22:00","notas":"Lina — Extraordinaria tentativa","color":"#D97706","icono":"🟡"},
            {"titulo":"Asamblea Ed. Risaralda","tipo":"Asamblea","fecha":"2026-07-25","hora":"18:00","fin":"20:00","notas":"🔥 Rafael/Luisa — Asamblea extraordinaria antes jul 30","color":"#EF4444","icono":"🔥"},
        ]

    COLORES = {"Asamblea":"#EF4444","Reunión consejo":"#D97706","Visita Alto 61":"#0D9488",
               "Comité":"#7C3AED","Llamada":"#2563EB","Firma contrato":"#059669",
               "Inicio obra":"#059669","Entrega":"#10B981","Otro":"#64748B"}
    ICONOS  = {"Asamblea":"🏛️","Reunión consejo":"📋","Visita Alto 61":"⭐",
               "Comité":"🏢","Llamada":"📞","Firma contrato":"📝",
               "Inicio obra":"🔨","Entrega":"🎉","Otro":"📅"}

    # ── Tabs principales
    tab_sem, tab_mes, tab_add, tab_sug = st.tabs([
        "📆 Semana actual",
        "📅 Vista mensual",
        "➕ Agregar evento",
        "💡 Sugerencias IA"
    ])

    hoy   = datetime.now().date()
    lunes = hoy - timedelta(days=hoy.weekday())

    # ════════════════════════════════════════
    # TAB 1: CALENDARIO SEMANAL
    # ════════════════════════════════════════
    with tab_sem:
        # Navegación de semana
        c_prev, c_titulo, c_next = st.columns([1,3,1])
        with c_prev:
            if st.button("← Semana anterior", key="sem_prev"):
                st.session_state["sem_offset"] = st.session_state.get("sem_offset",0) - 1
                st.rerun()
        offset = st.session_state.get("sem_offset", 0)
        lunes_vis = lunes + timedelta(weeks=offset)
        dias_vis  = [lunes_vis + timedelta(days=i) for i in range(7)]
        with c_titulo:
            st.markdown(f"<div style='text-align:center;font-family:Space Grotesk,sans-serif;"
                        f"font-weight:700;font-size:14px;color:#0F172A;padding:8px 0'>"
                        f"Semana del {lunes_vis.strftime('%d %b')} al "
                        f"{(lunes_vis+timedelta(days=6)).strftime('%d %b %Y')}</div>",
                        unsafe_allow_html=True)
        with c_next:
            if st.button("Semana siguiente →", key="sem_next"):
                st.session_state["sem_offset"] = st.session_state.get("sem_offset",0) + 1
                st.rerun()

        DIAS_NOM = ["LUN","MAR","MIÉ","JUE","VIE","SÁB","DOM"]
        HORAS_CAL = list(range(8, 21))  # 8am a 8pm

        # Filtrar eventos de la semana visible
        evs_sem = {d: [] for d in dias_vis}
        for e in st.session_state.eventos_cal:
            try:
                fd = datetime.strptime(str(e["fecha"])[:10], "%Y-%m-%d").date()
                if fd in evs_sem: evs_sem[fd].append(e)
            except: pass

        # Construir HTML del calendario
        col_w = 100/8
        th = f"<td style='width:{col_w*0.55:.1f}%;background:#F8FAFC;border:1px solid #E2E8F0;padding:5px 3px;font-size:9px;color:#94A3B8;text-align:center;vertical-align:middle'></td>"
        for i,d in enumerate(dias_vis):
            es_hoy = (d == hoy)
            bg_h   = "#EFF6FF" if es_hoy else "#F8FAFC"
            col_d  = "#1D4ED8" if es_hoy else "#334155"
            fw_d   = "800" if es_hoy else "600"
            num    = d.strftime('%d')
            dot_hoy= f"<div style='width:5px;height:5px;border-radius:50%;background:#2563EB;margin:1px auto 0'></div>" if es_hoy else ""
            th += (f"<td style='background:{bg_h};border:1px solid #E2E8F0;"
                   f"padding:7px 3px;text-align:center;width:{col_w:.1f}%'>"
                   f"<div style='font-size:9.5px;font-weight:{fw_d};color:{col_d};"
                   f"font-family:Space Grotesk,sans-serif;letter-spacing:.5px'>{DIAS_NOM[i]}</div>"
                   f"<div style='font-size:15px;font-weight:{fw_d};color:{col_d};"
                   f"font-family:Space Grotesk,sans-serif'>{num}</div>{dot_hoy}</td>")

        filas_html = ""
        for h in HORAS_CAL:
            hora_lbl = f"{h:02d}:00"
            fila = (f"<td style='background:#FAFAFA;border:1px solid #F1F5F9;"
                    f"padding:3px 5px;font-size:9px;color:#CBD5E1;text-align:right;"
                    f"white-space:nowrap;vertical-align:top'>{hora_lbl}</td>")
            for d in dias_vis:
                celdas = ""
                for e in evs_sem[d]:
                    h_ev = int(str(e.get("hora","00:00"))[:2])
                    if h_ev == h:
                        fin  = str(e.get("fin",""))
                        col  = e.get("color","#94A3B8")
                        ico  = e.get("icono","📅")
                        tit  = str(e["titulo"])[:20]
                        nota = str(e.get("notas",""))[:60]
                        celdas += (f"<div title='{nota}' style='background:{col}18;"
                                   f"border-left:3px solid {col};border-radius:0 5px 5px 0;"
                                   f"padding:3px 5px;margin-bottom:2px;cursor:default'>"
                                   f"<div style='font-size:9.5px;font-weight:700;color:{col};"
                                   f"white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>"
                                   f"{ico} {tit}</div>"
                                   f"<div style='font-size:8.5px;color:#64748B'>"
                                   f"{e.get('hora','')}{'–'+fin if fin else ''}</div>"
                                   f"</div>")
                bg_c = "#FAFBFF" if d==hoy else "white"
                fila += (f"<td style='background:{bg_c};border:1px solid #F1F5F9;"
                         f"padding:2px;vertical-align:top;min-height:34px'>{celdas}</td>")
            filas_html += f"<tr>{fila}</tr>"

        html_cal = f"""
        <div style='overflow-x:auto;border-radius:10px;border:1px solid #E2E8F0;
             box-shadow:0 1px 3px rgba(15,23,42,.07);margin-bottom:10px'>
          <table style='width:100%;border-collapse:collapse;background:white;min-width:600px'>
            <thead><tr>{th}</tr></thead>
            <tbody>{filas_html}</tbody>
          </table>
        </div>"""
        st.markdown(html_cal, unsafe_allow_html=True)

        # Leyenda
        st.markdown("""<div style='display:flex;flex-wrap:wrap;gap:14px;font-size:11px;color:#64748B;margin-top:4px'>
          <span style='display:flex;align-items:center;gap:5px'><span style='width:10px;height:10px;border-radius:2px;background:#7C3AED;display:inline-block'></span>🏢 Comité de Gerencia (martes 4–5:30pm)</span>
          <span style='display:flex;align-items:center;gap:5px'><span style='width:10px;height:10px;border-radius:2px;background:#EF4444;display:inline-block'></span>🔥 Asamblea crítica</span>
          <span style='display:flex;align-items:center;gap:5px'><span style='width:10px;height:10px;border-radius:2px;background:#D97706;display:inline-block'></span>📋 Reunión consejo</span>
          <span style='display:flex;align-items:center;gap:5px'><span style='width:10px;height:10px;border-radius:2px;background:#0D9488;display:inline-block'></span>⭐ Visita Alto 61</span>
          <span style='display:flex;align-items:center;gap:5px'><span style='width:10px;height:10px;border-radius:2px;background:#2563EB;display:inline-block'></span>📞 Llamada/seguimiento</span>
        </div>""", unsafe_allow_html=True)

        # Lista de eventos de la semana
        evs_lista = []
        for d in dias_vis:
            for e in evs_sem[d]:
                evs_lista.append((d, e))
        evs_lista.sort(key=lambda x:(x[0], x[1].get("hora","")))
        if evs_lista:
            st.markdown("**Eventos de esta semana:**")
            for d, e in evs_lista:
                col_e = e.get("color","#94A3B8")
                st.markdown(
                    f'<div style="background:white;border:1px solid #E2E8F0;border-left:3px solid {col_e};'
                    f'border-radius:0 8px 8px 0;padding:9px 13px;margin-bottom:5px;display:flex;gap:10px;align-items:center">'
                    f'<div style="min-width:44px;text-align:center"><div style="font-size:9px;font-weight:700;color:#94A3B8;text-transform:uppercase">{d.strftime("%a")}</div>'
                    f'<div style="font-size:15px;font-weight:700;color:#0F172A;font-family:Space Grotesk,sans-serif">{d.strftime("%d")}</div></div>'
                    f'<div style="flex:1"><div style="font-size:12.5px;font-weight:700;color:#0F172A">{e["icono"]} {e["titulo"]}</div>'
                    f'<div style="font-size:11px;color:#64748B;margin-top:2px">{e.get("hora","")}{"–"+e.get("fin","") if e.get("fin") else ""} · {e.get("notas","")[:80]}</div></div>'
                    f'</div>', unsafe_allow_html=True)
        else:
            st.info("No hay eventos programados esta semana. Agrégalos en la pestaña ➕")

    # ════════════════════════════════════════
    # TAB 2: VISTA MENSUAL
    # ════════════════════════════════════════
    with tab_mes:
        import calendar
        # Navegación de mes
        if "mes_offset" not in st.session_state: st.session_state["mes_offset"] = 0
        cp, ct, cn = st.columns([1,3,1])
        with cp:
            if st.button("← Mes anterior", key="mes_prev"):
                st.session_state["mes_offset"] -= 1; st.rerun()
        mes_off = st.session_state["mes_offset"]
        año_v   = (hoy.replace(day=1) + timedelta(days=32*mes_off)).year
        mes_v   = (hoy.replace(day=1) + timedelta(days=32*mes_off)).month
        MESES   = ["","Enero","Febrero","Marzo","Abril","Mayo","Junio",
                   "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
        with ct:
            st.markdown(f"<div style='text-align:center;font-family:Space Grotesk,sans-serif;"
                        f"font-weight:700;font-size:15px;color:#0F172A;padding:8px 0'>"
                        f"{MESES[mes_v]} {año_v}</div>", unsafe_allow_html=True)
        with cn:
            if st.button("Mes siguiente →", key="mes_next"):
                st.session_state["mes_offset"] += 1; st.rerun()

        # Construir grilla mensual
        cal_m = calendar.monthcalendar(año_v, mes_v)
        dias_header = "<tr>" + "".join(
            f"<th style='background:#F8FAFC;border:1px solid #E2E8F0;padding:7px;text-align:center;"
            f"font-size:10px;font-weight:700;color:#64748B;letter-spacing:1px'>{d}</th>"
            for d in ["LUN","MAR","MIÉ","JUE","VIE","SÁB","DOM"]) + "</tr>"

        # Indexar eventos por fecha
        evs_idx = {}
        for e in st.session_state.eventos_cal:
            try:
                fd = str(e["fecha"])[:10]
                evs_idx.setdefault(fd, []).append(e)
            except: pass

        filas_mes = ""
        for semana in cal_m:
            fila = ""
            for dia in semana:
                if dia == 0:
                    fila += "<td style='background:#FAFAFA;border:1px solid #F1F5F9;min-height:80px'></td>"
                else:
                    fecha_str = f"{año_v}-{mes_v:02d}-{dia:02d}"
                    es_hoy_m  = (datetime(año_v,mes_v,dia).date() == hoy)
                    evs_dia   = evs_idx.get(fecha_str, [])
                    bg_dia    = "#EFF6FF" if es_hoy_m else "white"
                    num_style = ("font-weight:800;color:#1D4ED8;background:#DBEAFE;"
                                 "border-radius:50%;width:22px;height:22px;display:inline-flex;"
                                 "align-items:center;justify-content:center") if es_hoy_m else "color:#334155;font-weight:600"
                    evs_html = ""
                    for e in evs_dia[:3]:
                        col_e = e.get("color","#94A3B8")
                        evs_html += (f"<div style='background:{col_e}18;border-left:2px solid {col_e};"
                                     f"border-radius:0 3px 3px 0;padding:2px 4px;margin-top:2px;"
                                     f"font-size:9px;font-weight:600;color:{col_e};"
                                     f"overflow:hidden;text-overflow:ellipsis;white-space:nowrap'>"
                                     f"{e.get('icono','📅')} {str(e['titulo'])[:16]}</div>")
                    if len(evs_dia)>3:
                        evs_html += f"<div style='font-size:8px;color:#94A3B8;margin-top:1px'>+{len(evs_dia)-3} más</div>"
                    fila += (f"<td style='background:{bg_dia};border:1px solid #E2E8F0;"
                             f"padding:6px;vertical-align:top;min-height:80px;cursor:default'>"
                             f"<div style='font-size:12px;{num_style};margin-bottom:3px'>{dia}</div>"
                             f"{evs_html}</td>")
            filas_mes += f"<tr>{fila}</tr>"

        html_mes = f"""
        <div style='overflow-x:auto;border-radius:10px;border:1px solid #E2E8F0;
             box-shadow:0 1px 3px rgba(15,23,42,.07)'>
          <table style='width:100%;border-collapse:collapse;background:white'>
            <thead>{dias_header}</thead>
            <tbody>{filas_mes}</tbody>
          </table>
        </div>"""
        st.markdown(html_mes, unsafe_allow_html=True)

    # ════════════════════════════════════════
    # TAB 3: AGREGAR EVENTO
    # ════════════════════════════════════════
    with tab_add:
        u_cal = st.session_state.user
        st.markdown("**Agregar evento al calendario**")
        with st.form("cal_form"):
            c1, c2 = st.columns(2)
            with c1:
                titulo_a = st.text_input("Título *", placeholder="Ej: Asamblea Edificio Camila")
                edif_a   = st.text_input("Edificio (opcional)")
                tipo_a   = st.selectbox("Tipo", list(COLORES.keys()))
                notas_a  = st.text_area("Notas / Observaciones", height=80,
                    placeholder="Detalles, quién asiste, qué preparar...")
            with c2:
                fecha_a  = st.date_input("Fecha", value=hoy)
                hora_ini = st.selectbox("Hora inicio",
                    [f"{h:02d}:{m:02d}" for h in range(7,22) for m in [0,30]], index=18)
                hora_fin = st.selectbox("Hora fin",
                    [f"{h:02d}:{m:02d}" for h in range(7,23) for m in [0,30]], index=21)
                if u_cal["rol"] in ["gerente","socio"]:
                    com_a = st.selectbox("Comercial responsable", ["—"]+COMS)
                else:
                    com_a = u_cal.get("comercial","")
            if st.form_submit_button("📅 Agregar al calendario", use_container_width=True):
                if not titulo_a.strip():
                    st.error("El título es obligatorio")
                else:
                    nuevo_ev = {
                        "titulo": titulo_a, "tipo": tipo_a,
                        "fecha": fecha_a.isoformat(),
                        "hora": hora_ini, "fin": hora_fin,
                        "notas": notas_a,
                        "color": COLORES.get(tipo_a,"#64748B"),
                        "icono": ICONOS.get(tipo_a,"📅"),
                        "edificio": edif_a, "comercial": com_a,
                    }
                    st.session_state.eventos_cal.append(nuevo_ev)
                    st.success(f"✅ **{titulo_a}** agregado para el {fecha_a.strftime('%d %b %Y')} a las {hora_ini}")
                    # Navegar a la semana del evento
                    ev_date = fecha_a
                    diff_weeks = (ev_date - hoy).days // 7
                    st.session_state["sem_offset"] = diff_weeks
                    st.rerun()

        # Lista de todos los eventos
        if st.session_state.eventos_cal:
            st.markdown("---")
            st.markdown("**Todos los eventos programados:**")
            evs_sorted = sorted(st.session_state.eventos_cal,
                                key=lambda x:(str(x.get("fecha","")), str(x.get("hora",""))))
            for i, e in enumerate(evs_sorted):
                col_e = e.get("color","#94A3B8")
                c1, c2 = st.columns([5,1])
                with c1:
                    st.markdown(
                        f'<div style="border-left:3px solid {col_e};padding:7px 12px;margin-bottom:4px">'
                        f'<span style="font-size:12.5px;font-weight:600;color:#0F172A">'
                        f'{e["icono"]} {e["titulo"]}</span> '
                        f'<span style="font-size:11px;color:#94A3B8">· {str(e.get("fecha",""))[:10]} {e.get("hora","")}–{e.get("fin","")}</span>'
                        f'<br><span style="font-size:11px;color:#64748B">{e.get("notas","")[:80]}</span>'
                        f'</div>', unsafe_allow_html=True)
                with c2:
                    if st.button("🗑", key=f"del_ev_{i}", help="Eliminar"):
                        st.session_state.eventos_cal.pop(i)
                        st.rerun()

    # ════════════════════════════════════════
    # TAB 4: SUGERENCIAS IA
    # ════════════════════════════════════════
    with tab_sug:
        st.markdown("#### 💡 Sugerencias de seguimiento por edificio")
        df_c = mis_proyectos()

        # Sugerencias fijas basadas en datos reales del CRM
        SUGERENCIAS = [
            ("🔥","COUNTRY 136","Rafael Torres","Asamblea jun 27 — preparar presentación ejecutiva. Gestiona Luisa. Llevar 3 referencias de edificios similares.","#EF4444"),
            ("🔥","PARK 104","Rafael Torres","Asamblea jun 13 — hay nuevo administrador. Confirmar quórum y si Ágora está en la agenda de proveedores.","#EF4444"),
            ("🔥","EDIFICIO RISARALDA","Rafael Torres","Asamblea extraordinaria antes jul 30 — fecha por confirmar. Llamar esta semana a Joaquín De Bedout.","#EF4444"),
            ("🟡","EDIFICIO SAHARA","Rafael Torres","Asamblea jun 13 — confirmar si va propuesta Ágora. Enviar modificaciones actualizadas antes del lunes.","#D97706"),
            ("🟡","EDIFICIO NOMAD","Rafael Torres","David Conde tiene cotización rival más económica. Agendar reunión para comparar y mostrar diferenciadores (financiación 100%).","#D97706"),
            ("🟡","EDIFICIO CAMILA","Lina Calle","Reunión consejo jun 9 — Javier Oviedo. Llevar propuesta con costos vs vigilancia actual.","#D97706"),
            ("🟡","EDIFICIO EL CERRO","Rafael Torres","Visita Alto 61 jun 11 — consejo ya aceptó ir. Preparar recorrido: mostrar app, pin, acceso vehicular.","#D97706"),
            ("🟡","EDIFICIO AVANTI","Rafael Torres","Presidente regresa en julio. Agendar reunión de cierre para primera semana de julio.","#D97706"),
            ("🟡","EDIFICIO URAPANES","Rafael Torres","Preseleccionados entre 3. Reunión consejo jun 16. Llevar análisis financiero vs competidores.","#D97706"),
            ("🔵","BOX OFFICE","Sonia Castro","Stand-by — Aprobaron automatización. Reactivar en septiembre cuando vence vigilancia. Agendar llamada para agosto.","#0EA5E9"),
            ("🔵","EDIFICIO ZAPPAN 109","Sonia Castro","Stand-by — Vencimiento vigilancia noviembre. Contactar antes de agosto para preparar contrato.","#0EA5E9"),
            ("🔵","EDIFICIO SAN MARCOS","Sonia Castro","Están definiendo retirar vigilantes. Contrato vence oct. Contactar HOY — oportunidad de cierre anticipado.","#0EA5E9"),
            ("💡","EDIFICIO LOS PINOS","Lina Calle","Asamblea extraordinaria tentativa jul 16. Confirmar con Daniel Sierra. Llevar pólizas y cubrimientos.","#6366F1"),
            ("💡","EDIFICIO BARCELO NA","Sonia Castro","Recibiendo cotizaciones hasta junio. Hacer seguimiento esta semana — confirmar si Ágora está en shortlist.","#6366F1"),
            ("💡","OLIVAR","Rafael Torres","Reunión consejo 11 jun. Sin avances informados. Llamar a Rafael para actualizar estado.","#6366F1"),
        ]

        # Filtros
        cf1, cf2 = st.columns(2)
        with cf1:
            filtro_prior = st.selectbox("Prioridad", ["Todas","🔥 Críticas","🟡 Importantes","🔵 Stand-by","💡 Seguimiento"])
        with cf2:
            if st.session_state.user["rol"] in ["gerente","socio"]:
                filtro_com_s = st.selectbox("Comercial", ["Todos"]+COMS)
            else:
                filtro_com_s = st.session_state.user.get("comercial","Todos")

        for ico, edif, com, sugerencia, color in SUGERENCIAS:
            if filtro_prior != "Todas" and not filtro_prior.startswith(ico):
                continue
            if filtro_com_s != "Todos" and com.upper() not in filtro_com_s.upper():
                continue
            st.markdown(f"""
            <div style='background:white;border:1px solid #E2E8F0;border-left:4px solid {color};
                 border-radius:0 10px 10px 0;padding:12px 16px;margin-bottom:8px'>
              <div style='display:flex;justify-content:space-between;align-items:flex-start'>
                <div style='font-size:13px;font-weight:700;color:#0F172A'>{ico} {edif}</div>
                <span style='font-size:10.5px;color:#94A3B8;background:#F8FAFC;padding:2px 8px;
                     border-radius:20px;border:1px solid #E2E8F0'>{com.split()[0]}</span>
              </div>
              <div style='font-size:12px;color:#334155;margin-top:5px;line-height:1.6'>{sugerencia}</div>
            </div>""", unsafe_allow_html=True)

        # Generar sugerencias con IA
        st.markdown("---")
        if st.button("🤖 Generar plan de acción personalizado con IA", use_container_width=True):
            if not ai_ok():
                st.error("Activa la IA en ⚙️ Configuración")
            else:
                df_act = df_c[df_c["estado"].isin(["evaluacion_consejo","negociacion"])]
                ctx = df_act[["nombre","comercial","estado","lastNote","totalNum"]].to_string()
                prompt = f"""Genera un plan de acción semanal para el equipo comercial de Ágora Tech.

Proyectos en evaluación activa:
{ctx}

Formato por comercial:
## RAFAEL TORRES — Acciones esta semana
## LINA CALLE — Acciones esta semana  
## SONIA CASTRO — Acciones esta semana
## ALBERTO FERRER — Acciones esta semana

Para cada edificio: acción concreta, qué decir, qué preparar. Máx 3 líneas por edificio. Usa • para bullets."""
                with st.spinner("Generando plan de acción..."):
                    resp = ask_ai(prompt, max_tokens=2000)
                st.markdown(resp)


def pg_configuracion():
    u=st.session_state.user; es_g=u["rol"]=="gerente"
    hdr("⚙️","Configuración","IA + conexión Sheet")
    if ai_ok():
        k=get_key()
        st.markdown(f'<div class="al green"><div>✅</div><div><strong>IA Groq activa</strong> — Llama 3.3 70B · ...{k[-4:]}</div></div>',unsafe_allow_html=True)
    else:
        st.markdown('<div class="al red"><div>🔴</div><div><strong>IA no configurada.</strong></div></div>',unsafe_allow_html=True)

    # Estado del Sheet
    sheet_ok=st.session_state.get("sheet_ok",False)
    status=st.session_state.get("sheet_status","No verificado")
    st.markdown(f'<div class="al {"green" if sheet_ok else "amber"}"><div>{"✅" if sheet_ok else "⚠️"}</div><div><strong>Google Sheet:</strong> {status}</div></div>',unsafe_allow_html=True)

    if st.button("🔄 Forzar sincronización con Sheet",use_container_width=True):
        refrescar_sheet(); st.rerun()

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
        st.markdown("**Configuración permanente en Streamlit Cloud → ⋮ → Settings → Secrets:**")
        st.code('GROQ_API_KEY = "gsk_tu-key"',language="toml")
        st.markdown("---")
        df=get_crm()
        c1,c2,c3,c4=st.columns(4)
        c1.metric("Proyectos en CRM",len(df))
        c2.metric("En evaluación",len(df[df["estado"]=="evaluacion_consejo"]))
        c3.metric("Stand-by",len(df[df["estado"]=="aprobado_espera"]))
        c4.metric("IA","🟢 Activa" if ai_ok() else "🔴 Inactiva")

def pg_auditoria():
    hdr("🔍","Auditoría","Análisis del equipo y pipeline")
    df=get_crm()
    c1,c2,c3,c4,c5=st.columns(5)
    c1.metric("Total",len(df)); c2.metric("Pipeline",cop(int(df["totalNum"].sum())))
    c3.metric("En evaluación",len(df[df["estado"]=="evaluacion_consejo"]))
    c4.metric("Perdidos",len(df[df["estado"]=="perdido"])); c5.metric("Contratos",len(df[df["estado"]=="cerrado"]))
    st.markdown('<div class="al red"><div>❗</div><div><strong>0 contratos cerrados.</strong> El cuello de botella está en el cierre en asamblea. El proceso de "evaluación consejo → asamblea" es la etapa más larga y donde se pierde el 70%.</div></div>',unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        res=df[df["totalNum"]>0].groupby("comercial").agg(n=("totalNum","count"),pip=("totalNum","sum")).reset_index()
        res["$M"]=(res["pip"]/1e6).round(1)
        st.dataframe(res[["comercial","n","$M"]].rename(columns={"comercial":"Comercial","n":"Cotiz."}),use_container_width=True,hide_index=True)
    with c2:
        if st.button("🤖 Diagnóstico estratégico",use_container_width=True):
            with st.spinner(): r=ask_ai("Top 8 proyectos más cercanos al cierre con acción concreta. Por qué 0 contratos. Plan 7 días.",df.to_string(max_rows=140))
            st.markdown(r)

def pg_pipeline():
    hdr("🎯","Pipeline Kanban","Embudo por etapas")
    df=mis_proyectos()
    etapas_k=[("lead","🔵 Lead"),("cotizado","🟡 Contacto frío"),("evaluacion_consejo","🟠 En evaluación"),("negociacion","🔥 Negociando"),("aprobado_espera","🔒 Stand-by"),("cerrado","✅ Cerrado")]
    cols=st.columns(6)
    for i,(k,lbl) in enumerate(etapas_k):
        items=df[df["estado"]==k]; tot=int(items["totalNum"].sum())
        with cols[i]:
            color=ETAPAS.get(k,{"dot":"#94A3B8"})["dot"]
            st.markdown(f'<div style="font-size:11.5px;font-weight:700;color:{color};margin-bottom:4px">{lbl}</div><div style="font-size:10px;color:#94A3B8;margin-bottom:8px">{len(items)} · {cop(tot)}</div>',unsafe_allow_html=True)
            for _,r in items.iterrows():
                tn=int(r.get("totalNum",0) or 0)
                st.markdown(f'<div style="background:white;border:1px solid #E2E8F0;border-radius:7px;padding:8px;margin-bottom:5px"><div style="font-size:11px;font-weight:600;color:#0F172A">{str(r["nombre"])[:22]}</div><div style="font-size:9.5px;color:#94A3B8;margin:1px 0">{str(r.get("comercial","—")).split()[0]}</div><div style="font-size:11.5px;font-weight:700;color:#059669">{cop(tn) if tn else "—"}</div></div>',unsafe_allow_html=True)

def pg_usuarios():
    hdr("👥","Usuarios","Administrar accesos")
    usuarios = get_usuarios()

    # Tabla de usuarios
    st.markdown("""<div style='display:grid;grid-template-columns:2fr 1.5fr 1fr 1fr 100px 100px;
        gap:6px;padding:8px 12px;background:#F8FAFC;border-radius:8px;margin-bottom:6px;
        font-size:10px;font-weight:700;color:#94A3B8;letter-spacing:.5px;text-transform:uppercase'>
      <span>Nombre</span><span>Usuario / Pass</span><span>Rol</span><span>Estado</span><span></span><span></span>
    </div>""", unsafe_allow_html=True)

    for uk, ud in usuarios.items():
        activo = ud.get("activo", True)
        rol_colors = {"gerente":"#7C3AED","comercial":"#2563EB","socio":"#0D9488"}
        rol_color  = rol_colors.get(ud["rol"],"#94A3B8")
        cols = st.columns([2, 1.5, 1, 1, 0.7, 0.7])
        cols[0].markdown(f"**{ud['nombre']}**")
        cols[1].markdown(
            f"<code style='font-size:11px'>{uk}</code><br>"
            f"<span style='font-size:10px;color:#94A3B8'>🔑 {ud['pass']}</span>",
            unsafe_allow_html=True)
        cols[2].markdown(
            f"<span style='background:{rol_color}22;color:{rol_color};border:1px solid {rol_color}44;"
            f"border-radius:20px;padding:2px 8px;font-size:10.5px;font-weight:600'>{ud['rol'].capitalize()}</span>",
            unsafe_allow_html=True)
        cols[3].markdown(
            f'<span class="tag {"tag-g" if activo else "tag-r"}">{"Activo" if activo else "Inactivo"}</span>',
            unsafe_allow_html=True)
        if cols[4].button("✏️ Editar", key=f"edit_{uk}", use_container_width=True):
            st.session_state["eu"] = uk
            st.rerun()
        if cols[5].button("🔒" if activo else "🔓", key=f"tog_{uk}", use_container_width=True):
            st.session_state.usuarios_db[uk]["activo"] = not activo
            st.rerun()
        st.markdown('<hr style="border:none;border-top:1px solid #F1F5F9;margin:3px 0">',
                    unsafe_allow_html=True)

    # ── Formulario de edición
    eu = st.session_state.get("eu", "")
    if eu and eu in usuarios:
        ud_e = usuarios[eu]
        st.markdown("---")
        st.markdown(f"#### ✏️ Editando: **{ud_e['nombre']}**")
        with st.form("euf", clear_on_submit=False):
            c1, c2 = st.columns(2)
            with c1:
                nn = st.text_input("Nombre completo", value=ud_e["nombre"])
                np = st.text_input("Nueva contraseña (vacío = sin cambio)",
                                   type="password", placeholder="••••••••")
            with c2:
                ROLES = ["gerente","comercial","socio"]
                idx_r = ROLES.index(ud_e["rol"]) if ud_e["rol"] in ROLES else 1
                nr = st.selectbox("Rol", ROLES, index=idx_r,
                    format_func=lambda x: {
                        "gerente":"🟣 Gerente — acceso total",
                        "comercial":"🔵 Comercial — sus proyectos",
                        "socio":"🟢 Socio — solo visualización"
                    }.get(x, x))
                COMS_EXT = [""] + COMS
                idx_c = COMS_EXT.index(ud_e.get("comercial","")) if ud_e.get("comercial","") in COMS_EXT else 0
                nc = st.selectbox("Comercial asociado", COMS_EXT, index=idx_c,
                    format_func=lambda x: "— Sin asignar —" if x=="" else x)
            ca, cb = st.columns(2)
            with ca:
                guardar = st.form_submit_button("💾 Guardar cambios", use_container_width=True)
            with cb:
                cancelar = st.form_submit_button("✕ Cancelar", use_container_width=True)
            if guardar:
                st.session_state.usuarios_db[eu].update({
                    "nombre": nn, "rol": nr, "comercial": nc
                })
                if np.strip():
                    st.session_state.usuarios_db[eu]["pass"] = np.strip()
                st.success(f"✅ **{nn}** actualizado")
                st.session_state.pop("eu", None)
                st.rerun()
            if cancelar:
                st.session_state.pop("eu", None)
                st.rerun()

    # ── Crear nuevo usuario
    st.markdown("---")
    with st.expander("➕ Crear nuevo usuario"):
        with st.form("auf"):
            c1, c2 = st.columns(2)
            with c1:
                nu   = st.text_input("Nombre de usuario *", placeholder="ej: jperez")
                nn2  = st.text_input("Nombre completo *")
                np2  = st.text_input("Contraseña *", type="password")
            with c2:
                nr2  = st.selectbox("Rol", ["comercial","gerente","socio"])
                nc2  = st.selectbox("Comercial", [""]+COMS,
                    format_func=lambda x: "— Sin asignar —" if x=="" else x)
            if st.form_submit_button("➕ Crear usuario", use_container_width=True):
                if not nu or not nn2 or not np2:
                    st.error("Nombre de usuario, nombre completo y contraseña son obligatorios")
                elif nu.lower() in usuarios:
                    st.error(f"El usuario '{nu}' ya existe")
                else:
                    st.session_state.usuarios_db[nu.lower()] = {
                        "pass":np2,"nombre":nn2,"rol":nr2,"comercial":nc2,"activo":True
                    }
                    st.success(f"✅ Usuario **{nu}** creado con contraseña **{np2}**")
                    st.rerun()



COORDS_CONOCIDAS = {
    # Desde PDFs de ofertas
    "EDIFICIO URAPANES":         {"lat": 4.6546, "lng": -74.0604, "dir": "Calle 63 No 20-40"},
    "EDIFICIO ARCADIA":          {"lat": 4.6783, "lng": -74.0487, "dir": "Calle 94 No 23-17"},
    "EDIFICIO RISARALDA":        {"lat": 4.6921, "lng": -74.0557, "dir": "Carrera 12 #91-15"},
    "EDIFICIO BEN HUR":          {"lat": 4.5812, "lng": -74.1512, "dir": "Calle 49 Sur #78-62"},
    "ESTUDIO 84":                {"lat": 4.6774, "lng": -74.0468, "dir": "Transversal 3 #84a-35"},
    "COUNTRY 136":               {"lat": 4.7285, "lng": -74.0437, "dir": "Av. 15 #135-41"},
    # Geocodificación por barrio/sector conocido
    "EDIFICIO CASTILLA":         {"lat": 4.6762, "lng": -74.0541, "dir": "Chapinero, Bogotá"},
    "EDIFICIO SAHARA":           {"lat": 4.6651, "lng": -74.0582, "dir": "Teusaquillo, Bogotá"},
    "PARK 104":                  {"lat": 4.6915, "lng": -74.0498, "dir": "Cra 15 #104, Bogotá"},
    "EDIFICIO FERROL":           {"lat": 4.6589, "lng": -74.0621, "dir": "Chapinero, Bogotá"},
    "EDIFICIO LOS PINOS":        {"lat": 4.6702, "lng": -74.0533, "dir": "Chapinero, Bogotá"},
    "EDIFICIO AVANTI":           {"lat": 4.6558, "lng": -74.0599, "dir": "Teusaquillo, Bogotá"},
    "EDIFICIO EL CERRO":         {"lat": 4.6481, "lng": -74.0641, "dir": "Bogotá"},
    "EDIFICIO ALTOS DEL RETIRO": {"lat": 4.6635, "lng": -74.0527, "dir": "El Retiro, Bogotá"},
    "EDIFICIO CAMILA":           {"lat": 4.6728, "lng": -74.0501, "dir": "Chapinero, Bogotá"},
    "EDIFICIO NOMAD":            {"lat": 4.6741, "lng": -74.0512, "dir": "Chapinero, Bogotá"},
    "EDIFICIO CESANNE":          {"lat": 4.6955, "lng": -74.0503, "dir": "Usaquén, Bogotá"},
    "TORRE DEL PARQUE":          {"lat": 4.6998, "lng": -74.0489, "dir": "Usaquén, Bogotá"},
    "EDIFICIO BARCELONA":        {"lat": 4.6641, "lng": -74.0569, "dir": "Bogotá"},
    "EDIFICIO PLAZA 47":         {"lat": 4.6631, "lng": -74.0579, "dir": "Bogotá"},
    "EDIFICIO HUNZA":            {"lat": 4.6679, "lng": -74.0551, "dir": "Bogotá"},
    "EDIFICIO RITACUBA":         {"lat": 4.6698, "lng": -74.0541, "dir": "Bogotá"},
    "EL PINO":                   {"lat": 4.6611, "lng": -74.0594, "dir": "Bogotá"},
    "TERRACINO 93":              {"lat": 4.6812, "lng": -74.0477, "dir": "Bogotá"},
    "OPORTO CHICO":              {"lat": 4.6799, "lng": -74.0488, "dir": "Bogotá"},
    "EDIFICIO FONTIBON":         {"lat": 4.6544, "lng": -74.1431, "dir": "Fontibón, Bogotá"},
    "EDIFICIO LABRADOR":         {"lat": 4.6621, "lng": -74.0571, "dir": "Bogotá"},
    "EL FONTANAR":               {"lat": 4.6633, "lng": -74.0563, "dir": "Bogotá"},
    "TIARA":                     {"lat": 4.6722, "lng": -74.0519, "dir": "Chapinero, Bogotá"},
    "EDIFICIO LA CANDELARIA":    {"lat": 4.5981, "lng": -74.0762, "dir": "La Candelaria, Bogotá"},
    "EDIFICIO REYES III Y IV":   {"lat": 4.6744, "lng": -74.0508, "dir": "Bogotá"},
    "EDIFICIO TORRE CARRARA":    {"lat": 4.6721, "lng": -74.0522, "dir": "Bogotá"},
    "ARGOS":                     {"lat": 4.6631, "lng": -74.0578, "dir": "Bogotá"},
    "EDIFICIO SAMORE":           {"lat": 4.6618, "lng": -74.0589, "dir": "Bogotá"},
    "SUITES GOLD":               {"lat": 4.6801, "lng": -74.0481, "dir": "Bogotá"},
    "MÁLAGA":                    {"lat": 4.6715, "lng": -74.0528, "dir": "Chapinero, Bogotá"},
    "TORRE 94":                  {"lat": 4.6841, "lng": -74.0462, "dir": "Cra 15 #94, Bogotá"},
    "EDIFICIO TULIPANES":        {"lat": 4.6759, "lng": -74.0499, "dir": "Chapinero, Bogotá"},
    "EDIFICIO ALTO ARAGÓN":      {"lat": 4.6788, "lng": -74.0491, "dir": "Bogotá"},
    "EDIFICIO NEPTUNO":          {"lat": 4.6658, "lng": -74.0561, "dir": "Bogotá"},
    "EDIFICIO LOS ANDES":        {"lat": 4.6621, "lng": -74.0577, "dir": "Bogotá"},
    "PARK 104":                  {"lat": 4.6918, "lng": -74.0493, "dir": "Calle 104, Bogotá"},
    "EDIFICIO ANCHICAYA":        {"lat": 4.6698, "lng": -74.0541, "dir": "Bogotá"},
    "EDIFICIO SANTA ISABEL":     {"lat": 4.6141, "lng": -74.1012, "dir": "Bosa, Bogotá"},
    "EDIFICIO ARBOLEDA PARK":    {"lat": 4.6551, "lng": -74.1421, "dir": "Fontibón, Bogotá"},
    "EDIFICIO CYAN 26":          {"lat": 4.6302, "lng": -74.0831, "dir": "Kennedy, Bogotá"},
    "BULEVAR":                   {"lat": 4.6921, "lng": -74.0501, "dir": "Usaquén, Bogotá"},
    "EDIFICIO ARAUCARIA":        {"lat": 4.6761, "lng": -74.0501, "dir": "Chapinero, Bogotá"},
    "EDIFICIO CALLE 67":         {"lat": 4.6631, "lng": -74.0580, "dir": "Calle 67, Bogotá"},
    "OLIVAR":                    {"lat": 4.6641, "lng": -74.0572, "dir": "Bogotá"},
    "ELITE":                     {"lat": 4.6651, "lng": -74.0563, "dir": "Bogotá"},
    "EDIFICIO CAPIRO":           {"lat": 4.6551, "lng": -74.0651, "dir": "Bogotá"},
    "EDIFICIO LUMINA":           {"lat": 4.6561, "lng": -74.0641, "dir": "Bogotá"},
    "SANTA VIVIANA":             {"lat": 4.6451, "lng": -74.0741, "dir": "Bogotá"},
    "EDIFICIO CALLE 58":         {"lat": 4.6419, "lng": -74.0781, "dir": "Calle 58, Bogotá"},
    "EDIFICIO GUAYACAN":         {"lat": 4.6501, "lng": -74.0701, "dir": "Bogotá"},
    "EDIFICIO CALIFORNIA ANTIGUA":{"lat": 4.6481, "lng": -74.0721, "dir": "Bogotá"},
    "EDIFICIO TRÍPOLI":          {"lat": 4.6471, "lng": -74.0731, "dir": "Bogotá"},
    "EDIFICIO YAKARTA":          {"lat": 4.6461, "lng": -74.0741, "dir": "Bogotá"},
    "EDIFICIO TORRE CHALETS":    {"lat": 4.6441, "lng": -74.0761, "dir": "Bogotá"},
    # Alto 61 (referencia instalación)
    "ALTO 61 (Referencia)":      {"lat": 4.6882, "lng": -74.0427, "dir": "Calle 61 #14-25, Bogotá"},
}


def pg_mapa():
    hdr("🗺️","Mapa de Proyectos","Ubicación de los edificios en Bogotá")
    df = mis_proyectos()

    # Filtros
    c1,c2,c3 = st.columns(3)
    with c1:
        filtro_estado = st.selectbox("Filtrar por estado", ["Todos"]+ESTADOS_LISTA,
            format_func=lambda x: ETAPAS.get(x,{"label":x})["label"] if x!="Todos" else "Todos")
    with c2:
        if st.session_state.user["rol"]=="gerente":
            filtro_com = st.selectbox("Comercial",["Todos"]+sorted(df["comercial"].dropna().unique().tolist()))
        else:
            filtro_com = "Todos"
    with c3:
        mostrar_perdidos = st.checkbox("Mostrar rechazados", value=False)

    # Aplicar filtros
    df_m = df.copy()
    if filtro_estado != "Todos": df_m = df_m[df_m["estado"]==filtro_estado]
    if filtro_com != "Todos": df_m = df_m[df_m["comercial"]==filtro_com]
    if not mostrar_perdidos: df_m = df_m[df_m["estado"]!="perdido"]

    # Colores por estado
    COLOR_ESTADO = {
        "lead":"#3B82F6","cotizado":"#F59E0B","evaluacion_consejo":"#D97706",
        "negociacion":"#F97316","aprobado_espera":"#0EA5E9","perdido":"#EF4444",
        "creacion_contrato":"#10B981","financiacion":"#10B981","obra":"#059669",
        "novedades_obra":"#D97706","entrega":"#059669","mantenimiento":"#6366F1","cerrado":"#059669"
    }
    ICON_ESTADO = {
        "lead":"🔵","cotizado":"🟡","evaluacion_consejo":"🟠","negociacion":"🔥",
        "aprobado_espera":"🔒","perdido":"❌","creacion_contrato":"📝",
        "financiacion":"💰","obra":"🔨","cerrado":"✅"
    }

    # Construir marcadores
    marcadores = []
    sin_dir = []
    for _, r in df_m.iterrows():
        nombre = str(r["nombre"]).strip().upper()
        # Buscar en coords conocidas
        coords = COORDS_CONOCIDAS.get(nombre)
        # Buscar coincidencia parcial si no hay exacta
        if not coords:
            for k,v in COORDS_CONOCIDAS.items():
                if k in nombre or nombre in k:
                    coords = v
                    break
        # Si tiene dirección en el Sheet
        dir_sheet = str(r.get("direccion","") or "").strip()
        if dir_sheet and dir_sheet.lower() not in ["nan",""]:
            dir_display = dir_sheet
        elif coords:
            dir_display = coords.get("dir","Bogotá")
        else:
            dir_display = "Dirección no registrada"
            sin_dir.append(nombre)

        if coords:
            est = str(r.get("estado","lead"))
            tn = int(r.get("totalNum",0) or 0)
            nota = str(r.get("lastNote","") or r.get("notas","") or "")[:80]
            com = str(r.get("comercial","")).split()[0] if r.get("comercial") else "—"
            color = COLOR_ESTADO.get(est,"#94A3B8")
            icon = ICON_ESTADO.get(est,"📍")
            marcadores.append({
                "lat": coords["lat"], "lng": coords["lng"],
                "nombre": nombre, "estado": est,
                "color": color, "icon": icon,
                "dir": dir_display, "valor": tn,
                "comercial": com, "nota": nota,
                "label": ETAPAS.get(est,{"label":est})["label"]
            })

    total_mapa = len(marcadores)
    st.markdown(f'<div style="font-size:12px;color:#94A3B8;margin-bottom:12px">{total_mapa} proyectos en el mapa · {len(sin_dir)} sin ubicación registrada</div>',unsafe_allow_html=True)

    if not marcadores:
        st.info("No hay proyectos con coordenadas para los filtros seleccionados.")
        return

    # Generar HTML del mapa con Leaflet (OpenStreetMap — gratis, sin API key)
    markers_js = ""
    for m in marcadores:
        popup = (f"<div style='font-family:Inter,sans-serif;min-width:180px'>"
                 f"<div style='font-weight:700;font-size:13px;color:#0F172A;margin-bottom:4px'>{m['icon']} {m['nombre']}</div>"
                 f"<div style='font-size:11px;color:#2563EB;margin-bottom:3px'>{m['label']}</div>"
                 f"<div style='font-size:11px;color:#64748B;margin-bottom:2px'>📍 {m['dir']}</div>"
                 f"<div style='font-size:11px;color:#64748B;margin-bottom:2px'>👤 {m['comercial']}</div>"
                 f"{'<div style=&quot;font-size:11px;color:#64748B;margin-bottom:2px&quot;>💰 '+cop(m['valor'])+'</div>' if m['valor'] else ''}"
                 f"{'<div style=&quot;font-size:10.5px;color:#94A3B8;margin-top:4px&quot;>'+m['nota']+'</div>' if m['nota'] else ''}"
                 f"</div>")
        markers_js += f"""
        L.circleMarker([{m['lat']}, {m['lng']}], {{
            radius: 9,
            fillColor: '{m['color']}',
            color: 'white',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.9
        }}).bindPopup(`{popup}`).addTo(map);
        """

    # Referencia Alto 61
    alto61 = COORDS_CONOCIDAS["ALTO 61 (Referencia)"]
    markers_js += f"""
    L.marker([{alto61['lat']}, {alto61['lng']}], {{
        icon: L.divIcon({{
            html: '<div style="background:#0D9488;color:white;font-size:9px;font-weight:700;padding:3px 6px;border-radius:4px;white-space:nowrap;box-shadow:0 2px 6px rgba(0,0,0,.3)">⭐ ALTO 61</div>',
            iconAnchor: [30, 10]
        }})
    }}).addTo(map);
    """

    mapa_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css"/>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<style>
  body{{margin:0;padding:0;font-family:Inter,sans-serif}}
  #map{{height:560px;width:100%;border-radius:12px}}
  .leaflet-popup-content-wrapper{{border-radius:10px;box-shadow:0 4px 16px rgba(0,0,0,.15)}}
  .leaflet-popup-content{{margin:10px 14px}}
  /* Leyenda */
  .leyenda{{background:white;border-radius:10px;padding:10px 14px;box-shadow:0 2px 8px rgba(0,0,0,.12);font-size:11px;line-height:1.9}}
  .leyenda h4{{margin:0 0 6px;font-size:11.5px;font-weight:700;color:#0F172A}}
  .dot{{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:5px;vertical-align:middle}}
</style>
</head>
<body>
<div id="map"></div>
<script>
  var map = L.map('map').setView([4.6722, -74.0538], 12);
  L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
    attribution: '© OpenStreetMap contributors',
    maxZoom: 18
  }}).addTo(map);

  {markers_js}

  // Leyenda
  var legend = L.control({{position: 'bottomright'}});
  legend.onAdd = function(map) {{
    var div = L.DomUtil.create('div', 'leyenda');
    div.innerHTML = '<h4>Estado del proyecto</h4>' +
      '<span class="dot" style="background:#D97706"></span>En evaluación/Consejo<br>' +
      '<span class="dot" style="background:#F59E0B"></span>Contacto frío<br>' +
      '<span class="dot" style="background:#F97316"></span>Negociando<br>' +
      '<span class="dot" style="background:#0EA5E9"></span>Stand-by Vigilancia<br>' +
      '<span class="dot" style="background:#EF4444"></span>Perdido<br>' +
      '<span class="dot" style="background:#059669"></span>Cerrado/Obra';
    return div;
  }};
  legend.addTo(map);
</script>
</body>
</html>"""

    st.components.v1.html(mapa_html, height=580, scrolling=False)

    # Sin dirección
    if sin_dir:
        with st.expander(f"⚠️ {len(sin_dir)} proyectos sin ubicación registrada"):
            st.markdown("Agrega la dirección en **Nueva Cotización** o directamente en el Google Sheet.")
            for n in sin_dir:
                st.markdown(f"- {n}")

    # Tip
    st.markdown(f'<div class="al blue" style="margin-top:10px"><div>💡</div><div>Haz <strong>clic en cualquier punto</strong> del mapa para ver el detalle. Para agregar direcciones que faltan, edítalas en el Sheet o en <strong>Nueva Cotización</strong>.</div></div>',unsafe_allow_html=True)



# ══════════════════════════════════════════
# LEADS WHATSAPP
# ══════════════════════════════════════════

ESTADOS_LEAD = [
    "Nuevo",
    "En contacto",
    "Explicado — sin respuesta",
    "No interesado",
    "Pasó a cotización",
    "Descartado",
]
COLOR_LEAD = {
    "Nuevo":                    "#3B82F6",
    "En contacto":              "#F59E0B",
    "Explicado — sin respuesta":"#94A3B8",
    "No interesado":            "#EF4444",
    "Pasó a cotización":        "#059669",
    "Descartado":               "#DC2626",
}

def get_leads():
    if "leads_db" not in st.session_state:
        st.session_state.leads_db = [
            # Ejemplos iniciales para que no aparezca vacío
            {"id":"L001","fecha_entrada":"2026-06-10","nombre":"Torres Residencias","contacto":"Luis Torres","telefono":"+57 300 123 4567","como_llego":"WhatsApp","asignado":"RAFAEL TORRES","fecha_asignacion":"2026-06-10","estado":"Pasó a cotización","fecha_cotizacion":"2026-06-15","notas":"Edificio de 80 unidades en Chapinero. Muy interesado.","dias_lead":5,"dias_cotizacion":5},
            {"id":"L002","fecha_entrada":"2026-06-12","nombre":"Conjunto Los Arrayanes","contacto":"Ana Gómez","telefono":"+57 315 987 6543","como_llego":"WhatsApp","asignado":"LINA CALLE","fecha_asignacion":"2026-06-13","estado":"En contacto","fecha_cotizacion":"","notas":"Habló con administradora. Quiere reunión presencial.","dias_lead":1,"dias_cotizacion":None},
            {"id":"L003","fecha_entrada":"2026-06-18","nombre":"Ed. Viento del Norte","contacto":"Jhon Reyes","telefono":"+57 311 555 0001","como_llego":"WhatsApp","asignado":"SONIA CASTRO","fecha_asignacion":"2026-06-18","estado":"Explicado — sin respuesta","fecha_cotizacion":"","notas":"Le explicamos el servicio. No ha vuelto a contestar.","dias_lead":0,"dias_cotizacion":None},
            {"id":"L004","fecha_entrada":"2026-06-20","nombre":"Conjunto Prados del Sur","contacto":"María Herrera","telefono":"+57 320 444 7890","como_llego":"WhatsApp","asignado":"","fecha_asignacion":"","estado":"Nuevo","fecha_cotizacion":"","notas":"Llegó por WhatsApp. Pendiente asignar.","dias_lead":None,"dias_cotizacion":None},
        ]
    return st.session_state.leads_db

def pg_leads():
    hdr("📲","Leads WhatsApp","Seguimiento de contactos entrantes → cotización")
    u = st.session_state.user
    es_g = u["rol"] in ["gerente","socio"]
    leads = get_leads()

    # ── KPIs
    total   = len(leads)
    nuevos  = sum(1 for l in leads if l["estado"]=="Nuevo")
    en_ctc  = sum(1 for l in leads if l["estado"]=="En contacto")
    cotiz   = sum(1 for l in leads if l["estado"]=="Pasó a cotización")
    sin_rep = sum(1 for l in leads if l["estado"]=="Explicado — sin respuesta")
    desc    = sum(1 for l in leads if l["estado"] in ["No interesado","Descartado"])
    tasa_c  = round(cotiz/total*100) if total else 0

    # Tiempo promedio lead→cotización
    dias_prom = None
    tiempos   = [l["dias_cotizacion"] for l in leads if l.get("dias_cotizacion") and l["estado"]=="Pasó a cotización"]
    if tiempos: dias_prom = round(sum(tiempos)/len(tiempos),1)

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.markdown(f'<div class="kpi blue"><div class="kpi-lbl">Total leads</div><div class="kpi-val blue">{total}</div><div class="kpi-sub">acumulados</div></div>',unsafe_allow_html=True)
    c2.markdown(f'<div class="kpi" style="border-bottom:2px solid #3B82F6"><div class="kpi-lbl">🆕 Nuevos</div><div class="kpi-val" style="color:#3B82F6">{nuevos}</div><div class="kpi-sub">sin asignar</div></div>',unsafe_allow_html=True)
    c3.markdown(f'<div class="kpi" style="border-bottom:2px solid #F59E0B"><div class="kpi-lbl">En contacto</div><div class="kpi-val amber">{en_ctc}</div><div class="kpi-sub">en proceso</div></div>',unsafe_allow_html=True)
    c4.markdown(f'<div class="kpi" style="border-bottom:2px solid #059669"><div class="kpi-lbl">→ Cotización</div><div class="kpi-val green">{cotiz}</div><div class="kpi-sub">tasa {tasa_c}%</div></div>',unsafe_allow_html=True)
    c5.markdown(f'<div class="kpi" style="border-bottom:2px solid #94A3B8"><div class="kpi-lbl">Sin respuesta</div><div class="kpi-val" style="color:#94A3B8">{sin_rep}</div><div class="kpi-sub">explicado</div></div>',unsafe_allow_html=True)
    c6.markdown(f'<div class="kpi" style="border-bottom:2px solid #D97706"><div class="kpi-lbl">T° lead→cotiz</div><div class="kpi-val amber">{f"{dias_prom}d" if dias_prom else "—"}</div><div class="kpi-sub">promedio días</div></div>',unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)

    # ── Tabs
    tab_lista, tab_nuevo, tab_stats = st.tabs(["📋 Lista de leads","➕ Registrar lead","📊 Estadísticas"])

    # ════════════════════════
    # TAB 1: LISTA
    # ════════════════════════
    with tab_lista:
        # Filtros
        cf1,cf2,cf3 = st.columns(3)
        with cf1:
            f_estado = st.selectbox("Estado",["Todos"]+ESTADOS_LEAD)
        with cf2:
            f_com = st.selectbox("Comercial",["Todos"]+COMS) if es_g else st.selectbox("Comercial",[u.get("comercial","")])
        with cf3:
            f_text = st.text_input("🔍 Buscar",placeholder="Nombre, contacto, teléfono...")

        # Filtrar
        leads_f = leads.copy()
        if f_estado != "Todos":   leads_f = [l for l in leads_f if l["estado"]==f_estado]
        if f_com != "Todos":      leads_f = [l for l in leads_f if l.get("asignado","").upper()==f_com.upper()]
        if f_text.strip():        leads_f = [l for l in leads_f if f_text.lower() in (l.get("nombre","")+l.get("contacto","")+l.get("telefono","")).lower()]

        # Ordenar: nuevos primero, luego por fecha
        orden = {"Nuevo":0,"En contacto":1,"Explicado — sin respuesta":2,"Pasó a cotización":3,"No interesado":4,"Descartado":5}
        leads_f = sorted(leads_f, key=lambda x:(orden.get(x["estado"],9), x.get("fecha_entrada","")))

        if not leads_f:
            st.info("No hay leads con esos filtros.")
        else:
            st.markdown(f'<div style="font-size:12px;color:#94A3B8;margin-bottom:10px">{len(leads_f)} leads</div>',unsafe_allow_html=True)
            for i,lead in enumerate(leads_f):
                est  = lead["estado"]
                col  = COLOR_LEAD.get(est,"#94A3B8")
                asig = lead.get("asignado","") or "Sin asignar"
                dias = lead.get("dias_cotizacion")

                # Encabezado del card
                with st.expander(
                    f"{'🆕' if est=='Nuevo' else '🔥' if est=='En contacto' else '✅' if est=='Pasó a cotización' else '❌' if est in ['No interesado','Descartado'] else '⏸'}"
                    f"  {lead['nombre']}  ·  {est}  ·  {lead.get('fecha_entrada','')[:10]}"
                    , expanded=(est in ["Nuevo","En contacto"])
                ):
                    c1,c2,c3 = st.columns(3)
                    c1.markdown(f"**Contacto:** {lead.get('contacto','—')}")
                    c1.markdown(f"**Tel:** {lead.get('telefono','—')}")
                    c2.markdown(f"**Llegó vía:** {lead.get('como_llego','WhatsApp')}")
                    c2.markdown(f"**Asignado a:** {asig}")
                    c3.markdown(f"**Fecha asignación:** {lead.get('fecha_asignacion','—')[:10] or '—'}")
                    c3.markdown(f"**Pasó a cotización:** {lead.get('fecha_cotizacion','')[:10] or 'Aún no'}")

                    if lead.get("notas"):
                        st.markdown(f'<div class="al blue"><div>📝</div><div>{lead["notas"]}</div></div>',unsafe_allow_html=True)

                    # Tiempos
                    if lead.get("dias_lead") is not None:
                        d_lead = lead["dias_lead"]
                        color_t = "#059669" if d_lead<=2 else "#D97706" if d_lead<=7 else "#EF4444"
                        st.markdown(
                            f'<div style="display:flex;gap:16px;margin:8px 0;font-size:11.5px">' +
                            f'<span>⏱ <strong>Respuesta:</strong> <span style="color:{color_t};font-weight:700">{d_lead} días</span> (entrada → asignación)</span>' +
                            (f'<span>📋 <strong>Lead→cotización:</strong> <span style="color:#059669;font-weight:700">{dias} días</span></span>' if dias else '') +
                            f'</div>',unsafe_allow_html=True)

                    # Acciones
                    if u["rol"] in ["gerente","comercial"]:
                        with st.form(f"upd_lead_{i}_{lead['id']}"):
                            ca,cb,cc = st.columns(3)
                            with ca:
                                nuevo_est = st.selectbox("Cambiar estado",ESTADOS_LEAD,
                                    index=ESTADOS_LEAD.index(est) if est in ESTADOS_LEAD else 0,
                                    key=f"est_s_{i}")
                            with cb:
                                nuevo_asig = st.selectbox("Reasignar a",["—"]+COMS,
                                    index=COMS.index(asig)+1 if asig in COMS else 0,
                                    key=f"asig_s_{i}")
                            with cc:
                                nueva_nota = st.text_input("Agregar nota",placeholder="Ej: Llamó y pidió cotización",key=f"nota_s_{i}")
                            if st.form_submit_button("💾 Actualizar",use_container_width=True):
                                # Encontrar el lead en la BD original
                                for l in st.session_state.leads_db:
                                    if l["id"]==lead["id"]:
                                        l["estado"] = nuevo_est
                                        if nuevo_asig != "—":
                                            if not l.get("asignado") or l["asignado"]=="":
                                                l["fecha_asignacion"] = datetime.now().strftime("%Y-%m-%d")
                                                try:
                                                    fe = datetime.strptime(l["fecha_entrada"],"%Y-%m-%d")
                                                    l["dias_lead"] = (datetime.now()-fe).days
                                                except: l["dias_lead"]=0
                                            l["asignado"] = nuevo_asig
                                        if nuevo_est == "Pasó a cotización" and not l.get("fecha_cotizacion"):
                                            l["fecha_cotizacion"] = datetime.now().strftime("%Y-%m-%d")
                                            try:
                                                fa = datetime.strptime(l.get("fecha_asignacion",l["fecha_entrada"]),"%Y-%m-%d")
                                                l["dias_cotizacion"] = (datetime.now()-fa).days
                                            except: l["dias_cotizacion"]=0
                                        if nueva_nota.strip():
                                            l["notas"] = (l.get("notas","") + f" | {datetime.now().strftime('%d %b')}: {nueva_nota}").strip(" | ")
                                        break
                                st.success("✅ Lead actualizado"); st.rerun()

    # ════════════════════════
    # TAB 2: REGISTRAR NUEVO
    # ════════════════════════
    with tab_nuevo:
        if u["rol"] == "socio":
            st.info("Los socios tienen acceso de solo visualización.")
        else:
            st.markdown("**Registrar nuevo lead de WhatsApp**")
            with st.form("nuevo_lead_form"):
                c1,c2 = st.columns(2)
                with c1:
                    nl_nombre  = st.text_input("Nombre del edificio / conjunto *",placeholder="Ej: Conjunto Prados del Norte")
                    nl_ctc     = st.text_input("Nombre del contacto *",placeholder="Administrador, propietario...")
                    nl_tel     = st.text_input("Teléfono / WhatsApp *",placeholder="+57 300 000 0000")
                    nl_como    = st.selectbox("¿Cómo llegó?",["WhatsApp","Referido","Instagram","Facebook","Web","Llamada directa","Otro"])
                with c2:
                    nl_fecha   = st.date_input("Fecha de entrada",value=datetime.now().date())
                    nl_asig    = st.selectbox("Asignar a comercial",["Sin asignar"]+COMS)
                    nl_notas   = st.text_area("Notas iniciales",height=100,placeholder="Qué dijo, cuántas unidades, ubicación, necesidad principal...")
                    nl_est     = st.selectbox("Estado inicial",["Nuevo","En contacto"])

                if st.form_submit_button("📲 Registrar lead",use_container_width=True):
                    if not nl_nombre.strip() or not nl_ctc.strip() or not nl_tel.strip():
                        st.error("Nombre del edificio, contacto y teléfono son obligatorios")
                    else:
                        nuevo_id = f"L{len(st.session_state.leads_db)+1:03d}"
                        fecha_str = nl_fecha.strftime("%Y-%m-%d")
                        asig_final = "" if nl_asig=="Sin asignar" else nl_asig
                        dias_l = (datetime.now().date()-nl_fecha).days if asig_final else None
                        st.session_state.leads_db.append({
                            "id": nuevo_id,
                            "fecha_entrada":   fecha_str,
                            "nombre":          nl_nombre.strip(),
                            "contacto":        nl_ctc.strip(),
                            "telefono":        nl_tel.strip(),
                            "como_llego":      nl_como,
                            "asignado":        asig_final,
                            "fecha_asignacion":datetime.now().strftime("%Y-%m-%d") if asig_final else "",
                            "estado":          nl_est,
                            "fecha_cotizacion":"",
                            "notas":           nl_notas.strip(),
                            "dias_lead":       dias_l,
                            "dias_cotizacion": None,
                        })
                        st.success(f"✅ Lead **{nl_nombre}** registrado — ID {nuevo_id}")
                        if asig_final:
                            st.info(f"📲 Asignado a {asig_final}")
                        st.rerun()

    # ════════════════════════
    # TAB 3: ESTADÍSTICAS
    # ════════════════════════
    with tab_stats:
        st.markdown("#### 📊 Rendimiento por comercial")
        if not leads:
            st.info("Sin datos aún."); return

        # Tabla por comercial
        stats_com = {}
        for l in leads:
            com = l.get("asignado","") or "Sin asignar"
            if com not in stats_com:
                stats_com[com] = {"total":0,"cotizados":0,"sin_resp":0,"descartados":0,"dias_lead":[],"dias_cotiz":[]}
            s = stats_com[com]
            s["total"] += 1
            if l["estado"]=="Pasó a cotización":
                s["cotizados"] += 1
                if l.get("dias_cotizacion"): s["dias_cotiz"].append(l["dias_cotizacion"])
            elif l["estado"]=="Explicado — sin respuesta": s["sin_resp"] += 1
            elif l["estado"] in ["No interesado","Descartado"]: s["descartados"] += 1
            if l.get("dias_lead") is not None: s["dias_lead"].append(l["dias_lead"])

        rows = []
        for com, s in sorted(stats_com.items()):
            rows.append({
                "Comercial":         com.split()[0] if com!="Sin asignar" else "⚠️ Sin asignar",
                "Leads asignados":   s["total"],
                "→ Cotización":      s["cotizados"],
                "Tasa conversión":   f"{round(s['cotizados']/s['total']*100)}%" if s["total"] else "—",
                "Sin respuesta":     s["sin_resp"],
                "T° asignación (d)": f"{round(sum(s['dias_lead'])/len(s['dias_lead']),1)}" if s["dias_lead"] else "—",
                "T° lead→cotiz (d)": f"{round(sum(s['dias_cotiz'])/len(s['dias_cotiz']),1)}" if s["dias_cotiz"] else "—",
            })

        import pandas as pd
        df_s = pd.DataFrame(rows)
        st.dataframe(df_s, use_container_width=True, hide_index=True)

        # Gráfica de barras — leads por estado y comercial
        st.markdown("<br>",unsafe_allow_html=True)
        if len(leads)>0:
            df_leads = pd.DataFrame(leads)
            if "estado" in df_leads.columns and "asignado" in df_leads.columns:
                df_grupo = df_leads.groupby(["asignado","estado"]).size().reset_index(name="n")
                df_grupo["Com"] = df_grupo["asignado"].str.split().str[0]
                fig_l = px.bar(df_grupo, x="Com", y="n", color="estado",
                    title="Leads por comercial y estado",
                    color_discrete_map=COLOR_LEAD,
                    labels={"n":"","Com":"","estado":"Estado"},
                    barmode="stack")
                fig_l.update_layout(paper_bgcolor="white",plot_bgcolor="white",
                    font_family="Inter",title_font_family="Space Grotesk",
                    margin=dict(t=40,b=6,l=0,r=0),
                    legend=dict(orientation="h",yanchor="bottom",y=1.02))
                fig_l.update_traces(marker_line_width=0)
                st.plotly_chart(fig_l, use_container_width=True)

        # Alertas
        sin_asig = [l for l in leads if not l.get("asignado") and l["estado"]=="Nuevo"]
        sin_resp_7 = [l for l in leads if l["estado"]=="Explicado — sin respuesta"
                      and l.get("dias_lead",0) is not None and (l.get("dias_lead",0) or 0)>7]
        if sin_asig:
            st.markdown(f'<div class="al red"><div>🚨</div><div><strong>{len(sin_asig)} leads SIN asignar:</strong> {", ".join(l["nombre"] for l in sin_asig)}</div></div>',unsafe_allow_html=True)
        if sin_resp_7:
            st.markdown(f'<div class="al amber"><div>⏰</div><div><strong>{len(sin_resp_7)} leads sin respuesta hace +7 días.</strong> Considera hacer un último intento o descartar.</div></div>',unsafe_allow_html=True)


# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════


if not st.session_state.logged_in:
    pg_login()
else:
    sidebar()
    pg=st.session_state.get("page","Dashboard")
    {
        "Dashboard":pg_dashboard,"Novedades":pg_novedades,
        "Proyectos":pg_proyectos,"Actualizar Estado":pg_actualizar,
        "Nueva Cotización":pg_nueva_cotizacion,"Correos IA":pg_correos,
        "Asistente IA":pg_asistente,"Encuesta Prospecto":pg_encuesta,
        "Calendario":pg_calendario,"Configuración":pg_configuracion,
        "Informe Semanal":pg_informe_semanal,"Pagos y Finanzas":pg_pagos,
        "Auditoría":pg_auditoria,"Pipeline":pg_pipeline,"Usuarios":pg_usuarios,"Mapa de Proyectos":pg_mapa,"Leads WhatsApp":pg_leads,
    }.get(pg,pg_dashboard)()
