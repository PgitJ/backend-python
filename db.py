# db.py

import os
import psycopg2
from urllib.parse import urlparse
from psycopg2 import sql

# Render deve ter a DATABASE_URL configurada
DATABASE_URL = 'postgres://avnadmin:AVNS_V4Z3ZVHqjnAtFb0n2sF@pg-2c1e95e3-pietrojordan1310-50c6.d.aivencloud.com:18780/defaultdb?sslmode=require'

def get_connection():
    if not DATABASE_URL:
        raise Exception("DATABASE_URL não configurada no ambiente do Render.")

    try:
        # A biblioteca psycopg2 se conecta diretamente via URI
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao PostgreSQL: {e}")
        raise

def query(text, params=None, fetch_all=True):
    """Executa uma consulta SQL e retorna os resultados como lista de dicionários."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(text, params)
        
        # Se for um SELECT, busca os resultados e converte para JSON-friendly
        if text.strip().upper().startswith('SELECT') and fetch_all:
            result = cur.fetchall()
            col_names = [desc[0] for desc in cur.description]
            data = [dict(zip(col_names, row)) for row in result]
            return data
        else:
            # Para INSERT, UPDATE, DELETE e CREATE
            conn.commit()
            return None 
            
    except Exception as e:
        if conn:
            conn.rollback()
        # Captura e relança exceções SQL (ex: chave duplicada, erro de constraint)
        raise Exception(f"Erro na consulta SQL: {e}")
    finally:
        if conn:
            conn.close()


def initialize_db():
    """Roda o script de criação de tabelas (schema.sql)."""
    try:
        # Lê o script SQL de um arquivo
        with open('schema.sql', 'r') as f:
            sql_script = f.read()
            
        # Executa a criação das tabelas
        query(sql_script, fetch_all=False)
        print("Tabelas criadas ou já existentes.")

    except FileNotFoundError:
        print("Aviso: Arquivo schema.sql não encontrado. Não foi possível inicializar o DB.")
    except Exception as e:
        print(f"Erro ao inicializar o banco de dados: {e}")
        raise

# A função initialize_db será chamada no app.py na inicialização.