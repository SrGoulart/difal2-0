import pandas as pd
import streamlit as st
from PIL import Image

# Cores da marca
COR_PRIMARIA = "#0d134c"
COR_SECUNDARIA = "#dd303e"
COR_CLARA = "#ffffff"
COR_DESTAQUE = "#8ff8e0"

st.set_page_config(
    page_title="Simulador DIFAL - GRAN",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        body, .stApp {
            background-color: white !important;
            color: black !important;
        }

        [data-testid="stHeader"] {
            background: white;
        }

        [data-testid="stToolbar"] {
            visibility: hidden;
        }
    </style>
""", unsafe_allow_html=True)


import base64

def get_logo_base64(path):
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

logo_base64 = get_logo_base64("GRAN_colorido_(1).png")

st.markdown(f"""
    <div style='display: flex; justify-content: space-between; align-items: center;'>
        <div style='text-align: left;'>
            <h1 style='color:#0d134c; margin-bottom: 0;'>Simulador de DIFAL</h1>
            <h4 style='color:#dd303e; margin-top: 0;'>GRAN - Simulação Comparativa de Custos</h4>
        </div>
        <div>
            <img src="data:image/png;base64,{logo_base64}" width="200">
        </div>
    </div>
    <hr>
""", unsafe_allow_html=True)


# Aplica CSS customizado
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def get_estado_aliquotas():
    estados = [
        'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS',
        'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC',
        'SP', 'SE', 'TO'
    ]
    estados_7 = ['MG', 'PR', 'RS', 'RJ', 'SC', 'SP']
    aliquotas = [7 if estado in estados_7 else 12 for estado in estados]
    return pd.DataFrame({
        'Estado': estados,
        'AliquotaInterestadual': aliquotas
    })

def calcular_difal(valor_produto_df, valor_produto_fora, frete_df, frete_ou, estado_origem, importado):
    aliquotas = get_estado_aliquotas()
    try:
        aliq_origem = 4 if importado else aliquotas.loc[aliquotas['Estado'] == estado_origem, 'AliquotaInterestadual'].values[0]
    except IndexError:
        return {'Erro': f"Estado '{estado_origem}' não encontrado."}

    aliq_destino = 20
    base_calculo_fora = valor_produto_fora
    difal = base_calculo_fora * ((aliq_destino - aliq_origem) / 100)
    total_df = valor_produto_df + frete_df
    total_outro_estado = valor_produto_fora + frete_ou + difal
    comparativo = 'Compra no DF é mais vantajosa' if total_df < total_outro_estado else 'Compra em outro estado é mais vantajosa'
    diferenca = abs(total_df - total_outro_estado)

    return {
        'Aliquota Estado de Origem (%)': aliq_origem,
        'Aliquota DF (%)': aliq_destino,
        'Aliquota Difal (%)': aliq_destino - aliq_origem,
        'DIFAL (R$)': round(difal, 2),
        'Total Compra no DF (R$)': round(total_df, 2),
        'Total Compra Outro Estado (R$)': round(total_outro_estado, 2),
        'Comparativo': comparativo,
        'Diferença de Custo (R$)': round(diferenca, 2)
    }

# Centralizar o formulário
st.markdown("<div class='centered-box'>", unsafe_allow_html=True)
with st.form("form_difal"):
    st.markdown(f"<h4 style='color:{COR_PRIMARIA}; text-align: center;'>Informações da Simulação</h4>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        valor_produto_df = st.number_input("Valor do Produto DF (R$)", min_value=0.0, step=0.01, format="%.2f")
        frete_df = st.number_input("Frete - Compra no DF (R$)", min_value=0.0, step=0.01, format="%.2f")
        importado = st.radio("Produto Importado?", options=[False, True], format_func=lambda x: "Sim" if x else "Não")

    with col2:
        valor_produto_fora = st.number_input("Valor do Produto fora do DF (R$)", min_value=0.0, step=0.01, format="%.2f")
        frete_ou = st.number_input("Frete - Compra de Outro Estado (R$)", min_value=0.0, step=0.01, format="%.2f")
        estado_origem = st.selectbox("Estado de Origem da Compra", get_estado_aliquotas()['Estado'])

    submit = st.form_submit_button("Calcular", use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# Centralizar resultado abaixo do formulário
if submit:
    resultado = calcular_difal(valor_produto_df, valor_produto_fora, frete_df, frete_ou, estado_origem, importado)
    if 'Erro' in resultado:
        st.error(resultado['Erro'])
    else:
        st.success("Simulação concluída com sucesso.")
        st.markdown("<div class='centered-result'>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='color:{COR_SECUNDARIA}; text-align: center;'>Resultado</h4>", unsafe_allow_html=True)
        for chave, valor in resultado.items():
            st.markdown(f"<div style='color:{COR_PRIMARIA}; font-size: 16px; text-align: center;'><strong>{chave}:</strong> {valor}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
