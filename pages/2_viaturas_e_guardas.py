import streamlit as st
import pandas as pd
from db_config import get_connection, init_database
import datetime

# Inicializar banco de dados
init_database()

st.set_page_config(page_title="Controle de Viaturas e Policiais", layout="wide")

st.title("🚓 Sistema de Controle de Viaturas e Policiais")
st.markdown("""
Sistema para gerenciar viaturas, policiais e delegacias da cidade inteligente.
""")

# Estatísticas básicas no topo
try:
    conn = get_connection()
    cur = conn.cursor()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        cur.execute("SELECT COUNT(*) FROM cidadao")
        total_cidadaos = cur.fetchone()[0]
        st.metric("Total de Cidadãos", total_cidadaos)
    
    with col2:
        cur.execute("SELECT COUNT(*) FROM policial")
        total_policiais = cur.fetchone()[0]
        st.metric("Total de Policiais", total_policiais)
    
    with col3:
        cur.execute("SELECT COUNT(*) FROM viatura")
        total_viaturas = cur.fetchone()[0]
        st.metric("Total de Viaturas", total_viaturas)
    
    with col4:
        cur.execute("SELECT COUNT(*) FROM delegacia")
        total_delegacias = cur.fetchone()[0]
        st.metric("Total de Delegacias", total_delegacias)
    
    cur.close()
    conn.close()
    
except Exception as e:
    st.error(f"Erro ao carregar estatísticas: {e}")

st.divider()

# Sistema de abas
abas = st.tabs([
    "👮 Cadastrar Policial/Guarda",
    "🚓 Cadastrar Viatura/Delegacia", 
    "📊 Consultar Policiais",
    "🔍 Consulta Avançada",
    "⚡ Testar Trigger"
])

