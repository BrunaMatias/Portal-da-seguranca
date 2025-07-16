import streamlit as st
import pandas as pd
from db_config import get_connection

st.set_page_config(page_title="Ocorrências - Bruna", layout="centered")

st.title("🚨 Página de Ocorrências")
st.markdown("""
Nesta seção do sistema, você pode registrar novas ocorrências e consultar registros já existentes na base de dados, com diferentes filtros.""")

# Estatísticas básicas no topo
try:
    conn = get_connection()
    cur = conn.cursor()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        cur.execute("SELECT COUNT(*) FROM Ocorrencia")
        total_ocorrencias = cur.fetchone()[0]
        st.metric("Ocorrências", total_ocorrencias)

    with col2:
        cur.execute("SELECT COUNT(*) FROM Endereco")
        total_enderecos = cur.fetchone()[0]
        st.metric("Endereços", total_enderecos)

    with col3:
        cur.execute("SELECT COUNT(*) FROM CameraOcorrencia")
        total_cameras = cur.fetchone()[0]
        st.metric("Câmeras", total_cameras)

    with col4:
        cur.execute("SELECT COUNT(DISTINCT tipo) FROM Ocorrencia")
        tipos_diferentes = cur.fetchone()[0]
        st.metric("Tipos de Ocorrência", tipos_diferentes)

    cur.close()
    conn.close()

except Exception as e:
    st.error(f"Erro ao carregar estatísticas: {e}")


aba = st.tabs([
    "1️⃣ Cadastrar Ocorrência",
    "2️⃣ Consultar por Status",
    "3️⃣ Consulta Avançada",
    "4️⃣ Trigger de Status",
    "5️⃣ Consulta por Endereço"
])

# 1. Cadastro de ocorrência
with aba[0]:
    st.subheader("📥 Cadastrar Nova Ocorrência")
    st.caption("Esta funcionalidade insere uma nova ocorrência na base de dados por meio da procedure `registrar_ocorrencia`, garantindo integridade e consistência dos dados.")

    with st.form("form_ocorrencia"):
        id_ocorrencia = st.text_input("ID da Ocorrência")
        tipo = st.selectbox("Tipo", ["Roubo", "Homicídio", "Furto", "Sequestro", "Tráfico", "Outros"])
        status = st.selectbox("Status", ["Em andamento", "Resolvido", "Em investigação"])
        id_endereco = st.text_input("ID do Endereço")

        submitted = st.form_submit_button("Cadastrar")

    if submitted:
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("CALL registrar_ocorrencia(%s, %s, %s, %s)", (id_ocorrencia, tipo, status, id_endereco))
            conn.commit()
            cur.close()
            conn.close()
            st.success("✅ Ocorrência registrada com sucesso!")
        except Exception as e:
            st.error(f"❌ Erro ao registrar ocorrência: {e}")

# 2. Consulta simples por status
with aba[1]:
    st.subheader("🔎 Consultar Ocorrências por Status")
    st.caption("Filtra as ocorrências cadastradas com base no status atual (em andamento, resolvido ou em investigação). Permite visualizar os dados em tempo real.")

    status_filtro = st.selectbox("Status", ["Em andamento", "Resolvido", "Em investigação", "Em Análise"])
    if st.button("Buscar"):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT idOcorrencia, tipo, status, idEndereco
                FROM Ocorrencia
                WHERE status = %s
            """, (status_filtro,))
            resultados = cur.fetchall()
            cur.close()
            conn.close()

            if resultados:
                df = pd.DataFrame(resultados, columns=["ID", "Tipo", "Status", "Endereço"])
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("Nenhuma ocorrência encontrada.")
        except Exception as e:
            st.error(f"Erro: {e}")

# 3. Consulta com 3 entidades + 2 relacionamentos
with aba[2]:
    st.subheader("📡 Ocorrências com Endereço e Câmeras")
    st.caption("Esta consulta combina dados de três entidades (`Ocorrencia`, `Endereco` e `CameraOcorrencia`) para exibir ocorrências com detalhes de localização e número de câmeras associadas.")

    if st.button("Executar Consulta"):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT o.idOcorrencia, o.tipo, o.status,
                       e.rua, e.bairro, e.cidade,
                       COUNT(co.idCamera) AS num_cameras
                FROM Ocorrencia o
                JOIN Endereco e ON o.idEndereco = e.idEndereco
                LEFT JOIN CameraOcorrencia co ON o.idOcorrencia = co.idOcorrencia
                GROUP BY o.idOcorrencia, o.tipo, o.status, e.rua, e.bairro, e.cidade
                ORDER BY o.idOcorrencia;
            """)
            resultados = cur.fetchall()
            cur.close()
            conn.close()

            if resultados:
                df = pd.DataFrame(resultados, columns=[
                    "ID", "Tipo", "Status", "Rua", "Bairro", "Cidade", "Câmeras Associadas"
                ])
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("Nenhuma ocorrência encontrada.")
        except Exception as e:
            st.error(f"Erro: {e}")

# 4. Trigger: Inserção sem status → “Em Análise”
with aba[3]:
    st.subheader("🧨 Testar Trigger de Status Automático")
    st.caption("Ao inserir uma ocorrência sem informar o status, o trigger `trg_status_padrao` entra em ação e define automaticamente o valor padrão `Em Análise`.")

    with st.form("form_trigger"):
        id_teste = st.text_input("ID da Ocorrência (Teste)")
        tipo_teste = st.text_input("Tipo")
        endereco_teste = st.text_input("ID do Endereço")
        submit_trigger = st.form_submit_button("Inserir sem Status")

    if submit_trigger:
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO Ocorrencia(idOcorrencia, tipo, idEndereco)
                VALUES (%s, %s, %s)
            """, (id_teste, tipo_teste, endereco_teste))
            conn.commit()
            cur.close()
            conn.close()
            st.success("✅ Ocorrência inserida sem status. Trigger ativada!")
        except Exception as e:
            st.error(f"Erro: {e}")

# 5. Function + Consulta: Total e Detalhes por Endereço
with aba[4]:
    st.markdown("### 📈 Ocorrências por Endereço")
    st.caption("Aqui você pode consultar quantas ocorrências foram registradas em um endereço específico por meio da função `total_ocorrencias_endereco`, além de visualizar os dados completos.")

    id_end_busca = st.text_input("🔎 Digite o ID do Endereço")

    col1, col2 = st.columns([1, 3])
    buscar_total = col1.button("Calcular Total")
    mostrar_detalhes = col2.checkbox("Mostrar ocorrências detalhadas")

    if buscar_total and id_end_busca.strip():
        try:
            conn = get_connection()
            cur = conn.cursor()

            # Function: Total de ocorrências no endereço
            cur.execute("SELECT total_ocorrencias_endereco(%s)", (id_end_busca,))
            total = cur.fetchone()[0]

            st.success(f"📍 Endereço {id_end_busca} possui **{total} ocorrência(s)** registrada(s).")

            if mostrar_detalhes and total > 0:
                cur.execute("""
                    SELECT idOcorrencia, tipo, status
                    FROM Ocorrencia
                    WHERE idEndereco = %s
                """, (id_end_busca,))
                dados = cur.fetchall()

                df = pd.DataFrame(dados, columns=["ID Ocorrência", "Tipo", "Status"])
                st.dataframe(df, use_container_width=True, height=300)

            cur.close()
            conn.close()

        except Exception as e:
            st.error(f"❌ Erro na consulta: {e}")

    elif buscar_total:
        st.warning("⚠️ Por favor, informe um ID de endereço válido.")
