import streamlit as st
import requests
import json
from datetime import datetime, timezone

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Radar Craft Albion", layout="wide")

# --- 2. CSS CUSTOMIZADO (Visual Dark Moderno) ---
st.markdown("""
<style>
.stApp { background: radial-gradient(circle at top, #0f172a, #020617); color: #e5e7eb; }
.block-container { background-color: rgba(15, 23, 42, 0.94); padding: 2.5rem; border-radius: 22px; }
.card { background-color: #1e293b; padding: 20px; border-radius: 12px; border-left: 6px solid #3b82f6; margin-bottom: 15px; border: 1px solid #334155; }
.recurso-item { font-size: 0.85em; color: #94a3b8; list-style: none; }
.lucro-positivo { color: #2ecc71; font-weight: bold; font-size: 1.1em; }
.cidade-label { color: #f59e0b; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 3. DATABASE E CONFIGURAÇÕES ---
API_URL = "https://west.albion-online-data.com/api/v2/stats/prices/"
CIDADES = ["Martlock", "Thetford", "FortSterling", "Lymhurst", "Bridgewatch", "Brecilien", "Caerleon", "Black Market"]
RECURSO_MAP = {"Tecido Fino": "CLOTH", "Couro Trabalhado": "LEATHER", "Barra de Aço": "METALBAR", "Tábuas de Pinho": "PLANKS"}
NUTRICAO_MAP = {"ARMOR": 44.4, "HEAD": 22.2, "SHOES": 22.2, "MAIN": 44.4, "2H": 88.8, "OFF": 22.2, "KNUCKLES": 44.4}

BONUS_CIDADE = {
    "Lymhurst": ["BOW", "ARCANE", "LEATHER"],
    "Bridgewatch": ["CROSSBOW", "DAGGER", "PLATE"],
    "Martlock": ["AXE", "SHOES", "STAFF"],
    "Thetford": ["MACE", "NATURE", "FIRE"],
    "Fort Sterling": ["HAMMER", "SPEAR", "HOLY"],
    "Caerleon": ["KNUCKLES", "SHAPESHIFTER"],
    "Brecilien": ["CAPE", "BAG"]
}

# Banco de Dados Unificado (O que estava faltando no 2º código)
ITENS_DB = {
    # --- OFF-HANDS E TOCHAS ---
    "TOMO DE FEITIÇOS": ["OFF_BOOK", "Tecido Fino", 4, "Couro Trabalhado", 4, None, 0],
    "OLHO DOS SEGREDOS": ["OFF_ORB_HELL", "Tecido Fino", 4, "Couro Trabalhado", 4, "ARTEFACT_OFF_ORB_HELL", 1],
    "MUISEC": ["OFF_LAMP_HELL", "Tecido Fino", 4, "Couro Trabalhado", 4, "ARTEFACT_OFF_LAMP_HELL", 1],
    "RAIZ MESTRA": ["OFF_DEMONSKULL_HELL", "Tecido Fino", 4, "Couro Trabalhado", 4, "ARTEFACT_OFF_DEMONSKULL_HELL", 1],
    "INCENSÁRIO CELESTE": ["OFF_TOWERSHIELD_HELL", "Tecido Fino", 4, "Couro Trabalhado", 4, "ARTEFACT_OFF_TOWERSHIELD_HELL", 1],
    "GRUMÓRIO ESTAGNADO": ["OFF_SHIELD_HELL", "Tecido Fino", 4, "Couro Trabalhado", 4, "ARTEFACT_OFF_SHIELD_HELL", 1],
    "TOCHA": ["OFF_TORCH", "Tábuas de Pinho", 4, "Tecido Fino", 4, None, 0],
    "BRUMÁRIO": ["OFF_HORN_KEEPER", "Tábuas de Pinho", 4, "Tecido Fino", 4, "ARTEFACT_OFF_HORN_KEEPER", 1],
    "BENGALA MALIGNA": ["OFF_JESTERCANE_HELL", "Tábuas de Pinho", 4, "Tecido Fino", 4, "ARTEFACT_OFF_JESTERCANE_HELL", 1],
    "LUME CRIPTICO": ["OFF_LAMP_UNDEAD", "Tábuas de Pinho", 4, "Tecido Fino", 4, "ARTEFACT_OFF_LAMP_UNDEAD", 1],
    "CETRO SAGRADO": ["OFF_CENSER_AVALON", "Tábuas de Pinho", 4, "Tecido Fino", 4, "ARTEFACT_OFF_CENSER_AVALON", 1],
    "TOCHA CHAMA AZUL": ["OFF_LAMP_CRYSTAL", "Tábuas de Pinho", 4, "Tecido Fino", 4, "QUESTITEM_TOKEN_CRYSTAL_LAMP", 1],
    # --- BOTAS DE PLACA ---
    "BOTAS DE SOLDADO": ["SHOES_PLATE_SET1", "Barra de Aço", 8, None, 0, None, 0],
    "BOTAS DE CAVALEIRO": ["SHOES_PLATE_SET2", "Barra de Aço", 8, None, 0, None, 0],
    "BOTAS DE GUARDIÃO": ["SHOES_PLATE_SET3", "Barra de Aço", 8, None, 0, None, 0],
    "BOTAS REAIS": ["SHOES_PLATE_ROYAL", "Barra de Aço", 8, None, 0, "QUESTITEM_TOKEN_ROYAL", 2],
    "BOTAS DE GUARDA-TUMBAS": ["SHOES_PLATE_UNDEAD", "Barra de Aço", 8, None, 0, "ARTEFACT_SHOES_PLATE_UNDEAD", 1],
    "BOTAS DEMÔNIAS": ["SHOES_PLATE_HELL", "Barra de Aço", 8, None, 0, "ARTEFACT_SHOES_PLATE_HELL", 1],
    "BOTAS JUDICANTES": ["SHOES_PLATE_KEEPER", "Barra de Aço", 8, None, 0, "ARTEFACT_SHOES_PLATE_KEEPER", 1],
    "BOTAS DE TECELÃO": ["SHOES_PLATE_AVALON", "Barra de Aço", 8, None, 0, "ARTEFACT_SHOES_PLATE_AVALON", 1],
    "BOTAS DA BRAVURA": ["SHOES_PLATE_CRYSTAL", "Barra de Aço", 8, None, 0, "QUESTITEM_TOKEN_CRYSTAL_SHOES_PLATE", 1],
    # --- ARMADURAS DE PLACA ---
    "ARMADURA DE SOLDADO": ["ARMOR_PLATE_SET1", "Barra de Aço", 16, None, 0, None, 0],
    "ARMADURA DE CAVALEIRO": ["ARMOR_PLATE_SET2", "Barra de Aço", 16, None, 0, None, 0],
    "ARMADURA DE GUARDIÃO": ["ARMOR_PLATE_SET3", "Barra de Aço", 16, None, 0, None, 0],
    "ARMADURA REAL": ["ARMOR_PLATE_ROYAL", "Barra de Aço", 16, None, 0, "QUESTITEM_TOKEN_ROYAL", 4],
    "ARMADURA DE GUARDA-TUMBAS": ["ARMOR_PLATE_UNDEAD", "Barra de Aço", 16, None, 0, "ARTEFACT_ARMOR_PLATE_UNDEAD", 1],
    "ARMADURA DEMÔNIA": ["ARMOR_PLATE_HELL", "Barra de Aço", 16, None, 0, "ARTEFACT_ARMOR_PLATE_HELL", 1],
    "ARMADURA JUDICANTE": ["ARMOR_PLATE_KEEPER", "Barra de Aço", 16, None, 0, "ARTEFACT_ARMOR_PLATE_KEEPER", 1],
    "ARMADURA DE TECELÃO": ["ARMOR_PLATE_AVALON", "Barra de Aço", 16, None, 0, "ARTEFACT_ARMOR_PLATE_AVALON", 1],
    "ARMADURA DA BRAVURA": ["ARMOR_PLATE_CRYSTAL", "Barra de Aço", 16, None, 0, "QUESTITEM_TOKEN_CRYSTAL_ARMOR_PLATE", 1],
    # --- ESPADAS ---
    "ESPADA LARGA": ["MAIN_SWORD", "Barra de Aço", 16, "Couro Trabalhado", 8, None, 0],
    "MONTANTE": ["2H_CLAYMORE", "Barra de Aço", 20, "Couro Trabalhado", 12, None, 0],
    "ESPADAS DUPLAS": ["2H_DUALSWORD", "Barra de Aço", 20, "Couro Trabalhado", 12, None, 0],
    "LÂMINA ACIARADA": ["MAIN_SWORD_HELL", "Barra de Aço", 16, "Couro Trabalhado", 8, "ARTEFACT_MAIN_SWORD_HELL", 1],
    "ESPADA ENTALHADA": ["2H_CLEAVER_SWORD", "Barra de Aço", 20, "Couro Trabalhado", 12, "ARTEFACT_2H_CLEAVER_SWORD", 1],
    "PAR DE GALATINAS": ["2H_DUALSWORD_HELL", "Barra de Aço", 20, "Couro Trabalhado", 12, "ARTEFACT_2H_DUALSWORD_HELL", 1],
    "CRIA-REAIS": ["2H_CLAYMORE_AVALON", "Barra de Aço", 20, "Couro Trabalhado", 12, "ARTEFACT_2H_CLAYMORE_AVALON", 1],
    "LÂMINA DA INFINIDADE": ["2H_SWORD_CRYSTAL", "Barra de Aço", 16, "Couro Trabalhado", 8, "QUESTITEM_TOKEN_CRYSTAL_SWORD", 1],
    # [ADICIONE AS OUTRAS CATEGORIAS AQUI IGUAL AO PRIMEIRO CÓDIGO]
}

FILTROS = {
    "armadura_placa": lambda k, v: "ARMOR_PLATE" in v[0],
    "armadura_couro": lambda k, v: "ARMOR_LEATHER" in v[0],
    "armadura_pano": lambda k, v: "ARMOR_CLOTH" in v[0],
    "botas_placa": lambda k, v: "SHOES_PLATE" in v[0],
    "capacete_placa": lambda k, v: "HEAD_PLATE" in v[0],
    "armas": lambda k, v: v[0].startswith(("MAIN_", "2H_")),
    "secundarias": lambda k, v: v[0].startswith("OFF_"),
}

# --- 4. FUNÇÕES DE LÓGICA ---
def calcular_dados_tempo(data_iso):
    if not data_iso or data_iso.startswith("0001"):
        return "Sem Dados", False
    try:
        clean_date = data_iso.split(".")[0].replace("Z", "")
        data_api = datetime.fromisoformat(clean_date).replace(tzinfo=timezone.utc)
        agora = datetime.now(timezone.utc)
        diff = (agora - data_api).total_seconds() / 3600
        return f"{int(diff)}h", (diff < 6)
    except:
        return "N/A", False

def id_item(tier, base, enc):
    return f"T{tier}_{base}@{enc}" if enc > 0 else f"T{tier}_{base}"

def identificar_cidade_bonus(item_internal_id):
    for cidade, chaves in BONUS_CIDADE.items():
        if any(chave in item_internal_id for chave in chaves):
            return cidade
    return "Caerleon (Geral)"

# --- 5. INTERFACE SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Configurações")
    categoria_sel = st.selectbox("Categoria", list(FILTROS.keys()))
    tier = st.number_input("Tier", 4, 8, 4)
    encanto = st.number_input("Encanto", 0, 4, 0)
    quantidade = st.number_input("Quantidade", 1, 999, 1)
    usar_foco = st.checkbox("Usar Foco (43.5% RRR)", value=False)
    taxa_loja = st.number_input("Taxa da Loja (por 100 nut.)", 0, 5000, 500)
    btn_scan = st.button("🚀 ESCANEAR AGORA")

# --- 6. EXECUÇÃO DO SCAN ---
if btn_scan:
    filtro_func = FILTROS[categoria_sel]
    itens_filtrados = {k: v for k, v in ITENS_DB.items() if filtro_func(k, v)}
    
    # Gerar IDs para busca na API
    ids_busca = set()
    for d in itens_filtrados.values():
        ids_busca.add(id_item(tier, d[0], encanto))
        # Recursos base
        for recurso in [d[1], d[3]]:
            if recurso:
                base_r = f"T{tier}_{RECURSO_MAP[recurso]}"
                ids_busca.add(f"{base_r}@{encanto}" if encanto > 0 else base_r)
        # Artefatos
        if d[5]: ids_busca.add(f"T{tier}_{d[5]}")

    try:
        url_completa = f"{API_URL}{','.join(ids_busca)}?locations={','.join(CIDADES)}"
        response = requests.get(url_completa).json()
        
        precos_itens = {}
        precos_recursos = {}

        # Organizar preços da API
        for p in response:
            pid, city = p["item_id"], p["city"]
            price = p["buy_price_max"] if city == "Black Market" else p["sell_price_min"]
            date_info = p["buy_price_max_date"] if city == "Black Market" else p["sell_price_min_date"]
            
            if price <= 10: continue

            # Se for o item final (ex: T4_ARMOR_PLATE_SET1)
            is_final = any(pid == id_item(tier, d[0], encanto) for d in itens_filtrados.values())
            
            if is_final:
                if pid not in precos_itens or price > precos_itens[pid]["price"]:
                    tempo_str, fresco = calcular_dados_tempo(date_info)
                    precos_itens[pid] = {"price": price, "city": city, "tempo": tempo_str, "fresco": fresco}
            else:
                if pid not in precos_recursos or price < precos_recursos[pid]["price"]:
                    precos_recursos[pid] = {"price": price, "city": city}

        # 7. CÁLCULO DE RESULTADOS
        rrr = 0.565 if usar_foco else 0.752
        resultados = []

        for nome, d in itens_filtrados.items():
            item_id = id_item(tier, d[0], encanto)
            if item_id not in precos_itens: continue

            custo_materiais = 0
            detalhes_mats = []
            erro_mat = False

            # Cálculo de Materiais 1 e 2
            for recurso, qtd in [(d[1], d[2]), (d[3], d[4])]:
                if not recurso or qtd == 0: continue
                rid = f"T{tier}_{RECURSO_MAP[recurso]}"
                rid_full = f"{rid}@{encanto}" if encanto > 0 else rid
                
                if rid_full in precos_recursos:
                    p_m = precos_recursos[rid_full]["price"]
                    custo_materiais += p_m * (qtd * quantidade)
                    detalhes_mats.append(f"<li>{qtd*quantidade}x {recurso}: {p_m:,} silver</li>")
                else:
                    erro_mat = True; break
            
            if erro_mat: continue

            # Cálculo de Artefatos
            if d[5]:
                art_id = f"T{tier}_{d[5]}"
                if art_id in precos_recursos:
                    p_a = precos_recursos[art_id]["price"]
                    custo_materiais += p_a * (d[6] * quantidade)
                    detalhes_mats.append(f"<li>{d[6]*quantidade}x Artefato: {p_a:,} silver</li>")
                else: continue

            # Cálculo de Taxa de Nutrição
            tipo_item = d[0].split("_")[0] # Pega ARMOR, HEAD, etc
            nutricao_base = NUTRICAO_MAP.get(tipo_item, 44.4)
            custo_taxa = (nutricao_base * tier * (taxa_loja / 100)) * quantidade

            investimento = int((custo_materiais * rrr) + custo_taxa)
            venda_bruta = precos_itens[item_id]["price"] * quantidade
            lucro = int((venda_bruta * 0.935) - investimento)
            roi = (lucro / investimento) * 100 if investimento > 0 else 0

            if lucro > 0:
                resultados.append({
                    "nome": nome, "lucro": lucro, "venda": venda_bruta, "roi": roi,
                    "cidade_venda": precos_itens[item_id]["city"],
                    "tempo": precos_itens[item_id]["tempo"],
                    "fresco": precos_itens[item_id]["fresco"],
                    "cidade_craft": identificar_cidade_bonus(d[0]),
                    "mats": "".join(detalhes_mats)
                })

        # 8. EXIBIÇÃO
        st.subheader(f"📊 Resultados para T{tier}.{encanto}")
        if not resultados:
            st.warning("Nenhum item lucrativo encontrado com os dados atuais.")
        else:
            resultados.sort(key=lambda x: x["lucro"], reverse=True)
            for res in resultados[:15]:
                tempo_class = "fresh-data" if res["fresco"] else "old-data"
                st.markdown(f"""
                <div class="card">
                    <div style="display: flex; justify-content: space-between;">
                        <b>💎 {res['nome']}</b>
                        <span class="{tempo_class}">🕒 {res['tempo']}</span>
                    </div>
                    <div style="margin-top: 10px;">
                        <span class="lucro-positivo">💰 Lucro: {res['lucro']:,} silver</span> | <b>ROI: {res['roi']:.1f}%</b><br>
                        🛒 Venda: <span class="cidade-label">{res['cidade_venda']}</span> | 
                        🔨 Local Craft: <span class="cidade-label">{res['cidade_craft']}</span>
                    </div>
                    <details style="margin-top: 10px; color: #94a3b8; font-size: 0.9em;">
                        <summary>Ver Detalhes dos Materiais</summary>
                        <ul style="padding-left: 20px; margin-top: 5px;">{res['mats']}</ul>
                    </details>
                </div>
                """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Erro ao processar dados: {e}")