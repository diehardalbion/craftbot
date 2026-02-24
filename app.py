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
            <a href="https://wa.me/5521983042557?text=Ol á! Gostaria de comprar uma key para o Radar Craft Albion." target="_blank" style="text-decoration: none;">
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

# NOVO: Mapeamento de corações por facção
CORACOES_MAP = {
    "Bridgewatch": "T1_FACTION_STEPPE_TOKEN_1",
    "Fort Sterling": "T1_FACTION_MOUNTAIN_TOKEN_1",
    "Lymhurst": "T1_FACTION_FOREST_TOKEN_1",
    "Martlock": "T1_FACTION_HIGHLAND_TOKEN_1",
    "Thetford": "T1_FACTION_SWAMP_TOKEN_1",
    "Caerleon": "T1_FACTION_CAERLEON_TOKEN_1",
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

# ================= NOMES CORRETOS POR TIER =================
NOMES_RECURSOS_TIER = {
    "Barra de Aço": {4: "Barra de Aço", 5: "Barra de Titânio", 6: "Barra de Runita", 7: "Barra de Meteorito", 8: "Barra de Adamante"},
    "Tábuas de Pinho": {4: "Tábuas de Pinho", 5: "Tábuas de Cedro", 6: "Tábuas de Carvalho-Sangue", 7: "Tábuas de Freixo", 8: "Tábuas de Pau-branco"},
    "Couro Trabalhado": {4: "Couro Trabalhado", 5: "Couro Curtido", 6: "Couro Endurecido", 7: "Couro Reforçado", 8: "Couro Fortificado"},
    "Tecido Fino": {4: "Tecido Fino", 5: "Tecido Ornado", 6: "Tecido Rico", 7: "Tecido Opulento", 8: "Tecido Barroco"}
}

# NOVO: Função para obter quantidade de corações por tier
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

    # ... (restante do seu ITENS_DB original aqui) ...
    "BOLSA": ["BAG", "Tecido Fino", 8, "Couro Trabalhado", 8, None, 0],
    # etc...
}

# ================= FILTROS =================
FILTROS = {
    # CAPAS
    "capas": lambda k, v: "CAPE" in v[0] and "CAPEITEM" not in v[0],
    "capas_cidade": lambda k, v: "CAPEITEM_FW_" in v[0],
    "capas_facao": lambda k, v: "CAPEITEM_HERETIC" in v[0] or "CAPEITEM_UNDEAD" in v[0] or "CAPEITEM_KEEPER" in v[0] or "CAPEITEM_MORGANA" in v[0] or "CAPEITEM_DEMON" in v[0],
    
    # ARMADURAS
    "armadura_placa": lambda k, v: "ARMOR_PLATE" in v[0],
    "armadura_couro": lambda k, v: "ARMOR_LEATHER" in v[0],
    "armadura_pano": lambda k, v: "ARMOR_CLOTH" in v[0],
    "botas_placa": lambda k, v: "SHOES_PLATE" in v[0],
    "botas_couro": lambda k, v: "SHOES_LEATHER" in v[0],
    "botas_pano": lambda k, v: "SHOES_CLOTH" in v[0],
    "capacete_placa": lambda k, v: "HEAD_PLATE" in v[0],
    "capacete_couro": lambda k, v: "HEAD_LEATHER" in v[0],
    "capacete_pano": lambda k, v: "HEAD_CLOTH" in v[0],
    "espadas": lambda k, v: "SWORD" in v[0],
    "machados": lambda k, v: "AXE" in v[0],
    "mace": lambda k, v: "MACE" in v[0],
    "martelos": lambda k, v: "HAMMER" in v[0],
    "lancas": lambda k, v: "SPEAR" in v[0] or "GLAIVE" in v[0],
    "adagas": lambda k, v: "DAGGER" in v[0],
    "bestas": lambda k, v: "CROSSBOW" in v[0],
    "manoplas": lambda k, v: "KNUCKLES" in v[0],
    "arcos": lambda k, v: "BOW" in v[0] and "CROSSBOW" not in v[0],
    "bordao": lambda k, v: "QUARTERSTAFF" in v[0] or "IRONCLAD" in v[0] or "DOUBLEBLADED" in v[0] or "COMBATSTAFF" in v[0] or "TWINSCYTHE" in v[0],
    "fogo": lambda k, v: "FIRESTAFF" in v[0],
    "gelo": lambda k, v: "FROSTSTAFF" in v[0],
    "arcano": lambda k, v: "ARCANESTAFF" in v[0],
    "sagrado": lambda k, v: "HOLYSTAFF" in v[0],
    "natureza": lambda k, v: "NATURESTAFF" in v[0],
    "amaldiçoado": lambda k, v: "CURSEDSTAFF" in v[0],
    "metamorfo": lambda k, v: "SHAPESHIFTER" in v[0],
    "secundarias": lambda k, v: v[0].startswith("OFF_"),
    "bolsas": lambda k, v: "BAG" in v[0] and "CAPE" not in v[0],
}

