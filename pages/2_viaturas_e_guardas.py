import streamlit as st
import pandas as pd
from db_config import get_connection
import datetime 


st.set_page_config(page_title="Controle de Viaturas e Policiais", layout="centered")

st.title("🚓 Sistema de Controle de Viaturas e Policiais")
st.markdown("""
Nesta seção, você pode gerenciar viaturas e policiais, registrar novos membros e delegacias, e consultar informações sobre o corpo de segurança da cidade inteligente.
""")

abas = st.tabs([
    "1️⃣ Cadastrar Policial/Guarda",
    "2️⃣ Cadastrar Viatura/Delegacia",
    "3️⃣ Consultar Policiais",
    "4️⃣ Consulta Avançada",
    "5️⃣ Trigger"
])

# 1. Cadastrar Policial/Guarda
with abas[0]:
    st.subheader("📥 Cadastrar Novo Membro (Policial ou Guarda)")
    st.caption("Esta funcionalidade permite o cadastro de novos cidadãos como policiais ou guardas, associando-os aos seus dados básicos e específicos de cargo.")

    tipo_membro = st.radio("Tipo de Membro", ["Policial", "Guarda"], key="tipo_membro_cadastro")

    with st.form("form_cadastrar_membro"):
        st.markdown("##### Dados do Cidadão")
        cpf = st.text_input("CPF (identificação única)")
        nome = st.text_input("Nome")
        telefone = st.text_input("Telefone")
        
        # Definindo datas mínima e máxima para o date_input
        min_date = datetime.date(1900, 1, 1) # Data mínima bem antiga
        max_date = datetime.date.today()     # Data atual

        # CORREÇÃO: data_nascimento com min_value e max_value, com indentação correta
        data_nascimento = st.date_input(
            "Data de Nascimento",
            min_value=min_date,
            max_value=max_date
        )
        sexo = st.selectbox("Sexo", ["M", "F", "Outro"])
        id_endereco = st.text_input("ID do Endereço")

        st.markdown("##### Dados Específicos do Membro")
        cargo = st.text_input("Cargo")
        especialidade = st.text_input("Especialidade")

        if tipo_membro == "Policial":
            delegacia_policial = st.text_input("ID da Delegacia (para Policial)")
        else:
            delegacia_policial = None

        submitted = st.form_submit_button("Cadastrar Membro")

    if submitted:
        try:
            conn = get_connection()
            cur = conn.cursor()

            # Inserir na tabela cidadao
            cur.execute("""
                INSERT INTO cidadao (cpf, nome, telefone, datanascimento, sexo, idendereco)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (cpf, nome, telefone, data_nascimento.strftime('%Y-%m-%d'), sexo, id_endereco))

            if tipo_membro == "Policial":
                cur.execute("""
                    INSERT INTO policial (idpolicial, delegacia, cargo, especialidade)
                    VALUES (?, ?, ?, ?)
                """, (cpf, delegacia_policial, cargo, especialidade))
            else: # Guarda
                cur.execute("""
                    INSERT INTO guarda (idguarda, cargo, especialidade)
                    VALUES (?, ?, ?)
                """, (cpf, cargo, especialidade))

            conn.commit()
            cur.close()
            conn.close()
            st.success(f"✅ {tipo_membro} cadastrado(a) com sucesso!")
        except Exception as e:
            st.error(f"❌ Erro ao cadastrar {tipo_membro}: {e}")

# 2. Cadastrar Viatura/Delegacia
with abas[1]:
    st.subheader("📥 Cadastrar Viatura ou Delegacia")
    st.caption("Esta funcionalidade permite registrar novas viaturas e delegacias no sistema.")

    tipo_cadastro = st.radio("O que você deseja cadastrar?", ["Viatura", "Delegacia"], key="tipo_cadastro_vd")

    if tipo_cadastro == "Delegacia":
        with st.form("form_cadastrar_delegacia"):
            id_delegacia = st.text_input("ID da Delegacia")
            id_endereco_delegacia = st.text_input("ID do Endereço da Delegacia")
            submit_delegacia = st.form_submit_button("Cadastrar Delegacia")

        if submit_delegacia:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("INSERT INTO delegacia (iddelegacia, idendereco) VALUES (?, ?)",
                                (id_delegacia, id_endereco_delegacia))
                conn.commit()
                cur.close()
                conn.close()
                st.success("✅ Delegacia cadastrada com sucesso!")
            except Exception as e:
                st.error(f"❌ Erro ao cadastrar delegacia: {e}")
    else: # Viatura
        with st.form("form_cadastrar_viatura"):
            id_viatura = st.text_input("ID da Viatura")
            id_delegacia_viatura = st.text_input("ID da Delegacia (Viatura)")
            placa_viatura = st.text_input("Placa")
            modelo_viatura = st.text_input("Modelo")
            submit_viatura = st.form_submit_button("Cadastrar Viatura")

        if submit_viatura:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("INSERT INTO viatura (idviatura, iddelegacia, placa, modelo) VALUES (?, ?, ?, ?)",
                                (id_viatura, id_delegacia_viatura, placa_viatura, modelo_viatura))
                conn.commit()
                cur.close()
                conn.close()
                st.success("✅ Viatura cadastrada com sucesso!")
            except Exception as e:
                st.error(f"❌ Erro ao cadastrar viatura: {e}")

# 3. Consulta de Policiais por Cargo e Especialidade (Consulta com 3 entidades e 2 relacionamentos)
with abas[2]:
    st.subheader("🔎 Consultar Policiais por Cargo e Especialidade")
    st.caption("Exibe informações de policiais, incluindo seus dados de cidadão, cargo e especialidade, e o nome da delegacia a que pertencem, se aplicável.")

    if st.button("Buscar Policiais"):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT
                    c.nome AS NomePolicial,
                    p.cargo AS CargoPolicial,
                    p.especialidade AS EspecialidadePolicial,
                    d.iddelegacia AS Delegacia,
                    e.rua || ', ' || e.numero || ' - ' || e.bairro || ', ' || e.cidade AS EnderecoDelegacia
                FROM
                    policial p
                JOIN
                    cidadao c ON p.idpolicial = c.cpf
                LEFT JOIN
                    delegacia d ON p.delegacia = d.iddelegacia
                LEFT JOIN
                    endereco e ON d.idendereco = e.idendereco;
            """)
            resultados = cur.fetchall()
            cur.close()
            conn.close()

            if resultados:
                df = pd.DataFrame(resultados, columns=[
                    "Nome do Policial", "Cargo", "Especialidade", "ID Delegacia", "Endereço da Delegacia"
                ])
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("Nenhum policial encontrado.")
        except Exception as e:
            st.error(f"Erro ao buscar policiais: {e}")

