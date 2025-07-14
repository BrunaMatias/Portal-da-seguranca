import streamlit as st
import pandas as pd
from db_config import get_connection

st.set_page_config(page_title="Infratores - Julia", layout="centered")

st.title("👥 Página de Infratores")
st.markdown("""
Nesta seção do sistema, você pode cadastrar novos infratores e consultar os infratores registrados com base na situação judicial de cada um.
""")

#abas da interface
aba = st.tabs([
    "1️⃣ Cadastrar Infrator",
    "2️⃣ Consultar por Situação Judicial",
    "3️⃣ Trigger de Situação Padrão"
])

#cadastro de um novo infrator
with aba[0]:
    st.subheader("📥 Cadastrar Novo Infrator")
    st.caption("Preencha os campos abaixo para registrar um novo infrator na base de dados.")

    with st.form("form_infrator"):
        cpf = st.text_input("CPF do Infrator")
        situacao_judicial = st.selectbox("Situação Judicial", ["Preso", "Solto", "Foragido", "Em julgamento"])
        organizacao = st.text_input("Organização Criminosa (opcional)")
        submitted = st.form_submit_button("Cadastrar")

    if submitted:
        try:
            conn = get_connection()
            cur = conn.cursor()

            #verifica se o cpf existe na tabela cidadao
            cur.execute("SELECT cpf FROM Cidadao WHERE cpf = %s", (cpf,))
            resultado = cur.fetchone()

            if resultado:
                cur.execute("""
                    INSERT INTO Infrator (idInfrator, situacaoJudicial, orgCriminosa)
                    VALUES (%s, %s, %s)
                """, (cpf, situacao_judicial, organizacao if organizacao else None))
                conn.commit()
                st.success("✅ Infrator cadastrado com sucesso!")
            else:
                st.warning("⚠️ O CPF informado não está cadastrado como cidadão. Cadastre primeiro em Cidadao.")

            cur.close()
            conn.close()

        except Exception as e:
            st.error(f"❌ Erro ao cadastrar infrator: {e}")

#consulta por situação judicial
with aba[1]:
    st.subheader("🔍 Consultar Infratores por Situação Judicial")
    st.caption("Filtra infratores com base em sua situação judicial atual.")

    filtro_situacao = st.selectbox("Situação Judicial", ["Preso", "Solto", "Foragido", "Em julgamento"])

    if st.button("Buscar"):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT idInfrator, situacaoJudicial, orgCriminosa
                FROM Infrator
                WHERE situacaoJudicial = %s
            """, (filtro_situacao,))
            resultados = cur.fetchall()
            cur.close()
            conn.close()

            if resultados:
                df = pd.DataFrame(resultados, columns=["CPF", "Situação Judicial", "Organização Criminosa"])
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("Nenhum infrator encontrado com essa situação.")
        except Exception as e:
            st.error(f"Erro na consulta: {e}")

#trigger de inserção sem situação judicial, define para a situação judicial padrão "em julgamento"
with aba[2]:
    st.subheader("🧨 Testar Trigger de Situação Judicial")
    st.caption("Ao inserir um infrator sem informar a situação judicial, a trigger `trg_situacao_padrao` define automaticamente o valor padrão `Em julgamento`.")

    with st.form("form_trigger_infrator"):
        cpf_trigger = st.text_input("CPF do Infrator (já cadastrado como Cidadão)")
        organizacao_trigger = st.text_input("Organização Criminosa (opcional)")
        submit_trigger = st.form_submit_button("Cadastrar sem Situação Judicial")

    if submit_trigger:
        try:
            conn = get_connection()
            cur = conn.cursor()

            #verifica se o cpf existe na tabela cidadao
            cur.execute("SELECT cpf FROM Cidadao WHERE cpf = %s", (cpf_trigger,))
            resultado = cur.fetchone()

            if resultado:
                cur.execute("""
                    INSERT INTO Infrator (idInfrator, situacaoJudicial, orgCriminosa)
                    VALUES (%s, NULL, %s)
                """, (cpf_trigger, organizacao_trigger if organizacao_trigger else None))
                conn.commit()
                st.success("✅ Infrator cadastrado sem situação judicial. Trigger ativada!")
            else:
                st.warning("⚠️ O CPF informado não está cadastrado como cidadão.")

            cur.close()
            conn.close()

        except Exception as e:
            st.error(f"Erro: {e}")