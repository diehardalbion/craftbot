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
            <h2 style="margin:0; color: #2ecc71;">R$ 20,00</h2>
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
    # Cidades
    "Bridgewatch": "T1_FACTION_STEPPE_TOKEN_1",
    "Fort Sterling": "T1_FACTION_MOUNTAIN_TOKEN_1",
    "Lymhurst": "T1_FACTION_FOREST_TOKEN_1",
    "Martlock": "T1_FACTION_HIGHLAND_TOKEN_1",
    "Thetford": "T1_FACTION_SWAMP_TOKEN_1",
    "Caerleon": "T1_FACTION_CAERLEON_TOKEN_1",
    # Facções
    "HEREGE": "T1_FACTION_FOREST_TOKEN_1",
    "MORTAVIVA": "T1_FACTION_MOUNTAIN_TOKEN_1",
    "PROTETORA": "T1_FACTION_HIGHLAND_TOKEN_1",
    "MORGANA": "T1_FACTION_SWAMP_TOKEN_1",
    "DEMONIACA": "T1_FACTION_STEPPE_TOKEN_1"
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
    "Capa de Bridgewatch": ["CAPEITEM_FW_BRIDGEWATCH", "CAPE", 1, "CORACAO_Bridgewatch", 1, "CAPEITEM_FW_BRIDGEWATCH_BP", 1],
    
    # ================= CAPAS FORT STERLING =================
    "Capa de Fort Sterling": ["CAPEITEM_FW_FORTSTERLING", "CAPE", 1, "CORACAO_Fort Sterling", 1, "CAPEITEM_FW_FORTSTERLING_BP", 1],
    
    # ================= CAPAS LYMHURST =================
    "Capa de Lymhurst": ["CAPEITEM_FW_LYMHURST", "CAPE", 1, "CORACAO_Lymhurst", 1, "CAPEITEM_FW_LYMHURST_BP", 1],
    
    # ================= CAPAS MARTLOCK =================
    "Capa de Martlock": ["CAPEITEM_FW_MARTLOCK", "CAPE", 1, "CORACAO_Martlock", 1, "CAPEITEM_FW_MARTLOCK_BP", 1],
    
    # ================= CAPAS THETFORD =================
    "Capa de Thetford": ["CAPEITEM_FW_THETFORD", "CAPE", 1, "CORACAO_Thetford", 1, "CAPEITEM_FW_THETFORD_BP", 1],
    
    # ================= CAPAS CAERLEON =================
    "Capa de Caerleon": ["CAPEITEM_FW_CAERLEON", "CAPE", 1, "CORACAO_Caerleon", 1, "CAPEITEM_FW_CAERLEON_BP", 1],
    
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

    # ================= CAJADOS AMALDIÇOADOS (CURSED) =================
    "Cajado Amaldiçoado": ["MAIN_CURSEDSTAFF", "Tábuas de Pinho", 16, "Barra de Aço", 8, None, 0],
    "Cajado Amaldiçoado Elevado": ["2H_CURSEDSTAFF", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0],
    "Cajado Demoníaco": ["2H_DEMONICSTAFF", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0],
    "Cajado Execrado": ["MAIN_CURSEDSTAFF_UNDEAD", "Tábuas de Pinho", 16, "Barra de Aço", 8, "ARTEFACT_MAIN_CURSEDSTAFF_UNDEAD", 1],
    "Caveira Amaldiçoada": ["2H_SKULLPANE_HELL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_SKULLPANE_HELL", 1],
    "Cajado da Danação": ["2H_CURSEDSTAFF_MORGANA", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_CURSEDSTAFF_MORGANA", 1],
    "Chama-sombra": ["MAIN_CURSEDSTAFF_AVALON", "Tábuas de Pinho", 16, "Barra de Aço", 8, "ARTEFACT_MAIN_CURSEDSTAFF_AVALON", 1],
    "Cajado Pútrido": ["2H_CURSEDSTAFF_CRYSTAL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "QUESTITEM_TOKEN_CRYSTAL_CURSEDSTAFF", 1],

    # ================= BORDÕES (QUARTERSTAFF) =================
    "Bordão": ["2H_QUARTERSTAFF", "Barra de Aço", 12, "Couro Trabalhado", 20, None, 0],
    "BOLSA": ["BAG", "Tecido Fino", 8, "Couro Trabalhado", 8, None, 0],
    "Cajado Férreo": ["2H_IRONCLADSTAFF", "Barra de Aço", 12, "Couro Trabalhado", 20, None, 0],
    "Cajado Biliminado": ["2H_DOUBLEBLADEDSTAFF", "Barra de Aço", 12, "Couro Trabalhado", 20, None, 0],
    "Cajado de Monge Negro": ["2H_COMBATSTAFF_MORGANA", "Barra de Aço", 12, "Couro Trabalhado", 20, "ARTEFACT_2H_COMBATSTAFF_MORGANA", 1],
    "Segamímica": ["2H_TWINSCYTHE_HELL", "Barra de Aço", 12, "Couro Trabalhado", 20, "ARTEFACT_2H_TWINSCYTHE_HELL", 1],
    "Cajado do Equilíbrio": ["2H_ROCKSTAFF_KEEPER", "Barra de Aço", 12, "Couro Trabalhado", 20, "ARTEFACT_2H_ROCKSTAFF_KEEPER", 1],
    "Buscador do Graal": ["2H_QUARTERSTAFF_AVALON", "Barra de Aço", 12, "Couro Trabalhado", 20, "ARTEFACT_2H_QUARTERSTAFF_AVALON", 1],
    "Lâminas Gêmeas Fantasmagóricas": ["2H_QUARTERSTAFF_CRYSTAL", "Barra de Aço", 12, "Couro Trabalhado", 20, "QUESTITEM_TOKEN_CRYSTAL_QUARTERSTAFF", 1],

    # ================= CAJADOS DE GELO (FROST) =================
    "Cajado de Gelo": ["MAIN_FROSTSTAFF", "Tábuas de Pinho", 16, "Barra de Aço", 8, None, 0],
    "Cajado de Gelo Elevado": ["2H_FROSTSTAFF", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0],
    "Cajado Glacial": ["2H_GLACIALSTAFF", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0],
    "Cajado Enregelante": ["MAIN_FROSTSTAFF_DEEPFREEZE", "Tábuas de Pinho", 16, "Barra de Aço", 8, "ARTEFACT_MAIN_FROSTSTAFF_DEEPFREEZE", 1],
    "Cajado de Sincelo": ["2H_ICE_CRYSTAL_HELL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_ICE_CRYSTAL_HELL", 1],
    "Prisma Geleterno": ["2H_RAMPY_FROST_KEEPER", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_RAMPY_FROST_KEEPER", 1],
    "Uivo Frio": ["MAIN_FROSTSTAFF_AVALON", "Tábuas de Pinho", 16, "Barra de Aço", 8, "ARTEFACT_MAIN_FROSTSTAFF_AVALON", 1],
    "Cajado Ártico": ["2H_FROSTSTAFF_CRYSTAL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "QUESTITEM_TOKEN_CRYSTAL_FROSTSTAFF", 1],

    # ================= CAJADOS ARCANOS (ARCANE) =================
    "Cajado Arcano": ["MAIN_ARCANESTAFF", "Tábuas de Pinho", 16, "Barra de Aço", 8, None, 0],
    "Cajado Arcano Elevado": ["2H_ARCANESTAFF", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0],
    "Cajado Enigmático": ["2H_ENIGMATICSTAFF", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0],
    "Cajado Feiticeiro": ["MAIN_ARCANESTAFF_UNDEAD", "Tábuas de Pinho", 16, "Barra de Aço", 8, "ARTEFACT_MAIN_ARCANESTAFF_UNDEAD", 1],
    "Cajado Oculto": ["2H_ARCANESTAFF_HELL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_ARCANESTAFF_HELL", 1],
    "Local Malévolo": ["2H_ENIGMATICSTAFF_MORGANA", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_ENIGMATICSTAFF_MORGANA", 1],
    "Som Equilibrado": ["2H_ARCANESTAFF_AVALON", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_ARCANESTAFF_AVALON", 1],
    "Cajado Astral": ["2H_ARCANESTAFF_CRYSTAL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "QUESTITEM_TOKEN_CRYSTAL_ARCANESTAFF", 1],

    # ================= CAJADOS SAGRADOS (HOLY) =================
    "Cajado Sagrado": ["MAIN_HOLYSTAFF", "Tábuas de Pinho", 16, "Tecido Fino", 8, None, 0],
    "Cajado Sagrado Elevado": ["2H_HOLYSTAFF", "Tábuas de Pinho", 20, "Tecido Fino", 12, None, 0],
    "Cajado Divino": ["2H_DIVINESTAFF", "Tábuas de Pinho", 20, "Tecido Fino", 12, None, 0],
    "Cajado Avivador": ["MAIN_HOLYSTAFF_MORGANA", "Tábuas de Pinho", 16, "Tecido Fino", 8, "ARTEFACT_MAIN_HOLYSTAFF_MORGANA", 1],
    "Cajado Corrompido": ["2H_HOLYSTAFF_HELL", "Tábuas de Pinho", 20, "Tecido Fino", 12, "ARTEFACT_2H_HOLYSTAFF_HELL", 1],
    "Cajado da Redenção": ["2H_HOLYSTAFF_UNDEAD", "Tábuas de Pinho", 20, "Tecido Fino", 12, "ARTEFACT_2H_HOLYSTAFF_UNDEAD", 1],
    "Queda Santa": ["MAIN_HOLYSTAFF_AVALON", "Tábuas de Pinho", 16, "Tecido Fino", 8, "ARTEFACT_MAIN_HOLYSTAFF_AVALON", 1],
    "Cajado Exaltado": ["2H_HOLYSTAFF_CRYSTAL", "Tábuas de Pinho", 20, "Tecido Fino", 12, "QUESTITEM_TOKEN_CRYSTAL_HOLYSTAFF", 1],

    # ================= CAJADOS DE FOGO (FIRE) =================
    "Cajado de Fogo": ["MAIN_FIRESTAFF", "Tábuas de Pinho", 16, "Barra de Aço", 8, None, 0],
    "Cajado de Fogo Elevado": ["2H_FIRESTAFF", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0],
    "Cajado Infernal": ["2H_INFERNALSTAFF", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0],
    "Cajado Incendiário": ["MAIN_FIRESTAFF_KEEPER", "Tábuas de Pinho", 16, "Barra de Aço", 8, "ARTEFACT_MAIN_FIRESTAFF_KEEPER", 1],
    "Cajado Sulfuroso": ["2H_FIRE_CRYSTAL_HELL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_FIRE_CRYSTAL_HELL", 1],
    "Cajado Fulgurante": ["2H_INFERNALSTAFF_MORGANA", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_INFERNALSTAFF_MORGANA", 1],
    "Canção da Alvorada": ["2H_FIRESTAFF_AVALON", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_FIRESTAFF_AVALON", 1],
    "Cajado do Andarilho Flamejante": ["MAIN_FIRESTAFF_CRYSTAL", "Tábuas de Pinho", 16, "Barra de Aço", 8, "QUESTITEM_TOKEN_CRYSTAL_FIRESTAFF", 1],

    # ================= CAJADOS DA NATUREZA (NATURE) =================
    "Cajado da Natureza": ["MAIN_NATURESTAFF", "Tábuas de Pinho", 16, "Tecido Fino", 8, None, 0],
    "Cajado da Natureza Elevado": ["2H_NATURESTAFF", "Tábuas de Pinho", 20, "Tecido Fino", 12, None, 0],
    "Cajado Selvagem": ["2H_WILDSTAFF", "Tábuas de Pinho", 20, "Tecido Fino", 12, None, 0],
    "Cajado Druídico": ["MAIN_NATURESTAFF_KEEPER", "Tábuas de Pinho", 16, "Tecido Fino", 8, "ARTEFACT_MAIN_NATURESTAFF_KEEPER", 1],
    "Cajado Pustulento": ["2H_NATURESTAFF_HELL", "Tábuas de Pinho", 20, "Tecido Fino", 12, "ARTEFACT_2H_NATURESTAFF_HELL", 1],
    "Cajado Rampante": ["2H_NATURESTAFF_KEEPER", "Tábuas de Pinho", 20, "Tecido Fino", 12, "ARTEFACT_2H_NATURESTAFF_KEEPER", 1],
    "Raiz Férrea": ["MAIN_NATURESTAFF_AVALON", "Tábuas de Pinho", 16, "Tecido Fino", 8, "ARTEFACT_MAIN_NATURESTAFF_AVALON", 1],
    "Cajado de Crosta Forjada": ["MAIN_NATURESTAFF_CRYSTAL", "Tábuas de Pinho", 16, "Tecido Fino", 8, "QUESTITEM_TOKEN_CRYSTAL_NATURESTAFF", 1],

    # ================= ARCOS (BOW) =================
    "Arco": ["2H_BOW", "Tábuas de Pinho", 32, None, 0, None, 0],
    "Arco de Guerra": ["2H_WARBOW", "Tábuas de Pinho", 32, None, 0, None, 0],
    "Arco Longo": ["2H_LONGBOW", "Tábuas de Pinho", 32, None, 0, None, 0],
    "Arco Sussurante": ["2H_BOW_KEEPER", "Tábuas de Pinho", 32, None, 0, "ARTEFACT_2H_BOW_KEEPER", 1],
    "Arco Plangente": ["2H_BOW_HELL", "Tábuas de Pinho", 32, None, 0, "ARTEFACT_2H_BOW_HELL", 1],
    "Arco Badônico": ["2H_BOW_UNDEAD", "Tábuas de Pinho", 32, None, 0, "ARTEFACT_2H_BOW_UNDEAD", 1],
    "Fura-bruma": ["2H_BOW_AVALON", "Tábuas de Pinho", 32, None, 0, "ARTEFACT_2H_BOW_AVALON", 1],
    "Arco do Andarilho Celeste": ["2H_BOW_CRYSTAL", "Tábuas de Pinho", 32, None, 0, "QUESTITEM_TOKEN_CRYSTAL_BOW", 1],
    
    # ================= CAJADOS TRANFORMAÇÃO (SHAPESHIFTER) =================
    "Cajado de Predador": ["2H_SHAPESHIFTER_PANT_TRACKER", "Tábuas de Pinho", 20, "Couro Trabalhado", 12, "ARTEFACT_2H_SHAPESHIFTER_PANT_TRACKER", 1],
    "Cajado Enraízado": ["2H_SHAPESHIFTER_TREANT", "Tábuas de Pinho", 20, "Couro Trabalhado", 12, "ARTEFACT_2H_SHAPESHIFTER_TREANT", 1],
    "Cajado Primitivo": ["2H_SHAPESHIFTER_BEAR", "Tábuas de Pinho", 20, "Couro Trabalhado", 12, "ARTEFACT_2H_SHAPESHIFTER_BEAR", 1],
    "Cajado da Lua de Sangue": ["2H_SHAPESHIFTER_WEREWOLF", "Tábuas de Pinho", 20, "Couro Trabalhado", 12, "ARTEFACT_2H_SHAPESHIFTER_WEREWOLF", 1],
    "Cajado Endemoniado": ["2H_SHAPESHIFTER_IMP", "Tábuas de Pinho", 20, "Couro Trabalhado", 12, "ARTEFACT_2H_SHAPESHIFTER_IMP", 1],
    "Cajado Rúnico da Terra": ["2H_SHAPESHIFTER_GOLEM", "Tábuas de Pinho", 20, "Couro Trabalhado", 12, "ARTEFACT_2H_SHAPESHIFTER_GOLEM", 1],
    "Cajado Invocador da Luz": ["2H_SHAPESHIFTER_EAGLE", "Tábuas de Pinho", 20, "Couro Trabalhado", 12, "ARTEFACT_2H_SHAPESHIFTER_EAGLE", 1],
    "Cajado Petrificante": ["2H_SHAPESHIFTER_CRYSTAL", "Tábuas de Pinho", 20, "Couro Trabalhado", 12, "QUESTITEM_TOKEN_CRYSTAL_SHAPESHIFTER", 1],
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
    "BOTAS DE SOLDADO": ["SHOES_PLATE_SET1", "Barra de Aço", 8, None, 0, None, 0],
    "BOTAS DE CAVALEIRO": ["SHOES_PLATE_SET2", "Barra de Aço", 8, None, 0, None, 0],
    "BOTAS DE GUARDIÃO": ["SHOES_PLATE_SET3", "Barra de Aço", 8, None, 0, None, 0],
    "BOTAS REAIS": ["SHOES_PLATE_ROYAL", "Barra de Aço", 8, None, 0, "QUESTITEM_TOKEN_ROYAL", 2],
    "BOTAS DE GUARDA-TUMBAS": ["SHOES_PLATE_UNDEAD", "Barra de Aço", 8, None, 0, "ARTEFACT_SHOES_PLATE_UNDEAD", 1],
    "BOTAS DEMÔNIAS": ["SHOES_PLATE_HELL", "Barra de Aço", 8, None, 0, "ARTEFACT_SHOES_PLATE_HELL", 1],
    "BOTAS JUDICANTES": ["SHOES_PLATE_KEEPER", "Barra de Aço", 8, None, 0, "ARTEFACT_SHOES_PLATE_KEEPER", 1],
    "BOTAS DE TECELÃO": ["SHOES_PLATE_AVALON", "Barra de Aço", 8, None, 0, "ARTEFACT_SHOES_PLATE_AVALON", 1],
    "BOTAS DA BRAVURA": ["SHOES_PLATE_CRYSTAL", "Barra de Aço", 8, None, 0, "QUESTITEM_TOKEN_CRYSTAL_SHOES_PLATE", 1],
    "ARMADURA DE SOLDADO": ["ARMOR_PLATE_SET1", "Barra de Aço", 16, None, 0, None, 0],
    "ARMADURA DE CAVALEIRO": ["ARMOR_PLATE_SET2", "Barra de Aço", 16, None, 0, None, 0],
    "ARMADURA DE GUARDIÃO": ["ARMOR_PLATE_SET3", "Barra de Aço", 16, None, 0, None, 0],
    "ARMADURA REAL": ["ARMOR_PLATE_ROYAL", "Barra de Aço", 16, None, 0, "QUESTITEM_TOKEN_ROYAL", 4],
    "ARMADURA DE GUARDA-TUMBAS": ["ARMOR_PLATE_UNDEAD", "Barra de Aço", 16, None, 0, "ARTEFACT_ARMOR_PLATE_UNDEAD", 1],
    "ARMADURA DEMÔNIA": ["ARMOR_PLATE_HELL", "Barra de Aço", 16, None, 0, "ARTEFACT_ARMOR_PLATE_HELL", 1],
    "ARMADURA JUDICANTE": ["ARMOR_PLATE_KEEPER", "Barra de Aço", 16, None, 0, "ARTEFACT_ARMOR_PLATE_KEEPER", 1],
    "ARMADURA DE TECELÃO": ["ARMOR_PLATE_AVALON", "Barra de Aço", 16, None, 0, "ARTEFACT_ARMOR_PLATE_AVALON", 1],
    "ARMADURA DA BRAVURA": ["ARMOR_PLATE_CRYSTAL", "Barra de Aço", 16, None, 0, "QUESTITEM_TOKEN_CRYSTAL_ARMOR_PLATE", 1],
    "ELMO DE SOLDADO": ["HEAD_PLATE_SET1", "Barra de Aço", 8, None, 0, None, 0],
    "ELMO DE CAVALEIRO": ["HEAD_PLATE_SET2", "Barra de Aço", 8, None, 0, None, 0],
    "ELMO DE GUARDIÃO": ["HEAD_PLATE_SET3", "Barra de Aço", 8, None, 0, None, 0],
    "ELMO REAL": ["HEAD_PLATE_ROYAL", "Barra de Aço", 8, None, 0, "QUESTITEM_TOKEN_ROYAL", 2],
    "ELMO DE GUARDA-TUMBAS": ["HEAD_PLATE_UNDEAD", "Barra de Aço", 8, None, 0, "ARTEFACT_HEAD_PLATE_UNDEAD", 1],
    "ELMO DEMÔNIO": ["HEAD_PLATE_HELL", "Barra de Aço", 8, None, 0, "ARTEFACT_HEAD_PLATE_HELL", 1],
    "ELMO JUDICANTE": ["HEAD_PLATE_KEEPER", "Barra de Aço", 8, None, 0, "ARTEFACT_HEAD_PLATE_KEEPER", 1],
    "ELMO DE TECELÃO": ["HEAD_PLATE_AVALON", "Barra de Aço", 8, None, 0, "ARTEFACT_HEAD_PLATE_AVALON", 1],
    "ELMO DA BRAVURA": ["HEAD_PLATE_CRYSTAL", "Barra de Aço", 8, None, 0, "QUESTITEM_TOKEN_CRYSTAL_HEAD_PLATE", 1],
    "Sapatos de Mercenário": ["SHOES_LEATHER_SET1", "Couro Trabalhado", 8, None, 0, None, 0],
    "Sapatos de Caçador": ["SHOES_LEATHER_SET2", "Couro Trabalhado", 8, None, 0, None, 0],
    "Sapatos de Assassino": ["SHOES_LEATHER_SET3", "Couro Trabalhado", 8, None, 0, None, 0],
    "Sapatos Reais": ["SHOES_LEATHER_ROYAL", "Couro Trabalhado", 8, None, 0, "QUESTITEM_TOKEN_ROYAL", 2],
    "Sapatos de Espreitador": ["SHOES_LEATHER_MORGANA", "Couro Trabalhado", 8, None, 0, "ARTEFACT_SHOES_LEATHER_MORGANA", 1],
    "Sapatos Espectrais": ["SHOES_LEATHER_UNDEAD", "Couro Trabalhado", 8, None, 0, "ARTEFACT_SHOES_LEATHER_UNDEAD", 1],
    "Sapatos de Andarilho da Névoa": ["SHOES_LEATHER_FEY", "Couro Trabalhado", 8, None, 0, "ARTEFACT_SHOES_LEATHER_FEY", 1],
    "Sapatos da Tenacidade": ["SHOES_LEATHER_CRYSTAL", "Couro Trabalhado", 8, None, 0, "QUESTITEM_TOKEN_CRYSTAL_SHOES_LEATHER", 1],
    "Casaco Mercenário": ["ARMOR_LEATHER_SET1", "Couro Trabalhado", 16, None, 0, None, 0],
    "Casaco de Caçador": ["ARMOR_LEATHER_SET2", "Couro Trabalhado", 16, None, 0, None, 0],
    "Casaco de Assassino": ["ARMOR_LEATHER_SET3", "Couro Trabalhado", 16, None, 0, None, 0],
    "Casaco Real": ["ARMOR_LEATHER_ROYAL", "Couro Trabalhado", 16, None, 0, "QUESTITEM_TOKEN_ROYAL", 4],
    "Casaco de Espreitador": ["ARMOR_LEATHER_MORGANA", "Couro Trabalhado", 16, None, 0, "ARTEFACT_ARMOR_LEATHER_MORGANA", 1],
    "Casaco Inferial": ["ARMOR_LEATHER_HELL", "Couro Trabalhado", 16, None, 0, "ARTEFACT_ARMOR_LEATHER_HELL", 1],
    "Casaco Espectral": ["ARMOR_LEATHER_UNDEAD", "Couro Trabalhado", 16, None, 0, "ARTEFACT_ARMOR_LEATHER_UNDEAD", 1],
    "Casaco de Andarilho da Névoa": ["ARMOR_LEATHER_FEY", "Couro Trabalhado", 16, None, 0, "ARTEFACT_ARMOR_LEATHER_FEY", 1],
    "Casaco da Tenacidade": ["ARMOR_LEATHER_CRYSTAL", "Couro Trabalhado", 16, None, 0, "QUESTITEM_TOKEN_CRYSTAL_ARMOR_LEATHER", 1],
    "Capuz de Mercenário de Mercenário": ["HEAD_LEATHER_SET1", "Couro Trabalhado", 8, None, 0, None, 0],
    "Capuz de Caçador": ["HEAD_LEATHER_SET2", "Couro Trabalhado", 8, None, 0, None, 0],
    "Capuz de Assassino": ["HEAD_LEATHER_SET3", "Couro Trabalhado", 8, None, 0, None, 0],
    "Capuz Real": ["HEAD_LEATHER_ROYAL", "Couro Trabalhado", 8, None, 0, "QUESTITEM_TOKEN_ROYAL", 2],
    "Capuz de Espreitador": ["HEAD_LEATHER_MORGANA", "Couro Trabalhado", 8, None, 0, "ARTEFACT_HEAD_LEATHER_MORGANA", 1],
    "Capuz Inferial": ["HEAD_LEATHER_HELL", "Couro Trabalhado", 8, None, 0, "ARTEFACT_HEAD_LEATHER_HELL", 1],
    "Capuz Espectral": ["HEAD_LEATHER_UNDEAD", "Couro Trabalhado", 8, None, 0, "ARTEFACT_HEAD_LEATHER_UNDEAD", 1],
    "Capuz de Andarilho da Névoa": ["HEAD_LEATHER_FEY", "Couro Trabalhado", 8, None, 0, "ARTEFACT_HEAD_LEATHER_FEY", 1],
    "Capuz da Tenacidade": ["HEAD_LEATHER_CRYSTAL", "Couro Trabalhado", 8, None, 0, "QUESTITEM_TOKEN_CRYSTAL_HEAD_LEATHER", 1],
    "Sandálias de Erudito": ["SHOES_CLOTH_SET1", "Tecido Fino", 8, None, 0, None, 0],
    "Sandálias de Clérigo": ["SHOES_CLOTH_SET2", "Tecido Fino", 8, None, 0, None, 0],
    "Sandálias de Mago": ["SHOES_CLOTH_SET3", "Tecido Fino", 8, None, 0, None, 0],
    "Sandálias Reais": ["SHOES_CLOTH_ROYAL", "Tecido Fino", 8, None, 0, "QUESTITEM_TOKEN_ROYAL", 2],
    "Sandálias de Druida": ["SHOES_CLOTH_KEEPER", "Tecido Fino", 8, None, 0, "ARTEFACT_SHOES_CLOTH_KEEPER", 1],
    "Sandálias Malévolas": ["SHOES_CLOTH_HELL", "Tecido Fino", 8, None, 0, "ARTEFACT_SHOES_CLOTH_HELL", 1],
    "Sandálias Sectárias": ["SHOES_CLOTH_MORGANA", "Tecido Fino", 8, None, 0, "ARTEFACT_SHOES_CLOTH_MORGANA", 1],
    "Sandálias Feéricas": ["SHOES_CLOTH_FEY", "Tecido Fino", 8, None, 0, "ARTEFACT_SHOES_CLOTH_FEY", 1],
    "Sandálias Da Pureza": ["SHOES_CLOTH_CRYSTAL", "Tecido Fino", 8, None, 0, "QUESTITEM_TOKEN_CRYSTAL_SHOES_CLOTH", 1],
    "Robe do Erudito": ["ARMOR_CLOTH_SET1", "Tecido Fino", 16, None, 0, None, 0],
    "Robe de Clérigo": ["ARMOR_CLOTH_SET2", "Tecido Fino", 16, None, 0, None, 0],
    "Robe de Mago": ["ARMOR_CLOTH_SET3", "Tecido Fino", 16, None, 0, None, 0],
    "Robe Real": ["ARMOR_CLOTH_ROYAL", "Tecido Fino", 16, None, 0, "QUESTITEM_TOKEN_ROYAL", 4],
    "Robe do Druída": ["ARMOR_CLOTH_KEEPER", "Tecido Fino", 16, None, 0, "ARTEFACT_ARMOR_CLOTH_KEEPER", 1],
    "Robe Malévolo": ["ARMOR_CLOTH_HELL", "Tecido Fino", 16, None, 0, "ARTEFACT_ARMOR_CLOTH_HELL", 1],
    "Robe Sectário": ["ARMOR_CLOTH_MORGANA", "Tecido Fino", 16, None, 0, "ARTEFACT_ARMOR_CLOTH_MORGANA", 1],
    "Robe Feérico": ["ARMOR_CLOTH_FEY", "Tecido Fino", 16, None, 0, "ARTEFACT_ARMOR_CLOTH_FEY", 1],
    "Robe da Pureza": ["ARMOR_CLOTH_CRYSTAL", "Tecido Fino", 16, None, 0, "QUESTITEM_TOKEN_CRYSTAL_ARMOR_CLOTH", 1],
    "Capote de Erudito": ["HEAD_CLOTH_SET1", "Tecido Fino", 8, None, 0, None, 0],
    "Capote de Clérigo": ["HEAD_CLOTH_SET2", "Tecido Fino", 8, None, 0, None, 0],
    "Capote de Mago": ["HEAD_CLOTH_SET3", "Tecido Fino", 8, None, 0, None, 0],
    "Capote Real": ["HEAD_CLOTH_ROYAL", "Tecido Fino", 8, None, 0, "QUESTITEM_TOKEN_ROYAL", 2],
    "Capote Druída": ["HEAD_CLOTH_KEEPER", "Tecido Fino", 8, None, 0, "ARTEFACT_HEAD_CLOTH_KEEPER", 1],
    "Capote Malévolo": ["HEAD_CLOTH_HELL", "Tecido Fino", 8, None, 0, "ARTEFACT_HEAD_CLOTH_HELL", 1],
    "Capote Sectário": ["HEAD_CLOTH_MORGANA", "Tecido Fino", 8, None, 0, "ARTEFACT_HEAD_CLOTH_MORGANA", 1],
    "Capote Feérico": ["HEAD_CLOTH_FEY", "Tecido Fino", 8, None, 0, "ARTEFACT_HEAD_CLOTH_FEY", 1],
    "Capote da Pureza": ["HEAD_CLOTH_CRYSTAL", "Tecido Fino", 8, None, 0, "QUESTITEM_TOKEN_CRYSTAL_HEAD_CLOTH", 1],
    "ESPADA LARGA": ["MAIN_SWORD", "Barra de Aço", 16, "Couro Trabalhado", 8, None, 0],
    "MONTANTE": ["2H_CLAYMORE", "Barra de Aço", 20, "Couro Trabalhado", 12, None, 0],
    "ESPADAS DUPLAS": ["2H_DUALSWORD", "Barra de Aço", 20, "Couro Trabalhado", 12, None, 0],
    "LÂMINA ACIARADA": ["MAIN_SWORD_HELL", "Barra de Aço", 16, "Couro Trabalhado", 8, "ARTEFACT_MAIN_SWORD_HELL", 1],
    "ESPADA ENTALHADA": ["2H_CLEAVER_SWORD", "Barra de Aço", 20, "Couro Trabalhado", 12, "ARTEFACT_2H_CLEAVER_SWORD", 1],
    "PAR DE GALATINAS": ["2H_DUALSWORD_HELL", "Barra de Aço", 20, "Couro Trabalhado", 12, "ARTEFACT_2H_DUALSWORD_HELL", 1],
    "CRIA-REAIS": ["2H_CLAYMORE_AVALON", "Barra de Aço", 20, "Couro Trabalhado", 12, "ARTEFACT_2H_CLAYMORE_AVALON", 1],
    "LÂMINA DA INFINIDADE": ["2H_SWORD_CRYSTAL", "Barra de Aço", 16, "Couro Trabalhado", 8, "QUESTITEM_TOKEN_CRYSTAL_SWORD", 1],
    "MACHADO DE GUERRA": ["MAIN_AXE", "Barra de Aço", 16, "Tábuas de Pinho", 8, None, 0],
    "MACHADÃO": ["2H_AXE", "Barra de Aço", 20, "Tábuas de Pinho", 12, None, 0],
    "ALABARDA": ["2H_HALBERD", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0],
    "CHAMA-CORPOS": ["2H_AXE_CARRION_MORGANA", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_AXE_CARRION_MORGANA", 1],
    "SEGADEIRA INFERNAL": ["2H_REAPER_AXE_HELL", "Tábuas de Pinho", 12, "Barra de Aço", 20, "ARTEFACT_2H_SCYTHE_HELL", 1],
    "PATAS DE URSO": ["2H_AXE_KEEPER", "Tábuas de Pinho", 12, "Barra de Aço", 20, "ARTEFACT_2H_DUALAXE_KEEPER", 1],
    "QUEBRA-REINO": ["2H_AXE_AVALON", "Tábuas de Pinho", 12, "Barra de Aço", 20, "ARTEFACT_2H_AXE_AVALON", 1],
    "FOICE DE CRISTAL": ["2H_AXE_CRYSTAL", "Tábuas de Pinho", 12, "Barra de Aço", 20, "QUESTITEM_TOKEN_CRYSTAL_AXE", 1],
    "MAÇA": ["MAIN_MACE", "Barra de Aço", 16, "Tecido Fino", 8, None, 0],
    "MAÇA PESADA": ["2H_MACE", "Barra de Aço", 20, "Tecido Fino", 12, None, 0],
    "MANGUAL": ["2H_FLAIL", "Barra de Aço", 20, "Tecido Fino", 12, None, 0],
    "MAÇA PÉTREA": ["MAIN_MACE_HELL", "Barra de Aço", 16, "Tecido Fino", 8, "ARTEFACT_MAIN_ROCKMACE_KEEPER", 1],
    "MAÇA DE ÍNCUBO": ["MAIN_MACE_HELL", "Barra de Aço", 16, "Tecido Fino", 8, "ARTEFACT_MAIN_MACE_HELL", 1],
    "MAÇA CAMBRIANA": ["2H_MACE_MORGANA", "Barra de Aço", 20, "Tecido Fino", 12, "ARTEFACT_2H_MACE_MORGANA", 1],
    "JURADOR": ["2H_MACE_AVALON", "Barra de Aço", 20, "Tecido Fino", 12, "ARTEFACT_2H_DUALMACE_AVALON", 1],
    "MONARCA TEMPESTUOSO": ["2H_MACE_CRYSTAL", "Barra de Aço", 16, "Tecido Fino", 8, "QUESTITEM_TOKEN_CRYSTAL_MACE", 1],
    "MARTELO": ["MAIN_HAMMER", "Barra de Aço", 24, None, 0, None, 0],
    "MARTELO DE BATALHA": ["2H_HAMMER", "Barra de Aço", 20, "Tecido Fino", 12, None, 0],
    "MARTELO ELEVADO": ["2H_POLEHAMMER", "Barra de Aço", 20, "Tecido Fino", 12, None, 0],
    "MARTELO DE FÚNEBRE": ["2H_HAMMER_UNDEAD", "Barra de Aço", 20, "Tecido Fino", 12, "ARTEFACT_2H_HAMMER_UNDEAD", 1],
    "MARTELO E FORJA": ["2H_HAMMER_HELL", "Barra de Aço", 20, "Tecido Fino", 12, "ARTEFACT_2H_DUALHAMMER_HELL", 1],
    "GUARDA-BOSQUES": ["2H_RAM_KEEPER", "Barra de Aço", 20, "Tecido Fino", 12, "ARTEFACT_2H_RAM_KEEPER", 1],
    "MÃO DA JUSTIÇA": ["2H_HAMMER_AVALON", "Barra de Aço", 20, "Tecido Fino", 12, "ARTEFACT_2H_HAMMER_AVALON", 1],
    "MARTELO ESTRONDOSO": ["2H_HAMMER_CRYSTAL", "Barra de Aço", 20, "Tecido Fino", 12, "QUESTITEM_TOKEN_CRYSTAL_HAMMER", 1],
    "LUVAS DE LUTADOR": ["MAIN_KNUCKLES", "Barra de Aço", 12, "Couro Trabalhado", 20, None, 0],
    "BRAÇADEIRAS DE BATALHA": ["2H_KNUCKLES", "Barra de Aço", 12, "Couro Trabalhado", 20, None, 0],
    "MANOPLAS CRAVADAS": ["2H_SPIKED_KNUCKLES", "Barra de Aço", 12, "Couro Trabalhado", 20, None, 0],
    "LUVAS URSINAS": ["2H_KNUCKLES_KEEPER", "Barra de Aço", 12, "Couro Trabalhado", 20, "ARTEFACT_2H_KNUCKLES_KEEPER", 1],
    "MÃOS INFERNAIS": ["2H_KNUCKLES_HELL", "Barra de Aço", 12, "Couro Trabalhado", 20, "ARTEFACT_2H_KNUCKLES_HELL", 1],
    "CESTUS GOLPEADORES": ["2H_KNUCKLES_MORGANA", "Barra de Aço", 12, "Couro Trabalhado", 20, "ARTEFACT_2H_KNUCKLES_MORGANA", 1],
    "PUNHOS DE AVALON": ["2H_KNUCKLES_AVALON", "Barra de Aço", 12, "Couro Trabalhado", 20, "ARTEFACT_2H_KNUCKLES_AVALON", 1],
    "BRAÇADEIRAS PULSANTES": ["2H_KNUCKLES_CRYSTAL", "Barra de Aço", 12, "Couro Trabalhado", 20, "QUESTITEM_TOKEN_CRYSTAL_KNUCKLES", 1],
    "BESTA": ["2H_CROSSBOW", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0],
    "BESTA PESADA": ["2H_CROSSBOW_LARGE", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0],
    "BESTA LEVE": ["MAIN_CROSSBOW", "Tábuas de Pinho", 16, "Barra de Aço", 8, None, 0],
    "REPETIDOR LAMENTOSO": ["2H_CROSSBOW_UNDEAD", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_REPEATINGCROSSBOW_UNDEAD", 1],
    "LANÇA-VIROTES": ["2H_CROSSBOW_HELL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_DUALCROSSBOW_HELL", 1],
    "ARCO DE CERGO": ["2H_CROSSBOW_MORGANA", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_CROSSBOWLARGE_MORGANA", 1],
    "MODELADOR DE ENERGIA": ["2H_CROSSBOW_AVALON", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_CROSSBOW_CANNON_AVALON", 1],
    "DETONADORES RELUZENTES": ["2H_CROSSBOW_CRYSTAL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "QUESTITEM_TOKEN_CRYSTAL_CROSSBOW", 1],
    "ESCUDO": ["OFF_SHIELD", "Tábuas de Pinho", 4, "Barra de Aço", 4, None, 0],
    "SARCÓFAGO": ["OFF_SHIELD_UNDEAD", "Tábuas de Pinho", 4, "Barra de Aço", 4, "ARTEFACT_OFF_SHIELD_UNDEAD", 1],
    "ESCUDO VAMPÍRICO": ["OFF_SHIELD_HELL", "Tábuas de Pinho", 4, "Barra de Aço", 4, "ARTEFACT_OFF_SHIELD_HELL", 1],
    "QUEBRA-ROSTOS": ["OFF_SHIELD_HELL", "Tábuas de Pinho", 4, "Barra de Aço", 4, "ARTEFACT_OFF_SHIELD_HELL_2", 1],
    "ÉGIDE ASTRAL": ["OFF_SHIELD_AVALON", "Tábuas de Pinho", 4, "Barra de Aço", 4, "ARTEFACT_OFF_SHIELD_AVALON", 1],
    "BARREIRA INQUEBRÁVEL": ["OFF_SHIELD_CRYSTAL", "Tábuas de Pinho", 4, "Barra de Aço", 4, "QUESTITEM_TOKEN_CRYSTAL_SHIELD", 1],
    "ADAGA": ["MAIN_DAGGER", "Barra de Aço", 12, "Couro Trabalhado", 12, None, 0],
    "PAR DE ADAGAS": ["2H_DAGGER", "Barra de Aço", 16, "Couro Trabalhado", 16, None, 0],
    "GARRAS": ["2H_DAGGER_HELL", "Barra de Aço", 12, "Couro Trabalhado", 20, None, 0], 
    "DESSANGRADOR": ["MAIN_DAGGER_HELL", "Barra de Aço", 16, "Couro Trabalhado", 8, "ARTEFACT_MAIN_DAGGER_HELL", 1],
    "PRESA DEMONÍACA": ["MAIN_DAGGER_PR_HELL", "Barra de Aço", 12, "Couro Trabalhado", 12, "ARTEFACT_2H_CLEAVER_HELL", 1],
    "MORTÍFICOS": ["2H_DUAL_DAGGER_HELL", "Barra de Aço", 16, "Couro Trabalhado", 16, "ARTEFACT_2H_TWINSCYTHE_HELL", 1],
    "FÚRIA CONTIDA": ["2H_DAGGER_AVALON", "Barra de Aço", 12, "Couro Trabalhado", 20, "ARTEFACT_2H_DAGGER_KATAR_AVALON", 1],
    "GÊMEAS ANIQUILADORAS": ["2H_DAGGER_CRYSTAL", "Barra de Aço", 16, "Couro Trabalhado", 16, "QUESTITEM_TOKEN_CRYSTAL_DAGGER", 1],
    "LANÇA": ["MAIN_SPEAR", "Tábuas de Pinho", 16, "Barra de Aço", 8, None, 0],
    "PIQUE": ["2H_SPEAR", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0],
    "ARCHA": ["2H_GLAIVE", "Tábuas de Pinho", 12, "Barra de Aço", 20, None, 0],
    "LANÇA GARCEIRA": ["MAIN_SPEAR_KEEPER", "Tábuas de Pinho", 16, "Barra de Aço", 8, "ARTEFACT_MAIN_SPEAR_KEEPER", 1],
    "CAÇA-ESPÍRITOS": ["2H_SPEAR_HELL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_HARPOON_HELL", 1],
    "LANÇA TRINA": ["2H_GLAIVE_HELL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_TRIDENT_UNDEAD", 1],
    "ALVORADA": ["MAIN_SPEAR_AVALON", "Tábuas de Pinho", 16, "Barra de Aço", 8, "ARTEFACT_MAIN_SPEAR_LANCE_AVALON", 1],
    "ARCHA FRATURADA": ["2H_SPEAR_CRYSTAL", "Tábuas de Pinho", 12, "Barra de Aço", 20, "QUESTITEM_TOKEN_CRYSTAL_SPEAR", 1]
}

# ================= FILTROS =================
FILTROS = {
    # CAPAS
    "todas_capas": lambda k, v: "CAPE" in v[0],
    "capas_normais": lambda k, v: v[0] == "CAPE",
    "capas_cidade": lambda k, v: "CAPEITEM_FW_" in v[0],
    "capas_faccao": lambda k, v: any(x in v[0] for x in ["CAPEITEM_HERETIC", "CAPEITEM_UNDEAD", "CAPEITEM_KEEPER", "CAPEITEM_MORGANA", "CAPEITEM_DEMON"]),
    
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
    
    # ARMAS
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
    
    # CAJADOS
    "fogo": lambda k, v: "FIRESTAFF" in v[0],
    "gelo": lambda k, v: "FROSTSTAFF" in v[0],
    "arcano": lambda k, v: "ARCANESTAFF" in v[0],
    "sagrado": lambda k, v: "HOLYSTAFF" in v[0],
    "natureza": lambda k, v: "NATURESTAFF" in v[0],
    "amaldiçoado": lambda k, v: "CURSEDSTAFF" in v[0],
    "metamorfo": lambda k, v: "SHAPESHIFTER" in v[0],
    
    # SECUNDÁRIAS
    "secundarias": lambda k, v: v[0].startswith("OFF_"),
    
    # BOLSAS
    "bolsas": lambda k, v: "BAG" in v[0],
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
    
    for nome, d in itens.items():
        # Item final
        item_id = id_item(tier, d[0], encanto)
        if item_id:
            ids_para_buscar.add(item_id)
        
        # Recurso 1 (Capa base ou recurso normal)
        if d[1]:
            for rid in ids_recurso_variantes(tier, d[1], encanto):
                if rid:
                    ids_para_buscar.add(rid)
        
        # Recurso 2 (Coração ou recurso normal)
        if d[3]:
            for rid in ids_recurso_variantes(tier, d[3], encanto):
                if rid:
                    ids_para_buscar.add(rid)
        
        # Artefato/Ornamento
        if d[5]:
            art_id = id_item(tier, d[5], 0)
            if art_id:
                ids_para_buscar.add(art_id)

    try:
        response = requests.get(
            f"{API_URL}{','.join(ids_para_buscar)}?locations=Thetford,FortSterling,Martlock,Lymhurst,Bridgewatch,Caerleon,Black Market",
            timeout=30
        )
        data_precos = response.json()
    except Exception as e:
        st.error(f"Erro ao conectar com a API: {e}")
        st.stop()

    # Processamento de preços
    precos_cache = {}
    for p in data_precos:
        pid = p.get("item_id")
        price = p.get("sell_price_min", 0)
        if pid and price > 0:
            if pid not in precos_cache or price < precos_cache[pid]["price"]:
                precos_cache[pid] = {"price": price, "city": p.get("city", "Desconhecida")}

    resultados = []
    progress_text = "Analisando Mercado e Calculando Lucros..."
    my_bar = st.progress(0, text=progress_text)

    total_itens = len(itens)

    for i, (nome, d) in enumerate(itens.items()):
        item_id = id_item(tier, d[0], encanto)
        preco_venda_bm = get_historical_price(item_id)

        my_bar.progress((i + 1) / total_itens, text=f"Analisando: {nome}")

        if preco_venda_bm <= 0:
            continue

        custo = 0
        detalhes = []
        valid_craft = True

        # ================= RECURSO 1 =================
        if d[1]:
            if d[1] == "CAPE":
                # Capa base do tier correspondente
                capa_id = f"T{tier}_CAPE"
                if capa_id in precos_cache:
                    info = precos_cache[capa_id]
                    custo += info["price"] * d[2] * quantidade
                    detalhes.append(f"{d[2] * quantidade}x Capa T{tier}: {info['price']:,} ({info['city']})")
                else:
                    valid_craft = False
            elif d[1] in RECURSO_MAP:
                # Recurso normal
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

        # ================= RECURSO 2 =================
        if d[3]:
            if d[3].startswith("CORACAO_"):
                # Coração de facção
                coracao_id = get_coracao_id(d[3])
                if coracao_id and coracao_id in precos_cache:
                    info = precos_cache[coracao_id]
                    qty_coracoes = get_coracoes_qty(tier)
                    custo += info["price"] * qty_coracoes * quantidade
                    facao = d[3].replace("CORACAO_", "")
                    detalhes.append(f"{qty_coracoes * quantidade}x Coração {facao}: {info['price']:,} ({info['city']})")
                else:
                    valid_craft = False
            elif d[3] in RECURSO_MAP:
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
            if art_id and art_id in precos_cache:
                info = precos_cache[art_id]
                qtd_art = d[6] * quantidade
                custo += info["price"] * qtd_art
                detalhes.append(f"{qtd_art}x Ornamento: {info['price']:,} ({info['city']})")
            else:
                # Tenta buscar em outras cidades
                preco_art = get_historical_price(art_id, "Caerleon,FortSterling,Thetford,Lymhurst,Bridgewatch,Martlock") if art_id else 0
                if preco_art > 0:
                    qtd_art = d[6] * quantidade
                    custo += preco_art * qtd_art
                    detalhes.append(f"{qtd_art}x Ornamento: {preco_art:,.0f} (Média Market)")
                else:
                    valid_craft = False

        if not valid_craft:
            continue

        custo_final = int(custo)
        venda_total = int(preco_venda_bm * quantidade)
        lucro = int((venda_total * 0.935) - custo_final)

        resultados.append((nome, lucro, venda_total, custo_final, detalhes, "Market Atual/24h"))

    my_bar.empty()

    # Ordenar pelo maior lucro
    resultados.sort(key=lambda x: x[1], reverse=True)

    if not resultados:
        st.warning("⚠️ A API não retornou preços recentes para os itens desta categoria no Black Market.")
    else:
        st.subheader(f"📊 {len(resultados)} Itens Encontrados - {categoria.upper()} T{tier}.{encanto}")

        for nome, lucro, venda, custo, detalhes, h_venda in resultados:
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
                        💰 Lucro Estimado: {lucro:,} ({perc_lucro:.2f}%)
                    </span>
                    <br><b>Investimento:</b> {custo:,} |
                    <b>Venda Estimada (BM):</b> {venda:,}
                </div>
                <div style="font-size: 0.95rem; color: #cbd5e1; margin-bottom: 10px;">
                    📍 <b>Foco Craft:</b> {cidade_foco} |
                    🕒 <b>Baseado em:</b> {h_venda}
                </div>
                <div style="background: rgba(0,0,0,0.4); padding: 12px; border-radius: 8px;
                            border: 1px solid rgba(255,255,255,0.1); font-size: 0.9rem;">
                    📦 <b>Detalhamento de Compras:</b> <br>
                    {" | ".join(detalhes)}
                </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("---")
st.caption("Radar Craft Albion - Desenvolvido para análise de mercado via Albion Online Data Project")
