import streamlit as st
import requests
import json
from datetime import datetime, timezone

# ================= CONFIGURAÇÃO E CSS =================
st.set_page_config("Radar Craft Albion", layout="wide", page_icon="⚔️")
st.markdown("""
<style>
    header {visibility: hidden;}
    .item-card-custom { 
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 12px; 
        padding: 15px; 
        margin-bottom: 15px; 
        border-left: 8px solid #2ecc71;
        color: white;
    }
    .stApp { background-color: #0e1117; }
</style>
""", unsafe_allow_html=True)

# ================= LOGIN =================
def verificar_chave(chave_usuario):
    try:
        with open("keys.json", "r") as f:
            keys_db = json.load(f)
        if chave_usuario in keys_db:
            return True, keys_db[chave_usuario]["cliente"]
        return False, "Chave inválida."
    except: return False, "Erro ao acessar base de chaves."

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🛡️ Radar Craft")
    key_input = st.text_input("Insira sua Chave:", type="password")
    if st.button("LIBERAR ACESSO"):
        sucesso, msg = verificar_chave(key_input)
        if sucesso:
            st.session_state.autenticado = True
            st.rerun()
        else: st.error(msg)
    st.stop()

# ================= CONFIG DE DADOS =================
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

# ================= DADOS E MAPAS =================
API_URL = "https://west.albion-online-data.com/api/v2/stats/prices/"
CIDADES = ["Martlock", "Thetford", "FortSterling", "Lymhurst", "Bridgewatch", "Caerleon", "Black Market"]
RECURSO_MAP = {"Tecido": "CLOTH", "Couro": "LEATHER", "Metal": "METALBAR", "Tabua": "PLANKS"}

