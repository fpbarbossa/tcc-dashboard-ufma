import streamlit as st
import pandas as pd
import utils

st.set_page_config(page_title="Métricas Gerais", layout="wide")

#utils.configurar_tema_global()

st.title("Indicadores Gerais de Desempenho")

# Verifica se os dados existem no session_state
if 'dados_ppg' not in st.session_state:
    st.error("Por favor, faça o upload do arquivo na página 'Home' primeiro.")
    st.stop()

df = st.session_state['dados_ppg']

# --- FILTRAGEM GLOBAL DE ATIVOS (quero que filtre somente os dados dos programas ATIVOS) ---
if 'Situação' in df.columns:
    df = df[df['Situação'].astype(str).str.strip().str.upper() == 'ATIVO']

# --- Filtros (Restritos) ---
with st.sidebar:
    st.header("Filtros")
    
    modalidades_alvo = ['Mestrado', 'Doutorado', 'Mestrado/Doutorado', 'Mestrado / Doutorado']
    opcoes_disponiveis = []
    if 'Modalidade' in df.columns:
        opcoes_disponiveis = [m for m in df['Modalidade'].unique() if m in modalidades_alvo]
    
    filtro_modalidade = st.multiselect("Modalidade", opcoes_disponiveis, default=opcoes_disponiveis)
    
    situacoes = df['Situação'].unique() if 'Situação' in df.columns else []
    # filtro_situacao removido conforme solicitação anterior

# Aplica Filtros
df_filtrado = df.copy()
if filtro_modalidade:
    df_filtrado = df_filtrado[df_filtrado['Modalidade'].isin(filtro_modalidade)]

# --- FUNÇÕES AUXILIARES ---
def encontrar_coluna(dataframe, lista_palavras):
    for col in dataframe.columns:
        for palavra in lista_palavras:
            if palavra.lower() in col.lower():
                return col
    return None

def somar_seguro(dataframe, col_name):
    if col_name and col_name in dataframe.columns:
        return pd.to_numeric(dataframe[col_name], errors='coerce').fillna(0).sum()
    return 0

# --- CÁLCULOS GERAIS (KPIs do Topo) ---
qtd_programas = len(df_filtrado)
qtd_com_inscritos = df_filtrado['Inscritos totais'].notna().sum()

# 1. Totais Absolutos (Considerando todos os programas filtrados)
total_vagas_ofertadas = somar_seguro(df_filtrado, 'Total de Vagas Oferecidas')
total_vagas_preenchidas = somar_seguro(df_filtrado, 'Vagas totais preenchidas')

# 2. Taxa de Ocupação (Cálculo Refinado)
taxa_ocupacao_geral = (total_vagas_preenchidas / total_vagas_ofertadas * 100) if total_vagas_ofertadas > 0 else 0

# --- VISUALIZAÇÃO 1: KPIs ---
st.subheader("Visão Geral do Sistema")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Programas Ativos", qtd_programas)
col2.metric("Com dados de Inscritos", f"{qtd_com_inscritos}")
col3.metric("Vagas Totais", f"{total_vagas_ofertadas:,.0f}")
col4.metric("Vagas Preenchidas", f"{total_vagas_preenchidas:,.0f}")
col5.metric(
    "Taxa de Ocupação", 
    f"{taxa_ocupacao_geral:.1f}%",
    help="Razão entre Vagas Preenchidas e Vagas Totais Ofertadas"
)

st.markdown("---")

# --- VISUALIZAÇÃO 2: TAXA DE SUCESSO (COMPARATIVO GERAL vs AA) ---
st.subheader("Análise Comparativa: Taxa de Sucesso (Geral vs AA)")
st.info("ℹ️ Esta análise considera **apenas** os cursos que divulgaram dados de inscritos AA, para garantir uma comparação justa.")

col_inscritos_aa = 'Inscritos AA'

# Filtra apenas quem tem dados de inscritos AA válidos
if col_inscritos_aa in df_filtrado.columns:
    mask_tem_dados_aa = pd.to_numeric(df_filtrado[col_inscritos_aa], errors='coerce').notna()
    df_comp = df_filtrado[mask_tem_dados_aa].copy()
else:
    df_comp = pd.DataFrame()

if not df_comp.empty:
    # --- DADOS GERAIS (DESSE GRUPO) ---
    inscritos_totais = somar_seguro(df_comp, 'Inscritos totais')
    aprovados_totais = somar_seguro(df_comp, 'Vagas totais preenchidas')
    taxa_sucesso_geral = (aprovados_totais / inscritos_totais * 100) if inscritos_totais > 0 else 0
    
    # --- DADOS AA (DESSE GRUPO) ---
    inscritos_aa = somar_seguro(df_comp, col_inscritos_aa)
    
    col_cota = encontrar_coluna(df_comp, ['preenchidas AA', 'vagas AA preenchidas'])
    col_ac = encontrar_coluna(df_comp, ['aprovados na AC', 'aprovados AC'])
    
    aprovados_aa_cota = somar_seguro(df_comp, col_cota)
    aprovados_aa_ac = somar_seguro(df_comp, col_ac)
    aprovados_aa_total = aprovados_aa_cota + aprovados_aa_ac
    
    taxa_sucesso_aa = (aprovados_aa_total / inscritos_aa * 100) if inscritos_aa > 0 else 0
    
    # --- EXIBIÇÃO ---
    c1, c2, c3, c4 = st.columns(4)
    
    c1.metric("Inscritos Totais (Recorte)", f"{inscritos_totais:,.0f}", help="Total de inscritos nos cursos que divulgaram dados AA")
    c2.metric("Aprovados Totais", f"{aprovados_totais:,.0f}", help="Total de vagas preenchidas nestes cursos")
    c3.metric("Taxa de Sucesso (Geral)", f"{taxa_sucesso_geral:.2f}%", help="Candidatos Aprovados / Total de Inscritos")
    
    delta_aa = taxa_sucesso_aa - taxa_sucesso_geral
    c4.metric("Taxa de Sucesso (AA)", f"{taxa_sucesso_aa:.2f}%", delta=f"{delta_aa:.2f} p.p. vs Geral", help="Aprovados AA (Cota+Ampla) / Inscritos AA")

else:
    st.warning("Não há dados suficientes de 'Inscritos AA' para realizar a comparação de taxas de sucesso.")