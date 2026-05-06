import streamlit as st
from config import EMPRESAS

# =====================================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================================
st.set_page_config(
    page_title="Dashboard Controle de Corte - Seletor",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =====================================================================
# ESTILOS
# =====================================================================
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #666;
        text-align: center;
        margin-bottom: 3rem;
    }
    .selector-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# INICIALIZAR SESSION STATE
# =====================================================================
if 'empresa_selecionada' not in st.session_state:
    st.session_state.empresa_selecionada = None
if 'cidade_selecionada' not in st.session_state:
    st.session_state.cidade_selecionada = None

# =====================================================================
# PÁGINA INICIAL
# =====================================================================
st.markdown('<div class="main-title">✂️ Dashboard Controle de Corte</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Análise de Produção por Estação de Corte</div>', unsafe_allow_html=True)

st.markdown("")
st.markdown("")

# Obter cidades disponíveis
cidades_disponiveis = list(EMPRESAS.keys())

# Seletor de Cidade
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🏙️ Selecione a Cidade")
    cidade = st.selectbox(
        "Cidades disponíveis:",
        options=cidades_disponiveis,
        key="cidade_selector",
        label_visibility="collapsed"
    )
    st.session_state.cidade_selecionada = cidade

with col2:
    st.markdown("### 🏭 Selecione a Empresa")
    
    # Obter empresas da cidade selecionada
    empresas_cidade = list(EMPRESAS[cidade].keys())
    
    empresa = st.selectbox(
        "Empresas disponíveis:",
        options=empresas_cidade,
        key="empresa_selector",
        label_visibility="collapsed"
    )
    st.session_state.empresa_selecionada = empresa

# Mostrar informações selecionadas
st.markdown("---")

col_info1, col_info2 = st.columns(2)
with col_info1:
    config_empresa = EMPRESAS[cidade][empresa]
    st.info(f"""
    **{config_empresa['emoji']} {config_empresa['nome_display']}**
    
    Planilha vinculada: `{config_empresa['sheet_id']}`
    """)

with col_info2:
    if st.button("🚀 Acessar Dashboard", use_container_width=True, key="btn_access"):
        # Salvar configuração e navegar
        st.session_state.empresa_config = EMPRESAS[cidade][empresa]
        st.session_state.page = "dashboard"
        st.switch_page("pages/dashboard.py")

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #999; margin-top: 3rem;">
    <small>
        💡 Cada empresa possui seus próprios dados de produção<br>
        🔄 Os dados são carregados em tempo real da planilha Google Sheets
    </small>
</div>
""", unsafe_allow_html=True)
