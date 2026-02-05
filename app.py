import streamlit as st
import requests
import json
from datetime import datetime, timezone

# --- 1. CONFIGURAÇÃO DA PÁGINA (Sempre o primeiro comando) ---
st.set_page_config(page_title="Radar Craft Albion", layout="wide")

# --- 2. SISTEMA DE ACESSO ---
def verificar_acesso():
    if "logado" not in st.session_state:
        st.session_state["logado"] = False

    if st.session_state["logado"]:
        return

    st.title("🔐 Acesso Restrito")
    st.write("Digite sua chave para acessar o Radar Craft")

    with st.form("login_form"):
        chave = st.text_input("Chave de acesso", type="password")
        submitted = st.form_submit_button("Entrar")

    if submitted:
        try:
            with open("keys.json", "r") as f:
                chaves = json.load(f)
            chave = chave.strip()
            if chave in chaves and chaves[chave]["ativa"]:
                st.session_state["logado"] = True
                st.success("✅ Acesso liberado")
                st.rerun()
            else:
                st.error("❌ Chave inválida ou desativada")
        except Exception as e:
            st.error(f"Erro ao validar a chave: {e}")
    st.stop()

verificar_acesso()

# --- 3. CSS CUSTOMIZADO (Design e Correção de Cores) ---
st.markdown("""
<style>
/* Reset e Fundo */
header { background: transparent !important; }
.stApp > header { display: none; }
.stApp { background: radial-gradient(circle at top, #0f172a, #020617); color: #e5e7eb; }
.block-container { background-color: rgba(15, 23, 42, 0.94); padding: 2.5rem; border-radius: 22px; }

/* Correção de Inputs (Number Input e Selectbox) */
input, div[data-baseweb="select"] > div, div[data-baseweb="input"] {
    background-color: #1e293b !important;
    color: #ffffff !important;
    border: 1px solid #334155 !important;
}
input { -webkit-text-fill-color: #ffffff !important; opacity: 1 !important; }
div[data-testid="stNumberInput"] button { background-color: #334155 !important; color: white !important; }

/* Dropdown Menu */
div[data-baseweb="popover"] ul { background-color: #1e293b !important; border: 1px solid #334155 !important; }
div[data-baseweb="popover"] li { color: #ffffff !important; }
div[data-baseweb="popover"] li:hover { background-color: #2563eb !important; }

/* Cards de Resultado Final */
.craft-card {
    background-color: rgba(30, 41, 59, 0.5);
    border-left: 5px solid #8b5cf6;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 20px;
}
.item-name { color: #ffffff; font-size: 1.3rem; font-weight: bold; margin-bottom: 10px; }
.stat-line { margin: 5px 0; display: flex; align-items: center; gap: 8px; font-size: 1rem; }
.perc-lucro { 
    background-color: #065f46; color: #34d399; padding: 2px 8px; 
    border-radius: 6px; font-weight: bold; font-size: 0.85rem; margin-left: 10px;
}
.cost-list { list-style: none; padding-left: 15px; margin-top: 8px; color: #cbd5e1; }
.cost-list li { margin-bottom: 4px; font-size: 0.95rem; }
.cost-list li::before { content: "■ "; color: #8b5cf6; }

/* Botão Escanear */
.stButton > button { 
    background: linear-gradient(135deg, #2563eb, #1d4ed8); 
    color: white !important; border-radius: 12px; width: 100%; font-weight: bold; height: 3.5rem; border: none;
}
</style>
""", unsafe_allow_html=True)

# --- 4. CONFIGURAÇÕES DA API E BANCO DE DADOS ---
API_URL = "https://west.albion-online-data.com/api/v2/stats/prices/"
CIDADES = ["Martlock", "Thetford", "FortSterling", "Lymhurst", "Bridgewatch", "Brecilien", "Caerleon", "Black Market"]
RECURSO_MAP = {"Tecido Fino": "CLOTH", "Couro Trabalhado": "LEATHER", "Barra de Aço": "METALBAR", "Tábuas de Pinho": "PLANKS"}
BONUS_CIDADE = {
    "Lymhurst": ["BOW", "ARCANE", "LEATHER"],
    "Bridgewatch": ["CROSSBOW", "DAGGER", "PLATE"],
    "Martlock": ["AXE", "SHOES", "STAFF"],
    "Thetford": ["MACE", "NATURE", "FIRE"],
    "Fort Sterling": ["HAMMER", "SPEAR", "HOLY"],
    "Caerleon": ["KNUCKLES", "SHAPESHIFTER"],
    "Brecilien": ["CAPE", "BAG"]
}

