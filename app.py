import streamlit as st
import requests
from datetime import datetime, timezone

# ================= CONFIGURAÇÃO DA PÁGINA =================
st.set_page_config(page_title="Radar Craft — Urban Space", layout="wide")

# CSS Profissional - Estilo Dark Mode Injetado
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    .item-card {
        background-color: #1c2128;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        color: white;
    }
    .lucro-valor { color: #2ecc71; font-weight: bold; font-size: 1.4em; }
    .venda-valor { color: #3498db; font-weight: bold; }
    .custo-valor { color: #e74c3c; font-weight: bold; }
    .recurso-texto { color: #8b949e; font-size: 0.9em; line-height: 1.4; }
    .badge-bonus { background-color: #f1c40f; color: #000; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 0.8em; }
</style>
""", unsafe_allow_html=True)

# ================= DATABASE & DICIONÁRIOS =================
API_URL = "https://west.albion-online-data.com/api/v2/stats/prices/"
CIDADES = ["Martlock", "Thetford", "FortSterling", "Lymhurst", "Bridgewatch", "Brecilien", "Caerleon", "Black Market"]

RECURSO_MAP = {
    "Tecido Fino": "CLOTH", 
    "Couro Trabalhado": "LEATHER", 
    "Barra de Aço": "METALBAR", 
    "Tábuas de Pinho": "PLANKS"
}

BONUS_CIDADE = {
    "Martlock": ["AXE", "QUARTERSTAFF", "FROSTSTAFF", "SHOES_PLATE", "OFF_"],
    "Bridgewatch": ["CROSSBOW", "DAGGER", "CURSEDSTAFF", "ARMOR_PLATE", "SHOES_CLOTH"],
    "Lymhurst": ["SWORD", "BOW", "ARCANESTAFF", "HEAD_LEATHER", "SHOES_LEATHER"],
    "Fort Sterling": ["HAMMER", "SPEAR", "HOLYSTAFF", "HEAD_PLATE", "ARMOR_CLOTH"],
    "Thetford": ["MACE", "NATURESTAFF", "FIRESTAFF", "ARMOR_LEATHER", "HEAD_CLOTH"],
    "Caerleon": ["KNUCKLES", "SHAPESHIFTER"]
}

ITENS_DB = {
    "TOMO DE FEITIÇOS": ["OFF_BOOK", "Tecido Fino", 4, "Couro Trabalhado", 4, None, 0],
    "OLHO DOS SEGREDOS": ["OFF_ORB_HELL", "Tecido Fino", 4, "Couro Trabalhado", 4, "ARTEFACT_OFF_ORB_HELL", 1],
    "MUISEC": ["OFF_LAMP_HELL", "Tecido Fino", 4, "Couro Trabalhado", 4, "ARTEFACT_OFF_LAMP_HELL", 1],
    "BOTAS DE SOLDADO": ["SHOES_PLATE_SET1", "Barra de Aço", 8, None, 0, None, 0],
    "ARMADURA DE SOLDADO": ["ARMOR_PLATE_SET1", "Barra de Aço", 16, None, 0, None, 0],
    "ARMADURA DE CAVALEIRO": ["ARMOR_PLATE_SET2", "Barra de Aço", 16, None, 0, None, 0],
    "ARMADURA DE GUARDIÃO": ["ARMOR_PLATE_SET3", "Barra de Aço", 16, None, 0, None, 0],
    "ARMADURA DEMÔNIA": ["ARMOR_PLATE_HELL", "Barra de Aço", 16, None, 0, "ARTEFACT_ARMOR_PLATE_HELL", 1],
    "ARMADURA DE GUARDA-TUMBAS": ["ARMOR_PLATE_UNDEAD", "Barra de Aço", 16, None, 0, "ARTEFACT_ARMOR_PLATE_UNDEAD", 1],
    "ARMADURA DE TECELÃO": ["ARMOR_PLATE_AVALON", "Barra de Aço", 16, None, 0, "ARTEFACT_ARMOR_PLATE_AVALON", 1],
    "ELMO DE SOLDADO": ["HEAD_PLATE_SET1", "Barra de Aço", 8, None, 0, None, 0],
    "CASACO MERCENÁRIO": ["ARMOR_LEATHER_SET1", "Couro Trabalhado", 16, None, 0, None, 0],
    "MACHADO DE GUERRA": ["MAIN_AXE", "Barra de Aço", 16, "Tábuas de Pinho", 8, None, 0],
    "ADAGA": ["MAIN_DAGGER", "Barra de Aço", 12, "Couro Trabalhado", 12, None, 0],
    "DESSANGRADOR": ["MAIN_DAGGER_HELL", "Barra de Aço", 16, "Couro Trabalhado", 8, "ARTEFACT_MAIN_DAGGER_HELL", 1],
}

# ================= FUNÇÕES AUXILIARES =================
def calcular_horas(data_iso):
    try:
        data_api = datetime.fromisoformat(data_iso.replace("Z", "+00:00"))
        diff = datetime.now(timezone.utc).replace(tzinfo=None) - data_api.replace(tzinfo=None)
        return int(diff.total_seconds() / 3600)
    except: return 999

def identificar_cidade_bonus(item_base):
    for cidade, chaves in BONUS_CIDADE.items():
        if any(chave in item_base for chave in chaves): return cidade
    return "Caerleon"

# ================= SIDEBAR UI =================
with st.sidebar:
    st.title("⚙️ Filtros")
    tier = st.number_input("Tier", 4, 8, 4)
    encanto = st.number_input("Encanto", 0, 4, 0)
    quantidade = st.number_input("Qtd para produzir", 1, 999, 1)
    taxa_retorno = st.slider("% Retorno de Recurso", 0.0, 50.0, 24.8) / 100
    st.divider()
    btn = st.button("🚀 ESCANEAR BLACK MARKET", use_container_width=True)

# ================= LÓGICA DE SCANNER =================
if btn:
    ids_busca = set()
    for d in ITENS_DB.values():
        # ID do Item
        item_id = f"T{tier}_{d[0]}"
        ids_busca.add(f"{item_id}@{encanto}" if encanto > 0 else item_id)
        # ID dos Recursos
        for res_nome in [d[1], d[3]]:
            if res_nome:
                res_id = f"T{tier}_{RECURSO_MAP[res_nome]}"
                ids_busca.add(f"{res_id}@{encanto}" if encanto > 0 else res_id)
        # ID Artefato
        if d[5]: ids_busca.add(f"T{tier}_{d[5]}")

    with st.spinner('Buscando preços atualizados...'):
        try:
            response = requests.get(f"{API_URL}{','.join(ids_busca)}?locations={','.join(CIDADES)}", timeout=15)
            data = response.json()
        except:
            st.error("Erro ao conectar com a API de Dados.")
            st.stop()

    precos_itens = {}
    precos_recursos = {}

    for p in data:
        pid, city = p["item_id"], p["city"]
        price = p["buy_price_max"] if city == "Black Market" else p["sell_price_min"]
        
        if price <= 0: continue

        if city == "Black Market":
            if pid not in precos_itens or price > precos_itens[pid]["price"]:
                precos_itens[pid] = {"price": price, "horas": calcular_horas(p["buy_price_max_date"])}
        else:
            if pid not in precos_recursos or price < precos_recursos[pid]["price"]:
                precos_recursos[pid] = {"price": price, "city": city}

    # Gerar Resultados
    resultados = []
    for nome, d in ITENS_DB.items():
        item_id = f"T{tier}_{d[0]}@{encanto}" if encanto > 0 else f"T{tier}_{d[0]}"
        if item_id not in precos_itens: continue

        custo_bruto = 0
        txt_recursos = []
        
        # Calcular recursos principais
        falta_dado = False
        for res_nome, qtd in [(d[1], d[2]), (d[3], d[4])]:
            if not res_nome: continue
            rid = f"T{tier}_{RECURSO_MAP[res_nome]}@{encanto}" if encanto > 0 else f"T{tier}_{RECURSO_MAP[res_nome]}"
            if rid in precos_recursos:
                preco_res = precos_recursos[rid]["price"]
                custo_bruto += preco_res * qtd * quantidade
                txt_recursos.append(f"📦 {qtd*quantidade}x {res_nome}: {preco_res:,} ({precos_recursos[rid]['city']})")
            else: falta_dado = True

        # Calcular artefato
        if d[5]:
            aid = f"T{tier}_{d[5]}"
            if aid in precos_recursos:
                preco_art = precos_recursos[aid]["price"]
                custo_bruto += preco_art * d[6] * quantidade
                txt_recursos.append(f"💎 {d[6]*quantidade}x Artefato: {preco_art:,} ({precos_recursos[aid]['city']})")
            else: falta_dado = True

        if falta_dado: continue

        investimento = int(custo_bruto * (1 - taxa_retorno))
        venda_total = precos_itens[item_id]["price"] * quantidade
        lucro_liquido = int((venda_total * 0.935) - investimento)
        pct = round((lucro_liquido / investimento) * 100, 1) if investimento > 0 else 0

        if lucro_liquido > 0:
            resultados.append({
                "nome": nome, "lucro": lucro_liquido, "pct": pct, "venda": venda_total,
                "invest": investimento, "recursos": txt_recursos, "bonus": identificar_cidade_bonus(d[0]),
                "h": precos_itens[item_id]["horas"]
            })

    # Exibir Cards
    if resultados:
        resultados.sort(key=lambda x: x["lucro"], reverse=True)
        st.success(f"Encontradas {len(resultados)} oportunidades lucrativas!")
        
        for r in resultados:
            html_recursos = "".join([f"<div>{linha}</div>" for linha in r['recursos']])
            
            # O código abaixo é escrito sem recuo à esquerda para o Streamlit não achar que é bloco de código
            card = f"""
<div class="item-card">
<div style="display: flex; justify-content: space-between; align-items: center;">
<h2 style="margin:0; color: white; font-size: 1.3em;">⚔️ {r['nome']}</h2>
<div style="text-align: right;">
<span class="lucro-valor">+{r['lucro']:,} silver</span><br>
<span style="color: #2ecc71; font-weight: bold;">📈 {r['pct']}% Lucro</span>
</div>
</div>
<hr style="opacity: 0.1; margin: 12px 0;">
<div style="display: flex; flex-wrap: wrap; gap: 20px;">
<div style="flex: 1; min-width: 250px;">
<p style="margin: 4px 0;">🏗️ <b>Bônus de Cidade:</b> <span class="badge-bonus">{r['bonus']}</span></p>
<p style="margin: 4px 0;">💰 <b>Investimento:</b> <span class="custo-valor">{r['invest']:,} silver</span></p>
<p style="margin: 4px 0;">🏛️ <b>Venda BM Total:</b> <span class="venda-valor">{r['venda']:,}</span> <small>({r['h']}h atrás)</small></p>
</div>
<div style="flex: 1; min-width: 250px; background: #0d1117; padding: 12px; border-radius: 8px;">
<b style="font-size: 0.8em; color: #8b949e; text-transform: uppercase;">Onde Comprar:</b>
<div class="recurso-texto" style="margin-top: 8px;">
{html_recursos}
</div>
</div>
</div>
</div>
"""
            st.markdown(card, unsafe_allow_html=True)
    else:
        st.warning("Nenhum lucro detectado com os filtros atuais.")