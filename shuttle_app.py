import streamlit as st
import pandas as pd
from shuttle_engine import *

st.set_page_config(layout="wide")
st.title("🚛 Shuttle Planning Engine")

# Inicializa estados da sessão
if "dataverse" not in st.session_state:
    st.session_state.dataverse = None
if "inbound" not in st.session_state:
    st.session_state.inbound = None
if "compounds" not in st.session_state:
    st.session_state.compounds = get_compounds()

# Uploads (só guardam se ficheiros forem fornecidos)
col1, col2 = st.columns(2)
dataverse_file = col1.file_uploader("Upload Dataverse", type="xlsx", key="dv")
inbound_file = col2.file_uploader("Upload Car Inbound", type="xlsx", key="ib")

if dataverse_file is not None:
    st.session_state.dataverse = pd.read_excel(dataverse_file)
if inbound_file is not None:
    st.session_state.inbound = pd.read_excel(inbound_file)

st.divider()

# Configuração das campas (editável)
st.header("Compound Configuration")
compounds_edit = st.data_editor(
    st.session_state.compounds,
    num_rows="dynamic",
    use_container_width=True,
    key="comp_editor"
)
st.session_state.compounds = compounds_edit

# Slider de peso do balanceamento logístico
st.subheader("Balanceamento por Transportista")
logistic_weight = st.slider(
    "Peso do balanceamento logístico (0 = sem influência, 1 = máxima)",
    min_value=0.0, max_value=1.0, value=0.5, step=0.05,
    help="Ajusta o equilíbrio entre carga dos parques e distribuição pelas transportadoras."
)

# Botões de ação
col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    if st.button("🔄 RUN SHUTTLE ENGINE"):
        if st.session_state.dataverse is None or st.session_state.inbound is None:
            st.warning("Faz upload dos dois ficheiros primeiro.")
        else:
            with st.spinner("A correr o motor..."):
                plan, status, stock = run_engine(
                    st.session_state.dataverse,
                    st.session_state.inbound,
                    st.session_state.compounds,
                    logistic_weight=logistic_weight
                )
                st.session_state.plan = plan
                st.session_state.status = status
                st.session_state.stock = stock
                st.success("Planeamento concluído!")

    if st.button("📂 RECALCULAR (usar ficheiros já carregados)"):
        if st.session_state.dataverse is None or st.session_state.inbound is None:
            st.warning("Faz upload dos ficheiros primeiro.")
        else:
            with st.spinner("A recalcular..."):
                plan, status, stock = run_engine(
                    st.session_state.dataverse,
                    st.session_state.inbound,
                    st.session_state.compounds,
                    logistic_weight=logistic_weight
                )
                st.session_state.plan = plan
                st.session_state.status = status
                st.session_state.stock = stock
                st.success("Recálculo concluído!")

# Mostra resultados se existirem
if "plan" in st.session_state:
    st.header("Compound Status")
    st.dataframe(st.session_state.status, use_container_width=True)

    st.header("Current Stock by Model")
    st.dataframe(st.session_state.stock, use_container_width=True)

    st.header("Shuttle Plan")
    st.dataframe(st.session_state.plan, use_container_width=True)

    st.download_button(
        "📥 Download Shuttle Plan",
        st.session_state.plan.to_csv(index=False),
        "shuttle_plan.csv"
    )