# (O ITENS_DB continua igual ao que você já tem, omitido aqui para o código não ficar gigante, mas deve estar aqui)
ITENS_DB = {
    # Cole aqui sua lista completa de itens (Armaduras, Armas, etc)
    "TOMO DE FEITIÇOS": ["OFF_BOOK", "Tecido Fino", 4, "Couro Trabalhado", 4, None, 0],
    "ARMADURA JUDICANTE": ["ARMOR_PLATE_KEEPER", "Barra de Aço", 16, None, 0, "ARTEFACT_ARMOR_PLATE_KEEPER", 1],
    "LUME CRIPTICO": ["OFF_LAMP_UNDEAD", "Tábuas de Pinho", 4, "Tecido Fino", 4, "ARTEFACT_OFF_LAMP_UNDEAD", 1],
    # ... adicione todos os outros itens aqui ...
}

FILTROS = {
    "armadura_placa": lambda k, v: "ARMOR_PLATE" in v[0],
    "armadura_couro": lambda k, v: "ARMOR_LEATHER" in v[0],
    "armadura_pano": lambda k, v: "ARMOR_CLOTH" in v[0],
    "botas_placa": lambda k, v: "SHOES_PLATE" in v[0],
    "botas_couro": lambda k, v: "SHOES_LEATHER" in v[0],
    "botas_pano": lambda k, v: "SHOES_CLOTH" in v[0],
    "capacete_placa": lambda k, v: "HEAD_PLATE" in v[0],
    "capacete_couro": lambda k, v: "HEAD_LEATHER" in v[0],
    "capacete_pano": lambda k, v: "HEAD_CLOTH" in v[0],
    "armas": lambda k, v: v[0].startswith(("MAIN_", "2H_")),
    "secundarias": lambda k, v: v[0].startswith("OFF_"),
}

# --- 5. LÓGICA DE CÁLCULO ---
def calcular_horas(data_iso):
    if not data_iso or data_iso == "0001-01-01T00:00:00":
        return "N/A"
    try:
        data_api = datetime.fromisoformat(data_iso.replace("Z", "+00:00"))
        agora = datetime.now(timezone.utc)
        diff = (agora - data_api).total_seconds() / 3600
        return f"{int(diff)}h" if diff < 48 else "Antigo"
    except:
        return "N/A"

def id_item(tier, base, enc):
    return f"T{tier}_{base}@{enc}" if enc > 0 else f"T{tier}_{base}"

def ids_recurso_variantes(tier, nome, enc):
    base = f"T{tier}_{RECURSO_MAP[nome]}"
    return [f"{base}@{enc}", f"{base}_LEVEL{enc}@{enc}"] if enc > 0 else [base]

def identificar_cidade_bonus(item_base):
    for cidade, chaves in BONUS_CIDADE.items():
        if any(chave in item_base for chave in chaves):
            return cidade
    return "Caerleon (Geral)"

# --- 6. INTERFACE SIDEBAR ---
st.title("⚔️ Radar Craft — Royal Cities + Black Market")
with st.sidebar:
    categoria = st.selectbox("Categoria", list(FILTROS.keys()))
    tier = st.number_input("Tier", 4, 8, 4)
    encanto = st.number_input("Encanto", 0, 4, 0)
    quantidade = st.number_input("Quantidade", 1, 999, 1)
    btn = st.button("🚀 ESCANEAR")

