import streamlit as st
import pandas as pd

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================

st.set_page_config(
    page_title="Simulador DIFAL - Vendas DF",
    page_icon="📊",
    layout="centered"
)

# =========================
# CORES
# =========================

COR_PRIMARIA = "#0d134c"
COR_SECUNDARIA = "#dd303e"


# =========================
# ESTILO
# =========================

st.markdown(
    f"""
    <style>
        h1 {{
            color: {COR_PRIMARIA};
            text-align: center;
        }}

        .box {{
            background-color: #f7f9fc;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }}

        .resultado {{
            background-color: #ffffff;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #ddd;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# TABELAS FISCAIS
# =========================

def get_aliquotas_interestadual():

    estados = [
        'AC','AL','AP','AM','BA','CE','DF','ES','GO','MA',
        'MT','MS','MG','PA','PB','PR','PE','PI','RJ','RN',
        'RS','RO','RR','SC','SP','SE','TO'
    ]

    estados_7 = ['MG','PR','RS','RJ','SC','SP']

    aliquotas = [
        7 if estado in estados_7 else 12
        for estado in estados
    ]

    return pd.DataFrame({
        "Estado": estados,
        "Aliquota": aliquotas
    })


def get_aliquotas_internas():

    return {
        "AC":19,"AL":19,"AP":18,"AM":20,"BA":20.5,"CE":18,
        "DF":20,"ES":17,"GO":19,"MA":22,"MT":17,"MS":17,
        "MG":18,"PA":19,"PB":18,"PR":19,"PE":20.5,"PI":18,
        "RJ":20,"RN":18,"RS":17,"RO":17.5,"RR":17,"SC":17,
        "SP":18,"SE":18,"TO":18
    }


# =========================
# MOTOR DE CÁLCULO
# =========================

def calcular_difal_venda(
    valor_produto,
    frete,
    estado_destino,
    importado,
    consumidor_final
):

    base = valor_produto + frete

    aliquotas_inter = get_aliquotas_interestadual()
    internas = get_aliquotas_internas()

    # Interestadual
    if importado:
        aliq_inter = 4
    else:
        aliq_inter = aliquotas_inter.loc[
            aliquotas_inter["Estado"] == estado_destino,
            "Aliquota"
        ].values[0]

    # Interna
    aliq_interna = internas.get(estado_destino)

    if not aliq_interna:
        return {"Erro": "Estado inválido."}

    # ICMS Origem
    icms_origem = base * (aliq_inter / 100)

    difal = 0
    icms_destino = 0

    # DIFAL só se consumidor final não contribuinte
    if consumidor_final:

        difal = base * ((aliq_interna - aliq_inter) / 100)
        icms_destino = difal

    total_icms = icms_origem + icms_destino

    return {

        "Base de Cálculo (R$)": round(base,2),

        "Alíquota Interestadual (%)": aliq_inter,

        "Alíquota Interna Destino (%)": aliq_interna,

        "ICMS Origem - DF (R$)": round(icms_origem,2),

        "DIFAL Destino (R$)": round(difal,2),

        "Total ICMS (R$)": round(total_icms,2)
    }


# =========================
# INTERFACE
# =========================

st.markdown("<h1>Simulador DIFAL - Vendas DF</h1>", unsafe_allow_html=True)


st.markdown(
    "<div class='box'>",
    unsafe_allow_html=True
)


with st.form("form_simulador"):

    st.subheader("📌 Dados da Venda")

    col1, col2 = st.columns(2)

    with col1:

        valor_produto = st.number_input(
            "Valor da Venda (R$)",
            min_value=0.0,
            step=0.01,
            format="%.2f"
        )

        frete = st.number_input(
            "Frete (R$)",
            min_value=0.0,
            step=0.01,
            format="%.2f"
        )


    with col2:

        estado_destino = st.selectbox(
            "Estado de Destino",
            get_aliquotas_interestadual()["Estado"]
        )

        importado = st.radio(
            "Produto Importado?",
            [False, True],
            format_func=lambda x: "Sim" if x else "Não",
            horizontal=True
        )

        consumidor_final = st.radio(
            "Consumidor Final Não Contribuinte?",
            [True, False],
            format_func=lambda x: "Sim" if x else "Não",
            horizontal=True
        )


    calcular = st.form_submit_button(
        "Calcular DIFAL",
        use_container_width=True
    )


st.markdown("</div>", unsafe_allow_html=True)


# =========================
# RESULTADO
# =========================

if calcular:

    resultado = calcular_difal_venda(
        valor_produto,
        frete,
        estado_destino,
        importado,
        consumidor_final
    )

    if "Erro" in resultado:

        st.error(resultado["Erro"])

    else:

        st.success("Simulação concluída")

        st.markdown(
            "<div class='resultado'>",
            unsafe_allow_html=True
        )

        st.subheader("📊 Resultado")

        for k, v in resultado.items():

            st.write(f"**{k}:** {v}")

        st.markdown("</div>", unsafe_allow_html=True)
