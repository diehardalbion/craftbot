import streamlit as st
import requests
import json
from datetime import datetime, timezone

# ================= CONFIGURAÇÃO DA PÁGINA =================
st.set_page_config("Radar Craft Albion", layout="wide", page_icon="⚔️")

# ================= CUSTOM CSS =================
st.markdown("""
<style>
    header {visibility: hidden;}
    .main .block-container { padding-top: 0rem; padding-bottom: 0rem; }
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.8)), 
                    url("https://i.imgur.com/kVAiMjD.png");
        background-size: cover;
        background-attachment: fixed;
    }
    .item-card-custom { 
        background-color: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px);
        border-radius: 12px; 
        padding: 20px; 
        margin-bottom: 20px; 
        border: 1px solid rgba(46, 204, 113, 0.2);
        border-left: 8px solid #2ecc71;
        color: white !important;
    }
    .stButton>button {
        width: 100%;
        background-color: #2ecc71 !important;
        color: white !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ================= SISTEMA DE LOGIN =================
def verificar_chave(chave_usuario):
    try:
        with open("keys.json", "r") as f:
            keys_db = json.load(f)
        if chave_usuario in keys_db:
            dados = keys_db[chave_usuario]
            if not dados["ativa"]: return False, "Chave desativada."
            if dados["expira"] != "null":
                data_expira = datetime.strptime(dados["expira"], "%Y-%m-%d").date()
                if datetime.now().date() > data_expira: return False, "Chave expirou."
            return True, dados["cliente"]
        return False, "Chave inválida."
    except: return False, "Erro ao acessar base de chaves."

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🛡️ Radar Craft - Acesso Restrito")
    key_input = st.text_input("Insira sua Chave:", type="password")
    if st.button("LIBERAR ACESSO"):
        sucesso, mensagem = verificar_chave(key_input)
        if sucesso:
            st.session_state.autenticado = True
            st.rerun()
        else: st.error(mensagem)
    st.stop()

# ================= DADOS E MAPAS =================
API_URL = "https://west.albion-online-data.com/api/v2/stats/prices/"
CIDADES = ["Martlock", "Thetford", "FortSterling", "Lymhurst", "Bridgewatch", "Brecilien", "Caerleon", "Black Market"]
RECURSO_MAP = {"Tecido": "CLOTH", "Couro": "LEATHER", "Metal": "METALBAR", "Tabua": "PLANKS"}

BONUS_CIDADE = {
    "Martlock": ["AXE", "QUARTERSTAFF", "FROSTSTAFF", "SHOES_PLATE", "OFF_"],
    "Bridgewatch": ["CROSSBOW", "DAGGER", "CURSEDSTAFF", "ARMOR_PLATE", "SHOES_CLOTH"],
    "Lymhurst": ["SWORD", "BOW", "ARCANESTAFF", "HEAD_LEATHER", "SHOES_LEATHER"],
    "Fort Sterling": ["HAMMER", "SPEAR", "HOLYSTAFF", "HEAD_PLATE", "ARMOR_CLOTH"],
    "Thetford": ["MACE", "NATURESTAFF", "FIRESTAFF", "ARMOR_LEATHER", "HEAD_CLOTH"],
}

ITENS_DB = {
    # ARMADURAS PANO
    "Robe do Erudito": ["ARMOR_CLOTH_SET1", "Tecido", 16, None, 0, None, 0],
    "Robe de Clérigo": ["ARMOR_CLOTH_SET2", "Tecido", 16, None, 0, None, 0],
    "Robe de Mago": ["ARMOR_CLOTH_SET3", "Tecido", 16, None, 0, None, 0],
    "Capote de Erudito": ["HEAD_CLOTH_SET1", "Tecido", 8, None, 0, None, 0],
    "Capote de Clérigo": ["HEAD_CLOTH_SET2", "Tecido", 8, None, 0, None, 0],
    "Capote de Mago": ["HEAD_CLOTH_SET3", "Tecido", 8, None, 0, None, 0],
    "Sandálias de Erudito": ["SHOES_CLOTH_SET1", "Tecido", 8, None, 0, None, 0],
    "Sandálias de Clérigo": ["SHOES_CLOTH_SET2", "Tecido", 8, None, 0, None, 0],
    "Sandálias de Mago": ["SHOES_CLOTH_SET3", "Tecido", 8, None, 0, None, 0],
    
    # ARMADURAS COURO
    "Casaco Mercenário": ["ARMOR_LEATHER_SET1", "Couro", 16, None, 0, None, 0],
    "Casaco de Caçador": ["ARMOR_LEATHER_SET2", "Couro", 16, None, 0, None, 0],
    "Casaco de Assassino": ["ARMOR_LEATHER_SET3", "Couro", 16, None, 0, None, 0],
    "Capuz de Mercenário": ["HEAD_LEATHER_SET1", "Couro", 8, None, 0, None, 0],
    "Capuz de Caçador": ["HEAD_LEATHER_SET2", "Couro", 8, None, 0, None, 0],
    "Capuz de Assassino": ["HEAD_LEATHER_SET3", "Couro", 8, None, 0, None, 0],
    "Sapatos de Mercenário": ["SHOES_LEATHER_SET1", "Couro", 8, None, 0, None, 0],
    "Sapatos de Caçador": ["SHOES_LEATHER_SET2", "Couro", 8, None, 0, None, 0],
    "Sapatos de Assassino": ["SHOES_LEATHER_SET3", "Couro", 8, None, 0, None, 0],

    # ARMADURAS PLACA
    "ARMADURA DE SOLDADO": ["ARMOR_PLATE_SET1", "Metal", 16, None, 0, None, 0],
    "ARMADURA DE CAVALEIRO": ["ARMOR_PLATE_SET2", "Metal", 16, None, 0, None, 0],
    "ARMADURA DE GUARDIÃO": ["ARMOR_PLATE_SET3", "Metal", 16, None, 0, None, 0],
    "ELMO DE SOLDADO": ["HEAD_PLATE_SET1", "Metal", 8, None, 0, None, 0],
    "ELMO DE CAVALEIRO": ["HEAD_PLATE_SET2", "Metal", 8, None, 0, None, 0],
    "ELMO DE GUARDIÃO": ["HEAD_PLATE_SET3", "Metal", 8, None, 0, None, 0],
    "BOTAS DE SOLDADO": ["SHOES_PLATE_SET1", "Metal", 8, None, 0, None, 0],
    "BOTAS DE CAVALEIRO": ["SHOES_PLATE_SET2", "Metal", 8, None, 0, None, 0],
    "BOTAS DE GUARDIÃO": ["SHOES_PLATE_SET3", "Metal", 8, None, 0, None, 0],

    # ESPADAS
    "ESPADA LARGA": ["MAIN_SWORD", "Metal", 16, "Couro", 8, None, 0],
    "MONTANTE": ["2H_CLAYMORE", "Metal", 20, "Couro", 12, None, 0],
    "ESPADAS DUPLAS": ["2H_DUALSWORD", "Metal", 20, "Couro", 12, None, 0],
    
    # BESTAS E LANÇAS
    "BESTA": ["2H_CROSSBOW", "Tabua", 20, "Metal", 12, None, 0],
    "LANÇA": ["MAIN_SPEAR", "Tabua", 16, "Metal", 8, None, 0],
    "PIQUE": ["2H_SPEAR", "Tabua", 20, "Metal", 12, None, 0],
}

# ================= FILTROS =================
FILTROS = {
    "Pano (Robe/Capote)": lambda k, v: "CLOTH" in v[0],
    "Couro (Casaco/Capuz)": lambda k, v: "LEATHER" in v[0],
    "Placa (Armor/Elmo)": lambda k, v: "PLATE" in v[0],
    "Armas (Espada/Besta/etc)": lambda k, v: v[0].startswith(("MAIN_", "2H_")),
}

# ================= AUXILIARES =================
def id_item(tier, base, enc):
    return f"T{tier}_{base}@{enc}" if enc > 0 else f"T{tier}_{base}"

def id_recurso(tier, nome, enc):
    base = f"T{tier}_{RECURSO_MAP[nome]}"
    return f"{base}_LEVEL{enc}@{enc}" if enc > 0 else base

# ================= SIDEBAR =================
with st.sidebar:
    categoria = st.selectbox("Categoria", list(FILTROS.keys()))
    tier = st.number_input("Tier", 4, 8, 6)
    encanto = st.number_input("Encanto", 0, 4, 0)
    quantidade = st.number_input("Quantidade", 1, 999, 1)
    btn = st.button("🚀 ESCANEAR")

# ================= LÓGICA PRINCIPAL =================
if btn:
    filtro = FILTROS[categoria]
    itens = {k: v for k, v in ITENS_DB.items() if filtro(k, v)}
    
    ids_busca = []
    for d in itens.values():
        ids_busca.append(id_item(tier, d[0], encanto))
        ids_busca.append(id_recurso(tier, d[1], encanto))
        if d[3]: ids_busca.append(id_recurso(tier, d[3], encanto))

    try:
        url = f"{API_URL}{','.join(set(ids_busca))}?locations={','.join(CIDADES)}"
        data = requests.get(url).json()
    except:
        st.error("Erro na API")
        st.stop()

    precos = {}
    for p in data:
        pid, city = p["item_id"], p["city"]
        if pid not in precos: precos[pid] = {}
        if city == "Black Market":
            precos[pid][city] = {"p": p["buy_price_max"], "h": p["buy_price_max_date"]}
        else:
            precos[pid][city] = {"p": p["sell_price_min"], "h": p["sell_price_min_date"]}

    resultados = []
    for nome, d in itens.items():
        iid = id_item(tier, d[0], encanto)
        if iid not in precos or "Black Market" not in precos[iid]: continue
        
        venda_bm = precos[iid]["Black Market"]["p"]
        if venda_bm == 0: continue

        # Cálculo de Custo
        total_mat = 0
        valid = True
        desc_mats = []
        
        for mat_nome, mat_qtd in [(d[1], d[2]), (d[3], d[4])]:
            if not mat_nome: continue
            rid = id_recurso(tier, mat_nome, encanto)
            
            # Pega o menor preço disponível entre as cidades
            if rid in precos:
                opcoes = {c: v["p"] for c, v in precos[rid].items() if v["p"] > 0 and c != "Black Market"}
                if opcoes:
                    best_city = min(opcoes, key=opcoes.get)
                    p_unit = opcoes[best_city]
                    total_mat += p_unit * mat_qtd
                    desc_mats.append(f"{mat_qtd}x {mat_nome}: {p_unit:,} ({best_city})")
                else: valid = False
            else: valid = False

        if not valid: continue

        investimento = int(total_mat * 0.752) # Aplicando RRR de 24.8%
        lucro = int((venda_bm * 0.935) - investimento)
        
        if lucro > 0:
            resultados.append((nome, lucro, venda_bm, investimento, desc_mats))

    resultados.sort(key=lambda x: x[1], reverse=True)

    if not resultados:
        st.warning("Sem itens lucrativos agora.")
    else:
        for r in resultados:
            st.markdown(f"""
            <div class="item-card-custom">
                <h3 style='margin:0; color:#2ecc71;'>{r[0]} [T{tier}.{encanto}]</h3>
                <b>💰 Lucro: {r[1]:,}</b> | Invest: {r[3]:,} | Venda BM: {r[2]:,}<br>
                <small>📦 { " | ".join(r[4]) }</small>
            </div>
            """, unsafe_allow_html=True)
