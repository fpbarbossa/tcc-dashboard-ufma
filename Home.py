import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Dashboard - Monografia AA UFMA",
    layout="wide"
)

# --- Função de Carregamento e Tratamento Inicial ---
@st.cache_data
def carregar_dados(uploaded_file):
    try:
        # Carrega ignorando as linhas de cabeçalho irrelevantes (padrão do arquivo: 8 linhas)
        df = pd.read_csv(uploaded_file, skiprows=8)
        df.columns = df.columns.str.strip()
        
        # Tratamento de colunas numéricas para evitar erros de cálculo
        cols_numericas = [
            'Total de Vagas Oferecidas', 'Total de Vagas AA Oferecidas',
            'Vagas totais preenchidas', 'Inscritos totais', 'Inscritos AA'
        ]
        for col in cols_numericas:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
        return None

# --- Cabeçalho Institucional ---
col_logo, col_titulo = st.columns([1, 4])

with col_logo:
    # Espaço reservado para logo (opcional) ou ícone
    st.markdown("### 🏛️ UFMA")
    st.caption("Universidade Federal do Maranhão")

with col_titulo:
    st.title("Painel de Monitoramento: Ações Afirmativas na Pós-Graduação")

st.markdown("---")

# --- Informações da Monografia ---
st.info("ℹ️ **Sobre esta Ferramenta:** Este dashboard foi desenvolvido como parte integrante da coleta e análise de dados do seguinte Trabalho de Conclusão de Curso (TCC):")

# Layout de informações do trabalho
col_info1, col_info2 = st.columns([2, 1])

with col_info1:
    st.markdown("### *Análise da Evolução e dos Impactos da Política de Ações Afirmativas na Pós-Graduação da Universidade Federal do Maranhão (UFMA)*")
    st.markdown("**Resumo do Projeto:**")
    st.markdown("""
    O estudo analisa a implementação e os impactos iniciais da **Resolução N° 3.058-CONSEPE/2023**, 
    que instituiu a Política de Ações Afirmativas nos cursos de pós-graduação *stricto sensu* e *lato sensu* da UFMA.
    
    Esta ferramenta processa os dados dos editais e inscrições para visualizar:
    * A evolução da adesão institucional às cotas.
    * A oferta de vagas reservadas (Negros, Indígenas, Quilombolas, PCDs, Trans, etc.).
    * As taxas de sucesso e ocupação dos programas.
    """)

with col_info2:
    st.markdown("#### Ficha Técnica")
    st.markdown("**🎓 Curso:** Bacharelado em Ciências e Tecnologia")
    st.markdown("**👤 Autor:** Felipe Pereira Barbosa")
    st.markdown("**👨‍🏫 Orientador:** Prof. Davi Viana dos Santos")
    st.markdown("**📅 Ano:** 2025")

st.markdown("---")

# --- Área de Upload ---
st.markdown("### 📂 Fonte de Dados")
st.markdown("""
Para gerar as visualizações utilizadas na monografia, faça o upload da base de dados abaixo.

**⚠️ Nota Importante:** O sistema aplicará um filtro automático para considerar **apenas Programas com situação 'ATIVO'**, 
garantindo que a análise reflita o cenário atual da pós-graduação.
""")

arquivo = st.file_uploader("Carregar arquivo CSV (Base de Dados)", type=["csv"])

# --- Lógica de Processamento ---
if arquivo is not None:
    df = carregar_dados(arquivo)
    
    if df is not None:
        # --- FILTRAGEM GLOBAL DE ATIVOS ---
        # Filtra aqui para garantir que todas as páginas recebam apenas dados ATIVOS
        if 'Situação' in df.columns:
            df_ativos = df[df['Situação'].astype(str).str.strip().str.upper() == 'ATIVO']
            
            # Salva no Session State
            st.session_state['dados_ppg'] = df_ativos
            
            st.success(f"✅ Base de dados carregada com sucesso!")
            st.info(f"Foram encontrados **{len(df)}** registros totais, dos quais **{len(df_ativos)}** são programas **ATIVOS** que serão utilizados nas análises.")
            
            st.markdown("### 🚀 Como navegar:")
            st.markdown("Utilize o menu lateral à esquerda para acessar as seções:")
            st.markdown("1.  **Métricas Gerais:** Indicadores globais de ocupação e sucesso.")
            st.markdown("2.  **Ações Afirmativas:** Análise específica da política de cotas.")
            st.markdown("3.  **Gráficos:** Visualizações comparativas e históricas.")
        else:
            st.error("A coluna 'Situação' não foi encontrada no arquivo. Verifique a base de dados.")

# Carregamento automático para demonstração (Opcional - se houver arquivo local)
elif "dados_ppg" not in st.session_state:
    try:
        # Tenta carregar arquivo padrão se existir na pasta (facilita para o avaliador)
        df_padrao = carregar_dados("dados_ufma.csv")
        if df_padrao is not None and 'Situação' in df_padrao.columns:
            df_ativos_padrao = df_padrao[df_padrao['Situação'].astype(str).str.strip().str.upper() == 'ATIVO']
            st.session_state['dados_ppg'] = df_ativos_padrao
            st.sidebar.info("ℹ️ Dados padrão carregados automaticamente.")
    except:
        st.warning("👈 Por favor, faça o upload do arquivo CSV para iniciar.")