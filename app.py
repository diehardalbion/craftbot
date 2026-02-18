import streamlit as st
import requests
import json
from datetime import datetime, timezone, timedelta

# ================= CONFIGURAÇÃO DA PÁGINA =================
st.set_page_config("Radar Craft Albion - Clareza Total", layout="wide", page_icon="🛡️")

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
    [data-testid="stSidebar"] { background-color: rgba(15, 17, 23, 0.95) !important; border-right: 1px solid #3e4149; }
    h1, h2, h3, label, .stMarkdown { color: #ffffff !important; font-family: 'Segoe UI', sans-serif; }
    .item-card-custom { 
        background-color: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px);
        border-radius: 12px; 
        padding: 20px; 
        margin-bottom: 20px; 
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        color: white !important;
    }
    .city-row {
        display: flex;
        justify-content: space-between;
        padding: 8px 12px;
        border-radius: 6px;
        margin: 5px 0;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.05);
    }
    .city-name { font-weight: bold; font-size: 0.95rem; }
    .city-profit { font-weight: bold; font-size: 0.95rem; }
    .stButton>button {
        width: 100%;
        background-color: #2ecc71 !important;
        color: white !important;
        font-weight: bold;
        border: none;
        padding: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ================= LOGIN =================
def verificar_chave(chave_usuario):
    try:
        with open("keys.json", "r") as f: keys_db = json.load(f)
        if chave_usuario in keys_db:
            dados = keys_db[chave_usuario]
            if not dados["ativa"]: return False, "Chave desativada."
            return True, dados["cliente"]
        return False, "Chave inválida."
    except: return False, "Erro no servidor de chaves."

if "autenticado" not in st.session_state: st.session_state.autenticado = False
if not st.session_state.autenticado:
    st.title("🛡️ Radar Craft - Acesso Restrito")
    key_input = st.text_input("Insira sua Chave:", type="password")
    if st.button("LIBERAR ACESSO"):
        sucesso, mensagem = verificar_chave(key_input)
        if sucesso:
            st.session_state.autenticado = True
            st.session_state.cliente = mensagem
            st.rerun()
        else: st.error(mensagem)
    st.stop()

# ================= CONFIG =================
API_URL = "https://west.albion-online-data.com/api/v2/stats/prices/"
HISTORY_URL = "https://west.albion-online-data.com/api/v2/stats/history/"
CIDADES_VENDA = ["Thetford", "Martlock", "FortSterling", "Lymhurst", "Bridgewatch", "Caerleon", "Brecilien", "Black Market"]
RECURSO_MAP = {"Tecido Fino": "CLOTH", "Couro Trabalhado": "LEATHER", "Barra de Aço": "METALBAR", "Tábuas de Pinho": "PLANKS"}

NOMES_RECURSOS_TIER = {
    "Barra de Aço": {4: "Barra de Aço", 5: "Barra de Titânio", 6: "Barra de Runita", 7: "Barra de Meteorito", 8: "Barra de Adamante"},
    "Tábuas de Pinho": {4: "Tábuas de Pinho", 5: "Tábuas de Cedro", 6: "Tábuas de Carvalho-Sangue", 7: "Tábuas de Freixo", 8: "Tábuas de Pau-branco"},
    "Couro Trabalhado": {4: "Couro Trabalhado", 5: "Couro Curtido", 6: "Couro Endurecido", 7: "Couro Reforçado", 8: "Couro Fortificado"},
    "Tecido Fino": {4: "Tecido Fino", 5: "Tecido Ornado", 6: "Tecido Rico", 7: "Tecido Opulento", 8: "Tecido Barroco"}
}

ITENS_DB = {
    "Cajado Amaldiçoado": ["MAIN_CURSEDSTAFF", "Tábuas de Pinho", 16, "Barra de Aço", 8, None, 0],
    "Cajado Amaldiçoado Elevado": ["2H_CURSEDSTAFF", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0],
    "Cajado Demoníaco": ["2H_DEMONICSTAFF", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0],
    "Cajado Execrado": ["MAIN_CURSEDSTAFF_UNDEAD", "Tábuas de Pinho", 16, "Barra de Aço", 8, "ARTEFACT_MAIN_CURSEDSTAFF_UNDEAD", 1],
    "Caveira Amaldiçoada": ["2H_SKULLPANE_HELL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_SKULLPANE_HELL", 1],
    "Cajado da Danação": ["2H_CURSEDSTAFF_MORGANA", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_CURSEDSTAFF_MORGANA", 1],
    "Chama-sombra": ["MAIN_CURSEDSTAFF_AVALON", "Tábuas de Pinho", 16, "Barra de Aço", 8, "ARTEFACT_MAIN_CURSEDSTAFF_AVALON", 1],
    "Cajado Pútrido": ["2H_CURSEDSTAFF_CRYSTAL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "QUESTITEM_TOKEN_CRYSTAL_CURSEDSTAFF", 1],
    "Bordão": ["2H_QUARTERSTAFF", "Barra de Aço", 12, "Couro Trabalhado", 20, None, 0],
    "BOLSA": ["BAG", "Tecido Fino", 8, "Couro Trabalhado", 8, None, 0],
    "Cajado Férreo": ["2H_IRONCLADSTAFF", "Barra de Aço", 12, "Couro Trabalhado", 20, None, 0],
    "Cajado Biliminado": ["2H_DOUBLEBLADEDSTAFF", "Barra de Aço", 12, "Couro Trabalhado", 20, None, 0],
    "Cajado de Monge Negro": ["2H_COMBATSTAFF_MORGANA", "Barra de Aço", 12, "Couro Trabalhado", 20, "ARTEFACT_2H_COMBATSTAFF_MORGANA", 1],
    "Segamímica": ["2H_TWINSCYTHE_HELL", "Barra de Aço", 12, "Couro Trabalhado", 20, "ARTEFACT_2H_TWINSCYTHE_HELL", 1],
    "Cajado do Equilíbrio": ["2H_ROCKSTAFF_KEEPER", "Barra de Aço", 12, "Couro Trabalhado", 20, "ARTEFACT_2H_ROCKSTAFF_KEEPER", 1],
    "Buscador do Graal": ["2H_QUARTERSTAFF_AVALON", "Barra de Aço", 12, "Couro Trabalhado", 20, "ARTEFACT_2H_QUARTERSTAFF_AVALON", 1],
    "Lâminas Gêmeas Fantasmagóricas": ["2H_QUARTERSTAFF_CRYSTAL", "Barra de Aço", 12, "Couro Trabalhado", 20, "QUESTITEM_TOKEN_CRYSTAL_QUARTERSTAFF", 1],
    "Cajado de Gelo": ["MAIN_FROSTSTAFF", "Tábuas de Pinho", 16, "Barra de Aço", 8, None, 0],
    "Cajado de Gelo Elevado": ["2H_FROSTSTAFF", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0],
    "Cajado Glacial": ["2H_GLACIALSTAFF", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0],
    "Arco": ["2H_BOW", "Tábuas de Pinho", 32, None, 0, None, 0],
    "Arco de Guerra": ["2H_WARBOW", "Tábuas de Pinho", 32, None, 0, None, 0],
    "Arco Longo": ["2H_LONGBOW", "Tábuas de Pinho", 32, None, 0, None, 0],
    "BOTAS DE SOLDADO": ["SHOES_PLATE_SET1", "Barra de Aço", 8, None, 0, None, 0],
    "ARMADURA DE SOLDADO": ["ARMOR_PLATE_SET1", "Barra de Aço", 16, None, 0, None, 0],
    "ELMO DE SOLDADO": ["HEAD_PLATE_SET1", "Barra de Aço", 8, None, 0, None, 0],
}

FILTROS = {
    "armaduras": lambda k, v: "ARMOR_" in v[0],
    "botas": lambda k, v: "SHOES_" in v[0],
    "capacetes": lambda k, v: "HEAD_" in v[0],
    "espadas": lambda k, v: "SWORD" in v[0],
    "machados": lambda k, v: "AXE" in v[0],
    "mace": lambda k, v: "MACE" in v[0],
    "martelos": lambda k, v: "HAMMER" in v[0],
    "lancas": lambda k, v: "SPEAR" in v[0] or "GLAIVE" in v[0],
    "adagas": lambda k, v: "DAGGER" in v[0],
    "bestas": lambda k, v: "CROSSBOW" in v[0],
    "arcos": lambda k, v: "BOW" in v[0] and "CROSSBOW" not in v[0],
    "cajados": lambda k, v: "STAFF" in v[0],
    "secundarias": lambda k, v: v[0].startswith("OFF_"),
    "bolsas": lambda k, v: "BAG" in v[0],
}

# ================= FUNÇÕES =================
def get_idade_str(data_iso):
    try:
        if not data_iso or data_iso == "0001-01-01T00:00:00": return "Média 24h"
        data_api = datetime.fromisoformat(data_iso.replace("Z", "+00:00"))
        diff = datetime.now(timezone.utc) - data_api
        minutos = int(diff.total_seconds() / 60)
        if minutos < 60: return f"{minutos}m"
        return f"{minutos // 60}h"
    except: return "Média 24h"

def get_historical_avg(item_id, location):
    try:
        url = f"{HISTORY_URL}{item_id}?locations={location}&timescale=24"
        resp = requests.get(url, timeout=10).json()
        if resp and "data" in resp[0] and resp[0]["data"]:
            prices = [d["avg_price"] for d in resp[0]["data"] if d["avg_price"] > 0]
            if prices: return sum(prices) / len(prices)
        return 0
    except: return 0

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("### 🛡️ Configurações")
    categoria = st.selectbox("Categoria", list(FILTROS.keys()))
    tier = st.number_input("Tier", 4, 8, 4)
    encanto = st.number_input("Encanto", 0, 4, 0)
    quantidade = st.number_input("Quantidade", 1, 999, 1)
    st.markdown("---")
    btn = st.button("🚀 ESCANEAR TUDO")

st.title("⚔️ Radar Craft — Comparativo de Lucros")

if btn:
    filtro = FILTROS[categoria]
    itens = {k: v for k, v in ITENS_DB.items() if filtro(k, v)}
    if not itens: st.error("Nada encontrado."); st.stop()

    # 1. Busca Preços de Venda
    ids_itens = [f"T{tier}_{d[0]}@{encanto}" if encanto > 0 else f"T{tier}_{d[0]}" for d in itens.values()]
    try:
        resp_venda = requests.get(f"{API_URL}{','.join(ids_itens)}?locations={','.join(CIDADES_VENDA)}", timeout=20).json()
        precos_venda = {}
        for entry in resp_venda:
            iid, city = entry["item_id"], entry["city"]
            if iid not in precos_venda: precos_venda[iid] = {}
            
            data_str = entry["sell_price_min_date"]
            idade_minutos = 9999
            try:
                data_api = datetime.fromisoformat(data_str.replace("Z", "+00:00"))
                idade_minutos = int((datetime.now(timezone.utc) - data_api).total_seconds() / 60)
            except: pass

            p_final = 0
            fonte = get_idade_str(data_str)
            
            if city == "Black Market":
                if idade_minutos < 1440: p_final = entry["sell_price_min"]
            else:
                # TRAVA DE SEGURANÇA: 6 HORAS
                if idade_minutos < 360 and 0 < entry["sell_price_min"] < 900000:
                    p_final = entry["sell_price_min"]
                else:
                    p_final = get_historical_avg(iid, city)
                    fonte = "Média 24h"

            if p_final > 0:
                precos_venda[iid][city] = {"price": int(p_final), "fonte": fonte}
    except: st.error("Erro na API de Venda."); st.stop()

    # 2. Busca Recursos
    ids_recursos = set()
    for d in itens.values():
        base = f"T{tier}_{RECURSO_MAP[d[1]]}"
        ids_recursos.add(f"{base}@{encanto}" if encanto > 0 else base)
        if d[3]:
            base2 = f"T{tier}_{RECURSO_MAP[d[3]]}"
            ids_recursos.add(f"{base2}@{encanto}" if encanto > 0 else base2)

    try:
        resp_rec = requests.get(f"{API_URL}{','.join(ids_recursos)}?locations=Martlock,Thetford,FortSterling,Lymhurst,Bridgewatch,Caerleon", timeout=20).json()
        precos_recursos = {}
        for p in resp_rec:
            rid, price = p["item_id"], p["sell_price_min"]
            if price > 0:
                if rid not in precos_recursos or price < precos_recursos[rid]["price"]:
                    precos_recursos[rid] = {"price": price, "city": p["city"]}
    except: st.error("Erro na API de Recursos."); st.stop()

    # 3. Processamento
    resultados = []
    my_bar = st.progress(0, text="Calculando Lucros Reais...")
    
    for i, (nome, d) in enumerate(itens.items()):
        item_id = f"T{tier}_{d[0]}@{encanto}" if encanto > 0 else f"T{tier}_{d[0]}"
        my_bar.progress((i + 1) / len(itens))
        
        custo, dets, valid = 0, [], True
        for recurso, qtd in [(d[1], d[2]), (d[3], d[4])]:
            if not recurso: continue
            rid = f"T{tier}_{RECURSO_MAP[recurso]}@{encanto}" if encanto > 0 else f"T{tier}_{RECURSO_MAP[recurso]}"
            if rid in precos_recursos:
                p_rec = precos_recursos[rid]["price"]
                custo += p_rec * qtd * quantidade
                dets.append(f"{qtd*quantidade}x {recurso}: {p_rec:,}")
            else: valid = False; break
        
        if not valid or item_id not in precos_venda: continue

        lucros = []
        for city, info in precos_venda[item_id].items():
            lucro = int((info["price"] * quantidade * 0.935) - custo)
            lucros.append({"city": city, "profit": lucro, "fonte": info["fonte"]})
        
        if lucros:
            lucros.sort(key=lambda x: x["profit"], reverse=True)
            resultados.append({"nome": nome, "custo": int(custo), "lucros": lucros, "detalhes": dets})

    my_bar.empty()
    if not resultados: st.warning("Sem dados recentes.")
    else:
        for res in resultados:
            cor = "#2ecc71" if res["lucros"][0]["profit"] > 0 else "#e74c3c"
            st.markdown(f"""
            <div class="item-card-custom" style="border-left: 8px solid {cor};">
                <div style="font-size: 1.2rem; font-weight: bold; color: {cor};">⚔️ {res['nome']} [T{tier}.{encanto}]</div>
                <div style="margin: 10px 0;"><b>Investimento Total:</b> {res['custo']:,} Silver</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    {"".join([f'<div class="city-row"><span>{l["city"]}</span><span class="city-profit" style="color:{"#2ecc71" if l["profit"] > 0 else "#e74c3c"}">Lucro: {l["profit"]:,} <br><small style="font-weight:normal; color:#aaa;">({l["fonte"]})</small></span></div>' for l in res["lucros"][:4]])}
                </div>
                <div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 8px; font-size: 0.85rem; margin-top: 10px; border: 1px solid rgba(255,255,255,0.1);">
                    📦 <b>Compras:</b> {" | ".join(res['detalhes'])}
                </div>
            </div>
            """, unsafe_allow_html=True)