# ================= FUNÇÕES =================
def get_historical_price(item_id, location="Black Market"):
    try:
        url_atual = f"{API_URL}{item_id}?locations={location}"
        resp_atual = requests.get(url_atual, timeout=10).json()
        if resp_atual and resp_atual[0]["sell_price_min"] > 0:
            return resp_atual[0]["sell_price_min"]

        url_hist = f"{HISTORY_URL}{item_id}?locations={location}&timescale=24"
        resp_hist = requests.get(url_hist, timeout=10).json()

        if not resp_hist or "data" not in resp_hist[0]:
            return 0

        prices = [d["avg_price"] for d in resp_hist[0]["data"] if d["avg_price"] > 0 and d["item_count"] >= 3]
        if not prices:
            return 0

        prices.sort()
        mid = len(prices) // 2
        return prices[mid]
    except:
        return 0

def calcular_horas(data_iso):
    try:
        data_api = datetime.fromisoformat(data_iso.replace("Z", "+00:00"))
        data_agora = datetime.now(timezone.utc)
        diff = data_agora.replace(tzinfo=None) - data_api.replace(tzinfo=None)
        return int(diff.total_seconds() / 3600)
    except: 
        return 999

def id_item(tier, base, enc):
    return f"T{tier}_{base}@{enc}" if enc > 0 else f"T{tier}_{base}"

def ids_recurso_variantes(tier, nome, enc):
    # NOVO: Tratamento especial para capas e corações
    if nome == "CAPE":
        base = f"T{tier}_CAPE"
        return [base]
    elif nome.startswith("CORACAO_"):
        # Retorna o ID do coração baseado no tipo
        facao = nome.replace("CORACAO_", "")
        if facao in CORACOES_MAP:
            return [CORACOES_MAP[facao]]
        return []
    
    base = f"T{tier}_{RECURSO_MAP[nome]}"
    if enc > 0: 
        return [f"{base}@{enc}", f"{base}_LEVEL{enc}@{enc}"]
    return [base]

def identificar_cidade_bonus(nome_item):
    for cidade, sufixos in BONUS_CIDADE.items():
        for s in sufixos:
            if s in ITENS_DB[nome_item][0]:
                return f"{cidade}"
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

st.title("⚔️ Radar Craft — Black Market")

