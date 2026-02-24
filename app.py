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
    .main .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
    }
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.8)), 
                    url("https://i.imgur.com/kVAiMjD.png ");
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
        with open("keys.json", "r") as f:
            keys_db = json.load(f)
        if chave_usuario in keys_db:
            dados = keys_db[chave_usuario]
            if not dados["ativa"]:
                return False, "Esta chave foi desativada."
            if dados["expira"] != "null":
                data_expira = datetime.strptime(dados["expira"], "%Y-%m-%d").date()
                if datetime.now().date() > data_expira:
                    return False, "Esta chave expirou."
            return True, dados["cliente"]
        return False, "Chave inválida."
    except Exception as e:
        return False, f"Erro ao acessar keys.json: {e}"

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🛡️ Radar Craft - Acesso Restrito")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### Já possui acesso?")
        key_input = st.text_input("Insira sua Chave:", type="password")
        if st.button("LIBERAR ACESSO"):
            sucesso, mensagem = verificar_chave(key_input)
            if sucesso:
                st.session_state.autenticado = True
                st.session_state.cliente = mensagem
                st.rerun()
            else:
                st.error(mensagem)
    with col2:
        st.markdown("### Adquirir Nova Chave")
        st.markdown("""
        <div style="background: rgba(46, 204, 113, 0.1); padding: 20px; border-radius: 10px; border: 1px solid #2ecc71; text-align: center;">
            <h2 style="margin:0; color: #2ecc71;">R$ 15,00</h2>
            <p style="color: white;">Acesso Mensal (30 dias)</p>
            <a href="https://wa.me/5521983042557?text=Olá! Gostaria de comprar uma key para o Radar Craft Albion." target="_blank" style="text-decoration: none;">
                <div style="background-color: #25d366; color: white; padding: 12px; border-radius: 5px; font-weight: bold; margin-top: 10px;">
                    COMPRAR VIA WHATSAPP
                </div>
            </a>
        </div>
        """, unsafe_allow_html=True)
    st.stop()

# ================= CONFIG DE DADOS =================
API_URL = "https://west.albion-online-data.com/api/v2/stats/prices/"
HISTORY_URL = "https://west.albion-online-data.com/api/v2/stats/history/"
CIDADES = ["Martlock", "Thetford", "FortSterling", "Lymhurst", "Bridgewatch", "Brecilien", "Caerleon", "Black Market"]
RECURSO_MAP = {"Tecido Fino": "CLOTH", "Couro Trabalhado": "LEATHER", "Barra de Aço": "METALBAR", "Tábuas de Pinho": "PLANKS"}

# IDs CORRETOS dos corações por facção
CORACOES_IDS = {
    "Bridgewatch": "T1_FACTION_STEPPE_TOKEN_1",
    "Fort Sterling": "T1_FACTION_MOUNTAIN_TOKEN_1",
    "Lymhurst": "T1_FACTION_FOREST_TOKEN_1",
    "Martlock": "T1_FACTION_HIGHLAND_TOKEN_1",
    "Thetford": "T1_FACTION_SWAMP_TOKEN_1",
    "Caerleon": "T1_FACTION_CAERLEON_TOKEN_1",
    # Facções usam mesmos corações das cidades
    "Herege": "T1_FACTION_FOREST_TOKEN_1",  # Mesmo de Lymhurst
    "Morta-viva": "T1_FACTION_MOUNTAIN_TOKEN_1",  # Mesmo de Fort Sterling
    "Protetora": "T1_FACTION_HIGHLAND_TOKEN_1",  # Mesmo de Martlock
    "Morgana": "T1_FACTION_SWAMP_TOKEN_1",  # Mesmo de Thetford
    "Demoníaca": "T1_FACTION_STEPPE_TOKEN_1"  # Mesmo de Bridgewatch
}

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

def get_coracoes_qty(tier):
    return {4: 1, 5: 1, 6: 3, 7: 5, 8: 10}.get(tier, 1)

