import streamlit as st
import pandas as pd
from db_config import get_connection
import datetime

st.set_page_config(page_title="Cadastro e Consulta de Infratores", layout="centered")

st.title("👥 Página de Cadastro e Consulta de Infratores")
st.markdown("""
Sistema que permite o cadastro de infratores e a consulta por situação judicial, com suporte a trigger de valor padrão.
""")

#estatísticas de infratores
try:
    conn = get_connection()
    cur = conn.cursor()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        cur.execute("SELECT COUNT(*) FROM Infrator WHERE situacaoJudicial = 'Preso'")
        presos = cur.fetchone()[0]
        st.metric("Presos", presos)

    with col2:
        cur.execute("SELECT COUNT(*) FROM Infrator WHERE situacaoJudicial = 'Solto'")
        soltos = cur.fetchone()[0]
        st.metric("Soltos", soltos)

    with col3:
        cur.execute("SELECT COUNT(*) FROM Infrator WHERE situacaoJudicial = 'Foragido'")
        foragidos = cur.fetchone()[0]
        st.metric("Foragidos", foragidos)

    with col4:
        cur.execute("SELECT COUNT(*) FROM Infrator WHERE situacaoJudicial = 'Em julgamento'")
        em_julgamento = cur.fetchone()[0]
        st.metric("Em Julgamento", em_julgamento)

    cur.close()
    conn.close()

except Exception as e:
    st.error(f"Erro ao carregar estatísticas de infratores: {e}")

#abas
aba1, aba2, aba3, aba4 = st.tabs([
    "1️⃣ Cadastrar Infrator",
    "2️⃣ Consultar por Situação Judicial",
    "3️⃣ Trigger de Situação Padrão",
    "🧑	Cadastrar Cidadão"
])

#aba 1 - cadastro de infrator
with aba1:
    st.subheader("📥 Cadastrar Novo Infrator")
    st.caption("Preencha os dados abaixo para cadastrar um novo infrator.")

    with st.form("form_infrator"):
        cpf = st.text_input("CPF do Infrator", placeholder="12345678901")
        situacao_judicial = st.selectbox("Situação Judicial", ["Preso", "Solto", "Foragido", "Em julgamento"])
        organizacao = st.text_input("Organização Criminosa (opcional)")
        submitted = st.form_submit_button("Cadastrar", type="primary")

    if submitted:
        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("SELECT cpf FROM Cidadao WHERE cpf = %s", (cpf,))
            if cur.fetchone():
                cur.execute("SELECT idInfrator FROM Infrator WHERE idInfrator = %s", (cpf,))
                if cur.fetchone():
                    st.warning("⚠️ Este CPF já está cadastrado como Infrator.")
                else:
                    cur.execute("""
                        INSERT INTO Infrator (idInfrator, situacaoJudicial, orgCriminosa)
                        VALUES (%s, %s, %s)
                    """, (cpf, situacao_judicial, organizacao or None))
                    conn.commit()
                    st.success("✅ Infrator cadastrado com sucesso!")
            else:
                st.warning("⚠️ Este CPF ainda não está registrado como cidadão. Cadastre primeiro a pessoa na aba 'Cadastrar Cidadão'.")

            cur.close()
            conn.close()

        except Exception as e:
            st.error(f"❌ Erro ao cadastrar infrator: {e}")