# ================= EXECUÇÃO =================
if btn:
    filtro = FILTROS[categoria]
    itens = {k: v for k, v in ITENS_DB.items() if filtro(k, v)}

    if not itens:
        st.error("Nenhum item encontrado nesta categoria.")
        st.stop()

    # Coleta de IDs para a API
    ids_para_buscar = set()
    
    for d in itens.values():
        # Item final
        ids_para_buscar.add(id_item(tier, d[0], encanto))
        
        # Recurso 1 (Capa base ou recurso normal)
        for rid in ids_recurso_variantes(tier, d[1], encanto):
            ids_para_buscar.add(rid)
        
        # Recurso 2 (Coração ou recurso normal)
        if d[3]:
            for rid in ids_recurso_variantes(tier, d[3], encanto):
                ids_para_buscar.add(rid)
        
        # Artefato/Ornamento
        if d[5]:
            art_id = id_item(tier, d[5], 0)  # Ornamentos não têm encanto
            ids_para_buscar.add(art_id)

    try:
        response = requests.get(
            f"{API_URL}{','.join(ids_para_buscar)}?locations=Thetford,FortSterling,Martlock,Lymhurst,Bridgewatch,Caerleon,Black Market",
            timeout=20
        )
        data_precos = response.json()
    except:
        st.error("Erro ao conectar com a API. Tente novamente.")
        st.stop()

    # Processamento de preços
    precos_cache = {}
    for p in data_precos:
        pid = p["item_id"]
        price = p["sell_price_min"]
        if price > 0:
            if pid not in precos_cache or price < precos_cache[pid]["price"]:
                precos_cache[pid] = {"price": price, "city": p["city"]}

    resultados = []
    progress_text = "Analisando Mercado..."
    my_bar = st.progress(0, text=progress_text)
    total_itens = len(itens)

    for i, (nome, d) in enumerate(itens.items()):
        item_id = id_item(tier, d[0], encanto)
        preco_venda_bm = get_historical_price(item_id, "Black Market")
        
        my_bar.progress((i + 1) / total_itens, text=f"Analisando: {nome}")
        
        if preco_venda_bm <= 0:
            continue

        custo = 0
        detalhes = []
        valid_craft = True

        # ================= RECURSO 1 (Capa base ou normal) =================
        if d[1]:
            # Verifica se é capa base (CAPE) ou recurso normal
            if d[1] == "CAPE":
                capa_id = f"T{tier}_CAPE"
                if capa_id in precos_cache:
                    info = precos_cache[capa_id]
                    custo += info["price"] * d[2] * quantidade
                    detalhes.append(f"{d[2] * quantidade}x Capa T{tier}: {info['price']:,} ({info['city']})")
                else:
                    valid_craft = False
            else:
                # Recurso normal (tecido, couro, etc.)
                for rid in ids_recurso_variantes(tier, d[1], encanto):
                    if rid in precos_cache:
                        info = precos_cache[rid]
                        nome_recurso = NOMES_RECURSOS_TIER.get(d[1], {}).get(tier, d[1])
                        custo += info["price"] * d[2] * quantidade
                        detalhes.append(f"{d[2] * quantidade}x {nome_recurso}: {info['price']:,} ({info['city']})")
                        break
                else:
                    valid_craft = False

        if not valid_craft:
            continue

        # ================= RECURSO 2 (Coração ou normal) =================
        if d[3]:
            if d[3].startswith("CORACAO_"):
                # É um coração de facção - quantidade varia por tier
                facao = d[3].replace("CORACAO_", "")
                coracao_id = CORACOES_MAP.get(facao, "")
                qty_coracoes = get_coracoes_qty(tier)
                
                if coracao_id and coracao_id in precos_cache:
                    info = precos_cache[coracao_id]
                    custo += info["price"] * qty_coracoes * quantidade
                    detalhes.append(f"{qty_coracoes * quantidade}x Coração {facao}: {info['price']:,} ({info['city']})")
                else:
                    valid_craft = False
            else:
                # Recurso normal
                for rid in ids_recurso_variantes(tier, d[3], encanto):
                    if rid in precos_cache:
                        info = precos_cache[rid]
                        nome_recurso = NOMES_RECURSOS_TIER.get(d[3], {}).get(tier, d[3])
                        custo += info["price"] * d[4] * quantidade
                        detalhes.append(f"{d[4] * quantidade}x {nome_recurso}: {info['price']:,} ({info['city']})")
                        break
                else:
                    valid_craft = False

        if not valid_craft:
            continue

        # ================= ARTEFATO/ORNAMENTO =================
        if d[5]:
            art_id = id_item(tier, d[5], 0)
            if art_id in precos_cache:
                info = precos_cache[art_id]
                qtd_art = d[6] * quantidade
                custo += info["price"] * qtd_art
                detalhes.append(f"{qtd_art}x Ornamento: {info['price']:,} ({info['city']})")
            else:
                # Tenta buscar em múltiplas cidades se não achou no cache
                preco_art = get_historical_price(art_id, "Caerleon,FortSterling,Thetford,Lymhurst,Bridgewatch,Martlock")
                if preco_art > 0:
                    qtd_art = d[6] * quantidade
                    custo += preco_art * qtd_art
                    detalhes.append(f"{qtd_art}x Ornamento: {preco_art:,.0f} (Market Geral)")
                else:
                    valid_craft = False

        if not valid_craft:
            continue

        custo_final = int(custo)
        venda_total = int(preco_venda_bm * quantidade)
        lucro = int((venda_total * 0.935) - custo_final)  # 6.5% taxa BM

        resultados.append((nome, lucro, venda_total, custo_final, detalhes, "Black Market"))

    my_bar.empty()

    resultados.sort(key=lambda x: x[1], reverse=True)

    if not resultados:
        st.warning("⚠️ Nenhum dado disponível para os itens selecionados.")
    else:
        st.subheader(f"📊 {len(resultados)} Itens - {categoria.upper()} T{tier}.{encanto}")

        for nome, lucro, venda, custo, detalhes, fonte in resultados:
            perc_lucro = (lucro / custo) * 100 if custo > 0 else 0
            cidade_foco = identificar_cidade_bonus(nome)
            cor_destaque = "#2ecc71" if lucro > 0 else "#e74c3c"

            st.markdown(f"""
            <div class="item-card-custom" style="border-left: 8px solid {cor_destaque};">
                <div style="font-weight: bold; font-size: 1.2rem; margin-bottom: 10px; color: {cor_destaque};">
                    ⚔️ {nome} [T{tier}.{encanto}] x{quantidade}
                </div>
                <div style="font-size: 1.05rem; margin-bottom: 8px;">
                    <span style="color: {cor_destaque}; font-weight: bold; font-size: 1.2rem;">
                        💰 Lucro: {lucro:,} ({perc_lucro:.1f}%)
                    </span>
                    <br><b>Custo:</b> {custo:,} | <b>Venda:</b> {venda:,}
                </div>
                <div style="font-size: 0.95rem; color: #cbd5e1; margin-bottom: 10px;">
                    📍 <b>Craft:</b> {cidade_foco} | 🕒 {fonte}
                </div>
                <div style="background: rgba(0,0,0,0.4); padding: 12px; border-radius: 8px; font-size: 0.9rem;">
                    📦 <b>Componentes:</b><br>
                    {" | ".join(detalhes)}
                </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("---")
st.caption("Radar Craft Albion - Desenvolvido para análise de mercado")
