import streamlit as st
import pandas as pd

st.set_page_config(page_title="Tabela de Dados", layout="wide")

st.title(" Base de Dados Completa")

if 'dados_ppg' not in st.session_state:
    st.error("Por favor, faça o upload do arquivo na página 'Home' primeiro.")
    st.stop()

df = st.session_state['dados_ppg']

# --- Filtros ---
with st.sidebar:
    st.header("Filtrar Tabela")
    modalidades = df['Modalidade'].unique() if 'Modalidade' in df.columns else []
    sel_mod = st.multiselect("Modalidade", modalidades, default=modalidades)
    
    situacoes = df['Situação'].unique() if 'Situação' in df.columns else []
    sel_sit = st.multiselect("Situação", situacoes, default=situacoes)

df_filtrado = df.copy()
if sel_mod: df_filtrado = df_filtrado[df_filtrado['Modalidade'].isin(sel_mod)]
if sel_sit: df_filtrado = df_filtrado[df_filtrado['Situação'].isin(sel_sit)]

# --- Exibição ---
st.write(f"Exibindo **{len(df_filtrado)}** registros.")

csv = df_filtrado.to_csv(index=False).encode('utf-8')
st.download_button(
    label=" Baixar dados filtrados (CSV)",
    data=csv,
    file_name='dados_filtrados.csv',
    mime='text/csv',
)

st.dataframe(df_filtrado, height=700)