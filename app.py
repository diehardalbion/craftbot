import streamlit as st
import requests
import json
from datetime import datetime, timezone

# ================= CONFIGURAÇÃO DA PÁGINA =================
st.set_page_config("Radar Craft Albion", layout="wide", page_icon="⚔️")

# ================= CUSTOM CSS (VISUAL) =================
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
    [data-testid="stSidebar"] {
        background-color: rgba(15, 17, 23, 0.95) !important;
        border-right: 1px solid #3e4149;
    }
    h1, h2, h3, label, .stMarkdown {
        color: #ffffff !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
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
        padding: 5px 10px;
        border-radius: 5px;
        margin: 2px 0;
        background: rgba(255,255,255,0.05);
    }
    .city-name { font-weight: bold; }
    .city-profit { font-weight: bold; }
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

# ================= SISTEMA DE LOGIN / KEYS =================
def verificar_chave(chave_usuario):
    try:
        try:
            with open("keys.json", "r") as f: keys_db = json.load(f)
        except FileNotFoundError: return False, "Arquivo keys.json não encontrado."
        if chave_usuario in keys_db:
            dados = keys_db[chave_usuario]
            if not dados["ativa"]: return False, "Esta chave foi desativada."
            if dados["expira"] != "null":
                data_expira = datetime.strptime(dados["expira"], "%Y-%m-%d").date()
                if datetime.now().date() > data_expira: return False, "Esta chave expirou."
            return True, dados["cliente"]
        return False, "Chave inválida."
    except Exception as e: return False, f"Erro: {e}"

if "autenticado" not in st.session_state: st.session_state.autenticado = False
if not st.session_state.autenticado:
    st.title("🛡️ Radar Craft - Acesso Restrito")
    col1, col2 = st.columns([1, 1])
    with col1:
        key_input = st.text_input("Insira sua Chave:", type="password")
        if st.button("LIBERAR ACESSO"):
            sucesso, mensagem = verificar_chave(key_input)
            if sucesso:
                st.session_state.autenticado = True
                st.session_state.cliente = mensagem
                st.rerun()
            else: st.error(mensagem)
    st.stop()

