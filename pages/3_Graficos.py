import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Gráficos", layout="wide")

st.title("📈 Análises Visuais (Ativos)")

if 'dados_ppg' not in st.session_state:
    st.error("Por favor, faça o upload do arquivo na página 'Home' primeiro.")
    st.stop()

df = st.session_state['dados_ppg']

# --- FILTRAGEM GLOBAL DE ATIVOS ---
if 'Situação' in df.columns:
    df = df[df['Situação'].astype(str).str.strip().str.upper() == 'ATIVO']

# --- Filtros (Modalidade) ---
with st.sidebar:
    st.header("Filtros de Gráfico")
    
    modalidades_alvo = ['Mestrado', 'Doutorado', 'Mestrado/Doutorado', 'Mestrado / Doutorado']
    opcoes_disponiveis = [m for m in df['Modalidade'].unique() if m in modalidades_alvo] if 'Modalidade' in df.columns else []
    
    sel_mod = st.multiselect("Modalidade", opcoes_disponiveis, default=opcoes_disponiveis)

# Aplica Filtro
df_filtrado = df.copy()
if sel_mod: df_filtrado = df_filtrado[df_filtrado['Modalidade'].isin(sel_mod)]

# --- FUNÇÕES ---
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

# ==============================================================================
# SEÇÃO 1: GRÁFICO DE DESTAQUE
# ==============================================================================
st.subheader("🟢 Distribuição dos Programas Ativos por Nível")

if 'Modalidade' in df_filtrado.columns:
    # O df_filtrado já contém apenas ativos
    df_mod = df_filtrado['Modalidade'].value_counts().reset_index()
    df_mod.columns = ['Nível', 'Quantidade']
    
    fig_mod = px.pie(
        df_mod, 
        names='Nível', 
        values='Quantidade', 
        hole=0.5, 
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_mod.update_traces(textposition='inside', textinfo='percent')
    fig_mod.update_layout(height=400, font=dict(size=14))
    
    st.plotly_chart(fig_mod, use_container_width=True)
else:
    st.warning("Dados insuficientes.")

st.markdown("---")

# ==============================================================================
# SEÇÃO 2: ANÁLISES
# ==============================================================================
st.subheader("📊 Oferta, Demanda e Evolução")

col_g1, col_g2 = st.columns(2)

with col_g1:
    st.markdown("##### Oferta vs Demanda")
    if 'Modalidade' in df_filtrado.columns:
        df_group = df_filtrado.groupby('Modalidade')[['Total de Vagas Oferecidas', 'Inscritos totais']].sum().reset_index()
        df_melted = df_group.melt(id_vars='Modalidade', value_vars=['Total de Vagas Oferecidas', 'Inscritos totais'], var_name='Métrica', value_name='Quantidade')
        
        fig_bar = px.bar(df_melted, x='Modalidade', y='Quantidade', color='Métrica', barmode='group', height=400)
        st.plotly_chart(fig_bar, use_container_width=True)

with col_g2:
    st.markdown("##### Evolução da Adesão Institucional às Ações Afirmativas")
    
    col_antes = encontrar_coluna(df_filtrado, ["antes da IN"])
    col_in = encontrar_coluna(df_filtrado, ["depois da criação da IN", "após a IN"])
    col_res = encontrar_coluna(df_filtrado, ["depois da criação da Resolução", "após a Resolução"])
    
    if col_antes and col_in and col_res:
        s_antes = df_filtrado[col_antes].astype(str).str.strip().str.upper().isin(['S', 'SIM'])
        s_in = df_filtrado[col_in].astype(str).str.strip().str.upper().isin(['S', 'SIM'])
        s_res = df_filtrado[col_res].astype(str).str.strip().str.upper().isin(['S', 'SIM'])
        
        total_antes = s_antes.sum()
        total_pos_in = (s_antes | s_in).sum()
        total_pos_res = (s_antes | s_in | s_res).sum()
        
        data_evolucao = {
            'Fase': ['Antes da IN', 'Pós-IN', 'Pós-Resolução'],
            'Programas com Cotas': [total_antes, total_pos_in, total_pos_res]
        }
        df_evolucao = pd.DataFrame(data_evolucao)
        
        fig_evo = px.bar(
            df_evolucao, 
            x='Fase', 
            y='Programas com Cotas',
            text_auto=True,
            color='Programas com Cotas',
            color_continuous_scale=px.colors.sequential.Blues,
            height=400
        )
        
        fig_evo.update_layout(
            coloraxis_showscale=False, 
            xaxis_title=None,          
            yaxis_title="Nº de Programas (PPGs)"
        )
        
        st.plotly_chart(fig_evo, use_container_width=True)

st.markdown("---")

# ==============================================================================
# SEÇÃO 3: COMPARATIVO
# ==============================================================================
st.subheader("⚖️ Comparativo de Eficiência: Taxa de Sucesso (Geral vs AA)")
st.info("ℹ️ Os dados abaixo consideram apenas os cursos ativos que divulgaram Inscritos AA.")

col_inscritos_aa = 'Inscritos AA'
col_aprovados_ac = encontrar_coluna(df_filtrado, ['aprovados na AC', 'aprovados AC'])
col_aprovados_cota = encontrar_coluna(df_filtrado, ['preenchidas AA', 'vagas AA preenchidas'])

if col_inscritos_aa in df_filtrado.columns:
    mask_tem_dados = pd.to_numeric(df_filtrado[col_inscritos_aa], errors='coerce').notna()
    df_comp = df_filtrado[mask_tem_dados].copy()
    
    if not df_comp.empty:
        ins_g = somar_seguro(df_comp, 'Inscritos totais')
        apr_g = somar_seguro(df_comp, 'Vagas totais preenchidas')
        taxa_g = (apr_g / ins_g * 100) if ins_g > 0 else 0
        
        ins_aa = somar_seguro(df_comp, col_inscritos_aa)
        apr_aa_cota = somar_seguro(df_comp, col_aprovados_cota)
        apr_aa_ac = somar_seguro(df_comp, col_aprovados_ac)
        total_apr_aa = apr_aa_cota + apr_aa_ac
        taxa_aa = (total_apr_aa / ins_aa * 100) if ins_aa > 0 else 0
        
        df_chart = pd.DataFrame([
            {'Categoria': 'Geral', 'Taxa de Sucesso (%)': taxa_g},
            {'Categoria': 'Candidatos AA', 'Taxa de Sucesso (%)': taxa_aa}
        ])
        
        fig_comp = px.bar(
            df_chart, 
            x='Categoria', 
            y='Taxa de Sucesso (%)', 
            color='Categoria', 
            text_auto='.1f',
            color_discrete_map={'Geral': '#A9A9A9', 'Candidatos AA': '#2E86C1'},
            height=450
        )
        fig_comp.update_layout(yaxis_title="Taxa de Aprovação (%)", xaxis_title=None, showlegend=False)
        st.plotly_chart(fig_comp, use_container_width=True)
    else:
        st.warning("Dados insuficientes.")