ITENS_DB = {
    "TOMO DE FEITIÇOS": ["OFF_BOOK", "Tecido", 4, "Couro", 4, None, 0],
    "OLHO DOS SEGREDOS": ["OFF_ORB_HELL", "Tecido", 4, "Couro", 4, "ARTEFACT_OFF_ORB_HELL", 1],
    "MUISEC": ["OFF_LAMP_HELL", "Tecido", 4, "Couro", 4, "ARTEFACT_OFF_LAMP_HELL", 1],
    "RAIZ MESTRA": ["OFF_DEMONSKULL_HELL", "Tecido", 4, "Couro", 4, "ARTEFACT_OFF_DEMONSKULL_HELL", 1],
    "INCENSÁRIO CELESTE": ["OFF_TOWERSHIELD_HELL", "Tecido", 4, "Couro", 4, "ARTEFACT_OFF_TOWERSHIELD_HELL", 1],
    "GRUMÓRIO ESTAGNADO": ["OFF_SHIELD_HELL", "Tecido", 4, "Couro", 4, "ARTEFACT_OFF_SHIELD_HELL", 1],
    "TOCHA": ["OFF_TORCH", "Tabua", 4, "Tecido", 4, None, 0],
    "BRUMÁRIO": ["OFF_HORN_KEEPER", "Tabua", 4, "Tecido", 4, "ARTEFACT_OFF_HORN_KEEPER", 1],
    "BENGALA MALIGNA": ["OFF_JESTERCANE_HELL", "Tabua", 4, "Tecido", 4, "ARTEFACT_OFF_JESTERCANE_HELL", 1],
    "LUME CRIPTICO": ["OFF_LAMP_UNDEAD", "Tabua", 4, "Tecido", 4, "ARTEFACT_OFF_LAMP_UNDEAD", 1],
    "CETRO SAGRADO": ["OFF_CENSER_AVALON", "Tabua", 4, "Tecido", 4, "ARTEFACT_OFF_CENSER_AVALON", 1],
    "TOCHA CHAMA AZUL": ["OFF_LAMP_CRYSTAL", "Tabua", 4, "Tecido", 4, "QUESTITEM_TOKEN_CRYSTAL_LAMP", 1],
    "BOTAS DE SOLDADO": ["SHOES_PLATE_SET1", "Metal", 8, None, 0, None, 0],
    "BOTAS DE CAVALEIRO": ["SHOES_PLATE_SET2", "Metal", 8, None, 0, None, 0],
    "BOTAS DE GUARDIÃO": ["SHOES_PLATE_SET3", "Metal", 8, None, 0, None, 0],
    "BOTAS REAIS": ["SHOES_PLATE_ROYAL", "Metal", 8, None, 0, "QUESTITEM_TOKEN_ROYAL", 2],
    "BOTAS DE GUARDA-TUMBAS": ["SHOES_PLATE_UNDEAD", "Metal", 8, None, 0, "ARTEFACT_SHOES_PLATE_UNDEAD", 1],
    "BOTAS DEMÔNIAS": ["SHOES_PLATE_HELL", "Metal", 8, None, 0, "ARTEFACT_SHOES_PLATE_HELL", 1],
    "BOTAS JUDICANTES": ["SHOES_PLATE_KEEPER", "Metal", 8, None, 0, "ARTEFACT_SHOES_PLATE_KEEPER", 1],
    "BOTAS DE TECELÃO": ["SHOES_PLATE_AVALON", "Metal", 8, None, 0, "ARTEFACT_SHOES_PLATE_AVALON", 1],
    "BOTAS DA BRAVURA": ["SHOES_PLATE_CRYSTAL", "Metal", 8, None, 0, "QUESTITEM_TOKEN_CRYSTAL_SHOES_PLATE", 1],
    "ARMADURA DE SOLDADO": ["ARMOR_PLATE_SET1", "Metal", 16, None, 0, None, 0],
    "ARMADURA DE CAVALEIRO": ["ARMOR_PLATE_SET2", "Metal", 16, None, 0, None, 0],
    "ARMADURA DE GUARDIÃO": ["ARMOR_PLATE_SET3", "Metal", 16, None, 0, None, 0],
    "ARMADURA REAL": ["ARMOR_PLATE_ROYAL", "Metal", 16, None, 0, "QUESTITEM_TOKEN_ROYAL", 4],
    "ARMADURA DE GUARDA-TUMBAS": ["ARMOR_PLATE_UNDEAD", "Metal", 16, None, 0, "ARTEFACT_ARMOR_PLATE_UNDEAD", 1],
    "ARMADURA DEMÔNIA": ["ARMOR_PLATE_HELL", "Metal", 16, None, 0, "ARTEFACT_ARMOR_PLATE_HELL", 1],
    "ARMADURA JUDICANTE": ["ARMOR_PLATE_KEEPER", "Metal", 16, None, 0, "ARTEFACT_ARMOR_PLATE_KEEPER", 1],
    "ARMADURA DE TECELÃO": ["ARMOR_PLATE_AVALON", "Metal", 16, None, 0, "ARTEFACT_ARMOR_PLATE_AVALON", 1],
    "ARMADURA DA BRAVURA": ["ARMOR_PLATE_CRYSTAL", "Metal", 16, None, 0, "QUESTITEM_TOKEN_CRYSTAL_ARMOR_PLATE", 1],
    "ELMO DE SOLDADO": ["HEAD_PLATE_SET1", "Metal", 8, None, 0, None, 0],
    "ELMO DE CAVALEIRO": ["HEAD_PLATE_SET2", "Metal", 8, None, 0, None, 0],
    "ELMO DE GUARDIÃO": ["HEAD_PLATE_SET3", "Metal", 8, None, 0, None, 0],
    "ELMO REAL": ["HEAD_PLATE_ROYAL", "Metal", 8, None, 0, "QUESTITEM_TOKEN_ROYAL", 2],
    "ELMO DE GUARDA-TUMBAS": ["HEAD_PLATE_UNDEAD", "Metal", 8, None, 0, "ARTEFACT_HEAD_PLATE_UNDEAD", 1],
    "ELMO DEMÔNIO": ["HEAD_PLATE_HELL", "Metal", 8, None, 0, "ARTEFACT_HEAD_PLATE_HELL", 1],
    "ELMO JUDICANTE": ["HEAD_PLATE_KEEPER", "Metal", 8, None, 0, "ARTEFACT_HEAD_PLATE_KEEPER", 1],
    "ELMO DE TECELÃO": ["HEAD_PLATE_AVALON", "Metal", 8, None, 0, "ARTEFACT_HEAD_PLATE_AVALON", 1],
    "ELMO DA BRAVURA": ["HEAD_PLATE_CRYSTAL", "Metal", 8, None, 0, "QUESTITEM_TOKEN_CRYSTAL_HEAD_PLATE", 1],
    "Sapatos de Mercenário": ["SHOES_LEATHER_SET1", "Couro", 8, None, 0, None, 0],
    "Sapatos de Caçador": ["SHOES_LEATHER_SET2", "Couro", 8, None, 0, None, 0],
    "Sapatos de Assassino": ["SHOES_LEATHER_SET3", "Couro", 8, None, 0, None, 0],
    "Sapatos Reais": ["SHOES_LEATHER_ROYAL", "Couro", 8, None, 0, "QUESTITEM_TOKEN_ROYAL", 2],
    "Sapatos de Espreitador": ["SHOES_LEATHER_HELL", "Couro", 8, None, 0, "ARTEFACT_SHOES_LEATHER_HELL", 1],
    "Sapatos Espectrais": ["SHOES_LEATHER_UNDEAD", "Couro", 8, None, 0, "ARTEFACT_SHOES_LEATHER_UNDEAD", 1],
    "Sapatos de Andarilho da Névoa": ["SHOES_LEATHER_FEY", "Couro", 8, None, 0, "ARTEFACT_SHOES_LEATHER_FEY", 1],
    "Sapatos da Tenacidade": ["SHOES_LEATHER_CRYSTAL", "Couro", 8, None, 0, "QUESTITEM_TOKEN_CRYSTAL_SHOES_LEATHER", 1],
    "Casaco Mercenário": ["ARMOR_LEATHER_SET1", "Couro", 16, None, 0, None, 0],
    "Casaco de Caçador": ["ARMOR_LEATHER_SET2", "Couro", 16, None, 0, None, 0],
    "Casaco de Assassino": ["ARMOR_LEATHER_SET3", "Couro", 16, None, 0, None, 0],
    "Casaco Real": ["ARMOR_LEATHER_ROYAL", "Couro", 16, None, 0, "QUESTITEM_TOKEN_ROYAL", 4],
    "Casaco de Espreitador": ["ARMOR_LEATHER_HELL", "Couro", 16, None, 0, "ARTEFACT_ARMOR_LEATHER_HELL", 1],
    "Casaco Infernal": ["ARMOR_LEATHER_MORGANA", "Couro", 16, None, 0, "ARTEFACT_ARMOR_LEATHER_MORGANA", 1],
    "Casaco Espectral": ["ARMOR_LEATHER_UNDEAD", "Couro", 16, None, 0, "ARTEFACT_ARMOR_LEATHER_UNDEAD", 1],
    "Casaco de Andarilho da Névoa": ["ARMOR_LEATHER_FEY", "Couro", 16, None, 0, "ARTEFACT_ARMOR_LEATHER_FEY", 1],
    "Casaco da Tenacidade": ["ARMOR_LEATHER_CRYSTAL", "Couro", 16, None, 0, "QUESTITEM_TOKEN_CRYSTAL_ARMOR_LEATHER", 1],
    "Capud de Mercenário": ["HEAD_LEATHER_SET1", "Couro", 8, None, 0, None, 0],
    "Capuz de Caçador": ["HEAD_LEATHER_SET2", "Couro", 8, None, 0, None, 0],
    "Capuz de Assassino": ["HEAD_LEATHER_SET3", "Couro", 8, None, 0, None, 0],
    "Capuz Real": ["HEAD_LEATHER_ROYAL", "Couro", 8, None, 0, "QUESTITEM_TOKEN_ROYAL", 2],
    "Capuz de Espreitador": ["HEAD_LEATHER_HELL", "Couro", 8, None, 0, "ARTEFACT_HEAD_LEATHER_HELL", 1],
    "Capuz Inferial": ["HEAD_LEATHER_MORGANA", "Couro", 8, None, 0, "ARTEFACT_HEAD_LEATHER_MORGANA", 1],
    "Capuz Espectral": ["HEAD_LEATHER_UNDEAD", "Couro", 8, None, 0, "ARTEFACT_HEAD_LEATHER_UNDEAD", 1],
    "Capuz de Andarilho da Névoa": ["HEAD_LEATHER_FEY", "Couro", 8, None, 0, "ARTEFACT_HEAD_LEATHER_FEY", 1],
    "Capuz da Tenacidade": ["HEAD_LEATHER_CRYSTAL", "Couro", 8, None, 0, "QUESTITEM_TOKEN_CRYSTAL_HEAD_LEATHER", 1],
    "Sandálias de Erudito": ["SHOES_CLOTH_SET1", "Tecido", 8, None, 0, None, 0],
    "Sandálias de Clérigo": ["SHOES_CLOTH_SET2", "Tecido", 8, None, 0, None, 0],
    "Sandálias de Mago": ["SHOES_CLOTH_SET3", "Tecido", 8, None, 0, None, 0],
    "Sandálais Reais": ["SHOES_CLOTH_ROYAL", "Tecido", 8, None, 0, "QUESTITEM_TOKEN_ROYAL", 2],
    "Sandálias de Druida": ["SHOES_CLOTH_KEEPER", "Tecido", 8, None, 0, "ARTEFACT_SHOES_CLOTH_KEEPER", 1],
    "Sandálias Malévolas": ["SHOES_CLOTH_HELL", "Tecido", 8, None, 0, "ARTEFACT_SHOES_CLOTH_HELL", 1],
    "Sandálias Sectárias": ["SHOES_CLOTH_MORGANA", "Tecido", 8, None, 0, "ARTEFACT_SHOES_CLOTH_MORGANA", 1],
    "Sandálias Feéricas": ["SHOES_CLOTH_FEY", "Tecido", 8, None, 0, "ARTEFACT_SHOES_CLOTH_FEY", 1],
    "Sandálias Da Pureza": ["SHOES_CLOTH_CRYSTAL", "Tecido", 8, None, 0, "QUESTITEM_TOKEN_CRYSTAL_SHOES_CLOTH", 1],
    "Robe do Erudito": ["ARMOR_CLOTH_SET1", "Tecido", 16, None, 0, None, 0],
    "Robe de Clérigo": ["ARMOR_CLOTH_SET2", "Tecido", 16, None, 0, None, 0],
    "Robe de Mago": ["ARMOR_CLOTH_SET3", "Tecido", 16, None, 0, None, 0],
    "Robe Real": ["ARMOR_CLOTH_ROYAL", "Tecido", 16, None, 0, "QUESTITEM_TOKEN_ROYAL", 4],
    "Robe do Druída": ["ARMOR_CLOTH_KEEPER", "Tecido", 16, None, 0, "ARTEFACT_ARMOR_CLOTH_KEEPER", 1],
    "Robe Malévolo": ["ARMOR_CLOTH_HELL", "Tecido", 16, None, 0, "ARTEFACT_ARMOR_CLOTH_HELL", 1],
    "Robe Sectário": ["ARMOR_CLOTH_MORGANA", "Tecido", 16, None, 0, "ARTEFACT_ARMOR_CLOTH_MORGANA", 1],
    "Robe Feérico": ["ARMOR_CLOTH_FEY", "Tecido", 16, None, 0, "ARTEFACT_ARMOR_CLOTH_FEY", 1],
    "Robe da Pureza": ["ARMOR_CLOTH_CRYSTAL", "Tecido", 16, None, 0, "QUESTITEM_TOKEN_CRYSTAL_ARMOR_CLOTH", 1],
    "Capote de Erudito": ["HEAD_CLOTH_SET1", "Tecido", 8, None, 0, None, 0],
    "Capote de Clérigo": ["HEAD_CLOTH_SET2", "Tecido", 8, None, 0, None, 0],
    "Capote de Mago": ["HEAD_CLOTH_SET3", "Tecido", 8, None, 0, None, 0],
    "Capote Real": ["HEAD_CLOTH_ROYAL", "Tecido", 8, None, 0, "QUESTITEM_TOKEN_ROYAL", 2],
    "Capote Druída": ["HEAD_CLOTH_KEEPER", "Tecido", 8, None, 0, "ARTEFACT_HEAD_CLOTH_KEEPER", 1],
    "Capote Malévolo": ["HEAD_CLOTH_HELL", "Tecido", 8, None, 0, "ARTEFACT_HEAD_CLOTH_HELL", 1],
    "Capote Sectário": ["HEAD_CLOTH_MORGANA", "Tecido", 8, None, 0, "ARTEFACT_HEAD_CLOTH_MORGANA", 1],
    "Capote Feérico": ["HEAD_CLOTH_FEY", "Tecido", 8, None, 0, "ARTEFACT_HEAD_CLOTH_FEY", 1],
    "Capote da Pureza": ["HEAD_CLOTH_CRYSTAL", "Tecido", 8, None, 0, "QUESTITEM_TOKEN_CRYSTAL_HEAD_CLOTH", 1],
    "ESPADA LARGA": ["MAIN_SWORD", "Metal", 16, "Couro", 8, None, 0],
    "MONTANTE": ["2H_CLAYMORE", "Metal", 20, "Couro", 12, None, 0],
    "ESPADAS DUPLAS": ["2H_DUALSWORD", "Metal", 20, "Couro", 12, None, 0],
    "LÂMINA ACIARADA": ["MAIN_SWORD_HELL", "Metal", 16, "Couro", 8, "ARTEFACT_MAIN_SWORD_HELL", 1],
    "ESPADA ENTALHADA": ["2H_CLEAVER_SWORD", "Metal", 20, "Couro", 12, "ARTEFACT_2H_CLEAVER_SWORD", 1],
    "PAR DE GALATINAS": ["2H_DUALSWORD_HELL", "Metal", 20, "Couro", 12, "ARTEFACT_2H_DUALSWORD_HELL", 1],
    "CRIA-REAIS": ["2H_CLAYMORE_AVALON", "Metal", 20, "Couro", 12, "ARTEFACT_2H_CLAYMORE_AVALON", 1],
    "LÂMINA DA INFINIDADE": ["2H_SWORD_CRYSTAL", "Metal", 16, "Couro", 8, "QUESTITEM_TOKEN_CRYSTAL_SWORD", 1],
    "MACHADO DE GUERRA": ["MAIN_AXE", "Metal", 16, "Tabua", 8, None, 0],
    "MACHADÃO": ["2H_AXE", "Metal", 20, "Tabua", 12, None, 0],
    "ALABARDA": ["2H_HALBERD", "Tabua", 20, "Metal", 12, None, 0],
    "CHAMA-CORPOS": ["2H_AXE_CARRION_MORGANA", "Tabua", 20, "Metal", 12, "ARTEFACT_2H_AXE_CARRION_MORGANA", 1],
    "SEGADEIRA INFERNAL": ["2H_REAPER_AXE_HELL", "Tabua", 12, "Metal", 20, "ARTEFACT_2H_REAPER_AXE_HELL", 1],
    "PATAS DE URSO": ["2H_AXE_KEEPER", "Tabua", 12, "Metal", 20, "ARTEFACT_2H_AXE_KEEPER", 1],
    "QUEBRA-REINO": ["2H_AXE_AVALON", "Tabua", 12, "Metal", 20, "ARTEFACT_2H_AXE_AVALON", 1],
    "FOICE DE CRISTAL": ["2H_AXE_CRYSTAL", "Tabua", 12, "Metal", 20, "QUESTITEM_TOKEN_CRYSTAL_AXE", 1],
    "MAÇA": ["MAIN_MACE", "Metal", 16, "Tecido", 8, None, 0],
    "MAÇA PESADA": ["2H_MACE", "Metal", 20, "Tecido", 12, None, 0],
    "MANGUAL": ["2H_FLAIL", "Metal", 20, "Tecido", 12, None, 0],
    "MAÇA PÉTREA": ["MAIN_MACE_HELL", "Metal", 16, "Tecido", 8, "ARTEFACT_MAIN_MACE_HELL", 1],
    "MAÇA Cam": ["MAIN_MACE_HELL", "Metal", 16, "Tecido", 8, "ARTEFACT_MAIN_MACE_HELL", 1],
    "MAÇA CAMBRIANA": ["2H_MACE_MORGANA", "Metal", 20, "Tecido", 12, "ARTEFACT_2H_MACE_MORGANA", 1],
    "JURADOR": ["2H_MACE_AVALON", "Metal", 20, "Tecido", 12, "ARTEFACT_2H_MACE_AVALON", 1],
    "MONARCA TEMPESTUOSO": ["2H_MACE_CRYSTAL", "Metal", 16, "Tecido", 8, "QUESTITEM_TOKEN_CRYSTAL_MACE", 1],
    "MARTELO": ["MAIN_HAMMER", "Metal", 24, None, 0, None, 0],
    "MARTELO DE BATALHA": ["2H_HAMMER", "Metal", 20, "Tecido", 12, None, 0],
    "MARTELO ELEVADO": ["2H_POLEHAMMER", "Metal", 20, "Tecido", 12, None, 0],
    "MARTELO DE FÚNEBRE": ["2H_HAMMER_UNDEAD", "Metal", 20, "Tecido", 12, "ARTEFACT_2H_HAMMER_UNDEAD", 1],
    "MARTELO E FORJA": ["2H_HAMMER_HELL", "Metal", 20, "Tecido", 12, "ARTEFACT_2H_HAMMER_HELL", 1],
    "GUARDA-BOSQUES": ["2H_RAM_KEEPER", "Metal", 20, "Tecido", 12, "ARTEFACT_2H_RAM_KEEPER", 1],
    "MÃO DA JUSTIÇA": ["2H_HAMMER_AVALON", "Metal", 20, "Tecido", 12, "ARTEFACT_2H_HAMMER_AVALON", 1],
    "MARTELO ESTRONDOSO": ["2H_HAMMER_CRYSTAL", "Metal", 20, "Tecido", 12, "QUESTITEM_TOKEN_CRYSTAL_HAMMER", 1],
    "LUVAS DE LUTADOR": ["MAIN_KNUCKLES", "Metal", 12, "Couro", 20, None, 0],
    "BRAÇADEIRAS DE BATALHA": ["2H_KNUCKLES", "Metal", 12, "Couro", 20, None, 0],
    "MANOPLAS CRAVADAS": ["2H_SPIKED_KNUCKLES", "Metal", 12, "Couro", 20, None, 0],
    "LUVAS URSINAS": ["2H_KNUCKLES_KEEPER", "Metal", 12, "Couro", 20, "ARTEFACT_2H_KNUCKLES_KEEPER", 1],
    "MÃOS INFERNAIS": ["2H_KNUCKLES_HELL", "Metal", 12, "Couro", 20, "ARTEFACT_2H_KNUCKLES_HELL", 1],
    "CESTUS GOLPEADORES": ["2H_KNUCKLES_MORGANA", "Metal", 12, "Couro", 20, "ARTEFACT_2H_KNUCKLES_MORGANA", 1],
    "PUNHOS DE AVALON": ["2H_KNUCKLES_AVALON", "Metal", 12, "Couro", 20, "ARTEFACT_2H_KNUCKLES_AVALON", 1],
    "BRAÇADEIRAS PULSANTES": ["2H_KNUCKLES_CRYSTAL", "Metal", 12, "Couro", 20, "QUESTITEM_TOKEN_CRYSTAL_KNUCKLES", 1],
    "BESTA": ["2H_CROSSBOW", "Tabua", 20, "Metal", 12, None, 0],
    "BESTA PESADA": ["2H_CROSSBOW_LARGE", "Tabua", 20, "Metal", 12, None, 0],
    "BESTA LEVE": ["MAIN_CROSSBOW", "Tabua", 16, "Metal", 8, None, 0],
    "REPETIDOR LAMENTOSO": ["2H_CROSSBOW_UNDEAD", "Tabua", 20, "Metal", 12, "ARTEFACT_2H_CROSSBOW_UNDEAD", 1],
    "LANÇA-VIROTES": ["2H_CROSSBOW_HELL", "Tabua", 20, "Metal", 12, "ARTEFACT_2H_CROSSBOW_HELL", 1],
    "ARCO DE CERGO": ["2H_CROSSBOW_MORGANA", "Tabua", 20, "Metal", 12, "ARTEFACT_2H_CROSSBOW_MORGANA", 1],
    "MODELADOR DE ENERGIA": ["2H_CROSSBOW_AVALON", "Tabua", 20, "Metal", 12, "ARTEFACT_2H_CROSSBOW_AVALON", 1],
    "DETONADORES RELUZENTES": ["2H_CROSSBOW_CRYSTAL", "Tabua", 20, "Metal", 12, "QUESTITEM_TOKEN_CRYSTAL_CROSSBOW", 1],
    "ESCUDO": ["OFF_SHIELD", "Tabua", 4, "Metal", 4, None, 0],
    "SARCÓFAGO": ["OFF_SHIELD_UNDEAD", "Tabua", 4, "Metal", 4, "ARTEFACT_OFF_SHIELD_UNDEAD", 1],
    "ESCUDO VAMPÍRICO": ["OFF_SHIELD_HELL", "Tabua", 4, "Metal", 4, "ARTEFACT_OFF_SHIELD_HELL", 1],
    "QUEBRA-ROSTOS": ["OFF_SHIELD_HELL", "Tabua", 4, "Metal", 4, "ARTEFACT_OFF_SHIELD_HELL_2", 1],
    "ÉGIDE ASTRAL": ["OFF_SHIELD_AVALON", "Tabua", 4, "Metal", 4, "ARTEFACT_OFF_SHIELD_AVALON", 1],
    "BARREIRA INQUEBRÁVEL": ["OFF_SHIELD_CRYSTAL", "Tabua", 4, "Metal", 4, "QUESTITEM_TOKEN_CRYSTAL_SHIELD", 1],
    "ADAGA": ["MAIN_DAGGER", "Metal", 12, "Couro", 12, None, 0],
    "PAR DE ADAGAS": ["2H_DAGGER", "Metal", 16, "Couro", 16, None, 0],
    "GARRAS": ["MAIN_DAGGER_HELL", "Metal", 12, "Couro", 20, None, 0],
    "DESSANGRADOR": ["MAIN_DAGGER_HELL", "Metal", 16, "Couro", 8, "ARTEFACT_MAIN_DAGGER_HELL", 1],
    "PRESA DEMONÍACA": ["MAIN_DAGGER_PR_HELL", "Metal", 12, "Couro", 12, "ARTEFACT_MAIN_DAGGER_PR_HELL", 1],
    "MORTÍFICOS": ["2H_DUAL_DAGGER_HELL", "Metal", 16, "Couro", 16, "ARTEFACT_2H_DUAL_DAGGER_HELL", 1],
    "FÚRIA CONTIDA": ["2H_DAGGER_AVALON", "Metal", 12, "Couro", 20, "ARTEFACT_2H_DAGGER_AVALON", 1],
    "GÊMEAS ANIQUILADORAS": ["2H_DAGGER_CRYSTAL", "Metal", 16, "Couro", 16, "QUESTITEM_TOKEN_CRYSTAL_DAGGER", 1],
    "LANÇA": ["MAIN_SPEAR", "Tabua", 16, "Metal", 8, None, 0],
    "PIQUE": ["2H_SPEAR", "Tabua", 20, "Metal", 12, None, 0],
    "ARCHA": ["2H_GLAIVE", "Tabua", 12, "Metal", 20, None, 0],
    "LANÇA GARCEIRA": ["MAIN_SPEAR_KEEPER", "Tabua", 16, "Metal", 8, "ARTEFACT_MAIN_SPEAR_KEEPER", 1],
    "CAÇA-ESPÍRITOS": ["2H_SPEAR_HELL", "Tabua", 20, "Metal", 12, "ARTEFACT_2H_SPEAR_HELL", 1],
    "LANÇA TRINA": ["2H_GLAIVE_HELL", "Tabua", 20, "Metal", 12, "ARTEFACT_2H_GLAIVE_HELL", 1],
    "ALVORADA": ["MAIN_SPEAR_AVALON", "Tabua", 16, "Metal", 8, "ARTEFACT_MAIN_SPEAR_AVALON", 1],
    "ARCHA FRATURADA": ["2H_SPEAR_CRYSTAL", "Tabua", 12, "Metal", 20, "QUESTITEM_TOKEN_CRYSTAL_SPEAR", 1]
}