# ================= CONFIG DE DADOS =================
API_URL = "https://west.albion-online-data.com/api/v2/stats/prices/"
CIDADES = ["Martlock", "Thetford", "FortSterling", "Lymhurst", "Bridgewatch", "Caerleon", "Brecilien", "Black Market"]
RECURSO_MAP = {"Tecido Fino": "CLOTH", "Couro Trabalhado": "LEATHER", "Barra de Aço": "METALBAR", "Tábuas de Pinho": "PLANKS"}
BONUS_CIDADE = {
    "Martlock": ["AXE", "QUARTERSTAFF", "FROSTSTAFF", "SHOES_PLATE", "OFF_"],
    "Bridgewatch": ["CROSSBOW", "DAGGER", "CURSEDSTAFF", "ARMOR_PLATE", "SHOES_CLOTH"],
    "Lymhurst": ["SWORD", "BOW", "ARCANESTAFF", "HEAD_LEATHER", "SHOES_LEATHER"],
    "Fort Sterling": ["HAMMER", "SPEAR", "HOLYSTAFF", "HEAD_PLATE", "ARMOR_CLOTH"],
    "Thetford": ["MACE", "NATURESTAFF", "FIRESTAFF", "ARMOR_LEATHER", "HEAD_CLOTH"],
    "Caerleon": ["KNUCKLES", "SHAPESHIFTER"],
    "Brecilien": ["CAPE", "BAG"]
}

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
    "Cajado Enregelante": ["MAIN_FROSTSTAFF_DEEPFREEZE", "Tábuas de Pinho", 16, "Barra de Aço", 8, "ARTEFACT_MAIN_FROSTSTAFF_DEEPFREEZE", 1],
    "Cajado de Sincelo": ["2H_ICE_CRYSTAL_HELL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_ICE_CRYSTAL_HELL", 1],
    "Prisma Geleterno": ["2H_RAMPY_FROST_KEEPER", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_RAMPY_FROST_KEEPER", 1],
    "Uivo Frio": ["MAIN_FROSTSTAFF_AVALON", "Tábuas de Pinho", 16, "Barra de Aço", 8, "ARTEFACT_MAIN_FROSTSTAFF_AVALON", 1],
    "Cajado Ártico": ["2H_FROSTSTAFF_CRYSTAL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "QUESTITEM_TOKEN_CRYSTAL_FROSTSTAFF", 1],
    "Cajado Arcano": ["MAIN_ARCANESTAFF", "Tábuas de Pinho", 16, "Barra de Aço", 8, None, 0],
    "Cajado Arcano Elevado": ["2H_ARCANESTAFF", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0],
    "Cajado Enigmático": ["2H_ENIGMATICSTAFF", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0],
    "Cajado Feiticeiro": ["MAIN_ARCANESTAFF_UNDEAD", "Tábuas de Pinho", 16, "Barra de Aço", 8, "ARTEFACT_MAIN_ARCANESTAFF_UNDEAD", 1],
    "Cajado Oculto": ["2H_ARCANESTAFF_HELL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_ARCANESTAFF_HELL", 1],
    "Local Malévolo": ["2H_ENIGMATICSTAFF_MORGANA", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_ENIGMATICSTAFF_MORGANA", 1],
    "Som Equilibrado": ["2H_ARCANESTAFF_AVALON", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_ARCANESTAFF_AVALON", 1],
    "Cajado Astral": ["2H_ARCANESTAFF_CRYSTAL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "QUESTITEM_TOKEN_CRYSTAL_ARCANESTAFF", 1],
    "Cajado Sagrado": ["MAIN_HOLYSTAFF", "Tábuas de Pinho", 16, "Tecido Fino", 8, None, 0],
    "Cajado Sagrado Elevado": ["2H_HOLYSTAFF", "Tábuas de Pinho", 20, "Tecido Fino", 12, None, 0],
    "Cajado Divino": ["2H_DIVINESTAFF", "Tábuas de Pinho", 20, "Tecido Fino", 12, None, 0],
    "Cajado Avivador": ["MAIN_HOLYSTAFF_MORGANA", "Tábuas de Pinho", 16, "Tecido Fino", 8, "ARTEFACT_MAIN_HOLYSTAFF_MORGANA", 1],
    "Cajado Corrompido": ["2H_HOLYSTAFF_HELL", "Tábuas de Pinho", 20, "Tecido Fino", 12, "ARTEFACT_2H_HOLYSTAFF_HELL", 1],
    "Cajado da Redenção": ["2H_HOLYSTAFF_UNDEAD", "Tábuas de Pinho", 20, "Tecido Fino", 12, "ARTEFACT_2H_HOLYSTAFF_UNDEAD", 1],
    "Queda Santa": ["MAIN_HOLYSTAFF_AVALON", "Tábuas de Pinho", 16, "Tecido Fino", 8, "ARTEFACT_MAIN_HOLYSTAFF_AVALON", 1],
    "Cajado Exaltado": ["2H_HOLYSTAFF_CRYSTAL", "Tábuas de Pinho", 20, "Tecido Fino", 12, "QUESTITEM_TOKEN_CRYSTAL_HOLYSTAFF", 1],
    "Cajado de Fogo": ["MAIN_FIRESTAFF", "Tábuas de Pinho", 16, "Barra de Aço", 8, None, 0],
    "Cajado de Fogo Elevado": ["2H_FIRESTAFF", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0],
    "Cajado Infernal": ["2H_INFERNALSTAFF", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0],
    "Cajado Incendiário": ["MAIN_FIRESTAFF_KEEPER", "Tábuas de Pinho", 16, "Barra de Aço", 8, "ARTEFACT_MAIN_FIRESTAFF_KEEPER", 1],
    "Cajado Sulfuroso": ["2H_FIRE_CRYSTAL_HELL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_FIRE_CRYSTAL_HELL", 1],
    "Cajado Fulgurante": ["2H_INFERNALSTAFF_MORGANA", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_INFERNALSTAFF_MORGANA", 1],
    "Canção da Alvorada": ["2H_FIRESTAFF_AVALON", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_FIRESTAFF_AVALON", 1],
    "Cajado do Andarilho Flamejante": ["MAIN_FIRESTAFF_CRYSTAL", "Tábuas de Pinho", 16, "Barra de Aço", 8, "QUESTITEM_TOKEN_CRYSTAL_FIRESTAFF", 1],
    "Cajado da Natureza": ["MAIN_NATURESTAFF", "Tábuas de Pinho", 16, "Tecido Fino", 8, None, 0],
    "Cajado da Natureza Elevado": ["2H_NATURESTAFF", "Tábuas de Pinho", 20, "Tecido Fino", 12, None, 0],
    "Arco": ["2H_BOW", "Tábuas de Pinho", 32, None, 0, None, 0],
    "Arco de Guerra": ["2H_WARBOW", "Tábuas de Pinho", 32, None, 0, None, 0],
    "Arco Longo": ["2H_LONGBOW", "Tábuas de Pinho", 32, None, 0, None, 0],
    "Arco Sussurante": ["2H_BOW_KEEPER", "Tábuas de Pinho", 32, None, 0, "ARTEFACT_2H_BOW_KEEPER", 1],
    "Arco Plangente": ["2H_BOW_HELL", "Tábuas de Pinho", 32, None, 0, "ARTEFACT_2H_BOW_HELL", 1],
    "Arco Badônico": ["2H_BOW_UNDEAD", "Tábuas de Pinho", 32, None, 0, "ARTEFACT_2H_BOW_UNDEAD", 1],
    "Fura-bruma": ["2H_BOW_AVALON", "Tábuas de Pinho", 32, None, 0, "ARTEFACT_2H_BOW_AVALON", 1],
    "Arco do Andarilho Celeste": ["2H_BOW_CRYSTAL", "Tábuas de Pinho", 32, None, 0, "QUESTITEM_TOKEN_CRYSTAL_BOW", 1],
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
def calcular_horas(data_iso):
    try:
        data_api = datetime.fromisoformat(data_iso.replace("Z", "+00:00"))
        data_agora = datetime.now(timezone.utc)
        diff = data_agora - data_api
        total_segundos = int(diff.total_seconds())
        if total_segundos < 60: return f"{total_segundos}s"
        if total_segundos < 3600: return f"{total_segundos // 60}m"
        return f"{total_segundos // 3600}h"
    except: return "???"

def id_item(tier, base, enc): return f"T{tier}_{base}@{enc}" if enc > 0 else f"T{tier}_{base}"

def ids_recurso_variantes(tier, nome, enc):
    if nome not in RECURSO_MAP: return []
    base = f"T{tier}_{RECURSO_MAP[nome]}"
    if enc > 0: return [f"{base}@{enc}", f"{base}_LEVEL{enc}@{enc}"]
    return [base]

def identificar_cidade_bonus(nome_item):
    for cidade, sufixos in BONUS_CIDADE.items():
        for s in sufixos:
            if s in ITENS_DB[nome_item][0]: return cidade
    return "Caerleon"

# ================= INTERFACE SIDEBAR =================
with st.sidebar:
    st.markdown("### ⚙️ Configurações")
    categoria = st.selectbox("Categoria", list(FILTROS.keys()))
    tier = st.number_input("Tier", 4, 8, 4)
    encanto = st.number_input("Encanto", 0, 4, 0)
    quantidade = st.number_input("Quantidade", 1, 999, 1)
    st.markdown("---")
    btn = st.button("🚀 ESCANEAR MERCADO")

st.title("⚔️ Radar Craft — Visão Multicidades")

# ================= EXECUÇÃO =================
if btn:
    filtro = FILTROS[categoria]
    itens = {k: v for k, v in ITENS_DB.items() if filtro(k, v)}
    if not itens:
        st.error("Nenhum item encontrado.")
        st.stop()

    # 1. Coleta IDs de Itens e Recursos
    ids_itens = [id_item(tier, d[0], encanto) for d in itens.values()]
    ids_recursos = set()
    for d in itens.values():
        for r in ids_recurso_variantes(tier, d[1], encanto): ids_recursos.add(r)
        if d[3]:
            for r in ids_recurso_variantes(tier, d[3], encanto): ids_recursos.add(r)
    
    # Adiciona artefatos se houver
    for d in itens.values():
        if d[5]: ids_itens.append(f"T{tier}_{d[5]}")

    # 2. Busca Preços de Venda (Todas as Cidades)
    try:
        locs_all = ",".join(CIDADES)
        resp_venda = requests.get(f"{API_URL}{','.join(ids_itens)}?locations={locs_all}", timeout=20).json()
        
        precos_venda = {}
        for entry in resp_venda:
            iid = entry["item_id"]
            city = entry["city"]
            if iid not in precos_venda: precos_venda[iid] = {}
            
            # Lógica: Black Market = Sell Price Min | Outras = Sell Price Min (se razoável) ou Buy Price Max
            p_final = 0
            if city == "Black Market": p_final = entry["sell_price_min"]
            else:
                p_final = entry["sell_price_min"] if 0 < entry["sell_price_min"] < 1000000 else entry["buy_price_max"]
            
            if p_final > 0:
                precos_venda[iid][city] = {"price": p_final, "idade": calcular_horas(entry["sell_price_min_date"])}
    except:
        st.error("Erro ao buscar preços de venda.")
        st.stop()

    # 3. Busca Preços de Recursos (Menor Preço entre Cidades Reais)
    try:
        locs_rec = "Thetford,FortSterling,Martlock,Lymhurst,Bridgewatch,Caerleon"
        resp_rec = requests.get(f"{API_URL}{','.join(ids_recursos)}?locations={locs_rec}", timeout=20).json()
        
        precos_recursos = {}
        for p in resp_rec:
            pid, price = p["item_id"], p["sell_price_min"]
            if price > 0:
                if pid not in precos_recursos or price < precos_recursos[pid]["price"]:
                    precos_recursos[pid] = {"price": price, "city": p["city"]}
    except:
        st.error("Erro ao buscar recursos.")
        st.stop()

    # 4. Processamento de Resultados
    resultados = []
    my_bar = st.progress(0, text="Calculando Lucros...")
    
    for i, (nome, d) in enumerate(itens.items()):
        item_id = id_item(tier, d[0], encanto)
        my_bar.progress((i + 1) / len(itens), text=f"Analisando: {nome}")
        
        # Custo de Craft
        custo_craft, dets, valid = 0, [], True
        for recurso, qtd in [(d[1], d[2]), (d[3], d[4])]:
            if not recurso or qtd == 0: continue
            found = False
            for rid in ids_recurso_variantes(tier, recurso, encanto):
                if rid in precos_recursos:
                    info = precos_recursos[rid]
                    custo_craft += info["price"] * qtd * quantidade
                    dets.append(f"{qtd*quantidade}x {recurso}: {int(info['price']):,} ({info['city']})")
                    found = True; break
            if not found: valid = False
        
        if not valid: continue
        
        # Custo de Artefato
        if d[5]:
            art_id = f"T{tier}_{d[5]}"
            best_art = 0
            if art_id in precos_venda:
                valid_arts = [v["price"] for k, v in precos_venda[art_id].items() if k != "Black Market"]
                if valid_arts: best_art = min(valid_arts)
            
            if best_art > 0:
                custo_craft += best_art * d[6] * quantidade
                dets.append(f"{d[6]*quantidade}x Artefato: {int(best_art):,}")
            else: continue

        # Calcula Lucro por Cidade
        lucros_cidades = []
        if item_id in precos_venda:
            for city, info in precos_venda[item_id].items():
                venda_total = info["price"] * quantidade
                lucro = int((venda_total * 0.935) - custo_craft)
                lucros_cidades.append({"city": city, "profit": lucro, "venda": info["price"], "idade": info["idade"]})
        
        if lucros_cidades:
            lucros_cidades.sort(key=lambda x: x["profit"], reverse=True)
            resultados.append({"nome": nome, "custo": int(custo_craft), "lucros": lucros_cidades, "detalhes": dets})

    my_bar.empty()
    
    # 5. Exibição
    if not resultados: st.warning("Nenhum item lucrativo encontrado.")
    else:
        for res in resultados:
            best = res["lucros"][0]
            cor = "#2ecc71" if best["profit"] > 0 else "#e74c3c"
            
            with st.container():
                st.markdown(f"""
                <div class="item-card-custom" style="border-left: 8px solid {cor};">
                    <div style="font-size: 1.2rem; font-weight: bold; color: {cor}; margin-bottom: 10px;">
                        ⚔️ {res['nome']} [T{tier}.{encanto}] x{quantidade}
                    </div>
                    <div style="margin-bottom: 15px;">
                        <b>Investimento Total:</b> {res['custo']:,} Silver
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 15px;">
                        {"".join([f'<div class="city-row"><span class="city-name">{l["city"]}</span><span class="city-profit" style="color: {"#2ecc71" if l["profit"] > 0 else "#e74c3c"}">{l["profit"]:,} ({l["idade"]})</span></div>' for l in res["lucros"][:4]])}
                    </div>
                    <div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 8px; font-size: 0.85rem;">
                        <b>Compras:</b> {" | ".join(res['detalhes'])}
                    </div>
                </div>
                """, unsafe_allow_html=True)

st.markdown("---")
st.caption("Radar Craft Albion - Comparativo Multicidades em Tempo Real")
