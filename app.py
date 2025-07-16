import streamlit as st
from PIL import Image

st.set_page_config(page_title="Portal da Segurança", layout="wide")

st.title("🏙️ Portal da Segurança - Sistema de Gestão de Cidade Inteligente")
st.markdown("### 👋 Bem-vindo(a) ao nosso projeto!")

st.markdown("#### Objetivo do Sistema")
st.write("""
O **Portal da Segurança** é um subsistema voltado à gestão de segurança pública municipal. Ele foi desenvolvido com o objetivo de integrar dados de ocorrências, infratores, policiais, guardas, cidadãos e câmeras de vigilância, delegacias e viaturas, promovendo mais eficiência nas ações de patrulhamento, prevenção e análise de criminalidade.
""")

with st.expander("🔧 Funcionalidades principais", expanded=True):
    st.markdown("""
- Cadastro e consulta de **ocorrências policiais**
- Registro e monitoramento de **infratores**
- Gerenciamento de **câmeras de vigilância**
- Controle e distribuição de **viaturas e guardas**
- Geração de **relatórios estatísticos por região**
    """)

st.markdown("#### 🧩 Modelagem de Dados")

col1, col2 = st.columns(2)

with col1:
    st.image(Image.open("der.png"), caption="Diagrama Entidade-Relacionamento (DER)", use_container_width=True)

with col2:
    st.image(Image.open("relacional.png"), caption="Esquema relacional", use_container_width=True)


st.markdown("#### 📁 Organização das Páginas do Sistema")
st.markdown("""

- 🚨 **Cadastro e consulta de ocorrências**
- 🎥 **Julia**
- 📊 **Controle de viaturas e policiais**

Use o menu lateral à esquerda para navegar entre as páginas.
""")


st.markdown("---")
st.caption("Projeto e Implementaçãos de Banco de Dados - UFSCar • Grupo 15 • 2025")