# ================= FILTROS =================
FILTROS = {
    "armadura_placa": lambda k, v: "ARMOR_PLATE" in v[0],
    "armadura_couro": lambda k, v: "ARMOR_LEATHER" in v[0],
    "armadura_pano": lambda k, v: "ARMOR_CLOTH" in v[0],
    "botas_placa": lambda k, v: "SHOES_PLATE" in v[0],
    "botas_couro": lambda k, v: "SHOES_LEATHER" in v[0],
    "botas_pano": lambda k, v: "SHOES_CLOTH" in v[0],
    "capacete_placa": lambda k, v: "HEAD_PLATE" in v[0],
    "capacete_couro": lambda k, v: "HEAD_LEATHER" in v[0],
    "capacete_pano": lambda k, v: "HEAD_CLOTH" in v[0],
    "armas": lambda k, v: v[0].startswith(("MAIN_", "2H_")),
    "secundarias": lambda k, v: v[0].startswith("OFF_"),
}

def id_item(tier, base, enc): return f"T{tier}_{base}@{enc}" if enc > 0 else f"T{tier}_{base}"
def id_recurso(tier, nome, enc):
    base = f"T{tier}_{RECURSO_MAP[nome]}"
    return f"{base}_LEVEL{enc}@{enc}" if enc > 0 else base

