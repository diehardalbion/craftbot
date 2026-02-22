import streamlit as st
import requests
import json
from datetime import datetime, timezone

# ================= CONFIGURAÇÃO DA PÁGINA =================
st.set_page_config("Radar Craft Albion", layout="wide", page_icon="⚔️")

# ================= CUSTOM CSS (VISUAL) =================
st.markdown("""
<style>
    /* REMOVER FAIXA BRANCA DO TOPO */
    header {visibility: hidden;}
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* FUNDO DA APLICAÇÃO */
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.8)), 
                    url("https://i.imgur.com/kVAiMjD.png");
        background-size: cover;
        background-attachment: fixed;
    }

    /* BARRA LATERAL */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 17, 23, 0.95) !important;
        border-right: 1px solid #3e4149;
    }

    /* TÍTULOS E TEXTOS */
    h1, h2, h3, label, .stMarkdown {
        color: #ffffff !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* CARD DE RESULTADO PERSONALIZADO */
    .item-card-custom { 
        background-color: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px);
        border-radius: 12px; 
        padding: 20px; 
        margin-bottom: 20px; 
        border: 1px solid rgba(46, 204, 113, 0.2);
        border-left: 8px solid #2ecc71;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        color: white !important;
    }

    /* INPUTS E BOTÕES */
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

# ================= FUNÇÕES DE SUPORTE =================
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

# ================= SISTEMA DE LOGIN / KEYS =================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center; color: #2ecc71;'>🛡️ Painel de Acesso</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### 🔑 Já possui acesso?")
        key_input = st.text_input("Insira sua Chave:", type="password", placeholder="Digite sua key...")
        if st.button("LIBERAR ACESSO"):
            sucesso, mensagem = verificar_chave(key_input)
            if sucesso:
                st.session_state.autenticado = True
                st.session_state.cliente = mensagem
                st.rerun()
            else:
                st.error(mensagem)

    with col2:
        st.markdown("### 💎 Adquirir Nova Chave")
        st.markdown("""
        <div style="background: rgba(46, 204, 113, 0.1); padding: 20px; border-radius: 10px; border: 1px solid #2ecc71; text-align: center;">
            <h2 style="margin:0; color: #2ecc71;">R$ 15,00</h2>
            <p style="color: white;">Acesso Mensal (30 dias)</p>
            <a href="https://wa.me/5521983042557?text=Olá! Gostaria de comprar uma key para o Radar Craft Albion." target="_blank" style="text-decoration: none;">
                <div style="background-color: #25d366; color: white; padding: 12px; border-radius: 5px; font-weight: bold; margin-top: 10px;">🟢 COMPRAR VIA WHATSAPP</div>
            </a>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><hr style='border: 0.5px solid rgba(46,204,113,0.2);'><br>", unsafe_allow_html=True)

    html_promocional = """
    <div style="background: linear-gradient(135deg, rgba(46, 204, 113, 0.1), rgba(26, 188, 156, 0.1)); padding: 30px; border-radius: 16px; border: 1px solid rgba(46, 204, 113, 0.3); margin-bottom: 40px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);">
        <h2 style="text-align: center; color: #2ecc71; margin-bottom: 25px; font-size: 1.8rem;">⚔️ RADAR CRAFT – A FERRAMENTA DEFINITIVA PARA DOMINAR O MARKET!</h2>
        <p style="text-align: center; color: #ecf0f1; font-size: 1.1rem; margin-bottom: 25px; line-height: 1.6;">Chega de perder prata tentando adivinhar qual craft vale a pena. Com o <strong style="color: #2ecc71;">Radar Craft</strong>, você transforma informação em lucro — <em>rápido, simples e eficiente</em>.</p>
        <div style="background: rgba(0,0,0,0.3); padding: 20px; border-radius: 12px; margin: 20px 0;">
            <h3 style="color: #2ecc71; margin-bottom: 15px; text-align: center;">🎯 O que o Radar Craft faz por você:</h3>
            <div style="margin: 10px 0; padding: 10px; background: rgba(46, 204, 113, 0.1); border-radius: 8px; border-left: 4px solid #2ecc71;"><strong style="color: #2ecc71;">✔ Escolha inteligente de craft</strong><br><span style="color: #bdc3c7; font-size: 0.95rem;">Selecione o item que deseja produzir e deixe o sistema fazer o resto.</span></div>
            <div style="margin: 10px 0; padding: 10px; background: rgba(46, 204, 113, 0.1); border-radius: 8px; border-left: 4px solid #2ecc71;"><strong style="color: #2ecc71;">✔ Busca automática de recursos</strong><br><span style="color: #bdc3c7; font-size: 0.95rem;">O Radar analisa todas as cidades e encontra os materiais com o menor preço disponível.</span></div>
            <div style="margin: 10px 0; padding: 10px; background: rgba(46, 204, 113, 0.1); border-radius: 8px; border-left: 4px solid #2ecc71;"><strong style="color: #2ecc71;">✔ Cidade ideal para craftar</strong><br><span style="color: #bdc3c7; font-size: 0.95rem;">Descubra exatamente onde craftar para aproveitar os melhores bônus de produção.</span></div>
            <div style="margin: 10px 0; padding: 10px; background: rgba(46, 204, 113, 0.1); border-radius: 8px; border-left: 4px solid #2ecc71;"><strong style="color: #2ecc71;">✔ Cálculo de investimento e lucro</strong><br><span style="color: #bdc3c7; font-size: 0.95rem;">Veja quanto você vai gastar e quanto pode ganhar antes mesmo de começar.</span></div>
            <div style="margin: 10px 0; padding: 10px; background: rgba(46, 204, 113, 0.1); border-radius: 8px; border-left: 4px solid #2ecc71;"><strong style="color: #2ecc71;">✔ Preço de venda otimizado</strong><br><span style="color: #bdc3c7; font-size: 0.95rem;">Receba o valor ideal para vender baseado no Black Market atualizado em 24h.</span></div>
        </div>
        <p style="text-align: center; color: #2ecc71; font-size: 1.3rem; font-weight: bold; margin-top: 30px;">🎯 Radar Craft: onde cada craft vira lucro.</p>
    </div>
    """
    st.markdown(html_promocional, unsafe_allow_html=True)
    st.stop()

# ================= RESTANTE DO CÓDIGO (APÓS LOGIN) =================
st.title("⚔️ Radar Craft — Painel de Controle")
st.write(f"Bem-vindo, {st.session_state.cliente}!")

# ================= CONFIG DE DADOS =================
API_URL = "https://west.albion-online-data.com/api/v2/stats/prices/"
CIDADES = ["Martlock", "Thetford", "FortSterling", "Lymhurst", "Bridgewatch", "Brecilien", "Caerleon", "Black Market"]

# Mapeamento de recursos em português para IDs da API
RECURSO_MAP = {
    "Tecido Fino": "CLOTH", "Couro Trabalhado": "LEATHER",
    "Barra de Aço": "METALBAR", "Tábuas de Pinho": "PLANKS",
    # Mapeamento para tiers superiores de capas
    "T4_CLOTH": "CLOTH", "T5_CLOTH": "CLOTH", "T6_CLOTH": "CLOTH", "T7_CLOTH": "CLOTH", "T8_CLOTH": "CLOTH",
    "T4_LEATHER": "LEATHER", "T5_LEATHER": "LEATHER", "T6_LEATHER": "LEATHER", "T7_LEATHER": "LEATHER", "T8_LEATHER": "LEATHER",
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
    "Capuz de Mercenário": ["HEAD_LEATHER_SET1", "Couro Trabalhado", 8, None, 0, None, 0],
    "Capuz de Caçador": ["HEAD_LEATHER_SET2", "Couro Trabalhado", 8, None, 0, None, 0],
    "Capuz de Assassino": ["HEAD_LEATHER_SET3", "Couro Trabalhado", 8, None, 0, None, 0],
    "Capuz Real": ["HEAD_LEATHER_ROYAL", "Couro Trabalhado", 8, None, 0, "QUESTITEM_TOKEN_ROYAL", 2],
    "Capuz de Espreitador": ["HEAD_LEATHER_HELL", "Couro Trabalhado", 8, None, 0, "ARTEFACT_HEAD_LEATHER_HELL", 1],
    "Capuz Infernal": ["HEAD_LEATHER_MORGANA", "Couro Trabalhado", 8, None, 0, "ARTEFACT_HEAD_LEATHER_MORGANA", 1],
    "Capuz Espectral": ["HEAD_LEATHER_UNDEAD", "Couro Trabalhado", 8, None, 0, "ARTEFACT_HEAD_LEATHER_UNDEAD", 1],
    "Capuz de Andarilho da Névoa": ["HEAD_LEATHER_FEY", "Couro Trabalhado", 8, None, 0, "ARTEFACT_HEAD_LEATHER_FEY", 1],
    "Capuz da Tenacidade": ["HEAD_LEATHER_CRYSTAL", "Couro Trabalhado", 8, None, 0, "QUESTITEM_TOKEN_CRYSTAL_HEAD_LEATHER", 1],

    # --- SANDÁLIAS DE TECIDO ---
    "Sandálias de Erudito": ["SHOES_CLOTH_SET1", "Tecido Fino", 8, None, 0, None, 0],
    "Sandálias de Clérigo": ["SHOES_CLOTH_SET2", "Tecido Fino", 8, None, 0, None, 0],
    "Sandálias de Mago": ["SHOES_CLOTH_SET3", "Tecido Fino", 8, None, 0, None, 0],
    "Sandálias Reais": ["SHOES_CLOTH_ROYAL", "Tecido Fino", 8, None, 0, "QUESTITEM_TOKEN_ROYAL", 2],
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
    "ARCHA FRATURADA": ["2H_SPEAR_CRYSTAL", "Tábuas de Pinho", 12, "Barra de Aço", 20, "QUESTITEM_TOKEN_CRYSTAL_SPEAR", 1],

    # ================= CAPAS - BASE =================
    "CAPA DO ADEPTO": ["CAPE", "T4_CLOTH", 4, "T4_LEATHER", 4, None, 0],
    "CAPA DO PERITO": ["CAPE", "T5_CLOTH", 4, "T5_LEATHER", 4, None, 0],
    "CAPA DO MESTRE": ["CAPE", "T6_CLOTH", 4, "T6_LEATHER", 4, None, 0],
    "CAPA DO GRÃO-MESTRE": ["CAPE", "T7_CLOTH", 4, "T7_LEATHER", 4, None, 0],
    "CAPA DO ANCIÃO": ["CAPE", "T8_CLOTH", 4, "T8_LEATHER", 4, None, 0],

    # ================= CAPAS - BRIDGEWATCH (CORACAO BESTIAL) =================
    "CAPA DE BRIDGEWATCH DO ADEPTO": ["CAPEITEM_FW_BRIDGEWATCH", "CAPE", 1, "ARTEFACT_CAPE_FW_BRIDGEWATCH", 1, "CORRUPTED_CORE", 1],
    "CAPA DE BRIDGEWATCH DO PERITO": ["CAPEITEM_FW_BRIDGEWATCH", "CAPE", 1, "ARTEFACT_CAPE_FW_BRIDGEWATCH", 1, "CORRUPTED_CORE", 1],
    "CAPA DE BRIDGEWATCH DO MESTRE": ["CAPEITEM_FW_BRIDGEWATCH", "CAPE", 1, "ARTEFACT_CAPE_FW_BRIDGEWATCH", 1, "CORRUPTED_CORE", 3],
    "CAPA DE BRIDGEWATCH DO GRÃO-MESTRE": ["CAPEITEM_FW_BRIDGEWATCH", "CAPE", 1, "ARTEFACT_CAPE_FW_BRIDGEWATCH", 1, "CORRUPTED_CORE", 5],
    "CAPA DE BRIDGEWATCH DO ANCIÃO": ["CAPEITEM_FW_BRIDGEWATCH", "CAPE", 1, "ARTEFACT_CAPE_FW_BRIDGEWATCH", 1, "CORRUPTED_CORE", 10],

    # ================= CAPAS - FORT STERLING (CORACAO MONTANHOSO) =================
    "CAPA DE FORT STERLING DO ADEPTO": ["CAPEITEM_FW_FORTSTERLING", "CAPE", 1, "ARTEFACT_CAPE_FW_FORTSTERLING", 1, "FROST_CORE", 1],
    "CAPA DE FORT STERLING DO PERITO": ["CAPEITEM_FW_FORTSTERLING", "CAPE", 1, "ARTEFACT_CAPE_FW_FORTSTERLING", 1, "FROST_CORE", 1],
    "CAPA DE FORT STERLING DO MESTRE": ["CAPEITEM_FW_FORTSTERLING", "CAPE", 1, "ARTEFACT_CAPE_FW_FORTSTERLING", 1, "FROST_CORE", 3],
    "CAPA DE FORT STERLING DO GRÃO-MESTRE": ["CAPEITEM_FW_FORTSTERLING", "CAPE", 1, "ARTEFACT_CAPE_FW_FORTSTERLING", 1, "FROST_CORE", 5],
    "CAPA DE FORT STERLING DO ANCIÃO": ["CAPEITEM_FW_FORTSTERLING", "CAPE", 1, "ARTEFACT_CAPE_FW_FORTSTERLING", 1, "FROST_CORE", 10],

    # ================= CAPAS - LYMHURST (CORACAO ARBOREO) =================
    "CAPA DE LYMHURST DO ADEPTO": ["CAPEITEM_FW_LYMHURST", "CAPE", 1, "ARTEFACT_CAPE_FW_LYMHURST", 1, "NATURE_CORE", 1],
    "CAPA DE LYMHURST DO PERITO": ["CAPEITEM_FW_LYMHURST", "CAPE", 1, "ARTEFACT_CAPE_FW_LYMHURST", 1, "NATURE_CORE", 1],
    "CAPA DE LYMHURST DO MESTRE": ["CAPEITEM_FW_LYMHURST", "CAPE", 1, "ARTEFACT_CAPE_FW_LYMHURST", 1, "NATURE_CORE", 3],
    "CAPA DE LYMHURST DO GRÃO-MESTRE": ["CAPEITEM_FW_LYMHURST", "CAPE", 1, "ARTEFACT_CAPE_FW_LYMHURST", 1, "NATURE_CORE", 5],
    "CAPA DE LYMHURST DO ANCIÃO": ["CAPEITEM_FW_LYMHURST", "CAPE", 1, "ARTEFACT_CAPE_FW_LYMHURST", 1, "NATURE_CORE", 10],

    # ================= CAPAS - MARTLOCK (CORACAO EMPEDRADO) =================
    "CAPA DE MARTLOCK DO ADEPTO": ["CAPEITEM_FW_MARTLOCK", "CAPE", 1, "ARTEFACT_CAPE_FW_MARTLOCK", 1, "ROCK_CORE", 1],
    "CAPA DE MARTLOCK DO PERITO": ["CAPEITEM_FW_MARTLOCK", "CAPE", 1, "ARTEFACT_CAPE_FW_MARTLOCK", 1, "ROCK_CORE", 1],
    "CAPA DE MARTLOCK DO MESTRE": ["CAPEITEM_FW_MARTLOCK", "CAPE", 1, "ARTEFACT_CAPE_FW_MARTLOCK", 1, "ROCK_CORE", 3],
    "CAPA DE MARTLOCK DO GRÃO-MESTRE": ["CAPEITEM_FW_MARTLOCK", "CAPE", 1, "ARTEFACT_CAPE_FW_MARTLOCK", 1, "ROCK_CORE", 5],
    "CAPA DE MARTLOCK DO ANCIÃO": ["CAPEITEM_FW_MARTLOCK", "CAPE", 1, "ARTEFACT_CAPE_FW_MARTLOCK", 1, "ROCK_CORE", 10],

    # ================= CAPAS - THETFORD (CORACAO VIDEIRA) =================
    "CAPA DE THETFORD DO ADEPTO": ["CAPEITEM_FW_THETFORD", "CAPE", 1, "ARTEFACT_CAPE_FW_THETFORD", 1, "VINE_CORE", 1],
    "CAPA DE THETFORD DO PERITO": ["CAPEITEM_FW_THETFORD", "CAPE", 1, "ARTEFACT_CAPE_FW_THETFORD", 1, "VINE_CORE", 1],
    "CAPA DE THETFORD DO MESTRE": ["CAPEITEM_FW_THETFORD", "CAPE", 1, "ARTEFACT_CAPE_FW_THETFORD", 1, "VINE_CORE", 3],
    "CAPA DE THETFORD DO GRÃO-MESTRE": ["CAPEITEM_FW_THETFORD", "CAPE", 1, "ARTEFACT_CAPE_FW_THETFORD", 1, "VINE_CORE", 5],
    "CAPA DE THETFORD DO ANCIÃO": ["CAPEITEM_FW_THETFORD", "CAPE", 1, "ARTEFACT_CAPE_FW_THETFORD", 1, "VINE_CORE", 10],

    # ================= CAPAS - CAERLEON (CORACAO SOMBRIO) =================
    "CAPA DE CAERLEON DO ADEPTO": ["CAPEITEM_FW_CAERLEON", "CAPE", 1, "ARTEFACT_CAPE_FW_CAERLEON", 1, "DARK_CORE", 1],
    "CAPA DE CAERLEON DO PERITO": ["CAPEITEM_FW_CAERLEON", "CAPE", 1, "ARTEFACT_CAPE_FW_CAERLEON", 1, "DARK_CORE", 1],
    "CAPA DE CAERLEON DO MESTRE": ["CAPEITEM_FW_CAERLEON", "CAPE", 1, "ARTEFACT_CAPE_FW_CAERLEON", 1, "DARK_CORE", 3],
    "CAPA DE CAERLEON DO GRÃO-MESTRE": ["CAPEITEM_FW_CAERLEON", "CAPE", 1, "ARTEFACT_CAPE_FW_CAERLEON", 1, "DARK_CORE", 5],
    "CAPA DE CAERLEON DO ANCIÃO": ["CAPEITEM_FW_CAERLEON", "CAPE", 1, "ARTEFACT_CAPE_FW_CAERLEON", 1, "DARK_CORE", 10],

    # ================= CAPAS - HEREGE =================
    "CAPA HEREGE DO ADEPTO": ["CAPEITEM_HERETIC", "CAPE", 1, "ARTEFACT_CAPE_HERETIC", 1, "NATURE_CORE", 1],
    "CAPA HEREGE DO PERITO": ["CAPEITEM_HERETIC", "CAPE", 1, "ARTEFACT_CAPE_HERETIC", 1, "NATURE_CORE", 1],
    "CAPA HEREGE DO MESTRE": ["CAPEITEM_HERETIC", "CAPE", 1, "ARTEFACT_CAPE_HERETIC", 1, "NATURE_CORE", 3],
    "CAPA HEREGE DO GRÃO-MESTRE": ["CAPEITEM_HERETIC", "CAPE", 1, "ARTEFACT_CAPE_HERETIC", 1, "NATURE_CORE", 5],
    "CAPA HEREGE DO ANCIÃO": ["CAPEITEM_HERETIC", "CAPE", 1, "ARTEFACT_CAPE_HERETIC", 1, "NATURE_CORE", 10],

    # ================= CAPAS - MORTA-VIVA =================
    "CAPA MORTA-VIVA DO ADEPTO": ["CAPEITEM_UNDEAD", "CAPE", 1, "ARTEFACT_CAPE_UNDEAD", 1, "FROST_CORE", 1],
    "CAPA MORTA-VIVA DO PERITO": ["CAPEITEM_UNDEAD", "CAPE", 1, "ARTEFACT_CAPE_UNDEAD", 1, "FROST_CORE", 1],
    "CAPA MORTA-VIVA DO MESTRE": ["CAPEITEM_UNDEAD", "CAPE", 1, "ARTEFACT_CAPE_UNDEAD", 1, "FROST_CORE", 3],
    "CAPA MORTA-VIVA DO GRÃO-MESTRE": ["CAPEITEM_UNDEAD", "CAPE", 1, "ARTEFACT_CAPE_UNDEAD", 1, "FROST_CORE", 5],
    "CAPA MORTA-VIVA DO ANCIÃO": ["CAPEITEM_UNDEAD", "CAPE", 1, "ARTEFACT_CAPE_UNDEAD", 1, "FROST_CORE", 10],

    # ================= CAPAS - PROTETORA =================
    "CAPA PROTETORA DO ADEPTO": ["CAPEITEM_KEEPER", "CAPE", 1, "ARTEFACT_CAPE_KEEPER", 1, "ROCK_CORE", 1],
    "CAPA PROTETORA DO PERITO": ["CAPEITEM_KEEPER", "CAPE", 1, "ARTEFACT_CAPE_KEEPER", 1, "ROCK_CORE", 1],
    "CAPA PROTETORA DO MESTRE": ["CAPEITEM_KEEPER", "CAPE", 1, "ARTEFACT_CAPE_KEEPER", 1, "ROCK_CORE", 3],
    "CAPA PROTETORA DO GRÃO-MESTRE": ["CAPEITEM_KEEPER", "CAPE", 1, "ARTEFACT_CAPE_KEEPER", 1, "ROCK_CORE", 5],
    "CAPA PROTETORA DO ANCIÃO": ["CAPEITEM_KEEPER", "CAPE", 1, "ARTEFACT_CAPE_KEEPER", 1, "ROCK_CORE", 10],

    # ================= CAPAS - MORGANA =================
    "CAPA MORGANA DO ADEPTO": ["CAPEITEM_MORGANA", "CAPE", 1, "ARTEFACT_CAPE_MORGANA", 1, "VINE_CORE", 1],
    "CAPA MORGANA DO PERITO": ["CAPEITEM_MORGANA", "CAPE", 1, "ARTEFACT_CAPE_MORGANA", 1, "VINE_CORE", 1],
    "CAPA MORGANA DO MESTRE": ["CAPEITEM_MORGANA", "CAPE", 1, "ARTEFACT_CAPE_MORGANA", 1, "VINE_CORE", 3],
    "CAPA MORGANA DO GRÃO-MESTRE": ["CAPEITEM_MORGANA", "CAPE", 1, "ARTEFACT_CAPE_MORGANA", 1, "VINE_CORE", 5],
    "CAPA MORGANA DO ANCIÃO": ["CAPEITEM_MORGANA", "CAPE", 1, "ARTEFACT_CAPE_MORGANA", 1, "VINE_CORE", 10],

    # ================= CAPAS - DEMONÍACA =================
    "CAPA DEMONÍACA DO ADEPTO": ["CAPEITEM_HELL", "CAPE", 1, "ARTEFACT_CAPE_HELL", 1, "CORRUPTED_CORE", 1],
    "CAPA DEMONÍACA DO PERITO": ["CAPEITEM_HELL", "CAPE", 1, "ARTEFACT_CAPE_HELL", 1, "CORRUPTED_CORE", 1],
    "CAPA DEMONÍACA DO MESTRE": ["CAPEITEM_HELL", "CAPE", 1, "ARTEFACT_CAPE_HELL", 1, "CORRUPTED_CORE", 3],
    "CAPA DEMONÍACA DO GRÃO-MESTRE": ["CAPEITEM_HELL", "CAPE", 1, "ARTEFACT_CAPE_HELL", 1, "CORRUPTED_CORE", 5],
    "CAPA DEMONÍACA DO ANCIÃO": ["CAPEITEM_HELL", "CAPE", 1, "ARTEFACT_CAPE_HELL", 1, "CORRUPTED_CORE", 10],

    # ================= CAPAS - BRECI LIEN =================
    "CAPA DE BRECI LIEN DO ADEPTO": ["CAPEITEM_FW_BRECILIEN", "CAPE", 1, "ARTEFACT_CAPE_FW_BRECILIEN", 1, "FAERIE_FIRE", 1],
    "CAPA DE BRECI LIEN DO PERITO": ["CAPEITEM_FW_BRECILIEN", "CAPE", 1, "ARTEFACT_CAPE_FW_BRECILIEN", 1, "FAERIE_FIRE", 1],
    "CAPA DE BRECI LIEN DO MESTRE": ["CAPEITEM_FW_BRECILIEN", "CAPE", 1, "ARTEFACT_CAPE_FW_BRECILIEN", 1, "FAERIE_FIRE", 3],
    "CAPA DE BRECI LIEN DO GRÃO-MESTRE": ["CAPEITEM_FW_BRECILIEN", "CAPE", 1, "ARTEFACT_CAPE_FW_BRECILIEN", 1, "FAERIE_FIRE", 5],
    "CAPA DE BRECI LIEN DO ANCIÃO": ["CAPEITEM_FW_BRECILIEN", "CAPE", 1, "ARTEFACT_CAPE_FW_BRECILIEN", 1, "FAERIE_FIRE", 10],

    # ================= CAPAS - AVALONIANA =================
    "CAPA AVALONIANA DO ADEPTO": ["CAPEITEM_AVALON", "CAPE", 1, "ARTEFACT_CAPE_AVALON", 1, "FAERIE_FIRE", 1],
    "CAPA AVALONIANA DO PERITO": ["CAPEITEM_AVALON", "CAPE", 1, "ARTEFACT_CAPE_AVALON", 1, "FAERIE_FIRE", 1],
    "CAPA AVALONIANA DO MESTRE": ["CAPEITEM_AVALON", "CAPE", 1, "ARTEFACT_CAPE_AVALON", 1, "FAERIE_FIRE", 3],
    "CAPA AVALONIANA DO GRÃO-MESTRE": ["CAPEITEM_AVALON", "CAPE", 1, "ARTEFACT_CAPE_AVALON", 1, "FAERIE_FIRE", 5],
    "CAPA AVALONIANA DO ANCIÃO": ["CAPEITEM_AVALON", "CAPE", 1, "ARTEFACT_CAPE_AVALON", 1, "FAERIE_FIRE", 10],

    # ================= CAPAS - CONTABANDISTA =================
    "CAPA CONTABANDISTA DO ADEPTO": ["CAPEITEM_SMUGGLER", "CAPE", 1, "ARTEFACT_CAPE_SMUGGLER", 1, "DARK_CORE", 1],
    "CAPA CONTABANDISTA DO PERITO": ["CAPEITEM_SMUGGLER", "CAPE", 1, "ARTEFACT_CAPE_SMUGGLER", 1, "DARK_CORE", 1],
    "CAPA CONTABANDISTA DO MESTRE": ["CAPEITEM_SMUGGLER", "CAPE", 1, "ARTEFACT_CAPE_SMUGGLER", 1, "DARK_CORE", 3],
    "CAPA CONTABANDISTA DO GRÃO-MESTRE": ["CAPEITEM_SMUGGLER", "CAPE", 1, "ARTEFACT_CAPE_SMUGGLER", 1, "DARK_CORE", 5],
    "CAPA CONTABANDISTA DO ANCIÃO": ["CAPEITEM_SMUGGLER", "CAPE", 1, "ARTEFACT_CAPE_SMUGGLER", 1, "DARK_CORE", 10],
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
    "capas": lambda k, v: v[0] == "CAPE" or "CAPEITEM" in v[0],
}

# ================= FUNÇÕES =================
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
    # Se já for um ID da API direto (começa com letra maiúscula e não está no RECURSO_MAP)
    if nome not in RECURSO_MAP and not nome.startswith("T"):
        base = f"T{tier}_{nome}"
        if enc > 0: return [f"{base}@{enc}", f"{base}_LEVEL{enc}@{enc}"]
        return [base]
    # Se for um ID já formatado (ex: T4_CLOTH)
    if nome.startswith("T"):
        if enc > 0: return [f"{nome}@{enc}", f"{nome}_LEVEL{enc}@{enc}"]
        return [nome]
    # Caso padrão: nome em português -> converte via RECURSO_MAP
    base = f"T{tier}_{RECURSO_MAP[nome]}"
    if enc > 0: return [f"{base}@{enc}", f"{base}_LEVEL{enc}@{enc}"]
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

st.title("⚔️ Radar Craft — Royal Cities + Black Market")

# ================= EXECUÇÃO =================
if btn:
    filtro = FILTROS[categoria]
    itens = {k: v for k, v in ITENS_DB.items() if filtro(k, v)}

    if not itens:
        st.error("Nenhum item encontrado.")
        st.stop()

    ids = set()
    for d in itens.values():
        ids.add(id_item(tier, d[0], encanto))
        for r in ids_recurso_variantes(tier, d[1], encanto): ids.add(r)
        if d[3]:
            for r in ids_recurso_variantes(tier, d[3], encanto): ids.add(r)
        if d[5]: ids.add(f"T{tier}_{d[5]}")

    try:
        response = requests.get(f"{API_URL}{','.join(ids)}?locations={','.join(CIDADES)}", timeout=20)
        data = response.json()
    except:
        st.error("Erro ao conectar com a API.")
        st.stop()

    precos_itens = {}
    precos_recursos = {}

    for p in data:
        pid = p["item_id"]
        if p["city"] == "Black Market":
            price = p["buy_price_max"]
            if price > 0:
                horas = calcular_horas(p["buy_price_max_date"])
                if pid not in precos_itens or price > precos_itens[pid]["price"]:
                    precos_itens[pid] = {"price": price, "horas": horas}
        else:
            price = p["sell_price_min"]
            if price > 0:
                horas = calcular_horas(p["sell_price_min_date"])
                if pid not in precos_recursos or price < precos_recursos[pid]["price"]:
                    precos_recursos[pid] = {"price": price, "city": p["city"], "horas": horas}

    resultados = []
    for nome, d in itens.items():
        item_id = id_item(tier, d[0], encanto)
        if item_id not in precos_itens: continue

        custo = 0
        detalhes = []
        valid_craft = True

        for recurso, qtd in [(d[1], d[2]), (d[3], d[4])]:
            if not recurso: continue
            found = False
            for rid in ids_recurso_variantes(tier, recurso, encanto):
                if rid in precos_recursos:
                    info = precos_recursos[rid]
                    custo += info["price"] * qtd * quantidade
                    detalhes.append(f"{qtd * quantidade}x {recurso}: {info['price']:,} ({info['city']})")
                    found = True
                    break
            if not found:
                valid_craft = False
                break
        
        if not valid_craft: continue

        if d[5]:
            art = f"T{tier}_{d[5]}"
            if art in precos_recursos:
                custo += precos_recursos[art]["price"] * d[6] * quantidade
                detalhes.append(f"Artefato: {precos_recursos[art]['price']:,} ({precos_recursos[art]['city']})")
            else: continue

        custo_final = int(custo * 0.752)
        venda = precos_itens[item_id]["price"] * quantidade
        lucro = int((venda * 0.935) - custo_final)

        if lucro > 0:
            resultados.append((nome, lucro, venda, custo_final, detalhes, precos_itens[item_id]["horas"]))

    resultados.sort(key=lambda x: x[1], reverse=True)

    if not resultados:
        st.warning("❌ Nenhum lucro encontrado para os filtros atuais.")
    else:
        st.subheader(f"📊 Resultados para {categoria.upper()} T{tier}.{encanto}")
        
        for nome, lucro, venda, custo, detalhes, h_venda in resultados[:20]:
            perc_lucro = (lucro / custo) * 100 if custo > 0 else 0
            cidade_foco = identificar_cidade_bonus(nome)

            st.markdown(f"""
            <div class="item-card-custom">
                <div style="font-weight: bold; font-size: 1.2rem; margin-bottom: 10px; color: #2ecc71;">
                    ⚔️ {nome} [T{tier}.{encanto}] x{quantidade}
                </div>
                <div style="font-size: 1.05rem; margin-bottom: 8px;">
                    <span style="color: #2ecc71; font-weight: bold; font-size: 1.2rem;">💰 Lucro: {lucro:,} ({perc_lucro:.2f}%)</span> 
                    <br><b>Investimento:</b> {custo:,} | <b>Venda BM:</b> {venda:,}
                </div>
                <div style="font-size: 0.95rem; color: #cbd5e1; margin-bottom: 10px;">
                    📍 <b>Foco Craft:</b> {cidade_foco} | 🕒 <b>Atualizado:</b> {h_venda}h atrás
                </div>
                <div style="background: rgba(0,0,0,0.4); padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); font-size: 0.9rem;">
                    📦 <b>Detalhamento de Compras:</b> <br> {" | ".join(detalhes)}
                </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("---")
st.caption("Radar Craft Albion - Desenvolvido para análise de mercado via Albion Online Data Project")