# 4. Consulta Avançada: Viaturas por Delegacia e Endereço (Exemplo de consulta SQL do PDF)
with abas[3]:
    st.subheader("📡 Viaturas por Delegacia e Endereço")
    st.caption("Esta consulta combina dados de `Viatura`, `Delegacia` e `Endereco` para exibir as viaturas e os detalhes de localização de suas respectivas delegacias. (Similar ao exemplo do PDF de consulta com 3 entidades e 2 relacionamentos).")

    if st.button("Executar Consulta de Viaturas"):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT
                    v.idviatura,
                    v.placa,
                    v.modelo,
                    d.iddelegacia AS IDDelegacia,
                    e.rua,
                    e.bairro,
                    e.cidade
                FROM
                    viatura v
                JOIN
                    delegacia d ON v.iddelegacia = d.iddelegacia
                JOIN
                    endereco e ON d.idendereco = e.idendereco
                ORDER BY
                    d.iddelegacia, v.idviatura;
            """)
            resultados = cur.fetchall()
            cur.close()
            conn.close()

            if resultados:
                df = pd.DataFrame(resultados, columns=[
                    "ID Viatura", "Placa", "Modelo", "ID Delegacia", "Rua", "Bairro", "Cidade"
                ])
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("Nenhuma viatura encontrada.")
        except Exception as e:
            st.error(f"Erro ao executar consulta de viaturas: {e}")

# 5. Trigger: Validação de Delegacia existente para Viatura
with abas[4]:
    st.subheader("🧨 Testar Trigger de Validação de Delegacia para Viatura")
    st.caption("Este teste demonstra o funcionamento do trigger `validar_delegacia_viatura`, que impede a inserção de uma viatura se o `iddelegacia` informado não existir na tabela `delegacia`.")

    with st.form("form_trigger_viatura"):
        id_viatura_trigger = st.text_input("ID da Viatura para Teste")
        id_delegacia_trigger = st.text_input("ID da Delegacia (existente ou não)")
        placa_trigger = st.text_input("Placa da Viatura")
        modelo_trigger = st.text_input("Modelo da Viatura")
        submit_trigger_viatura = st.form_submit_button("Inserir Viatura (Testar Trigger)")

    if submit_trigger_viatura:
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO viatura (idviatura, iddelegacia, placa, modelo)
                VALUES (?, ?, ?, ?)
            """, (id_viatura_trigger, id_delegacia_trigger, placa_trigger, modelo_trigger))
            conn.commit()
            cur.close()
            conn.close()
            st.success("✅ Viatura inserida com sucesso! (Se a delegacia existia)")
        except Exception as e:
            st.error(f"❌ Erro ao inserir viatura: {e} (Isso pode ser o trigger em ação!)")