ITENS_DB = {
    # ================= CAPAS NORMAIS =================
    "Capa do Adepto": ["CAPE", "Tecido Fino", 4, "Couro Trabalhado", 4, None, 0],
    "Capa do Perito": ["CAPE", "Tecido Fino", 4, "Couro Trabalhado", 4, None, 0],
    "Capa do Mestre": ["CAPE", "Tecido Fino", 4, "Couro Trabalhado", 4, None, 0],
    "Capa do Grão-Mestre": ["CAPE", "Tecido Fino", 4, "Couro Trabalhado", 4, None, 0],
    "Capa do Ancião": ["CAPE", "Tecido Fino", 4, "Couro Trabalhado", 4, None, 0],
    
    # ================= CAPAS BRIDGEWATCH =================
    "Capa de Bridgewatch": ["CAPEITEM_FW_BRIDGEWATCH", "CAPE", 1, "CORACAO_BRIDGEWATCH", 1, "CAPEITEM_FW_BRIDGEWATCH_BP", 1],
    
    # ================= CAPAS FORT STERLING =================
    "Capa de Fort Sterling": ["CAPEITEM_FW_FORTSTERLING", "CAPE", 1, "CORACAO_FORTSTERLING", 1, "CAPEITEM_FW_FORTSTERLING_BP", 1],
    
    # ================= CAPAS LYMHURST =================
    "Capa de Lymhurst": ["CAPEITEM_FW_LYMHURST", "CAPE", 1, "CORACAO_LYMHURST", 1, "CAPEITEM_FW_LYMHURST_BP", 1],
    
    # ================= CAPAS MARTLOCK =================
    "Capa de Martlock": ["CAPEITEM_FW_MARTLOCK", "CAPE", 1, "CORACAO_MARTLOCK", 1, "CAPEITEM_FW_MARTLOCK_BP", 1],
    
    # ================= CAPAS THETFORD =================
    "Capa de Thetford": ["CAPEITEM_FW_THETFORD", "CAPE", 1, "CORACAO_THETFORD", 1, "CAPEITEM_FW_THETFORD_BP", 1],
    
    # ================= CAPAS CAERLEON =================
    "Capa de Caerleon": ["CAPEITEM_FW_CAERLEON", "CAPE", 1, "CORACAO_CAERLEON", 1, "CAPEITEM_FW_CAERLEON_BP", 1],
    
    # ================= CAPAS HEREGE =================
    "Capa Herege": ["CAPEITEM_HERETIC", "CAPE", 1, "CORACAO_HEREGE", 1, "CAPEITEM_HERETIC_BP", 1],
    
    # ================= CAPAS MORTA-VIVA =================
    "Capa Morta-viva": ["CAPEITEM_UNDEAD", "CAPE", 1, "CORACAO_MORTAVIVA", 1, "CAPEITEM_UNDEAD_BP", 1],
    
    # ================= CAPAS PROTETORA =================
    "Capa Protetora": ["CAPEITEM_KEEPER", "CAPE", 1, "CORACAO_PROTETORA", 1, "CAPEITEM_KEEPER_BP", 1],
    
    # ================= CAPAS MORGANA =================
    "Capa de Morgana": ["CAPEITEM_MORGANA", "CAPE", 1, "CORACAO_MORGANA", 1, "CAPEITEM_MORGANA_BP", 1],
    
    # ================= CAPAS DEMONÍACA =================
    "Capa Demoníaca": ["CAPEITEM_DEMON", "CAPE", 1, "CORACAO_DEMONIACA", 1, "CAPEITEM_DEMON_BP", 1],

    # ================= BOLSAS =================
    "Bolsa": ["BAG", "Tecido Fino", 8, "Couro Trabalhado", 8, None, 0],
    
    # ================= OFF-HANDS =================
    "Tomo de Feitiços": ["OFF_BOOK", "Tecido Fino", 4, "Couro Trabalhado", 4, None, 0],
    "Olho dos Segredos": ["OFF_ORB_HELL", "Tecido Fino", 4, "Couro Trabalhado", 4, "ARTEFACT_OFF_ORB_HELL", 1],
    
    # ================= ARMADURAS PLACA =================
    "Botas de Soldado": ["SHOES_PLATE_SET1", "Barra de Aço", 8, None, 0, None, 0],
    "Armadura de Soldado": ["ARMOR_PLATE_SET1", "Barra de Aço", 16, None, 0, None, 0],
    "Elmo de Soldado": ["HEAD_PLATE_SET1", "Barra de Aço", 8, None, 0, None, 0],
    "Botas de Cavaleiro": ["SHOES_PLATE_SET2", "Barra de Aço", 8, None, 0, None, 0],
    "Armadura de Cavaleiro": ["ARMOR_PLATE_SET2", "Barra de Aço", 16, None, 0, None, 0],
    "Elmo de Cavaleiro": ["HEAD_PLATE_SET2", "Barra de Aço", 8, None, 0, None, 0],
    "Botas de Guardião": ["SHOES_PLATE_SET3", "Barra de Aço", 8, None, 0, None, 0],
    "Armadura de Guardião": ["ARMOR_PLATE_SET3", "Barra de Aço", 16, None, 0, None, 0],
    "Elmo de Guardião": ["HEAD_PLATE_SET3", "Barra de Aço", 8, None, 0, None, 0],
    
    # ================= ARMADURAS COURO =================
    "Sapatos de Mercenário": ["SHOES_LEATHER_SET1", "Couro Trabalhado", 8, None, 0, None, 0],
    "Casaco de Mercenário": ["ARMOR_LEATHER_SET1", "Couro Trabalhado", 16, None, 0, None, 0],
    "Capuz de Mercenário": ["HEAD_LEATHER_SET1", "Couro Trabalhado", 8, None, 0, None, 0],
    
    # ================= ARMADURAS PANo =================
    "Sandálias de Erudito": ["SHOES_CLOTH_SET1", "Tecido Fino", 8, None, 0, None, 0],
    "Robe do Erudito": ["ARMOR_CLOTH_SET1", "Tecido Fino", 16, None, 0, None, 0],
    "Capote de Erudito": ["HEAD_CLOTH_SET1", "Tecido Fino", 8, None, 0, None, 0],
    
    # ================= ESPADAS =================
    "Espada Larga": ["MAIN_SWORD", "Barra de Aço", 16, "Couro Trabalhado", 8, None, 0],
    "Montante": ["2H_CLAYMORE", "Barra de Aço", 20, "Couro Trabalhado", 12, None, 0],
    "Espadas Duplas": ["2H_DUALSWORD", "Barra de Aço", 20, "Couro Trabalhado", 12, None, 0],
    
    # ================= MACHADOS =================
    "Machado de Guerra": ["MAIN_AXE", "Barra de Aço", 16, "Tábuas de Pinho", 8, None, 0],
    "Machadão": ["2H_AXE", "Barra de Aço", 20, "Tábuas de Pinho", 12, None, 0],
    "Alabarda": ["2H_HALBERD", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0],
    
    # ================= CAJADOS AMALDIÇOADOS =================
    "Cajado Amaldiçoado": ["MAIN_CURSEDSTAFF", "Tábuas de Pinho", 16, "Barra de Aço", 8, None, 0],
    "Cajado Amaldiçoado Elevado": ["2H_CURSEDSTAFF", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0],
    "Cajado Demoníaco": ["2H_DEMONICSTAFF", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0],
    
    # ================= ARCOS =================
    "Arco": ["2H_BOW", "Tábuas de Pinho", 32, None, 0, None, 0],
    "Arco de Guerra": ["2H_WARBOW", "Tábuas de Pinho", 32, None, 0, None, 0],
    "Arco Longo": ["2H_LONGBOW", "Tábuas de Pinho", 32, None, 0, None, 0],
}