# Aba 1: Cadastrar Policial/Guarda
with abas[0]:
    st.subheader("📥 Cadastrar Novo Membro (Policial ou Guarda)")
    st.caption("Esta funcionalidade permite o cadastro de novos cidadãos como policiais ou guardas.")
    
    tipo_membro = st.radio("Tipo de Membro:", ["Policial", "Guarda"], key="tipo_membro_cadastro")
    
    with st.form("form_cadastrar_membro"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### Dados de Cidadão")
            cpf = st.text_input("CPF", placeholder="12345678901")
            nome = st.text_input("Nome Completo")
            telefone = st.text_input("Telefone", placeholder="(16)99999-9999")
            data_nascimento = st.date_input(
                "Data de Nascimento",
                min_value=datetime.date(1900, 1, 1),
                max_value=datetime.date.today()
            )
            sexo = st.selectbox("Sexo", ["M", "F", "Outro"])
            id_endereco = st.text_input("ID do Endereço", placeholder="end001")
            rua = st.text_input("Rua", placeholder="Rua das Flores")
            numero = st.text_input("Número", placeholder="123")
            bairro = st.text_input("Bairro", placeholder="Centro")
            cidade = st.text_input("Cidade", placeholder="São Carlos")
        
        with col2:
            st.markdown("##### Dados de Membro")
            cargo = st.text_input("Cargo")
            especialidade = st.text_input("Especialidade")
            
            if tipo_membro == "Policial":
                # Buscar delegacias disponíveis
                try:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("SELECT iddelegacia FROM delegacia ORDER BY iddelegacia")
                    delegacias = [row[0] for row in cur.fetchall()]
                    cur.close()
                    conn.close()
                    
                    if delegacias:
                        delegacia_policial = st.selectbox("Delegacia", delegacias)
                    else:
                        st.warning("Nenhuma delegacia encontrada!")
                        delegacia_policial = st.text_input("ID da Delegacia")
                except:
                    delegacia_policial = st.text_input("ID da Delegacia")
            else:
                delegacia_policial = None
        
        submitted = st.form_submit_button("Cadastrar Membro", type="primary")
    
    if submitted:
        if not cpf or not nome:
            st.error("CPF e Nome são obrigatórios!")
        else:
            try:
                conn = get_connection()
                cur = conn.cursor()
                
                #inserir endereço
                cur.execute("""
                    INSERT INTO endereco (idendereco, rua, bairro, numero, cidade)
                    VALUES (%s, %s, %s, %s, %s)
                """, (id_endereco, rua, bairro, numero, cidade))
                
                # Inserir cidadão
                cur.execute("""
                    INSERT INTO cidadao (cpf, nome, telefone, datanascimento, sexo, idendereco)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (cpf, nome, telefone, data_nascimento.strftime('%Y-%m-%d'), sexo, id_endereco))
                
                # Inserir membro específico
                if tipo_membro == "Policial":
                    cur.execute("""
                        INSERT INTO policial (idpolicial, delegacia, cargo, especialidade)
                        VALUES (%s, %s, %s, %s)
                    """, (cpf, delegacia_policial, cargo, especialidade))
                else:
                    cur.execute("""
                        INSERT INTO guarda (idguarda, cargo, especialidade)
                        VALUES (%s, %s, %s)
                    """, (cpf, cargo, especialidade))
                
                conn.commit()
                cur.close()
                conn.close()
                st.success(f"✅ {tipo_membro} cadastrado(a) com sucesso!")
                
            except Exception as e:
                st.error(f"❌ Erro ao cadastrar {tipo_membro}: {e}")

# Aba 2: Cadastrar Viatura/Delegacia
with abas[1]:
    st.subheader("📥 Cadastrar Viatura ou Delegacia")
    st.caption("Esta funcionalidade permite registrar novas viaturas e delegacias no sistema.")
    
    tipo_cadastro = st.radio("O que deseja cadastrar?", ["Delegacia", "Viatura"], key="tipo_cadastro_vd")
    
    if tipo_cadastro == "Delegacia":
        with st.form("form_cadastrar_delegacia"):
            st.markdown("##### Dados da Delegacia")
            id_delegacia = st.text_input("ID da Delegacia", placeholder="del003")
            
            st.markdown("##### Dados do Endereço")
            col1, col2 = st.columns(2)
            
            with col1:
                id_endereco_delegacia = st.text_input("ID do Endereço", placeholder="end003")
                rua = st.text_input("Rua", placeholder="Rua das Flores")
                numero = st.text_input("Número", placeholder="123")
            
            with col2:
                bairro = st.text_input("Bairro", placeholder="Centro")
                cidade = st.text_input("Cidade", placeholder="São Carlos")
            
            submit_delegacia = st.form_submit_button("Cadastrar Delegacia", type="primary")
        
        if submit_delegacia:
            if not id_delegacia or not id_endereco_delegacia or not rua or not cidade:
                st.error("ID da Delegacia, ID do Endereço, Rua e Cidade são obrigatórios!")
            else:
                try:
                    conn = get_connection()
                    cur = conn.cursor()
                    
                    # Primeiro, inserir o endereço
                    cur.execute("""
                        INSERT INTO endereco (idendereco, rua, numero, bairro, cidade)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (id_endereco_delegacia, rua, numero, bairro, cidade))
                    
                    # Depois, inserir a delegacia
                    cur.execute("""
                        INSERT INTO delegacia (iddelegacia, idendereco)
                        VALUES (%s, %s)
                    """, (id_delegacia, id_endereco_delegacia))
                    
                    conn.commit()
                    cur.close()
                    conn.close()
                    st.success("✅ Delegacia e endereço cadastrados com sucesso!")
                    
                except Exception as e:
                    st.error(f"❌ Erro ao cadastrar delegacia: {e}")
    
    else:  # Viatura
        with st.form("form_cadastrar_viatura"):
            col1, col2 = st.columns(2)
            
            with col1:
                id_viatura = st.text_input("ID da Viatura", placeholder="vtr003")
                placa_viatura = st.text_input("Placa", placeholder="ABC-1234")
                modelo_viatura = st.text_input("Modelo", placeholder="Ford Ranger")
            
            with col2:
                # Buscar delegacias disponíveis
                try:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("SELECT iddelegacia FROM delegacia ORDER BY iddelegacia")
                    delegacias = [row[0] for row in cur.fetchall()]
                    cur.close()
                    conn.close()
                    
                    if delegacias:
                        id_delegacia_viatura = st.selectbox("Delegacia", delegacias)
                    else:
                        st.warning("Nenhuma delegacia encontrada!")
                        id_delegacia_viatura = st.text_input("ID da Delegacia")
                except:
                    id_delegacia_viatura = st.text_input("ID da Delegacia")
            
            submit_viatura = st.form_submit_button("Cadastrar Viatura", type="primary")
        
        if submit_viatura:
            if not id_viatura or not placa_viatura:
                st.error("ID da Viatura e Placa são obrigatórios!")
            else:
                try:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("""
                        INSERT INTO viatura (idviatura, iddelegacia, placa, modelo) 
                        VALUES (%s, %s, %s, %s)
                    """, (id_viatura, id_delegacia_viatura, placa_viatura, modelo_viatura))
                    conn.commit()
                    cur.close()
                    conn.close()
                    st.success("✅ Viatura cadastrada com sucesso!")
                except Exception as e:
                    st.error(f"❌ Erro ao cadastrar viatura: {e}")

# Aba 3: Consultar Policiais
with abas[2]:
    st.subheader("🔎 Consultar Policiais por Cargo e Especialidade")
    st.caption("Exibe informações de policiais, incluindo seus dados de cidadão, cargo e especialidade, e o nome da delegacia.")
    
    if st.button("Buscar Todos os Policiais", type="primary"):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT
                    c.nome AS NomePolicial,
                    p.cargo AS CargoPolicial,
                    p.especialidade AS EspecialidadePolicial,
                    COALESCE(d.iddelegacia, 'Não informado') AS Delegacia,
                    COALESCE(e.rua || ', ' || e.numero || ' - ' || e.bairro || ', ' || e.cidade, 'Endereço não informado') AS EnderecoDelegacia
                FROM
                    policial p
                JOIN
                    cidadao c ON p.idpolicial = c.cpf
                LEFT JOIN
                    delegacia d ON p.delegacia = d.iddelegacia
                LEFT JOIN
                    endereco e ON d.idendereco = e.idendereco
                ORDER BY c.nome;
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

# Aba 4: Consulta Avançada
with abas[3]:
    st.subheader("📡 Viaturas por Delegacia e Endereço")
    st.caption("Esta consulta combina dados de Viatura, Delegacia e Endereco para exibir as viaturas e os detalhes de localização.")
    
    if st.button("Executar Consulta Avançada", type="primary"):
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
            st.error(f"Erro ao executar consulta: {e}")

# Aba 5: Testar Trigger
with abas[4]:
    st.subheader("🧨 Testar Trigger de Validação de Delegacia para Viatura")
    st.caption("Este teste demonstra o funcionamento do trigger 'validar_delegacia_viatura_func' que impede a inserção de uma viatura se o ID da delegacia não existir.")
    
    with st.form("form_trigger_viatura"):
        col1, col2 = st.columns(2)
        
        with col1:
            id_viatura_trigger = st.text_input("ID da Viatura para Teste", placeholder="vtr_teste")
            placa_trigger = st.text_input("Placa da Viatura", placeholder="TST-0000")
        
        with col2:
            id_delegacia_trigger = st.text_input("ID da Delegacia (existente ou não)", placeholder="del_inexistente")
            modelo_trigger = st.text_input("Modelo da Viatura", placeholder="Modelo Teste")
        
        submit_trigger = st.form_submit_button("Inserir Viatura (Testar Trigger)", type="primary")
    
    if submit_trigger:
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO viatura (idviatura, iddelegacia, placa, modelo)
                VALUES (%s, %s, %s, %s)
            """, (id_viatura_trigger, id_delegacia_trigger, placa_trigger, modelo_trigger))
            conn.commit()
            cur.close()
            conn.close()
            st.success("✅ Viatura inserida com sucesso! (A delegacia existia)")
        except Exception as e:
            st.error(f"❌ Erro ao inserir viatura: {e} (Isso pode ser o trigger em ação!)")