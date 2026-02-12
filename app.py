import streamlit as st
import pandas as pd
from io import BytesIO


# =========================
# CONFIG
# =========================

st.set_page_config(
    page_title="Simulador DIFAL - Vendas DF",
    page_icon="📊",
    layout="centered"
)


# =========================
# CSS
# =========================

st.markdown("""
<style>

body {
    background-color: #0f172a;
}

.main {
    background-color: #020617;
}

h1, h2, h3 {
    text-align: center;
}

.card {
    background: linear-gradient(145deg,#020617,#020617);
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 15px;
    box-shadow: 0px 0px 12px rgba(15,23,42,0.6);
}

.input-box {
    background-color: #020617;
    padding: 25px;
    border-radius: 15px;
    border: 1px solid #1e293b;
}

.result-box {
    background-color: #020617;
    padding: 25px;
    border-radius: 15px;
    border: 1px solid #1e293b;
}

.success {
    background-color: #052e16;
    color: #22c55e;
    padding: 12px;
    border-radius: 8px;
    text-align: center;
}

</style>
""", unsafe_allow_html=True)


# =========================
# DADOS FISCAIS
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
# MOTOR
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

    if importado:
        aliq_inter = 4
    else:
        aliq_inter = aliquotas_inter.loc[
            aliquotas_inter["Estado"] == estado_destino,
            "Aliquota"
        ].values[0]

    aliq_interna = internas.get(estado_destino)

    if not aliq_interna:
        return None

    icms_origem = base * (aliq_inter / 100)

    difal = 0

    if consumidor_final:
        difal = base * ((aliq_interna - aliq_inter) / 100)

    total = icms_origem + difal

    return {
        "Base de Cálculo": round(base,2),
        "Alíquota Interestadual": aliq_inter,
        "Alíquota Interna": aliq_interna,
        "ICMS Origem (DF)": round(icms_origem,2),
        "DIFAL Destino": round(difal,2),
        "Total ICMS": round(total,2)
    }


# =========================
# EXPORTAÇÃO
# =========================

def gerar_excel(resultado, dados):

    df = pd.DataFrame([{
        **dados,
        **resultado
    }])

    buffer = BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Simulação")

    return buffer.getvalue()


# =========================
# HEADER
# =========================

st.markdown("<h1>📊 Simulador DIFAL</h1>", unsafe_allow_html=True)
st.markdown("<h3>Vendas do DF para Outros Estados</h3>", unsafe_allow_html=True)


# =========================
# FORM
# =========================

st.markdown("<div class='input-box'>", unsafe_allow_html=True)

with st.form("simulador"):

    st.subheader("📌 Dados da Venda")

    col1, col2 = st.columns(2)

    with col1:

        valor = st.number_input("Valor da Venda (R$)", 0.0, step=0.01)
        frete = st.number_input("Frete (R$)", 0.0, step=0.01)

    with col2:

        estado = st.selectbox(
            "Estado de Destino",
            get_aliquotas_interestadual()["Estado"]
        )

        importado = st.radio(
            "Produto Importado?",
            [False, True],
            format_func=lambda x: "Sim" if x else "Não",
            horizontal=True
        )

        consumidor = st.radio(
            "Consumidor Final Não Contribuinte?",
            [True, False],
            format_func=lambda x: "Sim" if x else "Não",
            horizontal=True
        )

    calcular = st.form_submit_button("🚀 Calcular DIFAL", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)


# =========================
# PROCESSAMENTO
# =========================

if calcular:

    dados = {
        "Valor Venda": valor,
        "Frete": frete,
        "Destino": estado,
        "Importado": "Sim" if importado else "Não",
        "Consumidor Final": "Sim" if consumidor else "Não"
    }

    resultado = calcular_difal_venda(
        valor,
        frete,
        estado,
        importado,
        consumidor
    )

    if not resultado:

        st.error("Erro no cálculo.")

    else:

        st.markdown("<div class='success'>Simulação concluída</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Cards
        col1, col2, col3 = st.columns(3)

        col1.markdown(f"""
        <div class='card'>
        <h4>Base</h4>
        <h2>R$ {resultado['Base de Cálculo']}</h2>
        </div>
        """, unsafe_allow_html=True)

        col2.markdown(f"""
        <div class='card'>
        <h4>DIFAL</h4>
        <h2>R$ {resultado['DIFAL Destino']}</h2>
        </div>
        """, unsafe_allow_html=True)

        col3.markdown(f"""
        <div class='card'>
        <h4>Total ICMS</h4>
        <h2>R$ {resultado['Total ICMS']}</h2>
        </div>
        """, unsafe_allow_html=True)

        # Detalhes
        st.markdown("<div class='result-box'>", unsafe_allow_html=True)

        st.subheader("📈 Detalhamento")

        for k, v in resultado.items():
            st.write(f"**{k}:** {v}")

        st.markdown("</div>", unsafe_allow_html=True)

        # Exportação
        excel = gerar_excel(resultado, dados)

        st.download_button(
            "📥 Baixar Excel",
            excel,
            "simulacao_difal.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
