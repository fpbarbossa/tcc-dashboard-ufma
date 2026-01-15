import streamlit as st
import pandas as pd
import plotly.express as px
import utils 

st.set_page_config(page_title="Gráficos", layout="wide")

# --- RECUPERA CONFIGURAÇÃO DO TEMA ---
config_visual = utils.configurar_tema_global()

st.title("Análises Visuais (Ativos)")

if 'dados_ppg' not in st.session_state:
    st.error("Por favor, faça o upload do arquivo na página 'Home' primeiro.")
    st.stop()

df = st.session_state['dados_ppg']

# FILTRAGEM GLOBAL
if 'Situação' in df.columns:
    df = df[df['Situação'].astype(str).str.strip().str.upper() == 'ATIVO']

# FILTROS
with st.sidebar:
    st.header("Filtros de Gráfico")
    modalidades_alvo = ['Mestrado', 'Doutorado', 'Mestrado/Doutorado', 'Mestrado / Doutorado']
    opcoes_disponiveis = [m for m in df['Modalidade'].unique() if m in modalidades_alvo] if 'Modalidade' in df.columns else []
    sel_mod = st.multiselect("Modalidade", opcoes_disponiveis, default=opcoes_disponiveis)

df_filtrado = df.copy()
if sel_mod: df_filtrado = df_filtrado[df_filtrado['Modalidade'].isin(sel_mod)]

# FUNÇÕES AUXILIARES
def encontrar_coluna(dataframe, lista_palavras):
    for col in dataframe.columns:
        for palavra in lista_palavras:
            if palavra.lower() in col.lower(): return col
    return None

def somar_seguro(dataframe, col_name):
    if col_name and col_name in dataframe.columns:
        return pd.to_numeric(dataframe[col_name], errors='coerce').fillna(0).sum()
    return 0

def detectar_grupos(texto_celula):
    grupos_encontrados = set()
    if pd.isna(texto_celula) or str(texto_celula).strip() == '*': return grupos_encontrados
    texto = str(texto_celula).upper()
    termos = {'Negros': ['NEGRO'], 'Indígenas': ['INDIGENA', 'INDÍGENA'], 'PCD': ['PCD', 'DEFICIÊNCIA'], 'Quilombolas': ['QUILOMBOLA'], 'Trans': ['TRANS', 'TRAVESTI']}
    for grupo, palavras_chave in termos.items():
        for palavra in palavras_chave:
            if palavra in texto:
                grupos_encontrados.add(grupo)
                break
    return grupos_encontrados

# --- FUNÇÃO PARA APLICAR TEMA NOS GRÁFICOS ---
def aplicar_tema(fig):
    cor_texto = config_visual['font_color']
    cor_grade = config_visual['grid_color']
    
    fig.update_layout(
        template=config_visual['template'],
        paper_bgcolor=config_visual['paper_bgcolor'],
        plot_bgcolor=config_visual['paper_bgcolor'],
        
        # FORÇA A COR DA FONTE EM TUDO
        font=dict(color=cor_texto),
        
        # Força cor do Título do Gráfico
        title=dict(font=dict(color=cor_texto)),
        
        # Força cor da Legenda
        legend=dict(font=dict(color=cor_texto), title=dict(font=dict(color=cor_texto))),
        
        # Força cor dos Eixos X e Y (Títulos, Linhas e Ticks)
        xaxis=dict(
            title_font=dict(color=cor_texto),
            tickfont=dict(color=cor_texto),
            gridcolor=cor_grade,
            zerolinecolor=cor_grade
        ),
        yaxis=dict(
            title_font=dict(color=cor_texto),
            tickfont=dict(color=cor_texto),
            gridcolor=cor_grade,
            zerolinecolor=cor_grade
        )
    )
    return fig


# GRÁFICO 1: PIZZA

st.subheader(" Distribuição dos Programas Ativos por Nível")

