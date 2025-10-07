# data_manager.py - Implementação SQL

import uuid
from db import query

# Funções auxiliares de Autenticação (Users)

def find_user_by_username(username):
    sql_text = "SELECT id, username, password_hash FROM users WHERE username = %s"
    results = query(sql_text, (username,))
    return results[0] if results else None

def create_user(username, password_hash):
    new_id = str(uuid.uuid4())
    sql_text = "INSERT INTO users (id, username, password_hash) VALUES (%s, %s, %s) RETURNING id, username"
    query(sql_text, (new_id, username, password_hash), fetch_all=False)
    return {'id': new_id, 'username': username}

# --- Funções CRUD Genéricas para a Aplicação ---

# Função para encontrar um item (usada para Transaction, Goal, Bill, Category)
def find_all(table_name, user_id, order_by='id'):
    sql_text = sql.SQL("SELECT * FROM {} WHERE user_id = %s ORDER BY {}").format(
        sql.Identifier(table_name), sql.Identifier(order_by)
    )
    return query(sql_text, (user_id,))

def find_by_id(table_name, item_id, user_id):
    sql_text = sql.SQL("SELECT * FROM {} WHERE id = %s AND user_id = %s").format(
        sql.Identifier(table_name)
    )
    results = query(sql_text, (item_id, user_id))
    return results[0] if results else None

def delete(table_name, item_id, user_id):
    sql_text = sql.SQL("DELETE FROM {} WHERE id = %s AND user_id = %s RETURNING id").format(
        sql.Identifier(table_name)
    )
    results = query(sql_text, (item_id, user_id))
    return len(results) > 0 # Retorna True se algo foi deletado

# --- Implementação CRUD Específica ---

# Transações
def create_transaction(item, user_id):
    new_id = str(uuid.uuid4())
    sql_text = """
    INSERT INTO transactions (id, user_id, date, description, category, type, amount) 
    VALUES (%s, %s, %s, %s, %s, %s, %s) 
    RETURNING *
    """
    params = (new_id, user_id, item['date'], item['description'], item['category'], item['type'], item['amount'])
    return query(sql_text, params)[0]

def update_transaction(item_id, item, user_id):
    sql_text = """
    UPDATE transactions 
    SET date = %s, description = %s, category = %s, type = %s, amount = %s 
    WHERE id = %s AND user_id = %s 
    RETURNING *
    """
    params = (item['date'], item['description'], item['category'], item['type'], item['amount'], item_id, user_id)
    results = query(sql_text, params)
    return results[0] if results else None

# Metas
def create_goal(item, user_id):
    new_id = str(uuid.uuid4())
    sql_text = """
    INSERT INTO goals (id, user_id, name, amount, saved, target_date) 
    VALUES (%s, %s, %s, %s, %s, %s) 
    RETURNING *
    """
    params = (new_id, user_id, item['name'], item['amount'], item.get('saved', 0), item['target_date'])
    return query(sql_text, params)[0]

def update_goal(item_id, item, user_id):
    sql_text = """
    UPDATE goals 
    SET name = %s, amount = %s, saved = %s, target_date = %s 
    WHERE id = %s AND user_id = %s 
    RETURNING *
    """
    params = (item['name'], item['amount'], item['saved'], item['target_date'], item_id, user_id)
    results = query(sql_text, params)
    return results[0] if results else None

# Contas (Bills)
def create_bill(item, user_id):
    new_id = str(uuid.uuid4())
    sql_text = """
    INSERT INTO bills (id, user_id, description, amount, due_date, paid) 
    VALUES (%s, %s, %s, %s, %s, %s) 
    RETURNING *
    """
    params = (new_id, user_id, item['description'], item['amount'], item['due_date'], item.get('paid', False))
    return query(sql_text, params)[0]

def update_bill(item_id, item, user_id):
    # Usado para marcar como pago
    sql_text = """
    UPDATE bills 
    SET description = %s, amount = %s, due_date = %s, paid = %s 
    WHERE id = %s AND user_id = %s 
    RETURNING *
    """
    params = (item['description'], item['amount'], item['due_date'], item['paid'], item_id, user_id)
    results = query(sql_text, params)
    return results[0] if results else None

# Categorias (Simples)
def find_all_categories(user_id):
    return find_all('categories', user_id, order_by='name')

def create_category(name, user_id):
    new_id = str(uuid.uuid4())
    sql_text = "INSERT INTO categories (id, user_id, name) VALUES (%s, %s, %s) RETURNING *"
    return query(sql_text, (new_id, user_id, name))[0]

def delete_category(category_name, user_id):
    # Encontra o ID primeiro, pois o DELETE do frontend usa o NOME
    # Isso requer lógica manual para mapear nome para ID no data_manager
    # Assumindo que você tem um ID para a categoria:
    sql_text = "DELETE FROM categories WHERE name = %s AND user_id = %s RETURNING id"
    results = query(sql_text, (category_name, user_id))
    return len(results) > 0