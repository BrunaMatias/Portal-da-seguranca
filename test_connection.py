from db_config import get_connection

try:
    conn = get_connection()
    print("✅ Conexão com o banco de dados foi bem-sucedida!")
    conn.close()
except Exception as e:
    print("❌ Erro ao conectar:", e)
