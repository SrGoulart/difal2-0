import pandas as pd
import streamlit as st
from PIL import Image
import base64

# Cores da marca
COR_PRIMARIA = "#0d134c"
COR_SECUNDARIA = "#dd303e"
COR_CLARA = "#ffffff"
COR_DESTAQUE = "#8ff8e0"

# Configuração da página Streamlit
st.set_page_config(
    page_title="Simulador DIFAL - GRAN",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS gerais para o corpo e cabeçalho
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


# Função para obter a logo em base64
def get_logo_base64(path):
    """
    Carrega uma imagem do caminho especificado e a codifica em base64.
    Retorna uma string base64 da imagem.
    """
    try:
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except FileNotFoundError:
        st.error(f"Erro: Arquivo da logo '{path}' não encontrado. Certifique-se de que está no mesmo diretório.")
        return "" # Retorna uma string vazia em caso de erro

# Carrega a logo
# Certifique-se de que 'GRAN_colorido_(1).png' está no mesmo diretório que 'app.py'
logo_base64 = get_logo_base64("GRAN_colorido_(1).png")

# Layout do cabeçalho com título e logo
st.markdown(f'''
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; padding-bottom: 1rem;">
        <div style="text-align: left; flex-grow: 1;">
            <h1 style="color:{COR_PRIMARIA}; margin-bottom: 0; font-size: 2.5rem;">Simulador de DIFAL</h1>
            <h4 style="color:{COR_SECUNDARIA}; margin-top: 0; font-size: 1.2rem;">GRAN - Simulação Comparativa de Custos</h4>
        </div>
        <div style="flex-shrink: 0;">
            <img src="data:image/png;base64,{logo_base64}" width="200" style="max-width: 100%; height: auto;">
        </div>
    </div>
    <hr style="border: 0; height: 1px; background-image: linear-gradient(to right, rgba(13, 19, 76, 0), rgba(13, 19, 76, 0.75), rgba(13, 19, 76, 0));">
''', unsafe_allow_html=True)

# Aplica CSS customizado do arquivo style.css
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Função para obter alíquotas interestaduais
def get_estado_aliquotas():
    """
    Retorna um DataFrame com os estados brasileiros e suas alíquotas interestaduais.
    """
    estados = [
        'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS',
        'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC',
        'SP', 'SE', 'TO'
    ]
    estados_7 = ['MG', 'PR', 'RS', 'RJ', 'SC', 'SP'] # Estados com alíquota de 7%
    aliquotas = [7 if estado in estados_7 else 12 for estado in estados]
    return pd.DataFrame({
        'Estado': estados,
        'AliquotaInterestadual': aliquotas
    })

# Função principal para calcular o DIFAL
def calcular_difal(valor_produto_df, valor_produto_fora, frete_df, frete_ou, estado_origem, importado):
    """
    Calcula o DIFAL (Diferencial de Alíquotas) e compara os custos de compra.

    Args:
        valor_produto_df (float): Valor do produto se comprado no DF.
        valor_produto_fora (float): Valor do produto se comprado fora do DF.
        frete_df (float): Custo do frete se comprado no DF.
        frete_ou (float): Custo do frete se comprado de outro estado.
        estado_origem (str): Sigla do estado de origem da compra.
        importado (bool): Indica se o produto é importado.

    Returns:
        dict: Um dicionário com os resultados do cálculo ou uma mensagem de erro.
    """
    aliquotas = get_estado_aliquotas()
    
    # Define a alíquota de origem
    try:
        aliq_origem = 4 if importado else aliquotas.loc[aliquotas['Estado'] == estado_origem, 'AliquotaInterestadual'].values[0]
    except IndexError:
        return {'Erro': f"Estado '{estado_origem}' não encontrado na tabela de alíquotas."}

    aliq_destino = 20 # Alíquota interna do DF
    base_calculo_fora = valor_produto_fora
    
    # Cálculo do DIFAL
    difal = base_calculo_fora * ((aliq_destino - aliq_origem) / 100)
    
    # Custos totais
    total_df = valor_produto_df + frete_df
    total_outro_estado = valor_produto_fora + frete_ou + difal
    
    # Comparativo e diferença
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

# Seção do formulário de simulação
# Centraliza o formulário usando uma div com classe CSS
st.markdown("<div class='form-container'>", unsafe_allow_html=True)
with st.form("form_difal"):
    st.markdown(f"<h4 style='color:{COR_PRIMARIA}; text-align: center;'>Informações da Simulação</h4>", unsafe_allow_html=True)
    
    # Cria duas colunas para os campos de entrada
    col1, col2 = st.columns(2)

    with col1:
        # Campos de entrada de valores para compra no DF (sem botões de +/-)
        valor_produto_df = st.number_input("Valor do Produto DF (R$)", min_value=0.0, step=0.01, format="%.2f", label_visibility="visible")
        frete_df = st.number_input("Frete - Compra no DF (R$)", min_value=0.0, step=0.01, format="%.2f", label_visibility="visible")
        # Campo de rádio para produto importado (opções horizontais)
        importado = st.radio("Produto Importado?", options=[False, True], format_func=lambda x: "Sim" if x else "Não", horizontal=True)

    with col2:
        # Campos de entrada de valores para compra fora do DF (sem botões de +/-)
        valor_produto_fora = st.number_input("Valor do Produto fora do DF (R$)", min_value=0.0, step=0.01, format="%.2f", label_visibility="visible")
        frete_ou = st.number_input("Frete - Compra de Outro Estado (R$)", min_value=0.0, step=0.01, format="%.2f", label_visibility="visible")
        # Selectbox para o estado de origem
        estado_origem = st.selectbox("Estado de Origem da Compra", get_estado_aliquotas()['Estado'])

    # Botão de submissão do formulário
    submit = st.form_submit_button("Calcular", use_container_width=True, type="primary")
st.markdown("</div>", unsafe_allow_html=True)

# Seção de resultados
if submit:
    resultado = calcular_difal(valor_produto_df, valor_produto_fora, frete_df, frete_ou, estado_origem, importado)
    
    if 'Erro' in resultado:
        st.error(resultado['Erro'])
    else:
        st.success("Simulação concluída com sucesso.")
        # Centraliza e estiliza a caixa de resultados
        st.markdown("<div class='result-container'>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='color:{COR_SECUNDARIA}; text-align: center;'>Resultado da Simulação</h4>", unsafe_allow_html=True)
        for chave, valor in resultado.items():
            st.markdown(f"<p style='color:{COR_PRIMARIA}; font-size: 16px; text-align: center; margin-bottom: 0.5rem;'><strong>{chave}:</strong> {valor}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        for chave, valor in resultado.items():
            st.markdown(f"<div style='color:{COR_PRIMARIA}; font-size: 16px; text-align: center;'><strong>{chave}:</strong> {valor}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
