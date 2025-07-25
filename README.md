# 🏙️ Portal da Segurança

Sistema desenvolvido como parte do projeto da disciplina de Projeto e Implementação de Banco de Dados. O **Portal da Segurança** tem como objetivo simular o funcionamento de um sistema de segurança pública com funcionalidades como cadastro de ocorrências, consultas por status ou localização, uso de triggers, procedures, funções SQL e integração com banco de dados remoto.

---

## 🚀 Acesse a aplicação online

🔗 [Clique aqui para acessar o Portal da Segurança no Streamlit](https://app-seguranca.streamlit.app/)

---

## 🛠️ Funcionalidades principais

- Cadastro de ocorrências com dados como tipo, status e endereço
- Consulta de ocorrências por status
- Consulta detalhada com cruzamento de ocorrências, endereços e câmeras
- Inserção com **trigger automática** de status
- Consulta com função SQL para total de ocorrências por endereço
- Conexão com banco de dados **remoto (Neon PostgreSQL)**

---

## 🧠 Tecnologias utilizadas

- [Python](https://www.python.org/)
- [Streamlit](https://streamlit.io/) – para a interface web
- [Pandas](https://pandas.pydata.org/) – para manipulação e exibição de dados
- [PostgreSQL](https://www.postgresql.org/) – banco de dados relacional
- [Neon](https://neon.tech/) – hospedagem gratuita de banco de dados PostgreSQL na nuvem

---

## 📁 Como rodar o projeto localmente

1. Clone o repositório:

```bash
git clone https://github.com/BrunaMatias/Portal-da-seguranca.git
cd Portal-da-seguranca
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Configure o banco de dados:

- Crie um arquivo `.env` na raiz do projeto com os dados do banco:

```bash
DB_HOST=seu_host
DB_NAME=seu_banco
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_PORT=5432
```

*(Use como base o arquivo `.env.example` incluído no projeto)*

4. Execute o aplicativo:

```bash
streamlit run app.py
```

---

## 👩‍💻 Contribuidores

- Bruna Matias – Página de Ocorrências
- Julia Gaziero - Página de Infratores
- Larissa Dias - Página de Viaturas

---