# ================= SIDEBAR =================
with st.sidebar:
    st.header("Filtros")
    tier = st.number_input("Tier", 4, 8, 6)
    encanto = st.number_input("Encanto", 0, 4, 0)
    btn = st.button("🚀 ATUALIZAR RADAR")

# ================= LOGICA =================
if btn:
    ids_busca = []
    for d in ITENS_DB.values():
        ids_busca.append(id_item(tier, d[0], encanto))
        ids_busca.append(id_recurso(tier, d[1], encanto))
        if d[3]: ids_busca.append(id_recurso(tier, d[3], encanto))

    try:
        data = requests.get(f"{API_URL}{','.join(set(ids_busca))}?locations={','.join(CIDADES)}").json()
    except:
        st.error("Erro ao conectar com a API.")
        st.stop()

    precos = {}
    for p in data:
        pid, city = p["item_id"], p["city"]
        if pid not in precos: precos[pid] = {}
        precos[pid][city] = p["buy_price_max"] if city == "Black Market" else p["sell_price_min"]

    resultados = []
    for nome, d in ITENS_DB.items():
        iid = id_item(tier, d[0], encanto)
        venda_bm = precos.get(iid, {}).get("Black Market", 0)
        if venda_bm < 500: continue

        # Cálculo do Material 1
        rid1 = id_recurso(tier, d[1], encanto)
        opcoes1 = {c: v for c, v in precos.get(rid1, {}).items() if v > 0 and c != "Black Market"}
        if not opcoes1: continue
        melhor_c1 = min(opcoes1, key=opcoes1.get)
        custo_mats = opcoes1[melhor_c1] * d[2]
        detalhe = f"{d[2]}x {d[1]} ({melhor_c1})"

        # Cálculo do Material 2 (se houver)
        if d[3]:
            rid2 = id_recurso(tier, d[3], encanto)
            opcoes2 = {c: v for c, v in precos.get(rid2, {}).items() if v > 0 and c != "Black Market"}
            if not opcoes2: continue
            melhor_c2 = min(opcoes2, key=opcoes2.get)
            custo_mats += opcoes2[melhor_c2] * d[4]
            detalhe += f" + {d[4]}x {d[3]} ({melhor_c2})"

        investimento = int(custo_mats * 0.752) # Com Retorno de Recurso
        lucro = int((venda_bm * 0.935) - investimento) # Desconto Taxa BM

        if lucro > 1000: # Filtro para mostrar só lucro real
            resultados.append({
                "nome": nome, "lucro": lucro, "venda": venda_bm,
                "invest": investimento, "detalhe": detalhe,
                "perc": round((lucro/investimento)*100, 1)
            })

    resultados.sort(key=lambda x: x["lucro"], reverse=True)

    if not resultados:
        st.warning("Nenhum item altamente lucrativo encontrado no momento.")
    else:
        for r in resultados[:10]: # TOP 10
            st.markdown(f"""
            <div class="item-card-custom">
                <h3 style='margin:0; color:#2ecc71;'>{r['nome']} [T{tier}.{encanto}]</h3>
                <b>💰 Lucro: {r['lucro']:,} ({r['perc']}%)</b><br>
                Invest: {r['invest']:,} | Venda BM: {r['venda']:,}<br>
                <small>📦 {r['detalhe']}</small>
            </div>
            """, unsafe_allow_html=True)
