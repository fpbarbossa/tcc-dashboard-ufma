import streamlit as st
import pandas as pd
import utils

st.set_page_config(page_title="Ações Afirmativas", layout="wide")

#utils.configurar_tema_global()

st.title("⚖️ Indicadores de Ações Afirmativas (Ativos)")

if 'dados_ppg' not in st.session_state:
    st.error("Por favor, faça o upload do arquivo na página 'Home' primeiro.")
    st.stop()

df = st.session_state['dados_ppg']

# --- FILTRAGEM GLOBAL DE ATIVOS ---
if 'Situação' in df.columns:
    df = df[df['Situação'].astype(str).str.strip().str.upper() == 'ATIVO']

# --- Filtros (Modalidade) ---
with st.sidebar:
    st.header("Filtros AA")
    
    modalidades_alvo = ['Mestrado', 'Doutorado', 'Mestrado/Doutorado', 'Mestrado / Doutorado']
    opcoes_disponiveis = []
    if 'Modalidade' in df.columns:
        opcoes_disponiveis = [m for m in df['Modalidade'].unique() if m in modalidades_alvo]
    
    filtro_modalidade = st.multiselect("Modalidade", opcoes_disponiveis, default=opcoes_disponiveis)

# Aplica Filtro
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

def somar_coluna_segura(dataframe, nome_coluna):
    if nome_coluna and nome_coluna in dataframe.columns:
        return pd.to_numeric(dataframe[nome_coluna], errors='coerce').fillna(0).sum()
    return 0

# --- SEÇÃO 1: OFERTA DE VAGAS AA ---
st.subheader("1. Oferta de Vagas Reservadas")

total_vagas = somar_coluna_segura(df_filtrado, 'Total de Vagas Oferecidas')
total_vagas_aa = somar_coluna_segura(df_filtrado, 'Total de Vagas AA Oferecidas')
pct_aa_geral = (total_vagas_aa / total_vagas * 100) if total_vagas > 0 else 0

col_v1, col_v2 = st.columns(2)
col_v1.metric("Total de Vagas AA (Absoluto)", f"{total_vagas_aa:,.0f}")
col_v2.metric("Proporção de Vagas AA (Geral)", f"{pct_aa_geral:.1f}%", help="Vagas AA / Vagas Totais")

st.markdown("---")

# --- SEÇÃO 2: DEMANDA E APROVAÇÃO ---
st.subheader("2. Demanda e Aprovação AA")
st.info("ℹ️ Considera apenas programas ativos que divulgaram Inscritos AA.")

col_inscritos_aa = 'Inscritos AA'
col_aprovados_ac = encontrar_coluna(df_filtrado, ['aprovados na AC', 'aprovados AC']) 
col_aprovados_cota = encontrar_coluna(df_filtrado, ['preenchidas AA', 'vagas AA preenchidas']) 

if col_inscritos_aa in df_filtrado.columns:
    mask_tem_dados = pd.to_numeric(df_filtrado[col_inscritos_aa], errors='coerce').notna()
    df_demanda = df_filtrado[mask_tem_dados].copy()
else:
    df_demanda = pd.DataFrame() 

if not df_demanda.empty:
    qtd_programas_que_divulgaram = len(df_demanda)
    
    total_inscritos_desse_grupo = somar_coluna_segura(df_demanda, 'Inscritos totais')
    total_aprovados_desse_grupo = somar_coluna_segura(df_demanda, 'Vagas totais preenchidas')
    
    total_inscritos_aa = somar_coluna_segura(df_demanda, col_inscritos_aa)
    total_aprovados_cota = somar_coluna_segura(df_demanda, col_aprovados_cota)
    total_aprovados_ac = somar_coluna_segura(df_demanda, col_aprovados_ac)
    total_aa_aprovados = total_aprovados_cota + total_aprovados_ac
    
    pct_divulgacao = (qtd_programas_que_divulgaram / len(df_filtrado) * 100) if len(df_filtrado) > 0 else 0
    pct_inscritos_aa = (total_inscritos_aa / total_inscritos_desse_grupo * 100) if total_inscritos_desse_grupo > 0 else 0
    pct_aprovados_aa = (total_aa_aprovados / total_aprovados_desse_grupo * 100) if total_aprovados_desse_grupo > 0 else 0
    pct_cota = (total_aprovados_cota / total_aprovados_desse_grupo * 100) if total_aprovados_desse_grupo > 0 else 0
    pct_ac = (total_aprovados_ac / total_aprovados_desse_grupo * 100) if total_aprovados_desse_grupo > 0 else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Divulgaram Inscritos AA", f"{qtd_programas_que_divulgaram}")
    c2.metric("Inscritos AA", f"{total_inscritos_aa:,.0f}")
    c3.metric("Aprovados (Cota)", f"{total_aprovados_cota:,.0f}")
    c4.metric("Aprovados (Ampla)", f"{total_aprovados_ac:,.0f}")
    c5.metric("Total AA Aprovados", f"{total_aa_aprovados:,.0f}")
else:
    st.warning("Nenhum programa com dados de 'Inscritos AA' encontrado.")

st.markdown("---")

# --- SEÇÃO 3: HISTÓRICO ---
st.subheader("3. Evolução Histórica (Programas Ativos)")

col_antes = encontrar_coluna(df_filtrado, ["antes da IN"])
col_in = encontrar_coluna(df_filtrado, ["depois da criação da IN", "após a IN"])
col_res = encontrar_coluna(df_filtrado, ["depois da criação da Resolução", "após a Resolução"])

if col_antes and col_in and col_res:
    ch1, ch2, ch3 = st.columns(3)
    
    s_antes = df_filtrado[col_antes].astype(str).str.strip().str.upper().isin(['S', 'SIM'])
    s_in = df_filtrado[col_in].astype(str).str.strip().str.upper().isin(['S', 'SIM'])
    s_res = df_filtrado[col_res].astype(str).str.strip().str.upper().isin(['S', 'SIM'])
    
    qtd_total = len(df_filtrado)
    total_antes = s_antes.sum()
    total_pos_in = (s_antes | s_in).sum()
    total_pos_res = (s_antes | s_in | s_res).sum()
    
    p_antes = (total_antes / qtd_total * 100) if qtd_total > 0 else 0
    p_in = (total_pos_in / qtd_total * 100) if qtd_total > 0 else 0
    p_res = (total_pos_res / qtd_total * 100) if qtd_total > 0 else 0

    ch1.metric("Contemplavam (Pré-IN)", total_antes, f"{p_antes:.1f}%")
    ch2.metric("Contemplavam (Pós-IN)", total_pos_in, f"{p_in:.1f}%")
    ch3.metric("Contemplam (Pós-Resolução)", total_pos_res, f"{p_res:.1f}%")