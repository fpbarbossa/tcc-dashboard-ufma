import streamlit as st
import pandas as pd

st.set_page_config(page_title="Métricas Gerais", layout="wide")

st.title("📊 Indicadores Gerais de Desempenho (Ativos)")

# Verifica Session State
if 'dados_ppg' not in st.session_state:
    st.error("Por favor, faça o upload do arquivo na página 'Home' primeiro.")
    st.stop()

df = st.session_state['dados_ppg']

# --- FILTRAGEM GLOBAL DE ATIVOS ---
if 'Situação' in df.columns:
    # Mantém apenas os ATIVOS
    df = df[df['Situação'].astype(str).str.strip().str.upper() == 'ATIVO']
else:
    st.warning("Coluna 'Situação' não encontrada. Exibindo todos os dados.")

# --- Filtros (Apenas Modalidade) ---
with st.sidebar:
    st.header("Filtros")
    
    modalidades_alvo = ['Mestrado', 'Doutorado', 'Mestrado/Doutorado', 'Mestrado / Doutorado']
    opcoes_disponiveis = []
    if 'Modalidade' in df.columns:
        opcoes_disponiveis = [m for m in df['Modalidade'].unique() if m in modalidades_alvo]
    
    filtro_modalidade = st.multiselect("Modalidade", opcoes_disponiveis, default=opcoes_disponiveis)

# Aplica Filtro Modalidade
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

# --- CÁLCULOS GERAIS ---
qtd_programas = len(df_filtrado) # Agora isso já é o total de ativos filtrados
qtd_com_inscritos = df_filtrado['Inscritos totais'].notna().sum()

# Taxa de Ocupação (Baseado apenas em quem tem inscritos > 0)
mask_ocupacao = (df_filtrado['Inscritos totais'].notna()) & (df_filtrado['Inscritos totais'] > 0)
df_ocupacao = df_filtrado[mask_ocupacao]

vagas_geral = somar_seguro(df_ocupacao, 'Total de Vagas Oferecidas')
aprovados_geral = somar_seguro(df_ocupacao, 'Vagas totais preenchidas')
taxa_ocupacao_geral = (aprovados_geral / vagas_geral * 100) if vagas_geral > 0 else 0

# --- VISUALIZAÇÃO 1: KPIs ---
st.subheader("Visão Geral do Sistema")
col1, col2, col3 = st.columns(3)

col1.metric("Total de Programas Ativos", qtd_programas)
col2.metric("Com dados de Inscritos", f"{qtd_com_inscritos}")
col3.metric(
    "Taxa de Ocupação (Vagas)", 
    f"{taxa_ocupacao_geral:.1f}%",
    help="Vagas Preenchidas / Vagas Ofertadas (apenas cursos com inscritos)"
)

st.markdown("---")

# --- VISUALIZAÇÃO 2: TAXA DE SUCESSO ---
st.subheader("⚖️ Análise Comparativa: Taxa de Sucesso (Geral vs AA)")
st.info("ℹ️ Comparativo considerando apenas cursos ativos que divulgaram inscritos AA.")

col_inscritos_aa = 'Inscritos AA'

if col_inscritos_aa in df_filtrado.columns:
    mask_tem_dados_aa = pd.to_numeric(df_filtrado[col_inscritos_aa], errors='coerce').notna()
    df_comp = df_filtrado[mask_tem_dados_aa].copy()
else:
    df_comp = pd.DataFrame()

if not df_comp.empty:
    inscritos_totais = somar_seguro(df_comp, 'Inscritos totais')
    aprovados_totais = somar_seguro(df_comp, 'Vagas totais preenchidas')
    taxa_sucesso_geral = (aprovados_totais / inscritos_totais * 100) if inscritos_totais > 0 else 0
    
    inscritos_aa = somar_seguro(df_comp, col_inscritos_aa)
    
    col_cota = encontrar_coluna(df_comp, ['preenchidas AA', 'vagas AA preenchidas'])
    col_ac = encontrar_coluna(df_comp, ['aprovados na AC', 'aprovados AC'])
    
    aprovados_aa_cota = somar_seguro(df_comp, col_cota)
    aprovados_aa_ac = somar_seguro(df_comp, col_ac)
    aprovados_aa_total = aprovados_aa_cota + aprovados_aa_ac
    
    taxa_sucesso_aa = (aprovados_aa_total / inscritos_aa * 100) if inscritos_aa > 0 else 0
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Inscritos Totais (Recorte)", f"{inscritos_totais:,.0f}")
    c2.metric("Aprovados Totais", f"{aprovados_totais:,.0f}")
    c3.metric("Taxa de Sucesso (Geral)", f"{taxa_sucesso_geral:.2f}%")
    
    delta_aa = taxa_sucesso_aa - taxa_sucesso_geral
    c4.metric("Taxa de Sucesso (AA)", f"{taxa_sucesso_aa:.2f}%", delta=f"{delta_aa:.2f} p.p. vs Geral")

else:
    st.warning("Não há dados suficientes de 'Inscritos AA'.")