if 'Modalidade' in df_filtrado.columns:
    df_mod = df_filtrado['Modalidade'].value_counts().reset_index()
    df_mod.columns = ['Nível', 'Quantidade']
    
    fig_mod = px.pie(
        df_mod, names='Nível', values='Quantidade', hole=0.5, 
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_mod.update_traces(textposition='inside', textinfo='percent')
    fig_mod.update_layout(height=400, font=dict(size=14))
    
    # APLICA TEMA
    fig_mod = aplicar_tema(fig_mod)
    
    st.plotly_chart(fig_mod, use_container_width=True)
else:
    st.warning("Dados insuficientes.")

st.markdown("---")


# GRÁFICO 2: EVOLUÇÃO LINHA

st.subheader(" Evolução da Implementação por Grupo de Cota")
col_pre_desc = encontrar_coluna(df_filtrado, ["Se S, quais?", "quais?"]) 
col_in_desc = encontrar_coluna(df_filtrado, ["quais alterações?"]) 
col_atende_todas = encontrar_coluna(df_filtrado, ["Atende todas as cotas"])
col_res_desc = encontrar_coluna(df_filtrado, ["quais atende?"]) 

if col_pre_desc and col_in_desc and col_atende_todas:
    grupos_alvo = ['Negros', 'Indígenas', 'PCD', 'Quilombolas', 'Trans']
    contagem = {'Pré-IN': {g: 0 for g in grupos_alvo}, 'Pós-IN': {g: 0 for g in grupos_alvo}, 'Pós-Resolução': {g: 0 for g in grupos_alvo}}
    
    for index, row in df_filtrado.iterrows():
        grupos_pre = detectar_grupos(row[col_pre_desc])
        grupos_in_novos = detectar_grupos(row[col_in_desc])
        grupos_pos_in = grupos_pre.union(grupos_in_novos)
        if str(row[col_atende_todas]).strip().upper() in ['S', 'SIM']:
            grupos_pos_res = set(grupos_alvo)
        else:
            grupos_pos_res = detectar_grupos(row[col_res_desc]).union(grupos_pos_in)
        for g in grupos_alvo:
            if g in grupos_pre: contagem['Pré-IN'][g] += 1
            if g in grupos_pos_in: contagem['Pós-IN'][g] += 1
            if g in grupos_pos_res: contagem['Pós-Resolução'][g] += 1

    dados_grafico = []
    for fase in ['Pré-IN', 'Pós-IN', 'Pós-Resolução']:
        for grupo in grupos_alvo:
            dados_grafico.append({'Fase': fase, 'Grupo': grupo, 'Quantidade': contagem[fase][grupo]})
            
    fig_evo_line = px.line(
        pd.DataFrame(dados_grafico), x='Fase', y='Quantidade', color='Grupo', markers=True, symbol='Grupo',
        height=450, color_discrete_sequence=px.colors.qualitative.Dark24
    )
    fig_evo_line.update_layout(yaxis_title="Nº de Programas", xaxis_title=None)
    fig_evo_line.update_traces(line=dict(width=3), marker=dict(size=10))
    
    # APLICA TEMA
    fig_evo_line = aplicar_tema(fig_evo_line)
    
    st.plotly_chart(fig_evo_line, use_container_width=True)
else:
    st.warning("Colunas descritivas não encontradas.")

st.markdown("---")


# GRÁFICOS 3 e 4

col_g1, col_g2 = st.columns(2)

with col_g1:
    st.markdown("##### Oferta vs Demanda")
    if 'Modalidade' in df_filtrado.columns:
        df_group = df_filtrado.groupby('Modalidade')[['Total de Vagas Oferecidas', 'Inscritos totais']].sum().reset_index()
        df_melted = df_group.melt(id_vars='Modalidade', value_vars=['Total de Vagas Oferecidas', 'Inscritos totais'], var_name='Métrica', value_name='Quantidade')
        
        fig_bar = px.bar(
            df_melted, x='Modalidade', y='Quantidade', color='Métrica', barmode='group', height=400
        )
        # APLICA TEMA
        fig_bar = aplicar_tema(fig_bar)
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
        
        df_evolucao = pd.DataFrame({
            'Fase': ['Antes da IN', 'Pós-IN', 'Pós-Resolução'],
            'Programas com Cotas': [s_antes.sum(), (s_antes|s_in).sum(), (s_antes|s_in|s_res).sum()]
        })
        
        fig_evo_bar = px.bar(
            df_evolucao, x='Fase', y='Programas com Cotas', text_auto=True, color='Programas com Cotas',
            color_continuous_scale=px.colors.sequential.Blues, height=400
        )
        fig_evo_bar.update_layout(coloraxis_showscale=False, xaxis_title=None, yaxis_title="Nº de Programas (PPGs)")
        
        # APLICA TEMA
        fig_evo_bar = aplicar_tema(fig_evo_bar)
        st.plotly_chart(fig_evo_bar, use_container_width=True)

st.markdown("---")


# GRÁFICO 5: TAXA DE SUCESSO

st.subheader(" Comparativo de Eficiência: Taxa de Sucesso (Geral vs AA)")
col_inscritos_aa = 'Inscritos AA'
if col_inscritos_aa in df_filtrado.columns:
    mask_tem_dados = pd.to_numeric(df_filtrado[col_inscritos_aa], errors='coerce').notna()
    df_comp = df_filtrado[mask_tem_dados].copy()
    if not df_comp.empty:
        ins_g = somar_seguro(df_comp, 'Inscritos totais')
        apr_g = somar_seguro(df_comp, 'Vagas totais preenchidas')
        taxa_g = (apr_g / ins_g * 100) if ins_g > 0 else 0
        
        ins_aa = somar_seguro(df_comp, col_inscritos_aa)
        col_cota = encontrar_coluna(df_comp, ['preenchidas AA', 'vagas AA preenchidas'])
        col_ac = encontrar_coluna(df_comp, ['aprovados na AC', 'aprovados AC'])
        apr_aa_cota = somar_seguro(df_comp, col_cota)
        apr_aa_ac = somar_seguro(df_comp, col_ac)
        taxa_aa = ((apr_aa_cota + apr_aa_ac) / ins_aa * 100) if ins_aa > 0 else 0
        
        df_chart = pd.DataFrame([
            {'Categoria': 'Geral', 'Taxa de Sucesso (%)': taxa_g},
            {'Categoria': 'Candidatos AA', 'Taxa de Sucesso (%)': taxa_aa}
        ])
        
        cores = {'Geral': '#A9A9A9', 'Candidatos AA': '#2E86C1'}
        fig_comp = px.bar(
            df_chart, x='Categoria', y='Taxa de Sucesso (%)', color='Categoria', text_auto='.1f',
            color_discrete_map=cores, height=450
        )
        fig_comp.update_layout(yaxis_title="Taxa de Aprovação (%)", xaxis_title=None, showlegend=False)
        
        # APLICA TEMA
        fig_comp = aplicar_tema(fig_comp)
        
        st.plotly_chart(fig_comp, use_container_width=True)
    else:
        st.warning("Dados insuficientes.")