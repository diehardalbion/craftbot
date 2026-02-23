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
API_URL = "https://west.albion-online-data.com/api/v2/stats/prices/ "
HISTORY_URL = "https://west.albion-online-data.com/api/v2/stats/history/ "
CIDADES = ["Martlock", "Thetford", "FortSterling", "Lymhurst", "Bridgewatch", "Brecilien", "Caerleon", "Black Market"]

# ================= MAPA DE RECURSOS BASE (CRAFTING) =================
RECURSO_MAP = {
    "Tecido Fino": "CLOTH", 
    "Couro Trabalhado": "LEATHER", 
    "Barra de Aço": "METALBAR", 
    "Tábuas de Pinho": "PLANKS"
}

# ================= MAPA DE CORAÇÕES E ITENS ESPECIAIS =================
# IDs dos corações de facção (são T1 sempre)
CORACOES_MAP = {
    "Coração Bestial": "T1_FACTION_STEPPE_TOKEN_1",      # Bridgewatch
    "Coração Montanhoso": "T1_FACTION_MOUNTAIN_TOKEN_1",  # Fort Sterling
    "Coração Arbóreo": "T1_FACTION_FOREST_TOKEN_1",       # Lymhurst
    "Coração Empedrado": "T1_FACTION_HIGHLAND_TOKEN_1",   # Martlock
    "Coração Videira": "T1_FACTION_SWAMP_TOKEN_1",        # Thetford
    "Coração Sombrio": "T1_FACTION_CAERLEON_TOKEN_1",     # Caerleon
    "Fogo de Fada": "T1_FACTION_BRECILIEN_TOKEN_1"        # Brecilien/Avalon
}

# Quantidade de corações por tier
CORACOES_QTD = {
    4: 1,   # Adepto
    5: 1,   # Perito
    6: 3,   # Mestre
    7: 5,   # Grão-Mestre
    8: 10   # Ancião
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
    "Barra de Aço": {
        4: "Barra de Aço",
        5: "Barra de Titânio",
        6: "Barra de Runita",
        7: "Barra de Meteorito",
        8: "Barra de Adamante"
    },
    "Tábuas de Pinho": {
        4: "Tábuas de Pinho",
        5: "Tábuas de Cedro",
        6: "Tábuas de Carvalho-Sangue",
        7: "Tábuas de Freixo",
        8: "Tábuas de Pau-branco"
    },
    "Couro Trabalhado": {
        4: "Couro Trabalhado",
        5: "Couro Curtido",
        6: "Couro Endurecido",
        7: "Couro Reforçado",
        8: "Couro Fortificado"
    },
    "Tecido Fino": {
        4: "Tecido Fino",
        5: "Tecido Ornado",
        6: "Tecido Rico",
        7: "Tecido Opulento",
        8: "Tecido Barroco"
    }
}

