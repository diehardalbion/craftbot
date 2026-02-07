import streamlit as st
import requests
import json
from datetime import datetime, timezone

# ================= CONFIGURAÇÃO DA PÁGINA =================
st.set_page_config("Radar Craft Albion", layout="wide", page_icon="⚔️")

# ================= CUSTOM CSS (VISUAL MANTIDO) =================
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
    .item-card-custom { 
        background-color: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px);
        border-radius: 12px; 
        padding: 20px; 
        margin-bottom: 20px; 
        border: 1px solid rgba(46, 204, 113, 0.2);
        border-left: 8px solid #2ecc71;
        color: white !important;
    }
    .stButton>button {
        width: 100%;
        background-color: #2ecc71 !important;
        color: white !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ================= SISTEMA DE LOGIN (MANTIDO) =================
def verificar_chave(chave_usuario):
    try:
        with open("keys.json", "r") as f:
            keys_db = json.load(f)
        if chave_usuario in keys_db:
            dados = keys_db[chave_usuario]
            if not dados["ativa"]: return False, "Chave desativada."
            if dados["expira"] != "null":
                data_expira = datetime.strptime(dados["expira"], "%Y-%m-%d").date()
                if datetime.now().date() > data_expira: return False, "Chave expirou."
            return True, dados["cliente"]
        return False, "Chave inválida."
    except: return False, "Erro ao acessar base de chaves."

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🛡️ Radar Craft - Acesso Restrito")
    key_input = st.text_input("Insira sua Chave:", type="password")
    if st.button("LIBERAR ACESSO"):
        sucesso, mensagem = verificar_chave(key_input)
        if sucesso:
            st.session_state.autenticado = True
            st.rerun()
        else: st.error(mensagem)
    st.stop()

# ================= ITENS_DB =================
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

    # --- ELMOS DE PLACA ---
    "ELMO DE SOLDADO": ["HEAD_PLATE_SET1", "Barra de Aço", 8, None, 0, None, 0],
    "ELMO DE CAVALEIRO": ["HEAD_PLATE_SET2", "Barra de Aço", 8, None, 0, None, 0],
    "ELMO DE GUARDIÃO": ["HEAD_PLATE_SET3", "Barra de Aço", 8, None, 0, None, 0],
    "ELMO REAL": ["HEAD_PLATE_ROYAL", "Barra de Aço", 8, None, 0, "QUESTITEM_TOKEN_ROYAL", 2],
    "ELMO DE GUARDA-TUMBAS": ["HEAD_PLATE_UNDEAD", "Barra de Aço", 8, None, 0, "ARTEFACT_HEAD_PLATE_UNDEAD", 1],
    "ELMO DEMÔNIO": ["HEAD_PLATE_HELL", "Barra de Aço", 8, None, 0, "ARTEFACT_HEAD_PLATE_HELL", 1],
    "ELMO JUDICANTE": ["HEAD_PLATE_KEEPER", "Barra de Aço", 8, None, 0, "ARTEFACT_HEAD_PLATE_KEEPER", 1],
    "ELMO DE TECELÃO": ["HEAD_PLATE_AVALON", "Barra de Aço", 8, None, 0, "ARTEFACT_HEAD_PLATE_AVALON", 1],
    "ELMO DA BRAVURA": ["HEAD_PLATE_CRYSTAL", "Barra de Aço", 8, None, 0, "QUESTITEM_TOKEN_CRYSTAL_HEAD_PLATE", 1],

    # --- SAPATOS DE COURO ---
    "Sapatos de Mercenário": ["SHOES_LEATHER_SET1", "Couro Trabalhado", 8, None, 0, None, 0],
    "Sapatos de Caçador": ["SHOES_LEATHER_SET2", "Couro Trabalhado", 8, None, 0, None, 0],
    "Sapatos de Assassino": ["SHOES_LEATHER_SET3", "Couro Trabalhado", 8, None, 0, None, 0],
    "Sapatos Reais": ["SHOES_LEATHER_ROYAL", "Couro Trabalhado", 8, None, 0, "QUESTITEM_TOKEN_ROYAL", 2],
    "Sapatos de Espreitador": ["SHOES_LEATHER_HELL", "Couro Trabalhado", 8, None, 0, "ARTEFACT_SHOES_LEATHER_HELL", 1],
    "Sapatos Espectrais": ["SHOES_LEATHER_UNDEAD", "Couro Trabalhado", 8, None, 0, "ARTEFACT_SHOES_LEATHER_UNDEAD", 1],
    "Sapatos de Andarilho da Névoa": ["SHOES_LEATHER_FEY", "Couro Trabalhado", 8, None, 0, "ARTEFACT_SHOES_LEATHER_FEY", 1],
    "Sapatos da Tenacidade": ["SHOES_LEATHER_CRYSTAL", "Couro Trabalhado", 8, None, 0, "QUESTITEM_TOKEN_CRYSTAL_SHOES_LEATHER", 1],

    # --- CASACOS DE COURO ---
    "Casaco Mercenário": ["ARMOR_LEATHER_SET1", "Couro Trabalhado", 16, None, 0, None, 0],
    "Casaco de Caçador": ["ARMOR_LEATHER_SET2", "Couro Trabalhado", 16, None, 0, None, 0],
    "Casaco de Assassino": ["ARMOR_LEATHER_SET3", "Couro Trabalhado", 16, None, 0, None, 0],
    "Casaco Real": ["ARMOR_LEATHER_ROYAL", "Couro Trabalhado", 16, None, 0, "QUESTITEM_TOKEN_ROYAL", 4],
    "Casaco de Espreitador": ["ARMOR_LEATHER_HELL", "Couro Trabalhado", 16, None, 0, "ARTEFACT_ARMOR_LEATHER_HELL", 1],
    "Casaco Infernal": ["ARMOR_LEATHER_MORGANA", "Couro Trabalhado", 16, None, 0, "ARTEFACT_ARMOR_LEATHER_MORGANA", 1],
    "Casaco Espectral": ["ARMOR_LEATHER_UNDEAD", "Couro Trabalhado", 16, None, 0, "ARTEFACT_ARMOR_LEATHER_UNDEAD", 1],
    "Casaco de Andarilho da Névoa": ["ARMOR_LEATHER_FEY", "Couro Trabalhado", 16, None, 0, "ARTEFACT_ARMOR_LEATHER_FEY", 1],
    "Casaco da Tenacidade": ["ARMOR_LEATHER_CRYSTAL", "Couro Trabalhado", 16, None, 0, "QUESTITEM_TOKEN_CRYSTAL_ARMOR_LEATHER", 1],

    # --- CAPUZES DE COURO ---
    "Capud de Mercenário": ["HEAD_LEATHER_SET1", "Couro Trabalhado", 8, None, 0, None, 0],
    "Capuz de Caçador": ["HEAD_LEATHER_SET2", "Couro Trabalhado", 8, None, 0, None, 0],
    "Capuz de Assassino": ["HEAD_LEATHER_SET3", "Couro Trabalhado", 8, None, 0, None, 0],
    "Capuz Real": ["HEAD_LEATHER_ROYAL", "Couro Trabalhado", 8, None, 0, "QUESTITEM_TOKEN_ROYAL", 2],
    "Capuz de Espreitador": ["HEAD_LEATHER_HELL", "Couro Trabalhado", 8, None, 0, "ARTEFACT_HEAD_LEATHER_HELL", 1],
    "Capuz Inferial": ["HEAD_LEATHER_MORGANA", "Couro Trabalhado", 8, None, 0, "ARTEFACT_HEAD_LEATHER_MORGANA", 1],
    "Capuz Espectral": ["HEAD_LEATHER_UNDEAD", "Couro Trabalhado", 8, None, 0, "ARTEFACT_HEAD_LEATHER_UNDEAD", 1],
    "Capuz de Andarilho da Névoa": ["HEAD_LEATHER_FEY", "Couro Trabalhado", 8, None, 0, "ARTEFACT_HEAD_LEATHER_FEY", 1],
    "Capuz da Tenacidade": ["HEAD_LEATHER_CRYSTAL", "Couro Trabalhado", 8, None, 0, "QUESTITEM_TOKEN_CRYSTAL_HEAD_LEATHER", 1],

    # --- SANDÁLIAS DE TECIDO ---
    "Sandálias de Erudito": ["SHOES_CLOTH_SET1", "Tecido Fino", 8, None, 0, None, 0],
    "Sandálias de Clérigo": ["SHOES_CLOTH_SET2", "Tecido Fino", 8, None, 0, None, 0],
    "Sandálias de Mago": ["SHOES_CLOTH_SET3", "Tecido Fino", 8, None, 0, None, 0],
    "Sandálais Reais": ["SHOES_CLOTH_ROYAL", "Tecido Fino", 8, None, 0, "QUESTITEM_TOKEN_ROYAL", 2],
    "Sandálias de Druida": ["SHOES_CLOTH_KEEPER", "Tecido Fino", 8, None, 0, "ARTEFACT_SHOES_CLOTH_KEEPER", 1],
    "Sandálias Malévolas": ["SHOES_CLOTH_HELL", "Tecido Fino", 8, None, 0, "ARTEFACT_SHOES_CLOTH_HELL", 1],
    "Sandálias Sectárias": ["SHOES_CLOTH_MORGANA", "Tecido Fino", 8, None, 0, "ARTEFACT_SHOES_CLOTH_MORGANA", 1],
    "Sandálias Feéricas": ["SHOES_CLOTH_FEY", "Tecido Fino", 8, None, 0, "ARTEFACT_SHOES_CLOTH_FEY", 1],
    "Sandálias Da Pureza": ["SHOES_CLOTH_CRYSTAL", "Tecido Fino", 8, None, 0, "QUESTITEM_TOKEN_CRYSTAL_SHOES_CLOTH", 1],

    # --- ROBES DE TECIDO ---
    "Robe do Erudito": ["ARMOR_CLOTH_SET1", "Tecido Fino", 16, None, 0, None, 0],
    "Robe de Clérigo": ["ARMOR_CLOTH_SET2", "Tecido Fino", 16, None, 0, None, 0],
    "Robe de Mago": ["ARMOR_CLOTH_SET3", "Tecido Fino", 16, None, 0, None, 0],
    "Robe Real": ["ARMOR_CLOTH_ROYAL", "Tecido Fino", 16, None, 0, "QUESTITEM_TOKEN_ROYAL", 4],
    "Robe do Druída": ["ARMOR_CLOTH_KEEPER", "Tecido Fino", 16, None, 0, "ARTEFACT_ARMOR_CLOTH_KEEPER", 1],
    "Robe Malévolo": ["ARMOR_CLOTH_HELL", "Tecido Fino", 16, None, 0, "ARTEFACT_ARMOR_CLOTH_HELL", 1],
    "Robe Sectário": ["ARMOR_CLOTH_MORGANA", "Tecido Fino", 16, None, 0, "ARTEFACT_ARMOR_CLOTH_MORGANA", 1],
    "Robe Feérico": ["ARMOR_CLOTH_FEY", "Tecido Fino", 16, None, 0, "ARTEFACT_ARMOR_CLOTH_FEY", 1],
    "Robe da Pureza": ["ARMOR_CLOTH_CRYSTAL", "Tecido Fino", 16, None, 0, "QUESTITEM_TOKEN_CRYSTAL_ARMOR_CLOTH", 1],

    # --- CAPOTES DE TECIDO ---
    "Capote de Erudito": ["HEAD_CLOTH_SET1", "Tecido Fino", 8, None, 0, None, 0],
    "Capote de Clérigo": ["HEAD_CLOTH_SET2", "Tecido Fino", 8, None, 0, None, 0],
    "Capote de Mago": ["HEAD_CLOTH_SET3", "Tecido Fino", 8, None, 0, None, 0],
    "Capote Real": ["HEAD_CLOTH_ROYAL", "Tecido Fino", 8, None, 0, "QUESTITEM_TOKEN_ROYAL", 2],
    "Capote Druída": ["HEAD_CLOTH_KEEPER", "Tecido Fino", 8, None, 0, "ARTEFACT_HEAD_CLOTH_KEEPER", 1],
    "Capote Malévolo": ["HEAD_CLOTH_HELL", "Tecido Fino", 8, None, 0, "ARTEFACT_HEAD_CLOTH_HELL", 1],
    "Capote Sectário": ["HEAD_CLOTH_MORGANA", "Tecido Fino", 8, None, 0, "ARTEFACT_HEAD_CLOTH_MORGANA", 1],
    "Capote Feérico": ["HEAD_CLOTH_FEY", "Tecido Fino", 8, None, 0, "ARTEFACT_HEAD_CLOTH_FEY", 1],
    "Capote da Pureza": ["HEAD_CLOTH_CRYSTAL", "Tecido Fino", 8, None, 0, "QUESTITEM_TOKEN_CRYSTAL_HEAD_CLOTH", 1],

    # --- ESPADAS ---
    "ESPADA LARGA": ["MAIN_SWORD", "Barra de Aço", 16, "Couro Trabalhado", 8, None, 0],
    "MONTANTE": ["2H_CLAYMORE", "Barra de Aço", 20, "Couro Trabalhado", 12, None, 0],
    "ESPADAS DUPLAS": ["2H_DUALSWORD", "Barra de Aço", 20, "Couro Trabalhado", 12, None, 0],
    "LÂMINA ACIARADA": ["MAIN_SWORD_HELL", "Barra de Aço", 16, "Couro Trabalhado", 8, "ARTEFACT_MAIN_SWORD_HELL", 1],
    "ESPADA ENTALHADA": ["2H_CLEAVER_SWORD", "Barra de Aço", 20, "Couro Trabalhado", 12, "ARTEFACT_2H_CLEAVER_SWORD", 1],
    "PAR DE GALATINAS": ["2H_DUALSWORD_HELL", "Barra de Aço", 20, "Couro Trabalhado", 12, "ARTEFACT_2H_DUALSWORD_HELL", 1],
    "CRIA-REAIS": ["2H_CLAYMORE_AVALON", "Barra de Aço", 20, "Couro Trabalhado", 12, "ARTEFACT_2H_CLAYMORE_AVALON", 1],
    "LÂMINA DA INFINIDADE": ["2H_SWORD_CRYSTAL", "Barra de Aço", 16, "Couro Trabalhado", 8, "QUESTITEM_TOKEN_CRYSTAL_SWORD", 1],

    # --- MACHADOS ---
    "MACHADO DE GUERRA": ["MAIN_AXE", "Barra de Aço", 16, "Tábuas de Pinho", 8, None, 0],
    "MACHADÃO": ["2H_AXE", "Barra de Aço", 20, "Tábuas de Pinho", 12, None, 0],
    "ALABARDA": ["2H_HALBERD", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0],
    "CHAMA-CORPOS": ["2H_AXE_CARRION_MORGANA", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_AXE_CARRION_MORGANA", 1],
    "SEGADEIRA INFERNAL": ["2H_REAPER_AXE_HELL", "Tábuas de Pinho", 12, "Barra de Aço", 20, "ARTEFACT_2H_REAPER_AXE_HELL", 1],
    "PATAS DE URSO": ["2H_AXE_KEEPER", "Tábuas de Pinho", 12, "Barra de Aço", 20, "ARTEFACT_2H_AXE_KEEPER", 1],
    "QUEBRA-REINO": ["2H_AXE_AVALON", "Tábuas de Pinho", 12, "Barra de Aço", 20, "ARTEFACT_2H_AXE_AVALON", 1],
    "FOICE DE CRISTAL": ["2H_AXE_CRYSTAL", "Tábuas de Pinho", 12, "Barra de Aço", 20, "QUESTITEM_TOKEN_CRYSTAL_AXE", 1],

    # --- MAÇAS ---
    "MAÇA": ["MAIN_MACE", "Barra de Aço", 16, "Tecido Fino", 8, None, 0],
    "MAÇA PESADA": ["2H_MACE", "Barra de Aço", 20, "Tecido Fino", 12, None, 0],
    "MANGUAL": ["2H_FLAIL", "Barra de Aço", 20, "Tecido Fino", 12, None, 0],
    "MAÇA PÉTREA": ["MAIN_MACE_HELL", "Barra de Aço", 16, "Tecido Fino", 8, "ARTEFACT_MAIN_MACE_HELL", 1],
    "MAÇA DE ÍNCUBO": ["MAIN_MACE_HELL", "Barra de Aço", 16, "Tecido Fino", 8, "ARTEFACT_MAIN_MACE_HELL", 1],
    "MAÇA CAMBRIANA": ["2H_MACE_MORGANA", "Barra de Aço", 20, "Tecido Fino", 12, "ARTEFACT_2H_MACE_MORGANA", 1],
    "JURADOR": ["2H_MACE_AVALON", "Barra de Aço", 20, "Tecido Fino", 12, "ARTEFACT_2H_MACE_AVALON", 1],
    "MONARCA TEMPESTUOSO": ["2H_MACE_CRYSTAL", "Barra de Aço", 16, "Tecido Fino", 8, "QUESTITEM_TOKEN_CRYSTAL_MACE", 1],

    # --- MARTELOS ---
    "MARTELO": ["MAIN_HAMMER", "Barra de Aço", 24, None, 0, None, 0],
    "MARTELO DE BATALHA": ["2H_HAMMER", "Barra de Aço", 20, "Tecido Fino", 12, None, 0],
    "MARTELO ELEVADO": ["2H_POLEHAMMER", "Barra de Aço", 20, "Tecido Fino", 12, None, 0],
    "MARTELO DE FÚNEBRE": ["2H_HAMMER_UNDEAD", "Barra de Aço", 20, "Tecido Fino", 12, "ARTEFACT_2H_HAMMER_UNDEAD", 1],
    "MARTELO E FORJA": ["2H_HAMMER_HELL", "Barra de Aço", 20, "Tecido Fino", 12, "ARTEFACT_2H_HAMMER_HELL", 1],
    "GUARDA-BOSQUES": ["2H_RAM_KEEPER", "Barra de Aço", 20, "Tecido Fino", 12, "ARTEFACT_2H_RAM_KEEPER", 1],
    "MÃO DA JUSTIÇA": ["2H_HAMMER_AVALON", "Barra de Aço", 20, "Tecido Fino", 12, "ARTEFACT_2H_HAMMER_AVALON", 1],
    "MARTELO ESTRONDOSO": ["2H_HAMMER_CRYSTAL", "Barra de Aço", 20, "Tecido Fino", 12, "QUESTITEM_TOKEN_CRYSTAL_HAMMER", 1],

    # --- LUVAS ---
    "LUVAS DE LUTADOR": ["MAIN_KNUCKLES", "Barra de Aço", 12, "Couro Trabalhado", 20, None, 0],
    "BRAÇADEIRAS DE BATALHA": ["2H_KNUCKLES", "Barra de Aço", 12, "Couro Trabalhado", 20, None, 0],
    "MANOPLAS CRAVADAS": ["2H_SPIKED_KNUCKLES", "Barra de Aço", 12, "Couro Trabalhado", 20, None, 0],
    "LUVAS URSINAS": ["2H_KNUCKLES_KEEPER", "Barra de Aço", 12, "Couro Trabalhado", 20, "ARTEFACT_2H_KNUCKLES_KEEPER", 1],
    "MÃOS INFERNAIS": ["2H_KNUCKLES_HELL", "Barra de Aço", 12, "Couro Trabalhado", 20, "ARTEFACT_2H_KNUCKLES_HELL", 1],
    "CESTUS GOLPEADORES": ["2H_KNUCKLES_MORGANA", "Barra de Aço", 12, "Couro Trabalhado", 20, "ARTEFACT_2H_KNUCKLES_MORGANA", 1],
    "PUNHOS DE AVALON": ["2H_KNUCKLES_AVALON", "Barra de Aço", 12, "Couro Trabalhado", 20, "ARTEFACT_2H_KNUCKLES_AVALON", 1],
    "BRAÇADEIRAS PULSANTES": ["2H_KNUCKLES_CRYSTAL", "Barra de Aço", 12, "Couro Trabalhado", 20, "QUESTITEM_TOKEN_CRYSTAL_KNUCKLES", 1],

    # --- BESTAS ---
    "BESTA": ["2H_CROSSBOW", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0],
    "BESTA PESADA": ["2H_CROSSBOW_LARGE", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0],
    "BESTA LEVE": ["MAIN_CROSSBOW", "Tábuas de Pinho", 16, "Barra de Aço", 8, None, 0],
    "REPETIDOR LAMENTOSO": ["2H_CROSSBOW_UNDEAD", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_CROSSBOW_UNDEAD", 1],
    "LANÇA-VIROTES": ["2H_CROSSBOW_HELL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_CROSSBOW_HELL", 1],
    "ARCO DE CERGO": ["2H_CROSSBOW_MORGANA", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_CROSSBOW_MORGANA", 1],
    "MODELADOR DE ENERGIA": ["2H_CROSSBOW_AVALON", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_CROSSBOW_AVALON", 1],
    "DETONADORES RELUZENTES": ["2H_CROSSBOW_CRYSTAL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "QUESTITEM_TOKEN_CRYSTAL_CROSSBOW", 1],

    # --- ESCUDOS ---
    "ESCUDO": ["OFF_SHIELD", "Tábuas de Pinho", 4, "Barra de Aço", 4, None, 0],
    "SARCÓFAGO": ["OFF_SHIELD_UNDEAD", "Tábuas de Pinho", 4, "Barra de Aço", 4, "ARTEFACT_OFF_SHIELD_UNDEAD", 1],
    "ESCUDO VAMPÍRICO": ["OFF_SHIELD_HELL", "Tábuas de Pinho", 4, "Barra de Aço", 4, "ARTEFACT_OFF_SHIELD_HELL", 1],
    "QUEBRA-ROSTOS": ["OFF_SHIELD_HELL", "Tábuas de Pinho", 4, "Barra de Aço", 4, "ARTEFACT_OFF_SHIELD_HELL_2", 1],
    "ÉGIDE ASTRAL": ["OFF_SHIELD_AVALON", "Tábuas de Pinho", 4, "Barra de Aço", 4, "ARTEFACT_OFF_SHIELD_AVALON", 1],
    "BARREIRA INQUEBRÁVEL": ["OFF_SHIELD_CRYSTAL", "Tábuas de Pinho", 4, "Barra de Aço", 4, "QUESTITEM_TOKEN_CRYSTAL_SHIELD", 1],

    # --- ADAGAS ---
    "ADAGA": ["MAIN_DAGGER", "Barra de Aço", 12, "Couro Trabalhado", 12, None, 0],
    "PAR DE ADAGAS": ["2H_DAGGER", "Barra de Aço", 16, "Couro Trabalhado", 16, None, 0],
    "GARRAS": ["MAIN_DAGGER_HELL", "Barra de Aço", 12, "Couro Trabalhado", 20, None, 0],
    "DESSANGRADOR": ["MAIN_DAGGER_HELL", "Barra de Aço", 16, "Couro Trabalhado", 8, "ARTEFACT_MAIN_DAGGER_HELL", 1],
    "PRESA DEMONÍACA": ["MAIN_DAGGER_PR_HELL", "Barra de Aço", 12, "Couro Trabalhado", 12, "ARTEFACT_MAIN_DAGGER_PR_HELL", 1],
    "MORTÍFICOS": ["2H_DUAL_DAGGER_HELL", "Barra de Aço", 16, "Couro Trabalhado", 16, "ARTEFACT_2H_DUAL_DAGGER_HELL", 1],
    "FÚRIA CONTIDA": ["2H_DAGGER_AVALON", "Barra de Aço", 12, "Couro Trabalhado", 20, "ARTEFACT_2H_DAGGER_AVALON", 1],
    "GÊMEAS ANIQUILADORAS": ["2H_DAGGER_CRYSTAL", "Barra de Aço", 16, "Couro Trabalhado", 16, "QUESTITEM_TOKEN_CRYSTAL_DAGGER", 1],

    # --- LANÇAS ---
    "LANÇA": ["MAIN_SPEAR", "Tábuas de Pinho", 16, "Barra de Aço", 8, None, 0],
    "PIQUE": ["2H_SPEAR", "Tábuas de Pinho", 20, "Barra de Aço", 12, None, 0],
    "ARCHA": ["2H_GLAIVE", "Tábuas de Pinho", 12, "Barra de Aço", 20, None, 0],
    "LANÇA GARCEIRA": ["MAIN_SPEAR_KEEPER", "Tábuas de Pinho", 16, "Barra de Aço", 8, "ARTEFACT_MAIN_SPEAR_KEEPER", 1],
    "CAÇA-ESPÍRITOS": ["2H_SPEAR_HELL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_SPEAR_HELL", 1],
    "LANÇA TRINA": ["2H_GLAIVE_HELL", "Tábuas de Pinho", 20, "Barra de Aço", 12, "ARTEFACT_2H_GLAIVE_HELL", 1],
    "ALVORADA": ["MAIN_SPEAR_AVALON", "Tábuas de Pinho", 16, "Barra de Aço", 8, "ARTEFACT_MAIN_SPEAR_AVALON", 1],
    "ARCHA FRATURADA": ["2H_SPEAR_CRYSTAL", "Tábuas de Pinho", 12, "Barra de Aço", 20, "QUESTITEM_TOKEN_CRYSTAL_SPEAR", 1]
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
def ids_recurso_variantes(tier, nome, enc):
    base = f"T{tier}_{RECURSO_MAP[nome]}"
    return [f"{base}_LEVEL{enc}@{enc}"] if enc > 0 else [base]

def identificar_cidade_bonus(nome_item):
    for cidade, sufixos in BONUS_CIDADE.items():
        for s in sufixos:
            if s in ITENS_DB[nome_item][0]: return cidade
    return "Caerleon"

# ================= INTERFACE =================
with st.sidebar:
    categoria = st.selectbox("Categoria", list(FILTROS.keys()))
    tier, encanto = st.number_input("Tier", 4, 8, 6), st.number_input("Encanto", 0, 4, 0)
    btn = st.button("🚀 ESCANEAR")

# ================= LOGICA DE BUSCA (AQUI ESTÁ A CORREÇÃO) =================
if btn:
    filtro = FILTROS[categoria]
    itens = {k: v for k, v in ITENS_DB.items() if filtro(k, v)}
    
    ids = set()
    for d in itens.values():
        ids.add(id_item(tier, d[0], encanto))
        for r in ids_recurso_variantes(tier, d[1], encanto): ids.add(r)
        if d[3]:
            for r in ids_recurso_variantes(tier, d[3], encanto): ids.add(r)

    data = requests.get(f"{API_URL}{','.join(ids)}?locations={','.join(CIDADES)}").json()

    # Organiza preços
    precos = {}
    for p in data:
        pid, city = p["item_id"], p["city"]
        if pid not in precos: precos[pid] = {}
        precos[pid][city] = p["buy_price_max"] if city == "Black Market" else p["sell_price_min"]

    resultados = []
    for nome, d in itens.items():
        iid = id_item(tier, d[0], encanto)
        venda_bm = precos.get(iid, {}).get("Black Market", 0)
        if venda_bm == 0: continue

        custo_total = 0
        detalhes = []
        valido = True

        for mat_nome, mat_qtd in [(d[1], d[2]), (d[3], d[4])]:
            if not mat_nome: continue
            rid = ids_recurso_variantes(tier, mat_nome, encanto)[0]
            # Busca em todas as cidades o melhor preço
            opcoes = {c: v for c, v in precos.get(rid, {}).items() if v > 0 and c != "Black Market"}
            if opcoes:
                melhor_c = min(opcoes, key=opcoes.get)
                custo_total += opcoes[melhor_c] * mat_qtd
                detalhes.append(f"{mat_qtd}x {mat_nome}: {opcoes[melhor_c]:,} ({melhor_c})")
            else: valido = False

        if valido:
            invest = int(custo_total * 0.752)
            lucro = int((venda_bm * 0.935) - invest)
            if lucro > 0:
                resultados.append((nome, lucro, venda_bm, invest, detalhes))

    resultados.sort(key=lambda x: x[1], reverse=True)
    for r in resultados[:15]:
        st.markdown(f'<div class="item-card-custom"><b>{r[0]}</b><br>Lucro: {r[1]:,} | Invest: {r[3]:,}<br><small>{" | ".join(r[4])}</small></div>', unsafe_allow_html=True)