# ================= FILTROS =================
FILTROS = {
    "todas_capas": lambda k, v: "CAPE" in v[0],
    "capas_normais": lambda k, v: v[0] == "CAPE",
    "capas_cidade": lambda k, v: "CAPEITEM_FW_" in v[0],
    "capas_faccao": lambda k, v: any(x in v[0] for x in ["CAPEITEM_HERETIC", "CAPEITEM_UNDEAD", "CAPEITEM_KEEPER", "CAPEITEM_MORGANA", "CAPEITEM_DEMON"]),
    "bolsas": lambda k, v: v[0] == "BAG",
    "armadura_placa": lambda k, v: "ARMOR_PLATE" in v[0],
    "botas_placa": lambda k, v: "SHOES_PLATE" in v[0],
    "elmo_placa": lambda k, v: "HEAD_PLATE" in v[0],
    "armadura_couro": lambda k, v: "ARMOR_LEATHER" in v[0],
    "botas_couro": lambda k, v: "SHOES_LEATHER" in v[0],
    "elmo_couro": lambda k, v: "HEAD_LEATHER" in v[0],
    "armadura_pano": lambda k, v: "ARMOR_CLOTH" in v[0],
    "botas_pano": lambda k, v: "SHOES_CLOTH" in v[0],
    "elmo_pano": lambda k, v: "HEAD_CLOTH" in v[0],
    "espadas": lambda k, v: "SWORD" in v[0],
    "machados": lambda k, v: "AXE" in v[0],
    "cajados_amaldicoados": lambda k, v: "CURSEDSTAFF" in v[0],
    "arcos": lambda k, v: "BOW" in v[0] and "CROSSBOW" not in v[0],
    "offhands": lambda k, v: v[0].startswith("OFF_"),
}

