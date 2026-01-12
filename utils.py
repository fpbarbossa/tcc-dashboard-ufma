import streamlit as st

def configurar_tema_global():
    """
    Gerencia o tema global e retorna as configurações visuais.
    """
    
    if 'tema_escuro' not in st.session_state:
        st.session_state['tema_escuro'] = False 

    with st.sidebar:
        st.divider()
        st.session_state['tema_escuro'] = st.toggle(
            "🌗 Modo Escuro", 
            value=st.session_state['tema_escuro']
        )

    # --- DEFINIÇÃO DE CORES ---
    if st.session_state['tema_escuro']:
        # MODO ESCURO
        tema_plotly = 'plotly_dark'
        bg_color = '#0E1117'
        sidebar_bg = '#262730'
        text_color = '#FAFAFA'    # Branco
        chart_bg = '#0E1117'
        line_color = '#444444'
    else:
        # MODO CLARO
        tema_plotly = 'plotly_white'
        bg_color = '#FFFFFF'
        sidebar_bg = '#F0F2F6'
        text_color = '#000000'    # Preto Puro
        chart_bg = '#FFFFFF'
        line_color = '#E5E5E5'

    # CSS INJETADO (VERSÃO SEGURA)
    st.markdown(f"""
    <style>
        /* 1. Fundos Principais */
        .stApp {{ background-color: {bg_color}; }}
        [data-testid="stSidebar"] {{ background-color: {sidebar_bg}; }}
        
        /* 2. Textos do Streamlit (Alvos Específicos) */
        /* Em vez de usar tags genéricas HTML, usamos as classes do Streamlit */
        
        .stMarkdown, .stText, .stMetricValue, .stMetricLabel {{
            color: {text_color} !important;
        }}
        
        /* Headers (H1-H6 são seguros de alterar) */
        h1, h2, h3, h4, h5, h6 {{
            color: {text_color} !important;
        }}
        
        /* Parágrafos APENAS dentro de containers markdown (evita quebrar o Plotly) */
        [data-testid="stMarkdownContainer"] p {{
            color: {text_color} !important;
        }}
        
        /* Listas e Itens APENAS dentro de containers markdown */
        [data-testid="stMarkdownContainer"] ul, [data-testid="stMarkdownContainer"] li {{
            color: {text_color} !important;
        }}
        
        /* Inputs e Widgets */
        .stButton button, .stMultiSelect, .stSelectbox {{
            color: {text_color} !important;
        }}
        
        /* Dataframes */
        [data-testid="stDataFrame"] {{ color: {text_color} !important; }}
        
        /* 3. Correção para Plotly (Evita que textos SVG herdem cores erradas) */
        .js-plotly-plot .plotly text {{
            fill: {text_color} !important;
        }}
        
    </style>
    """, unsafe_allow_html=True)

    # Retorna dicionário completo para o Plotly
    config_graficos = {
        'template': tema_plotly,
        'paper_bgcolor': chart_bg,
        'plot_bgcolor': chart_bg,
        'font_color': text_color,
        'grid_color': line_color
    }

    return config_graficos