import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dao.db_config import DatabaseConfig

if DatabaseConfig.get_connection():
    print("Conexão estabelecida com sucesso")
else:
    print("Erro ao conectar a base de dados")