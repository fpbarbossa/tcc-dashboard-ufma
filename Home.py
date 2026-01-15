import streamlit as st
import pandas as pd
import utils

st.set_page_config(page_title="Dashboard - Monografia AA UFMA", layout="wide")

# Configura o tema global (claro/escuro)
#utils.configurar_tema_global()

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
col_logo, col_logo1  = st.columns([6, 6])

with col_logo:
    try:
        st.image("logo_ufma.png", width=200)
    except:
        st.write("UFMA") # Texto alternativo caso a imagem falhe
    st.caption("Universidade Federal do Maranhão")

with col_logo1:
    try:
        st.image("logo_bict.png", width=200)
    except:
        st.write("Bict") # Texto alternativo caso a imagem falhe
    st.caption("Bacharelado em Ciências e Tecnologia")

st.markdown("---")

# Layout de informações do trabalho
col_info1, col_info2 = st.columns([2, 1])

with col_info1:
    st.markdown("### *Análise da Evolução e dos Impactos da Política de Ações Afirmativas na Pós-Graduação da Universidade Federal do Maranhão (UFMA)*")
    st.markdown("**Resumo do Projeto:**")
    st.markdown("""
    O estudo analisa a implementação e os impactos iniciais da **Resolução N° 3.058-CONSEPE/2023**, 
    que instituiu a Política de Ações Afirmativas nos cursos de pós-graduação *stricto sensu* e *lato sensu* da UFMA.
    """)

with col_info2:
    st.markdown("**Curso:** Bacharelado em Ciências e Tecnologia")
    st.markdown("**Aluno:** Felipe Pereira Barbosa")
    st.markdown("**Orientador:** Prof. Davi Viana dos Santos")
    st.markdown("**Ano:** 2026")

st.markdown("---")

# --- Área de Upload ---
st.markdown("### Fonte de Dados")

arquivo = st.file_uploader("Carregar arquivo CSV (Base de Dados)", type=["csv"])

# --- Processamento ---
if arquivo is not None:
    df = carregar_dados(arquivo)
    
    if df is not None:
        # --- FILTRAGEM GLOBAL DE ATIVOS ---
        if 'Situação' in df.columns:
            df_ativos = df[df['Situação'].astype(str).str.strip().str.upper() == 'ATIVO']
            
            # Salva no Session State
            st.session_state['dados_ppg'] = df_ativos
            
            st.success(f" Base de dados carregada com sucesso!")
            st.info(f"Foram encontrados **{len(df)}** registros totais, dos quais **{len(df_ativos)}** são programas **ATIVOS** que serão utilizados nas análises.")
            
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
            st.sidebar.info(" Dados padrão carregados automaticamente.")
    except:
        st.warning(" Por favor, faça o upload do arquivo CSV para iniciar.")