# ================= FUNÇÕES =================
def get_historical_price(item_id, location="Black Market"):
    try:
        url_atual = f"{API_URL}{item_id}?locations={location}"
        resp_atual = requests.get(url_atual, timeout=10).json()
        if resp_atual and len(resp_atual) > 0 and resp_atual[0].get("sell_price_min", 0) > 0:
            return resp_atual[0]["sell_price_min"]

        url_hist = f"{HISTORY_URL}{item_id}?locations={location}&timescale=24"
        resp_hist = requests.get(url_hist, timeout=10).json()

        if not resp_hist or len(resp_hist) == 0 or "data" not in resp_hist[0]:
            return 0

        prices = [d["avg_price"] for d in resp_hist[0]["data"] if d.get("avg_price", 0) > 0 and d.get("item_count", 0) >= 3]
        if not prices:
            return 0

        prices.sort()
        return prices[len(prices) // 2]
    except Exception as e:
        return 0

def id_item(tier, base, enc):
    if not base:
        return None
    return f"T{tier}_{base}@{enc}" if enc > 0 else f"T{tier}_{base}"

def get_coracao_id(nome_coracao):
    """Converte 'CORACAO_NOME' para o ID da API"""
    if not nome_coracao.startswith("CORACAO_"):
        return None
    facao = nome_coracao.replace("CORACAO_", "")
    return CORACOES_IDS.get(facao)

def ids_recurso_variantes(tier, nome, enc):
    if nome == "CAPE":
        return [f"T{tier}_CAPE"]
    elif nome.startswith("CORACAO_"):
        coracao_id = get_coracao_id(nome)
        return [coracao_id] if coracao_id else []
    elif nome in RECURSO_MAP:
        base = f"T{tier}_{RECURSO_MAP[nome]}"
        if enc > 0:
            return [f"{base}@{enc}", f"{base}_LEVEL{enc}@{enc}"]
        return [base]
    return []

def identificar_cidade_bonus(nome_item):
    dados = ITENS_DB.get(nome_item, [""])
    item_id = dados[0]
    for cidade, sufixos in BONUS_CIDADE.items():
        for s in sufixos:
            if s in item_id:
                return cidade
    return "Caerleon"

# ================= INTERFACE SIDEBAR =================
with st.sidebar:
    st.markdown("### ⚙️ Configurações")
    categorias_opcoes = list(FILTROS.keys())
    categoria = st.selectbox("Categoria", categorias_opcoes)
    tier = st.number_input("Tier", 4, 8, 4)
    encanto = st.number_input("Encanto", 0, 4, 0)
    quantidade = st.number_input("Quantidade", 1, 999, 1)
    debug_mode = st.checkbox("Modo Debug", value=False)
    st.markdown("---")
    btn = st.button("🚀 ESCANEAR MERCADO")

st.title("⚔️ Radar Craft — Black Market")

# ================= EXECUÇÃO =================
if btn:
    filtro = FILTROS[categoria]
    itens = {k: v for k, v in ITENS_DB.items() if filtro(k, v)}
    
    if debug_mode:
        st.write(f"**Debug:** Categoria: {categoria}, Itens: {len(itens)}")
        st.write(f"**Debug:** {list(itens.keys())}")

    if not itens:
        st.error("Nenhum item encontrado.")
        st.stop()

    # Coleta IDs
    ids_para_buscar = set()
    for nome, d in itens.items():
        # Item final
        item_id = id_item(tier, d[0], encanto)
        if item_id:
            ids_para_buscar.add(item_id)
        
        # Recurso 1 (Capa base ou recurso)
        if d[1]:
            for rid in ids_recurso_variantes(tier, d[1], encanto):
                if rid:
                    ids_para_buscar.add(rid)
        
        # Recurso 2 (Coração ou recurso)
        if d[3]:
            for rid in ids_recurso_variantes(tier, d[3], encanto):
                if rid:
                    ids_para_buscar.add(rid)
        
        # Artefato/Ornamento
        if d[5]:
            art_id = id_item(tier, d[5], 0)
            if art_id:
                ids_para_buscar.add(art_id)
    
    if debug_mode:
        st.write(f"**Debug:** IDs únicos: {len(ids_para_buscar)}")

    # Busca na API
    try:
        url_api = f"{API_URL}{','.join(ids_para_buscar)}?locations=Thetford,FortSterling,Martlock,Lymhurst,Bridgewatch,Caerleon,Black Market"
        response = requests.get(url_api, timeout=30)
        data_precos = response.json()
    except Exception as e:
        st.error(f"Erro API: {e}")
        st.stop()

    # Processa preços
    precos_cache = {}
    for p in data_precos:
        pid = p.get("item_id")
        price = p.get("sell_price_min", 0)
        if pid and price > 0:
            if pid not in precos_cache or price < precos_cache[pid]["price"]:
                precos_cache[pid] = {"price": price, "city": p.get("city", "?")}

    if debug_mode:
        st.write(f"**Debug:** Preços encontrados: {len(precos_cache)}")

    # Calcula lucros
    resultados = []
    my_bar = st.progress(0)
    total = len(itens)

    for i, (nome, d) in enumerate(itens.items()):
        my_bar.progress((i + 1) / total)
        
        item_id = id_item(tier, d[0], encanto)
        preco_venda = get_historical_price(item_id, "Black Market") if item_id else 0
        
        if preco_venda <= 0:
            continue

        custo = 0
        detalhes = []
        ok = True

        # Recurso 1
        if d[1] == "CAPE":
            capa_id = f"T{tier}_CAPE"
            if capa_id in precos_cache:
                info = precos_cache[capa_id]
                custo += info["price"] * d[2] * quantidade
                detalhes.append(f"{d[2]*quantidade}x Capa T{tier}: {info['price']:,} ({info['city']})")
            else:
                ok = False
        elif d[1] in RECURSO_MAP:
            for rid in ids_recurso_variantes(tier, d[1], encanto):
                if rid in precos_cache:
                    info = precos_cache[rid]
                    nome_rec = NOMES_RECURSOS_TIER.get(d[1], {}).get(tier, d[1])
                    custo += info["price"] * d[2] * quantidade
                    detalhes.append(f"{d[2]*quantidade}x {nome_rec}: {info['price']:,} ({info['city']})")
                    break
            else:
                ok = False

        if not ok:
            continue

        # Recurso 2 (CORAÇÃO)
        if d[3] and d[3].startswith("CORACAO_"):
            coracao_id = get_coracao_id(d[3])
            if coracao_id and coracao_id in precos_cache:
                info = precos_cache[coracao_id]
                qty = get_coracoes_qty(tier)
                custo += info["price"] * qty * quantidade
                facao = d[3].replace("CORACAO_", "")
                detalhes.append(f"{qty*quantidade}x Coração {facao}: {info['price']:,} ({info['city']})")
            else:
                if debug_mode:
                    st.write(f"❌ {nome}: Coração {coracao_id} não encontrado")
                ok = False
        elif d[3] in RECURSO_MAP:
            for rid in ids_recurso_variantes(tier, d[3], encanto):
                if rid in precos_cache:
                    info = precos_cache[rid]
                    nome_rec = NOMES_RECURSOS_TIER.get(d[3], {}).get(tier, d[3])
                    custo += info["price"] * d[4] * quantidade
                    detalhes.append(f"{d[4]*quantidade}x {nome_rec}: {info['price']:,} ({info['city']})")
                    break
            else:
                ok = False

        if not ok:
            continue

        # Ornamento
        if d[5]:
            art_id = id_item(tier, d[5], 0)
            if art_id and art_id in precos_cache:
                info = precos_cache[art_id]
                custo += info["price"] * d[6] * quantidade
                detalhes.append(f"{d[6]*quantidade}x Ornamento: {info['price']:,} ({info['city']})")
            else:
                # Busca em outras cidades
                preco_art = get_historical_price(art_id, "Caerleon,Bridgewatch,Martlock,FortSterling,Lymhurst,Thetford") if art_id else 0
                if preco_art > 0:
                    custo += preco_art * d[6] * quantidade
                    detalhes.append(f"{d[6]*quantidade}x Ornamento: {preco_art:,.0f} (Market)")
                else:
                    if debug_mode:
                        st.write(f"❌ {nome}: Ornamento {art_id} não encontrado")
                    ok = False

        if not ok:
            continue

        venda_total = int(preco_venda * quantidade)
        custo_final = int(custo)
        lucro = int((venda_total * 0.935) - custo_final)
        
        if custo_final > 0:
            resultados.append((nome, lucro, venda_total, custo_final, detalhes))

    my_bar.empty()
    resultados.sort(key=lambda x: x[1], reverse=True)

    if not resultados:
        st.warning("⚠️ Nenhum resultado. Ative Modo Debug para verificar.")
    else:
        st.subheader(f"📊 {len(resultados)} Itens - {categoria.upper()} T{tier}.{encanto}")
        
        for nome, lucro, venda, custo, detalhes in resultados:
            perc = (lucro/custo)*100 if custo else 0
            cor = "#2ecc71" if lucro > 0 else "#e74c3c"
            
            st.markdown(f"""
            <div class="item-card-custom" style="border-left: 5px solid {cor};">
                <h4 style="color: {cor}; margin:0;">⚔️ {nome} T{tier}.{encanto} x{quantidade}</h4>
                <p><b>💰 Lucro:</b> {lucro:,} ({perc:.1f}%) | <b>Custo:</b> {custo:,} | <b>Venda:</b> {venda:,}</p>
                <p style="font-size:0.9em; color:#ccc;">📦 {" | ".join(detalhes)}</p>
            </div>
            """, unsafe_allow_html=True)

st.markdown("---")
st.caption("Radar Craft Albion")
