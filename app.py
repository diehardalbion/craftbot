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
        transition: transform 0.2s;
    }
    .item-card-custom:hover {
        transform: scale(1.01);
        border-color: #2ecc71;
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
            <a href="https://wa.me/5521983042557?text=Olá! Gostaria de comprar uma key." target="_blank" style="text-decoration: none;">
                <div style="background-color: #25d366; color: white; padding: 12px; border-radius: 5px; font-weight: bold; margin-top: 10px;">
                    COMPRAR VIA WHATSAPP
                </div>
            </a>
        </div>
        """, unsafe_allow_html=True)
    st.stop()

# ================= TRADUÇÃO DINÂMICA DE MATERIAIS =================
NOMES_RECURSOS_TIER = {
    "Barra de Aço": {4: "Barra de Aço", 5: "Barra de Titânio", 6: "Barra de Runita", 7: "Barra de Meteorito", 8: "Barra de Adamante"},
    "Tábuas de Pinho": {4: "Tábuas de Pinho", 5: "Tábuas de Cedro", 6: "Tábuas de Carvalho-Sangue", 7: "Tábuas de Freixo", 8: "Tábuas de Pau-branco"},
    "Couro Trabalhado": {4: "Couro Trabalhado", 5: "Couro Curtido", 6: "Couro Endurecido", 7: "Couro Reforçado", 8: "Couro Fortificado"},
    "Tecido Fino": {4: "Tecido Fino", 5: "Tecido Ornado", 6: "Tecido Rico", 7: "Tecido Opulento", 8: "Tecido Barroco"}
}

# ================= CONFIGURAÇÃO DE DADOS =================
API_URL = "https://west.albion-online-data.com/api/v2/stats/prices/"
CIDADES = ["Martlock", "Thetford", "FortSterling", "Lymhurst", "Bridgewatch", "Brecilien", "Caerleon", "Black Market"]
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

def identificar_cidade_bonus(nome_item):
    internal_code = ""
    for k, v in ITENS_DB.items():
        if k == nome_item:
            internal_code = v[0]
            break
    for cidade, sufixos in BONUS_CIDADE.items():
        if any(sufixo in internal_code for sufixo in sufixos):
            return cidade
    return "Desconhecida"

# ================= BANCO DE DADOS COMPLETO (DO SEU TXT) =================
ITENS_DB = {
    # BOLSAS
    "BOLSA": ["BAG", "Tecido Fino", 8, "Couro Trabalhado", 8, None, 0],
    
    # CURSED
    "Cajado Amaldiçoado": ["MAIN_CURSEDSTAFF", "Tábuas de Pinho", 16, "Barra de Aço", 8, None, 0],
    "Cajado Amaldiçoado Elevado": ["2H_CURSEDSTAFF", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0],
    "Cajado Demoníaco": ["2H_DEMONICSTAFF", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0],
    "Cajado Execrado": ["MAIN_CURSEDSTAFF_UNDEAD", "Tábuas de Pinho", 16, "Barra de Aço", 8, "ARTEFACT_MAIN_CURSEDSTAFF_UNDEAD", 1],
    "Caveira Amaldiçoada": ["2H_SKULLPANE_HELL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_SKULLPANE_HELL", 1],
    "Cajado da Danação": ["2H_CURSEDSTAFF_MORGANA", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_CURSEDSTAFF_MORGANA", 1],
    "Chama-sombra": ["MAIN_CURSEDSTAFF_AVALON", "Tábuas de Pinho", 16, "Barra de Aço", 8, "ARTEFACT_MAIN_CURSEDSTAFF_AVALON", 1],
    "Cajado Pútrido": ["2H_CURSEDSTAFF_CRYSTAL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "QUESTITEM_TOKEN_CRYSTAL_CURSEDSTAFF", 1],

    # QUARTERSTAFF
    "Bordão": ["2H_QUARTERSTAFF", "Barra de Aço", 12, "Couro Trabalhado", 20, None, 0],
    "Cajado Férreo": ["2H_IRONCLADSTAFF", "Barra de Aço", 12, "Couro Trabalhado", 20, None, 0],
    "Cajado Biliminado": ["2H_DOUBLEBLADEDSTAFF", "Barra de Aço", 12, "Couro Trabalhado", 20, None, 0],
    "Cajado de Monge Negro": ["2H_COMBATSTAFF_MORGANA", "Barra de Aço", 12, "Couro Trabalhado", 20, "ARTEFACT_2H_COMBATSTAFF_MORGANA", 1],
    "Segamímica": ["2H_TWINSCYTHE_HELL", "Barra de Aço", 12, "Couro Trabalhado", 20, "ARTEFACT_2H_TWINSCYTHE_HELL", 1],
    "Cajado do Equilíbrio": ["2H_ROCKSTAFF_KEEPER", "Barra de Aço", 12, "Couro Trabalhado", 20, "ARTEFACT_2H_ROCKSTAFF_KEEPER", 1],
    "Buscador do Graal": ["2H_QUARTERSTAFF_AVALON", "Barra de Aço", 12, "Couro Trabalhado", 20, "ARTEFACT_2H_QUARTERSTAFF_AVALON", 1],
    "Lâminas Gêmeas Fantasmagóricas": ["2H_QUARTERSTAFF_CRYSTAL", "Barra de Aço", 12, "Couro Trabalhado", 20, "QUESTITEM_TOKEN_CRYSTAL_QUARTERSTAFF", 1],

    # FROST
    "Cajado de Gelo": ["MAIN_FROSTSTAFF", "Tábuas de Pinho", 16, "Barra de Aço", 8, None, 0],
    "Cajado de Gelo Elevado": ["2H_FROSTSTAFF", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0],
    "Cajado Glacial": ["2H_GLACIALSTAFF", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0],
    "Cajado Enregelante": ["MAIN_FROSTSTAFF_DEEPFREEZE", "Tábuas de Pinho", 16, "Barra de Aço", 8, "ARTEFACT_MAIN_FROSTSTAFF_DEEPFREEZE", 1],
    "Cajado de Sincelo": ["2H_ICE_CRYSTAL_HELL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_ICE_CRYSTAL_HELL", 1],
    "Prisma Geleterno": ["2H_RAMPY_FROST_KEEPER", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_RAMPY_FROST_KEEPER", 1],
    "Uivo Frio": ["MAIN_FROSTSTAFF_AVALON", "Tábuas de Pinho", 16, "Barra de Aço", 8, "ARTEFACT_MAIN_FROSTSTAFF_AVALON", 1],
    "Cajado Ártico": ["2H_FROSTSTAFF_CRYSTAL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "QUESTITEM_TOKEN_CRYSTAL_FROSTSTAFF", 1],

    # ARCANO
    "Cajado Arcano": ["MAIN_ARCANESTAFF", "Tábuas de Pinho", 16, "Barra de Aço", 8, None, 0],
    "Cajado Arcano Elevado": ["2H_ARCANESTAFF", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0],
    "Cajado Enigmático": ["2H_ENIGMATICSTAFF", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0],
    "Cajado Feiticeiro": ["MAIN_ARCANESTAFF_UNDEAD", "Tábuas de Pinho", 16, "Barra de Aço", 8, "ARTEFACT_MAIN_ARCANESTAFF_UNDEAD", 1],
    "Cajado Oculto": ["2H_ARCANESTAFF_HELL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_ARCANESTAFF_HELL", 1],
    "Local Malévolo": ["2H_ENIGMATICSTAFF_MORGANA", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_ENIGMATICSTAFF_MORGANA", 1],
    "Som Equilibrado": ["2H_ARCANESTAFF_AVALON", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_ARCANESTAFF_AVALON", 1],
    "Cajado Astral": ["2H_ARCANESTAFF_CRYSTAL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "QUESTITEM_TOKEN_CRYSTAL_ARCANESTAFF", 1],

    # HOLY
    "Cajado Sagrado": ["MAIN_HOLYSTAFF", "Tábuas de Pinho", 16, "Tecido Fino", 8, None, 0],
    "Cajado Sagrado Elevado": ["2H_HOLYSTAFF", "Tábuas de Pinho", 20, "Tecido Fino", 12, None, 0],
    "Cajado Divino": ["2H_DIVINESTAFF", "Tábuas de Pinho", 20, "Tecido Fino", 12, None, 0],
    "Cajado Avivador": ["MAIN_HOLYSTAFF_MORGANA", "Tábuas de Pinho", 16, "Tecido Fino", 8, "ARTEFACT_MAIN_HOLYSTAFF_MORGANA", 1],
    "Cajado Corrompido": ["2H_HOLYSTAFF_HELL", "Tábuas de Pinho", 20, "Tecido Fino", 12, "ARTEFACT_2H_HOLYSTAFF_HELL", 1],
    "Cajado da Redenção": ["2H_HOLYSTAFF_UNDEAD", "Tábuas de Pinho", 20, "Tecido Fino", 12, "ARTEFACT_2H_HOLYSTAFF_UNDEAD", 1],
    "Queda Santa": ["MAIN_HOLYSTAFF_AVALON", "Tábuas de Pinho", 16, "Tecido Fino", 8, "ARTEFACT_MAIN_HOLYSTAFF_AVALON", 1],
    "Cajado Exaltado": ["2H_HOLYSTAFF_CRYSTAL", "Tábuas de Pinho", 20, "Tecido Fino", 12, "QUESTITEM_TOKEN_CRYSTAL_HOLYSTAFF", 1],

    # FIRE
    "Cajado de Fogo": ["MAIN_FIRESTAFF", "Tábuas de Pinho", 16, "Barra de Aço", 8, None, 0],
    "Cajado de Fogo Elevado": ["2H_FIRESTAFF", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0],
    "Cajado Infernal": ["2H_INFERNALSTAFF", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0],
    "Cajado Incendiário": ["MAIN_FIRESTAFF_KEEPER", "Tábuas de Pinho", 16, "Barra de Aço", 8, "ARTEFACT_MAIN_FIRESTAFF_KEEPER", 1],
    "Cajado Sulfuroso": ["2H_FIRE_CRYSTAL_HELL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_FIRE_CRYSTAL_HELL", 1],
    "Cajado Fulgurante": ["2H_INFERNALSTAFF_MORGANA", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_INFERNALSTAFF_MORGANA", 1],
    "Canção da Alvorada": ["2H_FIRESTAFF_AVALON", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_FIRESTAFF_AVALON", 1],
    "Cajado do Andarilho Flamejante": ["MAIN_FIRESTAFF_CRYSTAL", "Tábuas de Pinho", 16, "Barra de Aço", 8, "QUESTITEM_TOKEN_CRYSTAL_FIRESTAFF", 1],

    # NATURE
    "Cajado da Natureza": ["MAIN_NATURESTAFF", "Tábuas de Pinho", 16, "Tecido Fino", 8, None, 0],
    "Cajado da Natureza Elevado": ["2H_NATURESTAFF", "Tábuas de Pinho", 20, "Tecido Fino", 12, None, 0],
    "Cajado Selvagem": ["2H_WILDSTAFF", "Tábuas de Pinho", 20, "Tecido Fino", 12, None, 0],
    "Cajado Druídico": ["MAIN_NATURESTAFF_KEEPER", "Tábuas de Pinho", 16, "Tecido Fino", 8, "ARTEFACT_MAIN_NATURESTAFF_KEEPER", 1],
    "Cajado Pustulento": ["2H_NATURESTAFF_HELL", "Tábuas de Pinho", 20, "Tecido Fino", 12, "ARTEFACT_2H_NATURESTAFF_HELL", 1],
    "Cajado Rampante": ["2H_NATURESTAFF_KEEPER", "Tábuas de Pinho", 20, "Tecido Fino", 12, "ARTEFACT_2H_NATURESTAFF_KEEPER", 1],
    "Raiz Férrea": ["MAIN_NATURESTAFF_AVALON", "Tábuas de Pinho", 16, "Tecido Fino", 8, "ARTEFACT_MAIN_NATURESTAFF_AVALON", 1],
    "Cajado de Crosta Forjada": ["MAIN_NATURESTAFF_CRYSTAL", "Tábuas de Pinho", 16, "Tecido Fino", 8, "QUESTITEM_TOKEN_CRYSTAL_NATURESTAFF", 1],

    # ARCOS
    "Arco": ["2H_BOW", "Tábuas de Pinho", 32, None, 0, None, 0],
    "Arco de Guerra": ["2H_WARBOW", "Tábuas de Pinho", 32, None, 0, None, 0],
    "Arco Longo": ["2H_LONGBOW", "Tábuas de Pinho", 32, None, 0, None, 0],
    "Arco Sussurante": ["2H_BOW_KEEPER", "Tábuas de Pinho", 32, None, 0, "ARTEFACT_2H_BOW_KEEPER", 1],
    "Arco Plangente": ["2H_BOW_HELL", "Tábuas de Pinho", 32, None, 0, "ARTEFACT_2H_BOW_HELL", 1],
    "Arco Badônico": ["2H_BOW_UNDEAD", "Tábuas de Pinho", 32, None, 0, "ARTEFACT_2H_BOW_UNDEAD", 1],
    "Fura-bruma": ["2H_BOW_AVALON", "Tábuas de Pinho", 32, None, 0, "ARTEFACT_2H_BOW_AVALON", 1],
    "Arco do Andarilho Celeste": ["2H_BOW_CRYSTAL", "Tábuas de Pinho", 32, None, 0, "QUESTITEM_TOKEN_CRYSTAL_BOW", 1],

    # OFF-HANDS (MUITOS ITENS...)
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
    "ESCUDO": ["OFF_SHIELD", "Tábuas de Pinho", 4, "Barra de Aço", 4, None, 0],

    # ARMADURAS PLATE
    "BOTAS DE SOLDADO": ["SHOES_PLATE_SET1", "Barra de Aço", 8, None, 0, None, 0],
    "ARMADURA DE SOLDADO": ["ARMOR_PLATE_SET1", "Barra de Aço", 16, None, 0, None, 0],
    "ELMO DE SOLDADO": ["HEAD_PLATE_SET1", "Barra de Aço", 8, None, 0, None, 0],
    "BOTAS DE CAVALEIRO": ["SHOES_PLATE_SET2", "Barra de Aço", 8, None, 0, None, 0],
    "ARMADURA DE CAVALEIRO": ["ARMOR_PLATE_SET2", "Barra de Aço", 16, None, 0, None, 0],
    "ELMO DE CAVALEIRO": ["HEAD_PLATE_SET2", "Barra de Aço", 8, None, 0, None, 0],
    "BOTAS DE GUARDIÃO": ["SHOES_PLATE_SET3", "Barra de Aço", 8, None, 0, None, 0],
    "ARMADURA DE GUARDIÃO": ["ARMOR_PLATE_SET3", "Barra de Aço", 16, None, 0, None, 0],
    "ELMO DE GUARDIÃO": ["HEAD_PLATE_SET3", "Barra de Aço", 8, None, 0, None, 0],

    # ARMADURAS LEATHER
    "Sapatos de Mercenário": ["SHOES_LEATHER_SET1", "Couro Trabalhado", 8, None, 0, None, 0],
    "Casaco Mercenário": ["ARMOR_LEATHER_SET1", "Couro Trabalhado", 16, None, 0, None, 0],
    "Capud de Mercenário": ["HEAD_LEATHER_SET1", "Couro Trabalhado", 8, None, 0, None, 0],
    "Sapatos de Caçador": ["SHOES_LEATHER_SET2", "Couro Trabalhado", 8, None, 0, None, 0],
    "Casaco de Caçador": ["ARMOR_LEATHER_SET2", "Couro Trabalhado", 16, None, 0, None, 0],
    "Capuz de Caçador": ["HEAD_LEATHER_SET2", "Couro Trabalhado", 8, None, 0, None, 0],
    "Sapatos de Assassino": ["SHOES_LEATHER_SET3", "Couro Trabalhado", 8, None, 0, None, 0],
    "Casaco de Assassino": ["ARMOR_LEATHER_SET3", "Couro Trabalhado", 16, None, 0, None, 0],
    "Capuz de Assassino": ["HEAD_LEATHER_SET3", "Couro Trabalhado", 8, None, 0, None, 0],

    # ARMADURAS CLOTH
    "Sandálias de Erudito": ["SHOES_CLOTH_SET1", "Tecido Fino", 8, None, 0, None, 0],
    "Robe do Erudito": ["ARMOR_CLOTH_SET1", "Tecido Fino", 16, None, 0, None, 0],
    "Capote de Erudito": ["HEAD_CLOTH_SET1", "Tecido Fino", 8, None, 0, None, 0],
    "Sandálias de Clérigo": ["SHOES_CLOTH_SET2", "Tecido Fino", 8, None, 0, None, 0],
    "Robe de Clérigo": ["ARMOR_CLOTH_SET2", "Tecido Fino", 16, None, 0, None, 0],
    "Capote de Clérigo": ["HEAD_CLOTH_SET2", "Tecido Fino", 8, None, 0, None, 0],
    "Sandálias de Mago": ["SHOES_CLOTH_SET3", "Tecido Fino", 8, None, 0, None, 0],
    "Robe de Mago": ["ARMOR_CLOTH_SET3", "Tecido Fino", 16, None, 0, None, 0],
    "Capote de Mago": ["HEAD_CLOTH_SET3", "Tecido Fino", 8, None, 0, None, 0],

    # MELEE WEAPONS
    "ESPADA LARGA": ["MAIN_SWORD", "Barra de Aço", 16, "Couro Trabalhado", 8, None, 0],
    "MONTANTE": ["2H_CLAYMORE", "Barra de Aço", 20, "Couro Trabalhado", 12, None, 0],
    "ESPADAS DUPLAS": ["2H_DUALSWORD", "Barra de Aço", 20, "Couro Trabalhado", 12, None, 0],
    "MACHADO DE GUERRA": ["MAIN_AXE", "Barra de Aço", 16, "Tábuas de Pinho", 8, None, 0],
    "MACHADÃO": ["2H_AXE", "Barra de Aço", 20, "Tábuas de Pinho", 12, None, 0],
    "ALABARDA": ["2H_HALBERD", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0],
    "MAÇA": ["MAIN_MACE", "Barra de Aço", 16, "Tecido Fino", 8, None, 0],
    "MAÇA PESADA": ["2H_MACE", "Barra de Aço", 20, "Tecido Fino", 12, None, 0],
    "MANGUAL": ["2H_FLAIL", "Barra de Aço", 20, "Tecido Fino", 12, None, 0],
    "MARTELO": ["MAIN_HAMMER", "Barra de Aço", 24, None, 0, None, 0],
    "MARTELO DE BATALHA": ["2H_HAMMER", "Barra de Aço", 20, "Tecido Fino", 12, None, 0],
    "LUVAS DE LUTADOR": ["MAIN_KNUCKLES", "Barra de Aço", 12, "Couro Trabalhado", 20, None, 0],
    "BRAÇADEIRAS DE BATALHA": ["2H_KNUCKLES", "Barra de Aço", 12, "Couro Trabalhado", 20, None, 0],
    "ADAGA": ["MAIN_DAGGER", "Barra de Aço", 12, "Couro Trabalhado", 12, None, 0],
    "PAR DE ADAGAS": ["2H_DAGGER", "Barra de Aço", 16, "Couro Trabalhado", 16, None, 0],
    "LANÇA": ["MAIN_SPEAR", "Tábuas de Pinho", 16, "Barra de Aço", 8, None, 0],
    "PIQUE": ["2H_SPEAR", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0],
}

# ================= FILTROS =================
FILTROS = {
    "Armaduras (Placa)": lambda k, v: "ARMOR_PLATE" in v[0],
    "Botas (Placa)": lambda k, v: "SHOES_PLATE" in v[0],
    "Capacetes (Placa)": lambda k, v: "HEAD_PLATE" in v[0],
    "Armaduras (Couro)": lambda k, v: "ARMOR_LEATHER" in v[0],
    "Botas (Couro)": lambda k, v: "SHOES_LEATHER" in v[0],
    "Capacetes (Couro)": lambda k, v: "HEAD_LEATHER" in v[0],
    "Armaduras (Tecido)": lambda k, v: "ARMOR_CLOTH" in v[0],
    "Botas (Tecido)": lambda k, v: "SHOES_CLOTH" in v[0],
    "Capacetes (Tecido)": lambda k, v: "HEAD_CLOTH" in v[0],
    "Cajados (Amaldiçoados)": lambda k, v: "CURSEDSTAFF" in v[0],
    "Cajados (Gelo)": lambda k, v: "FROSTSTAFF" in v[0],
    "Cajados (Arcanos)": lambda k, v: "ARCANESTAFF" in v[0],
    "Cajados (Sagrados)": lambda k, v: "HOLYSTAFF" in v[0],
    "Cajados (Fogo)": lambda k, v: "FIRESTAFF" in v[0],
    "Cajados (Natureza)": lambda k, v: "NATURESTAFF" in v[0],
    "Bordão": lambda k, v: "QUARTERSTAFF" in v[0] or "IRONCLAD" in v[0] or "DOUBLEBLADED" in v[0],
    "Arcos": lambda k, v: "BOW" in v[0] and "CROSSBOW" not in v[0],
    "Espadas": lambda k, v: "SWORD" in v[0],
    "Machados": lambda k, v: "AXE" in v[0],
    "Maças": lambda k, v: "MACE" in v[0],
    "Martelos": lambda k, v: "HAMMER" in v[0],
    "Manoplas": lambda k, v: "KNUCKLES" in v[0],
    "Adagas": lambda k, v: "DAGGER" in v[0],
    "Lanças": lambda k, v: "SPEAR" in v[0],
    "Secundárias": lambda k, v: v[0].startswith("OFF_"),
    "Bolsas": lambda k, v: "BAG" in v[0]
}

# ================= SIDEBAR =================
with st.sidebar:
    st.image("https://i.imgur.com/kVAiMjD.png", width=100)
    st.title("Radar Craft")
    st.markdown("---")
    tier = st.selectbox("Selecione o Tier:", [4, 5, 6, 7, 8], index=0)
    encanto = st.selectbox("Encantamento:", [0, 1, 2, 3, 4], index=0)
    categoria = st.selectbox("Categoria:", list(FILTROS.keys()))
    quantidade = st.number_input("Qtd a fabricar:", min_value=1, value=1)
    taxa_loja = st.number_input("Taxa Uso da Loja (%):", value=0.0)
    st.markdown("---")
    if st.button("🚀 ANALISAR MERCADO"):
        st.session_state.buscar = True
    else:
        if "buscar" not in st.session_state:
            st.session_state.buscar = False

# ================= LÓGICA DE BUSCA E CÁLCULO =================
if st.session_state.buscar:
    itens_filtrados = {k: v for k, v in ITENS_DB.items() if FILTROS[categoria](k, v)}
    
    if not itens_filtrados:
        st.warning("Nenhum item encontrado nesta categoria.")
    else:
        ids_para_api = []
        for nome, d in itens_filtrados.items():
            sufixo = f"@{encanto}" if encanto > 0 else ""
            # Item principal
            ids_para_api.append(f"T{tier}_{d[0]}{sufixo}")
            # Recursos
            ids_para_api.append(f"T{tier}_{RECURSO_MAP[d[1]]}{sufixo}")
            if d[3]: ids_para_api.append(f"T{tier}_{RECURSO_MAP[d[3]]}{sufixo}")
            # Artefatos
            if d[5]: ids_para_api.append(f"T{tier}_{d[5]}")

        try:
            url_final = f"{API_URL}{','.join(list(set(ids_para_api)))}?locations={','.join(CIDADES)}"
            response = requests.get(url_final)
            data = response.json()

            precos_db = {}
            for entry in data:
                item_id = entry['item_id']
                if item_id not in precos_db: precos_db[item_id] = {}
                precos_db[item_id][entry['city']] = {
                    'price': entry['sell_price_min'],
                    'time': entry['sell_price_min_date']
                }

            # RESULTADOS
            st.subheader(f"📊 Análise {categoria} - T{tier}.{encanto}")
            
            for nome, d in itens_filtrados.items():
                sufixo = f"@{encanto}" if encanto > 0 else ""
                id_item = f"T{tier}_{d[0]}{sufixo}"
                id_mat1 = f"T{tier}_{RECURSO_MAP[d[1]]}{sufixo}"
                
                # Tradução Dinâmica para o detalhamento
                n_mat1 = NOMES_RECURSOS_TIER.get(d[1], {}).get(tier, d[1])
                n_mat2 = NOMES_RECURSOS_TIER.get(d[3], {}).get(tier, d[3]) if d[3] else None
                
                # Preços - Compra em Thetford (exemplo)
                p_mat1 = precos_db.get(id_mat1, {}).get("Thetford", {}).get('price', 0)
                custo_total = p_mat1 * d[2]
                
                if d[3]:
                    id_mat2 = f"T{tier}_{RECURSO_MAP[d[3]]}{sufixo}"
                    p_mat2 = precos_db.get(id_mat2, {}).get("Thetford", {}).get('price', 0)
                    custo_total += (p_mat2 * d[4])
                
                p_art = 0
                if d[5]:
                    id_art = f"T{tier}_{d[5]}"
                    p_art = precos_db.get(id_art, {}).get("Caerleon", {}).get('price', 0) # Artefato média Caerleon
                    custo_total += p_art
                
                # Taxa de Loja
                custo_total += (custo_total * (taxa_loja/100))
                custo_total_lote = custo_total * quantidade

                # Venda no Black Market
                venda_un = precos_db.get(id_item, {}).get("Black Market", {}).get('price', 0)
                h_venda = precos_db.get(id_item, {}).get("Black Market", {}).get('time', "N/A")
                venda_total_liquida = (venda_un * quantidade) * 0.935 # Taxa 6.5% BM
                
                lucro = venda_total_liquida - custo_total_lote
                perc_lucro = (lucro / custo_total_lote) * 100 if custo_total_lote > 0 else 0
                cidade_foco = identificar_cidade_bonus(nome)
                cor_destaque = "#2ecc71" if lucro > 0 else "#e74c3c"

                # CARD DE EXIBIÇÃO
                st.markdown(f"""
                <div class="item-card-custom" style="border-left: 8px solid {cor_destaque};">
                    <div style="font-weight: bold; font-size: 1.2rem; margin-bottom: 10px; color: {cor_destaque};">
                        ⚔️ {nome} [T{tier}.{encanto}] x{quantidade}
                    </div>
                    <div style="font-size: 1.05rem; margin-bottom: 8px;">
                        <span style="color: {cor_destaque}; font-weight: bold; font-size: 1.2rem;">💰 Lucro Estimado: {lucro:,.0f} ({perc_lucro:.2f}%)</span> 
                        <br><b>Investimento:</b> {custo_total_lote:,.0f} | <b>Venda Líquida (BM):</b> {venda_total_liquida:,.0f}
                    </div>
                    <div style="font-size: 0.95rem; color: #cbd5e1; margin-bottom: 10px;">
                        📍 <b>Foco Craft:</b> {cidade_foco} | 🕒 <b>Baseado em:</b> {h_venda}
                    </div>
                    <div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 5px; font-family: monospace; font-size: 0.85rem;">
                        📦 Detalhamento de Compras:<br>
                        {d[2]}x T{tier}.{encanto} {n_mat1}: {p_mat1:,.0f} (Thetford) 
                        {f" | {d[4]}x T{tier}.{encanto} {n_mat2}: {p_mat2:,.0f}" if n_mat2 else ""} 
                        {f" | 1x Artefato: {p_art:,.0f}" if p_art > 0 else ""}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Erro na conexão com API: {e}")