# --- 7. EXECUÇÃO DO SCAN ---
if btn:
    filtro = FILTROS[categoria]
    itens = {k: v for k, v in ITENS_DB.items() if filtro(k, v)}

    if not itens:
        st.error("Nenhum item encontrado.")
        st.stop()

    ids = set()
    for d in itens.values():
        ids.add(id_item(tier, d[0], encanto))
        for r in ids_recurso_variantes(tier, d[1], encanto): ids.add(r)
        if d[3]:
            for r in ids_recurso_variantes(tier, d[3], encanto): ids.add(r)
        if d[5]: ids.add(f"T{tier}_{d[5]}")

    response = requests.get(f"{API_URL}{','.join(ids)}?locations={','.join(CIDADES)}", timeout=20)
    data = response.json()

    precos_itens = {}
    precos_recursos = {}

    for p in data:
        pid = p["item_id"]
        if p["city"] == "Black Market":
            price = p["buy_price_max"]
            if price > 0:
                horas = calcular_horas(p["buy_price_max_date"])
                if pid not in precos_itens or price > precos_itens[pid]["price"]:
                    precos_itens[pid] = {"price": price, "horas": horas}
        else:
            price = p["sell_price_min"]
            if price > 0:
                horas = calcular_horas(p["sell_price_min_date"])
                if pid not in precos_recursos or price < precos_recursos[pid]["price"]:
                    precos_recursos[pid] = {"price": price, "city": p["city"], "horas": horas}

    resultados = []
    for nome, d in itens.items():
        item_id = id_item(tier, d[0], encanto)
        if item_id not in precos_itens: continue

        custo = 0
        detalhes = []
        falta_dado = False

        for recurso, qtd in [(d[1], d[2]), (d[3], d[4])]:
            if not recurso: continue
            for rid in ids_recurso_variantes(tier, recurso, encanto):
                if rid in precos_recursos:
                    info = precos_recursos[rid]
                    custo += info["price"] * (qtd * quantidade)
                    detalhes.append(f"{qtd * quantidade}x {recurso} — {info['price']:,} ({info['city']} {info['horas']})")
                    break
            else:
                falta_dado = True; break
        
        if falta_dado: continue

        if d[5]:
            art = f"T{tier}_{d[5]}"
            if art in precos_recursos:
                p_art = precos_recursos[art]["price"]
                custo += p_art * (d[6] * quantidade)
                detalhes.append(f"{d[6] * quantidade}x Artefato — {p_art:,} ({precos_recursos[art]['city']} {precos_recursos[art]['horas']})")
            else: continue

        # Cálculo final
        custo_final = custo * 0.752 # Bônus de retorno de recurso (ex: 24.8%)
        venda_total = precos_itens[item_id]["price"] * quantidade
        lucro_liquido = (venda_total * 0.935) - custo_final # Taxa BM

        if lucro_liquido > 0:
            resultados.append((nome, int(lucro_liquido), int(venda_total), int(custo_final), detalhes))

    resultados.sort(key=lambda x: x[1], reverse=True)

    # --- 8. EXIBIÇÃO DOS CARDS ---
    if not resultados:
        st.error("❌ Nenhum lucro encontrado.")
    else:
        for nome, lucro, venda, custo, detalhes in resultados[:20]:
            # Cálculo da Porcentagem de Lucro (ROI)
            porcentagem = (lucro / custo) * 100 if custo > 0 else 0
            
            # Identifica a cidade bônus (usando sua função)
            cidade_foco = identificar_cidade_bonus(nome)

            # Montagem do Card em HTML
            detalhes_html = "".join([f"<li>{d}</li>" for d in detalhes])
            
            st.markdown(f"""
                <div class="craft-card">
                    <div class="item-name">💎 {nome.upper()}</div>
                    <div class="stat-line">💰 <b>Lucro:</b> {lucro:,} <span class="perc-lucro">+{porcentagem:.1f}%</span></div>
                    <div class="stat-line">🛒 <b>Venda:</b> {venda:,} (Black Market)</div>
                    <div class="stat-line">🏗️ <b>Local:</b> {cidade_foco}</div>
                    <div class="stat-line">📦 <b>Custos:</b></div>
                    <ul class="cost-list">
                        {detalhes_html}
                    </ul>
                </div>
            """, unsafe_allow_html=True)