#aba 2 - consulta de infratores por situação judicial
with aba2:
    st.subheader("🔍 Consultar Infratores por Situação Judicial")
    st.caption("Selecione a situação judicial para listar os infratores correspondentes.")

    filtro = st.selectbox("Situação Judicial", ["Preso", "Solto", "Foragido", "Em julgamento"])
    if st.button("Buscar Infratores", type="primary"):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT idInfrator, situacaoJudicial, orgCriminosa
                FROM Infrator
                WHERE situacaoJudicial = %s
            """, (filtro,))
            dados = cur.fetchall()
            cur.close()
            conn.close()

            if dados:
                df = pd.DataFrame(dados, columns=["CPF", "Situação Judicial", "Organização Criminosa"])
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("Nenhum infrator encontrado com essa situação.")
        except Exception as e:
            st.error(f"Erro na consulta: {e}")

#aba 3 - trigger
with aba3:
    st.subheader("Testar Trigger de Situação Judicial Padrão")
    st.caption("Insira um infrator sem informar a situação judicial para que a aplicação defina automaticamente 'Em julgamento'.")

    with st.form("form_trigger"):
        cpf_trigger = st.text_input("CPF do Infrator", placeholder="12345678901")
        org_trigger = st.text_input("Organização Criminosa (opcional)")
        trigger_submit = st.form_submit_button("Cadastrar sem Situação Judicial", type="primary")

    if trigger_submit:
        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("SELECT cpf FROM Cidadao WHERE cpf = %s", (cpf_trigger,))
            if cur.fetchone():
                cur.execute("SELECT idInfrator FROM Infrator WHERE idInfrator = %s", (cpf_trigger,))
                if cur.fetchone():
                    st.warning("⚠️ Este CPF já está cadastrado como Infrator.")
                else:
                    situacao_padrao = "Em julgamento"
                    cur.execute("""
                        INSERT INTO Infrator (idInfrator, situacaoJudicial, orgCriminosa)
                        VALUES (%s, %s, %s)
                    """, (cpf_trigger, situacao_padrao, org_trigger or None))
                    conn.commit()
                    st.success("✅ Infrator inserido com situação judicial padrão: 'Em julgamento'!")
            else:
                st.warning("⚠️ Este CPF ainda não está registrado como cidadão. Cadastre primeiro na aba 'Cadastrar Cidadão'.")

            cur.close()
            conn.close()
        except Exception as e:
            st.error(f"Erro: {e}")

#aba 4 - cadastro de cidadão
with aba4:
    st.subheader("Cadastrar Cidadão")
    st.caption("Preencha os dados básicos de um cidadão.")

    with st.form("form_cidadao"):
        col1, col2 = st.columns(2)

        with col1:
            cpf_cidadao = st.text_input("CPF", placeholder="12345678901")
            nome_cidadao = st.text_input("Nome Completo")
            telefone = st.text_input("Telefone", placeholder="(16)99999-9999")
            data_nascimento = st.date_input("Data de Nascimento", min_value=datetime.date(1900, 1, 1), max_value=datetime.date.today())
            sexo = st.selectbox("Sexo", ["M", "F", "Outro"])

        with col2:
            id_endereco = st.text_input("ID do Endereço")
            rua = st.text_input("Rua")
            numero = st.text_input("Número")
            bairro = st.text_input("Bairro")
            cidade = st.text_input("Cidade")

        submit_cidadao = st.form_submit_button("Cadastrar Cidadão", type="primary")

    if submit_cidadao:
        if not cpf_cidadao or not nome_cidadao:
            st.error("⚠️ CPF e Nome são obrigatórios.")
        else:
            try:
                conn = get_connection()
                cur = conn.cursor()

                # Inserir endereço
                cur.execute("""
                    INSERT INTO Endereco (idEndereco, rua, numero, bairro, cidade)
                    VALUES (%s, %s, %s, %s, %s)
                """, (id_endereco, rua, numero, bairro, cidade))

                # Inserir cidadão
                cur.execute("""
                    INSERT INTO Cidadao (cpf, nome, telefone, datanascimento, sexo, idEndereco)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (cpf_cidadao, nome_cidadao, telefone, data_nascimento.strftime('%Y-%m-%d'), sexo, id_endereco))

                conn.commit()
                cur.close()
                conn.close()
                st.success("✅ Cidadão cadastrado com sucesso!")
            except Exception as e:
                st.error(f"❌ Erro ao cadastrar cidadão: {e}")