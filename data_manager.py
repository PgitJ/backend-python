import json
import os
from uuid import uuid4

DATA_DIR = 'data/'

def _load_data(filename):
    """Carrega dados de um arquivo JSON. Cria um arquivo vazio se não existir."""
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        # Garante que o arquivo exista e não esteja vazio
        with open(filepath, 'w') as f:
            json.dump([], f)
        return []
    
    with open(filepath, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            # Retorna lista vazia em caso de JSON inválido
            return []

def _save_data(filename, data):
    """Salva dados em um arquivo JSON."""
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

def find_all(filename, user_id):
    """Retorna todos os registros para um dado usuário."""
    data = _load_data(filename)
    # Filtra os dados apenas para o usuário atual (simulando WHERE user_id = $1)
    return [item for item in data if str(item.get('user_id')) == str(user_id)]

def find_by_id(filename, item_id, user_id):
    """Retorna um registro pelo ID para um dado usuário."""
    data = _load_data(filename)
    for item in data:
        if str(item.get('id')) == str(item_id) and str(item.get('user_id')) == str(user_id):
            return item
    return None

def create(filename, new_item, user_id):
    """Cria um novo registro com ID e user_id."""
    data = _load_data(filename)
    new_item['id'] = str(uuid4()) # Gera um UUID único para o ID
    new_item['user_id'] = str(user_id)
    
    # Garantindo consistência de tipo para 'amount' se for usado
    if 'amount' in new_item:
        try:
            new_item['amount'] = float(new_item['amount'])
        except (TypeError, ValueError):
            pass # Mantém o valor original se não puder converter
            
    data.append(new_item)
    _save_data(filename, data)
    return new_item

def update(filename, item_id, updated_item, user_id):
    """Atualiza um registro existente."""
    data = _load_data(filename)
    for i, item in enumerate(data):
        if str(item.get('id')) == str(item_id) and str(item.get('user_id')) == str(user_id):
            # Atualiza apenas os campos permitidos
            updated_data = {**item, **updated_item}
            
            # Garante que ID e user_id não sejam alterados
            updated_data['id'] = item_id
            updated_data['user_id'] = user_id
            
            data[i] = updated_data
            _save_data(filename, data)
            return updated_data
    return None

def delete(filename, item_id, user_id):
    """Deleta um registro existente."""
    data = _load_data(filename)
    original_len = len(data)
    
    # Filtra a lista, removendo o item que corresponde ao ID e user_id
    new_data = [item for item in data if not (str(item.get('id')) == str(item_id) and str(item.get('user_id')) == str(user_id))]

    if len(new_data) < original_len:
        _save_data(filename, new_data)
        return True
    return False

# Funções auxiliares para Autenticação (usuários)
def find_user_by_username(username):
    data = _load_data('users.json')
    return next((user for user in data if user.get('username') == username), None)

def create_user(username, password_hash):
    data = _load_data('users.json')
    new_user = {
        'id': str(uuid4()),
        'username': username,
        'password_hash': password_hash
    }
    data.append(new_user)
    _save_data('users.json', data)
    return new_user