ITENS_DB = {
    # ================= CAJADOS AMALDIÇOADOS (CURSED) =================
    "Cajado Amaldiçoado": ["MAIN_CURSEDSTAFF", "Tábuas de Pinho", 16, "Barra de Aço", 8, None, 0, None],
    "Cajado Amaldiçoado Elevado": ["2H_CURSEDSTAFF", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0, None],
    "Cajado Demoníaco": ["2H_DEMONICSTAFF", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0, None],
    "Cajado Execrado": ["MAIN_CURSEDSTAFF_UNDEAD", "Tábuas de Pinho", 16, "Barra de Aço", 8, "ARTEFACT_MAIN_CURSEDSTAFF_UNDEAD", 1, None],
    "Caveira Amaldiçoada": ["2H_SKULLPANE_HELL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_SKULLPANE_HELL", 1, None],
    "Cajado da Danação": ["2H_CURSEDSTAFF_MORGANA", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_CURSEDSTAFF_MORGANA", 1, None],
    "Chama-sombra": ["MAIN_CURSEDSTAFF_AVALON", "Tábuas de Pinho", 16, "Barra de Aço", 8, "ARTEFACT_MAIN_CURSEDSTAFF_AVALON", 1, None],
    "Cajado Pútrido": ["2H_CURSEDSTAFF_CRYSTAL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "QUESTITEM_TOKEN_CRYSTAL_CURSEDSTAFF", 1, None],

    # ================= BORDÕES (QUARTERSTAFF) =================
    "Bordão": ["2H_QUARTERSTAFF", "Barra de Aço", 12, "Couro Trabalhado", 20, None, 0, None],
    "BOLSA": ["BAG", "Tecido Fino", 8, "Couro Trabalhado", 8, None, 0, None],
    "Cajado Férreo": ["2H_IRONCLADSTAFF", "Barra de Aço", 12, "Couro Trabalhado", 20, None, 0, None],
    "Cajado Biliminado": ["2H_DOUBLEBLADEDSTAFF", "Barra de Aço", 12, "Couro Trabalhado", 20, None, 0, None],
    "Cajado de Monge Negro": ["2H_COMBATSTAFF_MORGANA", "Barra de Aço", 12, "Couro Trabalhado", 20, "ARTEFACT_2H_COMBATSTAFF_MORGANA", 1, None],
    "Segamímica": ["2H_TWINSCYTHE_HELL", "Barra de Aço", 12, "Couro Trabalhado", 20, "ARTEFACT_2H_TWINSCYTHE_HELL", 1, None],
    "Cajado do Equilíbrio": ["2H_ROCKSTAFF_KEEPER", "Barra de Aço", 12, "Couro Trabalhado", 20, "ARTEFACT_2H_ROCKSTAFF_KEEPER", 1, None],
    "Buscador do Graal": ["2H_QUARTERSTAFF_AVALON", "Barra de Aço", 12, "Couro Trabalhado", 20, "ARTEFACT_2H_QUARTERSTAFF_AVALON", 1, None],
    "Lâminas Gêmeas Fantasmagóricas": ["2H_QUARTERSTAFF_CRYSTAL", "Barra de Aço", 12, "Couro Trabalhado", 20, "QUESTITEM_TOKEN_CRYSTAL_QUARTERSTAFF", 1, None],

    # ================= CAJADOS DE GELO (FROST) =================
    "Cajado de Gelo": ["MAIN_FROSTSTAFF", "Tábuas de Pinho", 16, "Barra de Aço", 8, None, 0, None],
    "Cajado de Gelo Elevado": ["2H_FROSTSTAFF", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0, None],
    "Cajado Glacial": ["2H_GLACIALSTAFF", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0, None],
    "Cajado Enregelante": ["MAIN_FROSTSTAFF_DEEPFREEZE", "Tábuas de Pinho", 16, "Barra de Aço", 8, "ARTEFACT_MAIN_FROSTSTAFF_DEEPFREEZE", 1, None],
    "Cajado de Sincelo": ["2H_ICE_CRYSTAL_HELL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_ICE_CRYSTAL_HELL", 1, None],
    "Prisma Geleterno": ["2H_RAMPY_FROST_KEEPER", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_RAMPY_FROST_KEEPER", 1, None],
    "Uivo Frio": ["MAIN_FROSTSTAFF_AVALON", "Tábuas de Pinho", 16, "Barra de Aço", 8, "ARTEFACT_MAIN_FROSTSTAFF_AVALON", 1, None],
    "Cajado Ártico": ["2H_FROSTSTAFF_CRYSTAL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "QUESTITEM_TOKEN_CRYSTAL_FROSTSTAFF", 1, None],

    # ================= CAJADOS ARCANOS (ARCANE) =================
    "Cajado Arcano": ["MAIN_ARCANESTAFF", "Tábuas de Pinho", 16, "Barra de Aço", 8, None, 0, None],
    "Cajado Arcano Elevado": ["2H_ARCANESTAFF", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0, None],
    "Cajado Enigmático": ["2H_ENIGMATICSTAFF", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0, None],
    "Cajado Feiticeiro": ["MAIN_ARCANESTAFF_UNDEAD", "Tábuas de Pinho", 16, "Barra de Aço", 8, "ARTEFACT_MAIN_ARCANESTAFF_UNDEAD", 1, None],
    "Cajado Oculto": ["2H_ARCANESTAFF_HELL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_ARCANESTAFF_HELL", 1, None],
    "Local Malévolo": ["2H_ENIGMATICSTAFF_MORGANA", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_ENIGMATICSTAFF_MORGANA", 1, None],
    "Som Equilibrado": ["2H_ARCANESTAFF_AVALON", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_ARCANESTAFF_AVALON", 1, None],
    "Cajado Astral": ["2H_ARCANESTAFF_CRYSTAL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "QUESTITEM_TOKEN_CRYSTAL_ARCANESTAFF", 1, None],

    # ================= CAJADOS SAGRADOS (HOLY) =================
    "Cajado Sagrado": ["MAIN_HOLYSTAFF", "Tábuas de Pinho", 16, "Tecido Fino", 8, None, 0, None],
    "Cajado Sagrado Elevado": ["2H_HOLYSTAFF", "Tábuas de Pinho", 20, "Tecido Fino", 12, None, 0, None],
    "Cajado Divino": ["2H_DIVINESTAFF", "Tábuas de Pinho", 20, "Tecido Fino", 12, None, 0, None],
    "Cajado Avivador": ["MAIN_HOLYSTAFF_MORGANA", "Tábuas de Pinho", 16, "Tecido Fino", 8, "ARTEFACT_MAIN_HOLYSTAFF_MORGANA", 1, None],
    "Cajado Corrompido": ["2H_HOLYSTAFF_HELL", "Tábuas de Pinho", 20, "Tecido Fino", 12, "ARTEFACT_2H_HOLYSTAFF_HELL", 1, None],
    "Cajado da Redenção": ["2H_HOLYSTAFF_UNDEAD", "Tábuas de Pinho", 20, "Tecido Fino", 12, "ARTEFACT_2H_HOLYSTAFF_UNDEAD", 1, None],
    "Queda Santa": ["MAIN_HOLYSTAFF_AVALON", "Tábuas de Pinho", 16, "Tecido Fino", 8, "ARTEFACT_MAIN_HOLYSTAFF_AVALON", 1, None],
    "Cajado Exaltado": ["2H_HOLYSTAFF_CRYSTAL", "Tábuas de Pinho", 20, "Tecido Fino", 12, "QUESTITEM_TOKEN_CRYSTAL_HOLYSTAFF", 1, None],

    # ================= CAJADOS DE FOGO (FIRE) =================
    "Cajado de Fogo": ["MAIN_FIRESTAFF", "Tábuas de Pinho", 16, "Barra de Aço", 8, None, 0, None],
    "Cajado de Fogo Elevado": ["2H_FIRESTAFF", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0, None],
    "Cajado Infernal": ["2H_INFERNALSTAFF", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0, None],
    "Cajado Incendiário": ["MAIN_FIRESTAFF_KEEPER", "Tábuas de Pinho", 16, "Barra de Aço", 8, "ARTEFACT_MAIN_FIRESTAFF_KEEPER", 1, None],
    "Cajado Sulfuroso": ["2H_FIRE_CRYSTAL_HELL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_FIRE_CRYSTAL_HELL", 1, None],
    "Cajado Fulgurante": ["2H_INFERNALSTAFF_MORGANA", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_INFERNALSTAFF_MORGANA", 1, None],
    "Canção da Alvorada": ["2H_FIRESTAFF_AVALON", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_FIRESTAFF_AVALON", 1, None],
    "Cajado do Andarilho Flamejante": ["MAIN_FIRESTAFF_CRYSTAL", "Tábuas de Pinho", 16, "Barra de Aço", 8, "QUESTITEM_TOKEN_CRYSTAL_FIRESTAFF", 1, None],

    # ================= CAJADOS DA NATUREZA (NATURE) =================
    "Cajado da Natureza": ["MAIN_NATURESTAFF", "Tábuas de Pinho", 16, "Tecido Fino", 8, None, 0, None],
    "Cajado da Natureza Elevado": ["2H_NATURESTAFF", "Tábuas de Pinho", 20, "Tecido Fino", 12, None, 0, None],
    "Cajado Selvagem": ["2H_WILDSTAFF", "Tábuas de Pinho", 20, "Tecido Fino", 12, None, 0, None],
    "Cajado Druídico": ["MAIN_NATURESTAFF_KEEPER", "Tábuas de Pinho", 16, "Tecido Fino", 8, "ARTEFACT_MAIN_NATURESTAFF_KEEPER", 1, None],
    "Cajado Pustulento": ["2H_NATURESTAFF_HELL", "Tábuas de Pinho", 20, "Tecido Fino", 12, "ARTEFACT_2H_NATURESTAFF_HELL", 1, None],
    "Cajado Rampante": ["2H_NATURESTAFF_KEEPER", "Tábuas de Pinho", 20, "Tecido Fino", 12, "ARTEFACT_2H_NATURESTAFF_KEEPER", 1, None],
    "Raiz Férrea": ["MAIN_NATURESTAFF_AVALON", "Tábuas de Pinho", 16, "Tecido Fino", 8, "ARTEFACT_MAIN_NATURESTAFF_AVALON", 1, None],
    "Cajado de Crosta Forjada": ["MAIN_NATURESTAFF_CRYSTAL", "Tábuas de Pinho", 16, "Tecido Fino", 8, "QUESTITEM_TOKEN_CRYSTAL_NATURESTAFF", 1, None],

    # ================= ARCOS (BOW) =================
    "Arco": ["2H_BOW", "Tábuas de Pinho", 32, None, 0, None, 0, None],
    "Arco de Guerra": ["2H_WARBOW", "Tábuas de Pinho", 32, None, 0, None, 0, None],
    "Arco Longo": ["2H_LONGBOW", "Tábuas de Pinho", 32, None, 0, None, 0, None],
    "Arco Sussurante": ["2H_BOW_KEEPER", "Tábuas de Pinho", 32, None, 0, "ARTEFACT_2H_BOW_KEEPER", 1, None],
    "Arco Plangente": ["2H_BOW_HELL", "Tábuas de Pinho", 32, None, 0, "ARTEFACT_2H_BOW_HELL", 1, None],
    "Arco Badônico": ["2H_BOW_UNDEAD", "Tábuas de Pinho", 32, None, 0, "ARTEFACT_2H_BOW_UNDEAD", 1, None],
    "Fura-bruma": ["2H_BOW_AVALON", "Tábuas de Pinho", 32, None, 0, "ARTEFACT_2H_BOW_AVALON", 1, None],
    "Arco do Andarilho Celeste": ["2H_BOW_CRYSTAL", "Tábuas de Pinho", 32, None, 0, "QUESTITEM_TOKEN_CRYSTAL_BOW", 1, None],
    
    # ================= CAJADOS TRANFORMAÇÃO (SHAPESHIFTER) =================
    "Cajado de Predador": ["2H_SHAPESHIFTER_PANT_TRACKER", "Tábuas de Pinho", 20, "Couro Trabalhado", 12, "ARTEFACT_2H_SHAPESHIFTER_PANT_TRACKER", 1, None],
    "Cajado Enraízado": ["2H_SHAPESHIFTER_TREANT", "Tábuas de Pinho", 20, "Couro Trabalhado", 12, "ARTEFACT_2H_SHAPESHIFTER_TREANT", 1, None],
    "Cajado Primitivo": ["2H_SHAPESHIFTER_BEAR", "Tábuas de Pinho", 20, "Couro Trabalhado", 12, "ARTEFACT_2H_SHAPESHIFTER_BEAR", 1, None],
    "Cajado da Lua de Sangue": ["2H_SHAPESHIFTER_WEREWOLF", "Tábuas de Pinho", 20, "Couro Trabalhado", 12, "ARTEFACT_2H_SHAPESHIFTER_WEREWOLF", 1, None],
    "Cajado Endemoniado": ["2H_SHAPESHIFTER_IMP", "Tábuas de Pinho", 20, "Couro Trabalhado", 12, "ARTEFACT_2H_SHAPESHIFTER_IMP", 1, None],
    "Cajado Rúnico da Terra": ["2H_SHAPESHIFTER_GOLEM", "Tábuas de Pinho", 20, "Couro Trabalhado", 12, "ARTEFACT_2H_SHAPESHIFTER_GOLEM", 1, None],
    "Cajado Invocador da Luz": ["2H_SHAPESHIFTER_EAGLE", "Tábuas de Pinho", 20, "Couro Trabalhado", 12, "ARTEFACT_2H_SHAPESHIFTER_EAGLE", 1, None],
    "Cajado Petrificante": ["2H_SHAPESHIFTER_CRYSTAL", "Tábuas de Pinho", 20, "Couro Trabalhado", 12, "QUESTITEM_TOKEN_CRYSTAL_SHAPESHIFTER", 1, None],
    "TOMO DE FEITIÇOS": ["OFF_BOOK", "Tecido Fino", 4, "Couro Trabalhado", 4, None, 0, None],
    "OLHO DOS SEGREDOS": ["OFF_ORB_HELL", "Tecido Fino", 4, "Couro Trabalhado", 4, "ARTEFACT_OFF_ORB_HELL", 1, None],
    "MUISEC": ["OFF_LAMP_HELL", "Tecido Fino", 4, "Couro Trabalhado", 4, "ARTEFACT_OFF_LAMP_HELL", 1, None],
    "RAIZ MESTRA": ["OFF_DEMONSKULL_HELL", "Tecido Fino", 4, "Couro Trabalhado", 4, "ARTEFACT_OFF_DEMONSKULL_HELL", 1, None],
    "INCENSÁRIO CELESTE": ["OFF_TOWERSHIELD_HELL", "Tecido Fino", 4, "Couro Trabalhado", 4, "ARTEFACT_OFF_TOWERSHIELD_HELL", 1, None],
    "GRUMÓRIO ESTAGNADO": ["OFF_SHIELD_HELL", "Tecido Fino", 4, "Couro Trabalhado", 4, "ARTEFACT_OFF_SHIELD_HELL", 1, None],
    "TOCHA": ["OFF_TORCH", "Tábuas de Pinho", 4, "Tecido Fino", 4, None, 0, None],
    "BRUMÁRIO": ["OFF_HORN_KEEPER", "Tábuas de Pinho", 4, "Tecido Fino", 4, "ARTEFACT_OFF_HORN_KEEPER", 1, None],
    "BENGALA MALIGNA": ["OFF_JESTERCANE_HELL", "Tábuas de Pinho", 4, "Tecido Fino", 4, "ARTEFACT_OFF_JESTERCANE_HELL", 1, None],
    "LUME CRIPTICO": ["OFF_LAMP_UNDEAD", "Tábuas de Pinho", 4, "Tecido Fino", 4, "ARTEFACT_OFF_LAMP_UNDEAD", 1, None],
    "CETRO SAGRADO": ["OFF_CENSER_AVALON", "Tábuas de Pinho", 4, "Tecido Fino", 4, "ARTEFACT_OFF_CENSER_AVALON", 1, None],
    "TOCHA CHAMA AZUL": ["OFF_LAMP_CRYSTAL", "Tábuas de Pinho", 4, "Tecido Fino", 4, "QUESTITEM_TOKEN_CRYSTAL_LAMP", 1, None],
    "BOTAS DE SOLDADO": ["SHOES_PLATE_SET1", "Barra de Aço", 8, None, 0, None, 0, None],
    "BOTAS DE CAVALEIRO": ["SHOES_PLATE_SET2", "Barra de Aço", 8, None, 0, None, 0, None],
    "BOTAS DE GUARDIÃO": ["SHOES_PLATE_SET3", "Barra de Aço", 8, None, 0, None, 0, None],
    "BOTAS REAIS": ["SHOES_PLATE_ROYAL", "Barra de Aço", 8, None, 0, "QUESTITEM_TOKEN_ROYAL", 2, None],
    "BOTAS DE GUARDA-TUMBAS": ["SHOES_PLATE_UNDEAD", "Barra de Aço", 8, None, 0, "ARTEFACT_SHOES_PLATE_UNDEAD", 1, None],
    "BOTAS DEMÔNIAS": ["SHOES_PLATE_HELL", "Barra de Aço", 8, None, 0, "ARTEFACT_SHOES_PLATE_HELL", 1, None],
    "BOTAS JUDICANTES": ["SHOES_PLATE_KEEPER", "Barra de Aço", 8, None, 0, "ARTEFACT_SHOES_PLATE_KEEPER", 1, None],
    "BOTAS DE TECELÃO": ["SHOES_PLATE_AVALON", "Barra de Aço", 8, None, 0, "ARTEFACT_SHOES_PLATE_AVALON", 1, None],
    "BOTAS DA BRAVURA": ["SHOES_PLATE_CRYSTAL", "Barra de Aço", 8, None, 0, "QUESTITEM_TOKEN_CRYSTAL_SHOES_PLATE", 1, None],
    "ARMADURA DE SOLDADO": ["ARMOR_PLATE_SET1", "Barra de Aço", 16, None, 0, None, 0, None],
    "ARMADURA DE CAVALEIRO": ["ARMOR_PLATE_SET2", "Barra de Aço", 16, None, 0, None, 0, None],
    "ARMADURA DE GUARDIÃO": ["ARMOR_PLATE_SET3", "Barra de Aço", 16, None, 0, None, 0, None],
    "ARMADURA REAL": ["ARMOR_PLATE_ROYAL", "Barra de Aço", 16, None, 0, "QUESTITEM_TOKEN_ROYAL", 4, None],
    "ARMADURA DE GUARDA-TUMBAS": ["ARMOR_PLATE_UNDEAD", "Barra de Aço", 16, None, 0, "ARTEFACT_ARMOR_PLATE_UNDEAD", 1, None],
    "ARMADURA DEMÔNIA": ["ARMOR_PLATE_HELL", "Barra de Aço", 16, None, 0, "ARTEFACT_ARMOR_PLATE_HELL", 1, None],
    "ARMADURA JUDICANTE": ["ARMOR_PLATE_KEEPER", "Barra de Aço", 16, None, 0, "ARTEFACT_ARMOR_PLATE_KEEPER", 1, None],
    "ARMADURA DE TECELÃO": ["ARMOR_PLATE_AVALON", "Barra de Aço", 16, None, 0, "ARTEFACT_ARMOR_PLATE_AVALON", 1, None],
    "ARMADURA DA BRAVURA": ["ARMOR_PLATE_CRYSTAL", "Barra de Aço", 16, None, 0, "QUESTITEM_TOKEN_CRYSTAL_ARMOR_PLATE", 1, None],
    "ELMO DE SOLDADO": ["HEAD_PLATE_SET1", "Barra de Aço", 8, None, 0, None, 0, None],
    "ELMO DE CAVALEIRO": ["HEAD_PLATE_SET2", "Barra de Aço", 8, None, 0, None, 0, None],
    "ELMO DE GUARDIÃO": ["HEAD_PLATE_SET3", "Barra de Aço", 8, None, 0, None, 0, None],
    "ELMO REAL": ["HEAD_PLATE_ROYAL", "Barra de Aço", 8, None, 0, "QUESTITEM_TOKEN_ROYAL", 2, None],
    "ELMO DE GUARDA-TUMBAS": ["HEAD_PLATE_UNDEAD", "Barra de Aço", 8, None, 0, "ARTEFACT_HEAD_PLATE_UNDEAD", 1, None],
    "ELMO DEMÔNIO": ["HEAD_PLATE_HELL", "Barra de Aço", 8, None, 0, "ARTEFACT_HEAD_PLATE_HELL", 1, None],
    "ELMO JUDICANTE": ["HEAD_PLATE_KEEPER", "Barra de Aço", 8, None, 0, "ARTEFACT_HEAD_PLATE_KEEPER", 1, None],
    "ELMO DE TECELÃO": ["HEAD_PLATE_AVALON", "Barra de Aço", 8, None, 0, "ARTEFACT_HEAD_PLATE_AVALON", 1, None],
    "ELMO DA BRAVURA": ["HEAD_PLATE_CRYSTAL", "Barra de Aço", 8, None, 0, "QUESTITEM_TOKEN_CRYSTAL_HEAD_PLATE", 1, None],
    "Sapatos de Mercenário": ["SHOES_LEATHER_SET1", "Couro Trabalhado", 8, None, 0, None, 0, None],
    "Sapatos de Caçador": ["SHOES_LEATHER_SET2", "Couro Trabalhado", 8, None, 0, None, 0, None],
    "Sapatos de Assassino": ["SHOES_LEATHER_SET3", "Couro Trabalhado", 8, None, 0, None, 0, None],
    "Sapatos Reais": ["SHOES_LEATHER_ROYAL", "Couro Trabalhado", 8, None, 0, "QUESTITEM_TOKEN_ROYAL", 2, None],
    "Sapatos de Espreitador": ["SHOES_LEATHER_MORGANA", "Couro Trabalhado", 8, None, 0, "ARTEFACT_SHOES_LEATHER_MORGANA", 1, None],
    "Sapatos Espectrais": ["SHOES_LEATHER_UNDEAD", "Couro Trabalhado", 8, None, 0, "ARTEFACT_SHOES_LEATHER_UNDEAD", 1, None],
    "Sapatos de Andarilho da Névoa": ["SHOES_LEATHER_FEY", "Couro Trabalhado", 8, None, 0, "ARTEFACT_SHOES_LEATHER_FEY", 1, None],
    "Sapatos da Tenacidade": ["SHOES_LEATHER_CRYSTAL", "Couro Trabalhado", 8, None, 0, "QUESTITEM_TOKEN_CRYSTAL_SHOES_LEATHER", 1, None],
    "Casaco Mercenário": ["ARMOR_LEATHER_SET1", "Couro Trabalhado", 16, None, 0, None, 0, None],
    "Casaco de Caçador": ["ARMOR_LEATHER_SET2", "Couro Trabalhado", 16, None, 0, None, 0, None],
    "Casaco de Assassino": ["ARMOR_LEATHER_SET3", "Couro Trabalhado", 16, None, 0, None, 0, None],
    "Casaco Real": ["ARMOR_LEATHER_ROYAL", "Couro Trabalhado", 16, None, 0, "QUESTITEM_TOKEN_ROYAL", 4, None],
    "Casaco de Espreitador": ["ARMOR_LEATHER_MORGANA", "Couro Trabalhado", 16, None, 0, "ARTEFACT_ARMOR_LEATHER_MORGANA", 1, None],
    "Casaco Inferial": ["ARMOR_LEATHER_HELL", "Couro Trabalhado", 16, None, 0, "ARTEFACT_ARMOR_LEATHER_HELL", 1, None],
    "Casaco Espectral": ["ARMOR_LEATHER_UNDEAD", "Couro Trabalhado", 16, None, 0, "ARTEFACT_ARMOR_LEATHER_UNDEAD", 1, None],
    "Casaco de Andarilho da Névoa": ["ARMOR_LEATHER_FEY", "Couro Trabalhado", 16, None, 0, "ARTEFACT_ARMOR_LEATHER_FEY", 1, None],
    "Casaco da Tenacidade": ["ARMOR_LEATHER_CRYSTAL", "Couro Trabalhado", 16, None, 0, "QUESTITEM_TOKEN_CRYSTAL_ARMOR_LEATHER", 1, None],
    "Capuz de Mercenário de Mercenário": ["HEAD_LEATHER_SET1", "Couro Trabalhado", 8, None, 0, None, 0, None],
    "Capuz de Caçador": ["HEAD_LEATHER_SET2", "Couro Trabalhado", 8, None, 0, None, 0, None],
    "Capuz de Assassino": ["HEAD_LEATHER_SET3", "Couro Trabalhado", 8, None, 0, None, 0, None],
    "Capuz Real": ["HEAD_LEATHER_ROYAL", "Couro Trabalhado", 8, None, 0, "QUESTITEM_TOKEN_ROYAL", 2, None],
    "Capuz de Espreitador": ["HEAD_LEATHER_MORGANA", "Couro Trabalhado", 8, None, 0, "ARTEFACT_HEAD_LEATHER_MORGANA", 1, None],
    "Capuz Inferial": ["HEAD_LEATHER_HELL", "Couro Trabalhado", 8, None, 0, "ARTEFACT_HEAD_LEATHER_HELL", 1, None],
    "Capuz Espectral": ["HEAD_LEATHER_UNDEAD", "Couro Trabalhado", 8, None, 0, "ARTEFACT_HEAD_LEATHER_UNDEAD", 1, None],
    "Capuz de Andarilho da Névoa": ["HEAD_LEATHER_FEY", "Couro Trabalhado", 8, None, 0, "ARTEFACT_HEAD_LEATHER_FEY", 1, None],
    "Capuz da Tenacidade": ["HEAD_LEATHER_CRYSTAL", "Couro Trabalhado", 8, None, 0, "QUESTITEM_TOKEN_CRYSTAL_HEAD_LEATHER", 1, None],
    "Sandálias de Erudito": ["SHOES_CLOTH_SET1", "Tecido Fino", 8, None, 0, None, 0, None],
    "Sandálias de Clérigo": ["SHOES_CLOTH_SET2", "Tecido Fino", 8, None, 0, None, 0, None],
    "Sandálias de Mago": ["SHOES_CLOTH_SET3", "Tecido Fino", 8, None, 0, None, 0, None],
    "Sandálias Reais": ["SHOES_CLOTH_ROYAL", "Tecido Fino", 8, None, 0, "QUESTITEM_TOKEN_ROYAL", 2, None],
    "Sandálias de Druida": ["SHOES_CLOTH_KEEPER", "Tecido Fino", 8, None, 0, "ARTEFACT_SHOES_CLOTH_KEEPER", 1, None],
    "Sandálias Malévolas": ["SHOES_CLOTH_HELL", "Tecido Fino", 8, None, 0, "ARTEFACT_SHOES_CLOTH_HELL", 1, None],
    "Sandálias Sectárias": ["SHOES_CLOTH_MORGANA", "Tecido Fino", 8, None, 0, "ARTEFACT_SHOES_CLOTH_MORGANA", 1, None],
    "Sandálias Feéricas": ["SHOES_CLOTH_FEY", "Tecido Fino", 8, None, 0, "ARTEFACT_SHOES_CLOTH_FEY", 1, None],
    "Sandálias Da Pureza": ["SHOES_CLOTH_CRYSTAL", "Tecido Fino", 8, None, 0, "QUESTITEM_TOKEN_CRYSTAL_SHOES_CLOTH", 1, None],
    "Robe do Erudito": ["ARMOR_CLOTH_SET1", "Tecido Fino", 16, None, 0, None, 0, None],
    "Robe de Clérigo": ["ARMOR_CLOTH_SET2", "Tecido Fino", 16, None, 0, None, 0, None],
    "Robe de Mago": ["ARMOR_CLOTH_SET3", "Tecido Fino", 16, None, 0, None, 0, None],
    "Robe Real": ["ARMOR_CLOTH_ROYAL", "Tecido Fino", 16, None, 0, "QUESTITEM_TOKEN_ROYAL", 4, None],
    "Robe do Druída": ["ARMOR_CLOTH_KEEPER", "Tecido Fino", 16, None, 0, "ARTEFACT_ARMOR_CLOTH_KEEPER", 1, None],
    "Robe Malévolo": ["ARMOR_CLOTH_HELL", "Tecido Fino", 16, None, 0, "ARTEFACT_ARMOR_CLOTH_HELL", 1, None],
    "Robe Sectário": ["ARMOR_CLOTH_MORGANA", "Tecido Fino", 16, None, 0, "ARTEFACT_ARMOR_CLOTH_MORGANA", 1, None],
    "Robe Feérico": ["ARMOR_CLOTH_FEY", "Tecido Fino", 16, None, 0, "ARTEFACT_ARMOR_CLOTH_FEY", 1, None],
    "Robe da Pureza": ["ARMOR_CLOTH_CRYSTAL", "Tecido Fino", 16, None, 0, "QUESTITEM_TOKEN_CRYSTAL_ARMOR_CLOTH", 1, None],
    "Capote de Erudito": ["HEAD_CLOTH_SET1", "Tecido Fino", 8, None, 0, None, 0, None],
    "Capote de Clérigo": ["HEAD_CLOTH_SET2", "Tecido Fino", 8, None, 0, None, 0, None],
    "Capote de Mago": ["HEAD_CLOTH_SET3", "Tecido Fino", 8, None, 0, None, 0, None],
    "Capote Real": ["HEAD_CLOTH_ROYAL", "Tecido Fino", 8, None, 0, "QUESTITEM_TOKEN_ROYAL", 2, None],
    "Capote Druída": ["HEAD_CLOTH_KEEPER", "Tecido Fino", 8, None, 0, "ARTEFACT_HEAD_CLOTH_KEEPER", 1, None],
    "Capote Malévolo": ["HEAD_CLOTH_HELL", "Tecido Fino", 8, None, 0, "ARTEFACT_HEAD_CLOTH_HELL", 1, None],
    "Capote Sectário": ["HEAD_CLOTH_MORGANA", "Tecido Fino", 8, None, 0, "ARTEFACT_HEAD_CLOTH_MORGANA", 1, None],
    "Capote Feérico": ["HEAD_CLOTH_FEY", "Tecido Fino", 8, None, 0, "ARTEFACT_HEAD_CLOTH_FEY", 1, None],
    "Capote da Pureza": ["HEAD_CLOTH_CRYSTAL", "Tecido Fino", 8, None, 0, "QUESTITEM_TOKEN_CRYSTAL_HEAD_CLOTH", 1, None],
    "ESPADA LARGA": ["MAIN_SWORD", "Barra de Aço", 16, "Couro Trabalhado", 8, None, 0, None],
    "MONTANTE": ["2H_CLAYMORE", "Barra de Aço", 20, "Couro Trabalhado", 12, None, 0, None],
    "ESPADAS DUPLAS": ["2H_DUALSWORD", "Barra de Aço", 20, "Couro Trabalhado", 12, None, 0, None],
    "LÂMINA ACIARADA": ["MAIN_SWORD_HELL", "Barra de Aço", 16, "Couro Trabalhado", 8, "ARTEFACT_MAIN_SWORD_HELL", 1, None],
    "ESPADA ENTALHADA": ["2H_CLEAVER_SWORD", "Barra de Aço", 20, "Couro Trabalhado", 12, "ARTEFACT_2H_CLEAVER_SWORD", 1, None],
    "PAR DE GALATINAS": ["2H_DUALSWORD_HELL", "Barra de Aço", 20, "Couro Trabalhado", 12, "ARTEFACT_2H_DUALSWORD_HELL", 1, None],
    "CRIA-REAIS": ["2H_CLAYMORE_AVALON", "Barra de Aço", 20, "Couro Trabalhado", 12, "ARTEFACT_2H_CLAYMORE_AVALON", 1, None],
    "LÂMINA DA INFINIDADE": ["2H_SWORD_CRYSTAL", "Barra de Aço", 16, "Couro Trabalhado", 8, "QUESTITEM_TOKEN_CRYSTAL_SWORD", 1, None],
    "MACHADO DE GUERRA": ["MAIN_AXE", "Barra de Aço", 16, "Tábuas de Pinho", 8, None, 0, None],
    "MACHADÃO": ["2H_AXE", "Barra de Aço", 20, "Tábuas de Pinho", 12, None, 0, None],
    "ALABARDA": ["2H_HALBERD", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0, None],
    "CHAMA-CORPOS": ["2H_AXE_CARRION_MORGANA", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_AXE_CARRION_MORGANA", 1, None],
    "SEGADEIRA INFERNAL": ["2H_REAPER_AXE_HELL", "Tábuas de Pinho", 12, "Barra de Aço", 20, "ARTEFACT_2H_SCYTHE_HELL", 1, None],
    "PATAS DE URSO": ["2H_AXE_KEEPER", "Tábuas de Pinho", 12, "Barra de Aço", 20, "ARTEFACT_2H_DUALAXE_KEEPER", 1, None],
    "QUEBRA-REINO": ["2H_AXE_AVALON", "Tábuas de Pinho", 12, "Barra de Aço", 20, "ARTEFACT_2H_AXE_AVALON", 1, None],
    "FOICE DE CRISTAL": ["2H_AXE_CRYSTAL", "Tábuas de Pinho", 12, "Barra de Aço", 20, "QUESTITEM_TOKEN_CRYSTAL_AXE", 1, None],
    "MAÇA": ["MAIN_MACE", "Barra de Aço", 16, "Tecido Fino", 8, None, 0, None],
    "MAÇA PESADA": ["2H_MACE", "Barra de Aço", 20, "Tecido Fino", 12, None, 0, None],
    "MANGUAL": ["2H_FLAIL", "Barra de Aço", 20, "Tecido Fino", 12, None, 0, None],
    "MAÇA PÉTREA": ["MAIN_MACE_HELL", "Barra de Aço", 16, "Tecido Fino", 8, "ARTEFACT_MAIN_ROCKMACE_KEEPER", 1, None],
    "MAÇA DE ÍNCUBO": ["MAIN_MACE_HELL", "Barra de Aço", 16, "Tecido Fino", 8, "ARTEFACT_MAIN_MACE_HELL", 1, None],
    "MAÇA CAMBRIANA": ["2H_MACE_MORGANA", "Barra de Aço", 20, "Tecido Fino", 12, "ARTEFACT_2H_MACE_MORGANA", 1, None],
    "JURADOR": ["2H_MACE_AVALON", "Barra de Aço", 20, "Tecido Fino", 12, "ARTEFACT_2H_DUALMACE_AVALON", 1, None],
    "MONARCA TEMPESTUOSO": ["2H_MACE_CRYSTAL", "Barra de Aço", 16, "Tecido Fino", 8, "QUESTITEM_TOKEN_CRYSTAL_MACE", 1, None],
    "MARTELO": ["MAIN_HAMMER", "Barra de Aço", 24, None, 0, None, 0, None],
    "MARTELO DE BATALHA": ["2H_HAMMER", "Barra de Aço", 20, "Tecido Fino", 12, None, 0, None],
    "MARTELO ELEVADO": ["2H_POLEHAMMER", "Barra de Aço", 20, "Tecido Fino", 12, None, 0, None],
    "MARTELO DE FÚNEBRE": ["2H_HAMMER_UNDEAD", "Barra de Aço", 20, "Tecido Fino", 12, "ARTEFACT_2H_HAMMER_UNDEAD", 1, None],
    "MARTELO E FORJA": ["2H_HAMMER_HELL", "Barra de Aço", 20, "Tecido Fino", 12, "ARTEFACT_2H_DUALHAMMER_HELL", 1, None],
    "GUARDA-BOSQUES": ["2H_RAM_KEEPER", "Barra de Aço", 20, "Tecido Fino", 12, "ARTEFACT_2H_RAM_KEEPER", 1, None],
    "MÃO DA JUSTIÇA": ["2H_HAMMER_AVALON", "Barra de Aço", 20, "Tecido Fino", 12, "ARTEFACT_2H_HAMMER_AVALON", 1, None],
    "MARTELO ESTRONDOSO": ["2H_HAMMER_CRYSTAL", "Barra de Aço", 20, "Tecido Fino", 12, "QUESTITEM_TOKEN_CRYSTAL_HAMMER", 1, None],
    "LUVAS DE LUTADOR": ["MAIN_KNUCKLES", "Barra de Aço", 12, "Couro Trabalhado", 20, None, 0, None],
    "BRAÇADEIRAS DE BATALHA": ["2H_KNUCKLES", "Barra de Aço", 12, "Couro Trabalhado", 20, None, 0, None],
    "MANOPLAS CRAVADAS": ["2H_SPIKED_KNUCKLES", "Barra de Aço", 12, "Couro Trabalhado", 20, None, 0, None],
    "LUVAS URSINAS": ["2H_KNUCKLES_KEEPER", "Barra de Aço", 12, "Couro Trabalhado", 20, "ARTEFACT_2H_KNUCKLES_KEEPER", 1, None],
    "MÃOS INFERNAIS": ["2H_KNUCKLES_HELL", "Barra de Aço", 12, "Couro Trabalhado", 20, "ARTEFACT_2H_KNUCKLES_HELL", 1, None],
    "CESTUS GOLPEADORES": ["2H_KNUCKLES_MORGANA", "Barra de Aço", 12, "Couro Trabalhado", 20, "ARTEFACT_2H_KNUCKLES_MORGANA", 1, None],
    "PUNHOS DE AVALON": ["2H_KNUCKLES_AVALON", "Barra de Aço", 12, "Couro Trabalhado", 20, "ARTEFACT_2H_KNUCKLES_AVALON", 1, None],
    "BRAÇADEIRAS PULSANTES": ["2H_KNUCKLES_CRYSTAL", "Barra de Aço", 12, "Couro Trabalhado", 20, "QUESTITEM_TOKEN_CRYSTAL_KNUCKLES", 1, None],
    "BESTA": ["2H_CROSSBOW", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0, None],
    "BESTA PESADA": ["2H_CROSSBOW_LARGE", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0, None],
    "BESTA LEVE": ["MAIN_CROSSBOW", "Tábuas de Pinho", 16, "Barra de Aço", 8, None, 0, None],
    "REPETIDOR LAMENTOSO": ["2H_CROSSBOW_UNDEAD", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_REPEATINGCROSSBOW_UNDEAD", 1, None],
    "LANÇA-VIROTES": ["2H_CROSSBOW_HELL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_DUALCROSSBOW_HELL", 1, None],
    "ARCO DE CERGO": ["2H_CROSSBOW_MORGANA", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_CROSSBOWLARGE_MORGANA", 1, None],
    "MODELADOR DE ENERGIA": ["2H_CROSSBOW_AVALON", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_CROSSBOW_CANNON_AVALON", 1, None],
    "DETONADORES RELUZENTES": ["2H_CROSSBOW_CRYSTAL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "QUESTITEM_TOKEN_CRYSTAL_CROSSBOW", 1, None],
    "ESCUDO": ["OFF_SHIELD", "Tábuas de Pinho", 4, "Barra de Aço", 4, None, 0, None],
    "SARCÓFAGO": ["OFF_SHIELD_UNDEAD", "Tábuas de Pinho", 4, "Barra de Aço", 4, "ARTEFACT_OFF_SHIELD_UNDEAD", 1, None],
    "ESCUDO VAMPÍRICO": ["OFF_SHIELD_HELL", "Tábuas de Pinho", 4, "Barra de Aço", 4, "ARTEFACT_OFF_SHIELD_HELL", 1, None],
    "QUEBRA-ROSTOS": ["OFF_SHIELD_HELL", "Tábuas de Pinho", 4, "Barra de Aço", 4, "ARTEFACT_OFF_SHIELD_HELL_2", 1, None],
    "ÉGIDE ASTRAL": ["OFF_SHIELD_AVALON", "Tábuas de Pinho", 4, "Barra de Aço", 4, "ARTEFACT_OFF_SHIELD_AVALON", 1, None],
    "BARREIRA INQUEBRÁVEL": ["OFF_SHIELD_CRYSTAL", "Tábuas de Pinho", 4, "Barra de Aço", 4, "QUESTITEM_TOKEN_CRYSTAL_SHIELD", 1, None],
    "ADAGA": ["MAIN_DAGGER", "Barra de Aço", 12, "Couro Trabalhado", 12, None, 0, None],
    "PAR DE ADAGAS": ["2H_DAGGER", "Barra de Aço", 16, "Couro Trabalhado", 16, None, 0, None],
    "GARRAS": ["2H_DAGGER_HELL", "Barra de Aço", 12, "Couro Trabalhado", 20, None, 0, None], 
    "DESSANGRADOR": ["MAIN_DAGGER_HELL", "Barra de Aço", 16, "Couro Trabalhado", 8, "ARTEFACT_MAIN_DAGGER_HELL", 1, None],
    "PRESA DEMONÍACA": ["MAIN_DAGGER_PR_HELL", "Barra de Aço", 12, "Couro Trabalhado", 12, "ARTEFACT_2H_CLEAVER_HELL", 1, None],
    "MORTÍFICOS": ["2H_DUAL_DAGGER_HELL", "Barra de Aço", 16, "Couro Trabalhado", 16, "ARTEFACT_2H_TWINSCYTHE_HELL", 1, None],
    "FÚRIA CONTIDA": ["2H_DAGGER_AVALON", "Barra de Aço", 12, "Couro Trabalhado", 20, "ARTEFACT_2H_DAGGER_KATAR_AVALON", 1, None],
    "GÊMEAS ANIQUILADORAS": ["2H_DAGGER_CRYSTAL", "Barra de Aço", 16, "Couro Trabalhado", 16, "QUESTITEM_TOKEN_CRYSTAL_DAGGER", 1, None],
    "LANÇA": ["MAIN_SPEAR", "Tábuas de Pinho", 16, "Barra de Aço", 8, None, 0, None],
    "PIQUE": ["2H_SPEAR", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0, None],
    "ARCHA": ["2H_GLAIVE", "Tábuas de Pinho", 12, "Barra de Aço", 20, None, 0, None],
    "LANÇA GARCEIRA": ["MAIN_SPEAR_KEEPER", "Tábuas de Pinho", 16, "Barra de Aço", 8, "ARTEFACT_MAIN_SPEAR_KEEPER", 1, None],
    "CAÇA-ESPÍRITOS": ["2H_SPEAR_HELL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_HARPOON_HELL", 1, None],
    "LANÇA TRINA": ["2H_GLAIVE_HELL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_TRIDENT_UNDEAD", 1, None],
    "ALVORADA": ["MAIN_SPEAR_AVALON", "Tábuas de Pinho", 16, "Barra de Aço", 8, "ARTEFACT_MAIN_SPEAR_LANCE_AVALON", 1, None],
    "ARCHA FRATURADA": ["2H_SPEAR_CRYSTAL", "Tábuas de Pinho", 12, "Barra de Aço", 20, "QUESTITEM_TOKEN_CRYSTAL_SPEAR", 1, None],

    # ================= CAPAS NORMAIS =================
    "Capa do Adepto": ["CAPEITEM_LEVEL1", "Tecido Fino", 4, "Couro Trabalhado", 4, None, 0, None],
    "Capa do Perito": ["CAPEITEM_LEVEL2", "Tecido Ornado", 4, "Couro Curtido", 4, None, 0, None],
    "Capa do Mestre": ["CAPEITEM_LEVEL3", "Tecido Rico", 4, "Couro Endurecido", 4, None, 0, None],
    "Capa do Grão-Mestre": ["CAPEITEM_LEVEL4", "Tecido Opulento", 4, "Couro Reforçado", 4, None, 0, None],
    "Capa do Ancião": ["CAPEITEM_LEVEL5", "Tecido Barroco", 4, "Couro Fortificado", 4, None, 0, None],

    # ================= CAPAS BRIDGEWATCH =================
    "Capa de Bridgewatch do Adepto": ["CAPEITEM_FW_BRIDGEWATCH_LEVEL1", "Capa do Adepto", 1, None, 0, "CAPEITEM_FW_BRIDGEWATCH_BP_LEVEL1", 1, "Coração Bestial"],
    "Capa de Bridgewatch do Perito": ["CAPEITEM_FW_BRIDGEWATCH_LEVEL2", "Capa do Perito", 1, None, 0, "CAPEITEM_FW_BRIDGEWATCH_BP_LEVEL2", 1, "Coração Bestial"],
    "Capa de Bridgewatch do Mestre": ["CAPEITEM_FW_BRIDGEWATCH_LEVEL3", "Capa do Mestre", 1, None, 0, "CAPEITEM_FW_BRIDGEWATCH_BP_LEVEL3", 1, "Coração Bestial"],
    "Capa de Bridgewatch do Grão-Mestre": ["CAPEITEM_FW_BRIDGEWATCH_LEVEL4", "Capa do Grão-Mestre", 1, None, 0, "CAPEITEM_FW_BRIDGEWATCH_BP_LEVEL4", 1, "Coração Bestial"],
    "Capa de Bridgewatch do Ancião": ["CAPEITEM_FW_BRIDGEWATCH_LEVEL5", "Capa do Ancião", 1, None, 0, "CAPEITEM_FW_BRIDGEWATCH_BP_LEVEL5", 1, "Coração Bestial"],

    # ================= CAPAS FORT STERLING =================
    "Capa de Fort Sterling do Adepto": ["CAPEITEM_FW_FORTSTERLING_LEVEL1", "Capa do Adepto", 1, None, 0, "CAPEITEM_FW_FORTSTERLING_BP_LEVEL1", 1, "Coração Montanhoso"],
    "Capa de Fort Sterling do Perito": ["CAPEITEM_FW_FORTSTERLING_LEVEL2", "Capa do Perito", 1, None, 0, "CAPEITEM_FW_FORTSTERLING_BP_LEVEL2", 1, "Coração Montanhoso"],
    "Capa de Fort Sterling do Mestre": ["CAPEITEM_FW_FORTSTERLING_LEVEL3", "Capa do Mestre", 1, None, 0, "CAPEITEM_FW_FORTSTERLING_BP_LEVEL3", 1, "Coração Montanhoso"],
    "Capa de Fort Sterling do Grão-Mestre": ["CAPEITEM_FW_FORTSTERLING_LEVEL4", "Capa do Grão-Mestre", 1, None, 0, "CAPEITEM_FW_FORTSTERLING_BP_LEVEL4", 1, "Coração Montanhoso"],
    "Capa de Fort Sterling do Ancião": ["CAPEITEM_FW_FORTSTERLING_LEVEL5", "Capa do Ancião", 1, None, 0, "CAPEITEM_FW_FORTSTERLING_BP_LEVEL5", 1, "Coração Montanhoso"],

    # ================= CAPAS LYMHURST =================
    "Capa de Lymhurst do Adepto": ["CAPEITEM_FW_LYMHURST_LEVEL1", "Capa do Adepto", 1, None, 0, "CAPEITEM_FW_LYMHURST_BP_LEVEL1", 1, "Coração Arbóreo"],
    "Capa de Lymhurst do Perito": ["CAPEITEM_FW_LYMHURST_LEVEL2", "Capa do Perito", 1, None, 0, "CAPEITEM_FW_LYMHURST_BP_LEVEL2", 1, "Coração Arbóreo"],
    "Capa de Lymhurst do Mestre": ["CAPEITEM_FW_LYMHURST_LEVEL3", "Capa do Mestre", 1, None, 0, "CAPEITEM_FW_LYMHURST_BP_LEVEL3", 1, "Coração Arbóreo"],
    "Capa de Lymhurst do Grão-Mestre": ["CAPEITEM_FW_LYMHURST_LEVEL4", "Capa do Grão-Mestre", 1, None, 0, "CAPEITEM_FW_LYMHURST_BP_LEVEL4", 1, "Coração Arbóreo"],
    "Capa de Lymhurst do Ancião": ["CAPEITEM_FW_LYMHURST_LEVEL5", "Capa do Ancião", 1, None, 0, "CAPEITEM_FW_LYMHURST_BP_LEVEL5", 1, "Coração Arbóreo"],

    # ================= CAPAS MARTLOCK =================
    "Capa de Martlock do Adepto": ["CAPEITEM_FW_MARTLOCK_LEVEL1", "Capa do Adepto", 1, None, 0, "CAPEITEM_FW_MARTLOCK_BP_LEVEL1", 1, "Coração Empedrado"],
    "Capa de Martlock do Perito": ["CAPEITEM_FW_MARTLOCK_LEVEL2", "Capa do Perito", 1, None, 0, "CAPEITEM_FW_MARTLOCK_BP_LEVEL2", 1, "Coração Empedrado"],
    "Capa de Martlock do Mestre": ["CAPEITEM_FW_MARTLOCK_LEVEL3", "Capa do Mestre", 1, None, 0, "CAPEITEM_FW_MARTLOCK_BP_LEVEL3", 1, "Coração Empedrado"],
    "Capa de Martlock do Grão-Mestre": ["CAPEITEM_FW_MARTLOCK_LEVEL4", "Capa do Grão-Mestre", 1, None, 0, "CAPEITEM_FW_MARTLOCK_BP_LEVEL4", 1, "Coração Empedrado"],
    "Capa de Martlock do Ancião": ["CAPEITEM_FW_MARTLOCK_LEVEL5", "Capa do Ancião", 1, None, 0, "CAPEITEM_FW_MARTLOCK_BP_LEVEL5", 1, "Coração Empedrado"],

    # ================= CAPAS THETFORD =================
    "Capa de Thetford do Adepto": ["CAPEITEM_FW_THETFORD_LEVEL1", "Capa do Adepto", 1, None, 0, "CAPEITEM_FW_THETFORD_BP_LEVEL1", 1, "Coração Videira"],
    "Capa de Thetford do Perito": ["CAPEITEM_FW_THETFORD_LEVEL2", "Capa do Perito", 1, None, 0, "CAPEITEM_FW_THETFORD_BP_LEVEL2", 1, "Coração Videira"],
    "Capa de Thetford do Mestre": ["CAPEITEM_FW_THETFORD_LEVEL3", "Capa do Mestre", 1, None, 0, "CAPEITEM_FW_THETFORD_BP_LEVEL3", 1, "Coração Videira"],
    "Capa de Thetford do Grão-Mestre": ["CAPEITEM_FW_THETFORD_LEVEL4", "Capa do Grão-Mestre", 1, None, 0, "CAPEITEM_FW_THETFORD_BP_LEVEL4", 1, "Coração Videira"],
    "Capa de Thetford do Ancião": ["CAPEITEM_FW_THETFORD_LEVEL5", "Capa do Ancião", 1, None, 0, "CAPEITEM_FW_THETFORD_BP_LEVEL5", 1, "Coração Videira"],

    # ================= CAPAS CAERLEON =================
    "Capa de Caerleon do Adepto": ["CAPEITEM_FW_CAERLEON_LEVEL1", "Capa do Adepto", 1, None, 0, "CAPEITEM_FW_CAERLEON_BP_LEVEL1", 1, "Coração Sombrio"],
    "Capa de Caerleon do Perito": ["CAPEITEM_FW_CAERLEON_LEVEL2", "Capa do Perito", 1, None, 0, "CAPEITEM_FW_CAERLEON_BP_LEVEL2", 1, "Coração Sombrio"],
    "Capa de Caerleon do Mestre": ["CAPEITEM_FW_CAERLEON_LEVEL3", "Capa do Mestre", 1, None, 0, "CAPEITEM_FW_CAERLEON_BP_LEVEL3", 1, "Coração Sombrio"],
    "Capa de Caerleon do Grão-Mestre": ["CAPEITEM_FW_CAERLEON_LEVEL4", "Capa do Grão-Mestre", 1, None, 0, "CAPEITEM_FW_CAERLEON_BP_LEVEL4", 1, "Coração Sombrio"],
    "Capa de Caerleon do Ancião": ["CAPEITEM_FW_CAERLEON_LEVEL5", "Capa do Ancião", 1, None, 0, "CAPEITEM_FW_CAERLEON_BP_LEVEL5", 1, "Coração Sombrio"],

    # ================= CAPAS HERETIC (HEREGE) =================
    "Capa Herege do Adepto": ["CAPEITEM_HERETIC_LEVEL1", "Capa do Adepto", 1, None, 0, "CAPEITEM_HERETIC_BP_LEVEL1", 1, "Coração Arbóreo"],
    "Capa Herege do Perito": ["CAPEITEM_HERETIC_LEVEL2", "Capa do Perito", 1, None, 0, "CAPEITEM_HERETIC_BP_LEVEL2", 1, "Coração Arbóreo"],
    "Capa Herege do Mestre": ["CAPEITEM_HERETIC_LEVEL3", "Capa do Mestre", 1, None, 0, "CAPEITEM_HERETIC_BP_LEVEL3", 1, "Coração Arbóreo"],
    "Capa Herege do Grão-Mestre": ["CAPEITEM_HERETIC_LEVEL4", "Capa do Grão-Mestre", 1, None, 0, "CAPEITEM_HERETIC_BP_LEVEL4", 1, "Coração Arbóreo"],
    "Capa Herege do Ancião": ["CAPEITEM_HERETIC_LEVEL5", "Capa do Ancião", 1, None, 0, "CAPEITEM_HERETIC_BP_LEVEL5", 1, "Coração Arbóreo"],

    # ================= CAPAS UNDEAD (MORTA-VIVA) =================
    "Capa Morta-Viva do Adepto": ["CAPEITEM_UNDEAD_LEVEL1", "Capa do Adepto", 1, None, 0, "CAPEITEM_UNDEAD_BP_LEVEL1", 1, "Coração Montanhoso"],
    "Capa Morta-Viva do Perito": ["CAPEITEM_UNDEAD_LEVEL2", "Capa do Perito", 1, None, 0, "CAPEITEM_UNDEAD_BP_LEVEL2", 1, "Coração Montanhoso"],
    "Capa Morta-Viva do Mestre": ["CAPEITEM_UNDEAD_LEVEL3", "Capa do Mestre", 1, None, 0, "CAPEITEM_UNDEAD_BP_LEVEL3", 1, "Coração Montanhoso"],
    "Capa Morta-Viva do Grão-Mestre": ["CAPEITEM_UNDEAD_LEVEL4", "Capa do Grão-Mestre", 1, None, 0, "CAPEITEM_UNDEAD_BP_LEVEL4", 1, "Coração Montanhoso"],
    "Capa Morta-Viva do Ancião": ["CAPEITEM_UNDEAD_LEVEL5", "Capa do Ancião", 1, None, 0, "CAPEITEM_UNDEAD_BP_LEVEL5", 1, "Coração Montanhoso"],

    # ================= CAPAS KEEPER (PROTETORA) =================
    "Capa Protetora do Adepto": ["CAPEITEM_KEEPER_LEVEL1", "Capa do Adepto", 1, None, 0, "CAPEITEM_KEEPER_BP_LEVEL1", 1, "Coração Empedrado"],
    "Capa Protetora do Perito": ["CAPEITEM_KEEPER_LEVEL2", "Capa do Perito", 1, None, 0, "CAPEITEM_KEEPER_BP_LEVEL2", 1, "Coração Empedrado"],
    "Capa Protetora do Mestre": ["CAPEITEM_KEEPER_LEVEL3", "Capa do Mestre", 1, None, 0, "CAPEITEM_KEEPER_BP_LEVEL3", 1, "Coração Empedrado"],
    "Capa Protetora do Grão-Mestre": ["CAPEITEM_KEEPER_LEVEL4", "Capa do Grão-Mestre", 1, None, 0, "CAPEITEM_KEEPER_BP_LEVEL4", 1, "Coração Empedrado"],
    "Capa Protetora do Ancião": ["CAPEITEM_KEEPER_LEVEL5", "Capa do Ancião", 1, None, 0, "CAPEITEM_KEEPER_BP_LEVEL5", 1, "Coração Empedrado"],

    # ================= CAPAS MORGANA =================
    "Capa Morgana do Adepto": ["CAPEITEM_MORGANA_LEVEL1", "Capa do Adepto", 1, None, 0, "CAPEITEM_MORGANA_BP_LEVEL1", 1, "Coração Videira"],
    "Capa Morgana do Perito": ["CAPEITEM_MORGANA_LEVEL2", "Capa do Perito", 1, None, 0, "CAPEITEM_MORGANA_BP_LEVEL2", 1, "Coração Videira"],
    "Capa Morgana do Mestre": ["CAPEITEM_MORGANA_LEVEL3", "Capa do Mestre", 1, None, 0, "CAPEITEM_MORGANA_BP_LEVEL3", 1, "Coração Videira"],
    "Capa Morgana do Grão-Mestre": ["CAPEITEM_MORGANA_LEVEL4", "Capa do Grão-Mestre", 1, None, 0, "CAPEITEM_MORGANA_BP_LEVEL4", 1, "Coração Videira"],
    "Capa Morgana do Ancião": ["CAPEITEM_MORGANA_LEVEL5", "Capa do Ancião", 1, None, 0, "CAPEITEM_MORGANA_BP_LEVEL5", 1, "Coração Videira"],

    # ================= CAPAS DEMON (DEMONÍACA) =================
    "Capa Demoníaca do Adepto": ["CAPEITEM_DEMON_LEVEL1", "Capa do Adepto", 1, None, 0, "CAPEITEM_DEMON_BP_LEVEL1", 1, "Coração Bestial"],
    "Capa Demoníaca do Perito": ["CAPEITEM_DEMON_LEVEL2", "Capa do Perito", 1, None, 0, "CAPEITEM_DEMON_BP_LEVEL2", 1, "Coração Bestial"],
    "Capa Demoníaca do Mestre": ["CAPEITEM_DEMON_LEVEL3", "Capa do Mestre", 1, None, 0, "CAPEITEM_DEMON_BP_LEVEL3", 1, "Coração Bestial"],
    "Capa Demoníaca do Grão-Mestre": ["CAPEITEM_DEMON_LEVEL4", "Capa do Grão-Mestre", 1, None, 0, "CAPEITEM_DEMON_BP_LEVEL4", 1, "Coração Bestial"],
    "Capa Demoníaca do Ancião": ["CAPEITEM_DEMON_LEVEL5", "Capa do Ancião", 1, None, 0, "CAPEITEM_DEMON_BP_LEVEL5", 1, "Coração Bestial"],

    # ================= CAPAS BRECILIEN =================
    "Capa de Brecilien do Adepto": ["CAPEITEM_BRECILIEN_LEVEL1", "Capa do Adepto", 1, None, 0, "CAPEITEM_BRECILIEN_BP_LEVEL1", 1, "Fogo de Fada"],
    "Capa de Brecilien do Perito": ["CAPEITEM_BRECILIEN_LEVEL2", "Capa do Perito", 1, None, 0, "CAPEITEM_BRECILIEN_BP_LEVEL2", 1, "Fogo de Fada"],
    "Capa de Brecilien do Mestre": ["CAPEITEM_BRECILIEN_LEVEL3", "Capa do Mestre", 1, None, 0, "CAPEITEM_BRECILIEN_BP_LEVEL3", 1, "Fogo de Fada"],
    "Capa de Brecilien do Grão-Mestre": ["CAPEITEM_BRECILIEN_LEVEL4", "Capa do Grão-Mestre", 1, None, 0, "CAPEITEM_BRECILIEN_BP_LEVEL4", 1, "Fogo de Fada"],
    "Capa de Brecilien do Ancião": ["CAPEITEM_BRECILIEN_LEVEL5", "Capa do Ancião", 1, None, 0, "CAPEITEM_BRECILIEN_BP_LEVEL5", 1, "Fogo de Fada"],

    # ================= CAPAS AVALONIANA =================
    "Capa Avaloniana do Adepto": ["CAPEITEM_AVALON_LEVEL1", "Capa do Adepto", 1, None, 0, "CAPEITEM_AVALON_BP_LEVEL1", 1, "Fogo de Fada"],
    "Capa Avaloniana do Perito": ["CAPEITEM_AVALON_LEVEL2", "Capa do Perito", 1, None, 0, "CAPEITEM_AVALON_BP_LEVEL2", 1, "Fogo de Fada"],
    "Capa Avaloniana do Mestre": ["CAPEITEM_AVALON_LEVEL3", "Capa do Mestre", 1, None, 0, "CAPEITEM_AVALON_BP_LEVEL3", 1, "Fogo de Fada"],
    "Capa Avaloniana do Grão-Mestre": ["CAPEITEM_AVALON_LEVEL4", "Capa do Grão-Mestre", 1, None, 0, "CAPEITEM_AVALON_BP_LEVEL4", 1, "Fogo de Fada"],
    "Capa Avaloniana do Ancião": ["CAPEITEM_AVALON_LEVEL5", "Capa do Ancião", 1, None, 0, "CAPEITEM_AVALON_BP_LEVEL5", 1, "Fogo de Fada"],

    # ================= CAPAS CONTRABANDISTA (SMUGGLER) =================
    "Capa de Contrabandista do Adepto": ["CAPEITEM_SMUGGLER_LEVEL1", "Capa do Adepto", 1, None, 0, "CAPEITEM_SMUGGLER_BP_LEVEL1", 1, "Coração Sombrio"],
    "Capa de Contrabandista do Perito": ["CAPEITEM_SMUGGLER_LEVEL2", "Capa do Perito", 1, None, 0, "CAPEITEM_SMUGGLER_BP_LEVEL2", 1, "Coração Sombrio"],
    "Capa de Contrabandista do Mestre": ["CAPEITEM_SMUGGLER_LEVEL3", "Capa do Mestre", 1, None, 0, "CAPEITEM_SMUGGLER_BP_LEVEL3", 1, "Coração Sombrio"],
    "Capa de Contrabandista do Grão-Mestre": ["CAPEITEM_SMUGGLER_LEVEL4", "Capa do Grão-Mestre", 1, None, 0, "CAPEITEM_SMUGGLER_BP_LEVEL4", 1, "Coração Sombrio"],
    "Capa de Contrabandista do Ancião": ["CAPEITEM_SMUGGLER_LEVEL5", "Capa do Ancião", 1, None, 0, "CAPEITEM_SMUGGLER_BP_LEVEL5", 1, "Coração Sombrio"],
}

# ================= FILTROS CORRIGIDOS =================
FILTROS = {
    # ARMADURAS
    "armadura_placa": lambda k, v: "ARMOR_PLATE" in v[0],
    "armadura_couro": lambda k, v: "ARMOR_LEATHER" in v[0],
    "armadura_pano": lambda k, v: "ARMOR_CLOTH" in v[0],

    # BOTAS
    "botas_placa": lambda k, v: "SHOES_PLATE" in v[0],
    "botas_couro": lambda k, v: "SHOES_LEATHER" in v[0],
    "botas_pano": lambda k, v: "SHOES_CLOTH" in v[0],

    # CAPACETES
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

    # BORDÃO (CORRIGIDO PARA NÃO PEGAR MANOPLAS)
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

    # CAPAS
    "capas_normais": lambda k, v: "CAPEITEM_LEVEL" in v[0] and "FW_" not in v[0] and "HERETIC" not in v[0] and "UNDEAD" not in v[0] and "KEEPER" not in v[0] and "MORGANA" not in v[0] and "DEMON" not in v[0] and "BRECILIEN" not in v[0] and "AVALON" not in v[0] and "SMUGGLER" not in v[0],
    "capas_cidade": lambda k, v: "CAPEITEM_FW_" in v[0],
    "capas_herege": lambda k, v: "CAPEITEM_HERETIC" in v[0],
    "capas_mortaviva": lambda k, v: "CAPEITEM_UNDEAD" in v[0],
    "capas_protetora": lambda k, v: "CAPEITEM_KEEPER" in v[0],
    "capas_morgana": lambda k, v: "CAPEITEM_MORGANA" in v[0],
    "capas_demoniaca": lambda k, v: "CAPEITEM_DEMON" in v[0],
    "capas_brecilien": lambda k, v: "CAPEITEM_BRECILIEN" in v[0],
    "capas_avaloniana": lambda k, v: "CAPEITEM_AVALON" in v[0],
    "capas_contrabandista": lambda k, v: "CAPEITEM_SMUGGLER" in v[0],
    "todas_capas": lambda k, v: "CAPEITEM" in v[0],

}

# ================= FUNÇÕES =================
# MUDANÇA 1 IMPLEMENTADA: Prioriza preço de venda direto se histórico estiver defasado
def get_historical_price(item_id, location="Black Market"):
    try:
        # 1️⃣ Tenta preço atual primeiro (sempre prioridade)
        url_atual = f"{API_URL}{item_id}?locations={location}"
        resp_atual = requests.get(url_atual, timeout=10).json()
        if resp_atual and resp_atual[0]["sell_price_min"] > 0:
            return resp_atual[0]["sell_price_min"]

        # 2️⃣ Histórico das últimas 24h
        url_hist = f"{HISTORY_URL}{item_id}?locations={location}&timescale=24"
        resp_hist = requests.get(url_hist, timeout=10).json()

        if not resp_hist or "data" not in resp_hist[0]:
            return 0

        # 3️⃣ Filtra preços válidos
        prices = [
            d["avg_price"]
            for d in resp_hist[0]["data"]
            if d["avg_price"] > 0 and d["item_count"] >= 3
        ]

        if not prices:
            return 0

        # 4️⃣ Usa mediana (não média!)
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
    except: return 999

def id_item(tier, base, enc):
    return f"T{tier}_{base}@{enc}" if enc > 0 else f"T{tier}_{base}"

def ids_recurso_variantes(tier, nome, enc):
    # Se for um item do ITENS_DB (como capas), retorna o ID direto
    if nome in ITENS_DB:
        base_id = ITENS_DB[nome][0]
        return [id_item(tier, base_id, enc)]
    
    # Se for um recurso base normal
    if nome in RECURSO_MAP:
        base = f"T{tier}_{RECURSO_MAP[nome]}"
        if enc > 0: 
            return [f"{base}@{enc}", f"{base}_LEVEL{enc}@{enc}"]
        return [base]
    
    # Se não encontrar, retorna lista vazia
    return []

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

    # Coleta de IDs de recursos para a API
    ids_para_recursos = set()
    ids_para_itens = set()  # Para capas e itens intermediários
    
    for d in itens.values():
        # Recurso 1
        if d[1]:
            if d[1] in ITENS_DB:
                # É uma capa/item intermediário
                ids_para_itens.add(id_item(tier, ITENS_DB[d[1]][0], encanto))
            elif d[1] in RECURSO_MAP:
                # É recurso base
                for r in ids_recurso_variantes(tier, d[1], encanto):
                    ids_para_recursos.add(r)
        
        # Recurso 2
        if d[3]:
            if d[3] in ITENS_DB:
                ids_para_itens.add(id_item(tier, ITENS_DB[d[3]][0], encanto))
            elif d[3] in RECURSO_MAP:
                for r in ids_recurso_variantes(tier, d[3], encanto):
                    ids_para_recursos.add(r)

    # Buscar preços de recursos base
    precos_recursos = {}
    if ids_para_recursos:
        try:
            response = requests.get(
                f"{API_URL}{','.join(ids_para_recursos)}?locations=Thetford,FortSterling,Martlock,Lymhurst,Bridgewatch,Caerleon",
                timeout=20
            )
            data_recursos = response.json()
            
            for p in data_recursos:
                pid = p["item_id"]
                price = p["sell_price_min"]
                if price > 0:
                    if pid not in precos_recursos or price < precos_recursos[pid]["price"]:
                        precos_recursos[pid] = {"price": price, "city": p["city"]}
        except:
            st.error("Erro ao conectar com a API de recursos. Tente novamente.")
            st.stop()

    # Buscar preços de itens intermediários (capas) no Black Market
    precos_itens = {}
    if ids_para_itens:
        try:
            response = requests.get(
                f"{API_URL}{','.join(ids_para_itens)}?locations=Black Market",
                timeout=20
            )
            data_itens = response.json()
            
            for p in data_itens:
                pid = p["item_id"]
                price = p["sell_price_min"]
                if price > 0:
                    if pid not in precos_itens or price < precos_itens[pid]["price"]:
                        precos_itens[pid] = {"price": price, "city": p["city"]}
        except:
            pass  # Se falhar, continua sem os preços dos itens intermediários

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

        # ================= CÁLCULO DE RECURSOS BASE E ITENS =================
        for recurso, qtd in [(d[1], d[2]), (d[3], d[4])]:
            if not recurso or qtd == 0:
                continue

            found = False

            # Verifica se é um item do ITENS_DB (capa intermediária)
            if recurso in ITENS_DB:
                item_base_id = id_item(tier, ITENS_DB[recurso][0], encanto)
                if item_base_id in precos_itens:
                    info = precos_itens[item_base_id]
                    custo += info["price"] * qtd * quantidade
                    detalhes.append(
                        f"{qtd * quantidade}x {recurso} T{tier}.{encanto}: "
                        f"{info['price']:,} (Black Market)"
                    )
                    found = True
            
            # Verifica se é recurso base
            elif recurso in RECURSO_MAP:
                for rid in ids_recurso_variantes(tier, recurso, encanto):
                    if rid in precos_recursos:
                        info = precos_recursos[rid]
                        nome_recurso = NOMES_RECURSOS_TIER.get(recurso, {}).get(tier, recurso)
                        custo += info["price"] * qtd * quantidade
                        detalhes.append(
                            f"{qtd * quantidade}x T{tier}.{encanto} {nome_recurso}: "
                            f"{info['price']:,} ({info['city']})"
                        )
                        found = True
                        break

            if not found:
                valid_craft = False
                break

        if not valid_craft:
            continue

        # ================= CÁLCULO DE ARTEFATOS (ORNAMENTOS) =================
        if d[5]:
            art_id = f"T{tier}_{d[5]}"
            preco_artefato = get_historical_price(
                art_id,
                location="Caerleon,FortSterling,Thetford,Lymhurst,Bridgewatch,Martlock"
            )

            if preco_artefato > 0:
                qtd_art = d[6] * quantidade
                custo += preco_artefato * qtd_art

                detalhes.append(
                    f"{qtd_art}x Ornamento: "
                    f"{preco_artefato:,.0f} (Média Market)"
                )
            else:
                valid_craft = False

        # ================= CÁLCULO DE CORAÇÕES/FOGO DE FADA =================
        if len(d) > 7 and d[7]:
            coracao_nome = d[7]
            if coracao_nome in CORACOES_MAP:
                coracao_id = CORACOES_MAP[coracao_nome]
                qtd_coracao = CORACOES_QTD.get(tier, 1) * quantidade
                
                # Buscar preço do coração
                preco_coracao = get_historical_price(
                    coracao_id,
                    location="Caerleon,FortSterling,Thetford,Lymhurst,Bridgewatch,Martlock"
                )
                
                if preco_coracao > 0:
                    custo += preco_coracao * qtd_coracao
                    detalhes.append(
                        f"{qtd_coracao}x {coracao_nome}: "
                        f"{preco_coracao:,.0f} (Média Market)"
                    )
                else:
                    # Se não achar preço, assume 0 mas continua
                    detalhes.append(
                        f"{qtd_coracao}x {coracao_nome}: "
                        f"Preço não encontrado"
                    )

        if not valid_craft:
            continue

        custo_final = int(custo)
        venda_total = int(preco_venda_bm * quantidade)
        lucro = int((venda_total * 0.935) - custo_final)

        resultados.append(
            (nome, lucro, venda_total, custo_final, detalhes, "Market Atual/24h")
        )

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
