from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import jwt
import uuid
import os
from functools import wraps
from data_manager import find_all, create, update, delete, find_user_by_username
from auth import auth_bp # Importa o Blueprint de autenticação

# 1. Configuração
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], "allow_headers": ["Content-Type", "Authorization"]}})

bcrypt = Bcrypt(app) 

# Certifique-se de que a pasta 'data' existe
if not os.path.exists('data'):
    os.makedirs('data')

# Variáveis de ambiente
SECRET_KEY = os.environ.get('SECRET_KEY', '7c7769737faea4ff3adeda50fada7fa7c0d141f347e6f69d21399d4865ab3c94')
app.config['SECRET_KEY'] = SECRET_KEY

# Mapeamento para o data_manager
FILE_MAP = {
    'transactions': 'transactions.json',
    'goals': 'goals.json',
    'bills': 'bills.json',
    'categories': 'categories.json'
}

# 2. Middleware de Autenticação (Decorator)
def authenticate_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'error': 'Token não fornecido.'}), 401

        try:
            # Verifica e decodifica o token
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            # Adiciona user_id à requisição (simulando req.user.userId)
            request.user_id = data['userId'] 
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado.'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido.'}), 403

        return f(*args, **kwargs, **kwargs)
    return decorated

# Monta o Blueprint de Autenticação
app.register_blueprint(auth_bp, url_prefix='/auth')

# 3. Rotas da API (Implementação usando data_manager)

# --- CATEGORIAS ---
# Nota: No frontend, as categorias são extraídas de transactions. 
# Esta rota será simplificada para retornar uma lista estática/gerenciada.
@app.route('/api/categories', methods=['GET'])
@authenticate_token
def get_categories():
    user_id = request.user_id
    # No backend Node.js, você buscava do BD. Aqui, simulamos isso:
    categories_data = find_all(FILE_MAP['categories'], user_id)
    # Garante que sempre haja categorias padrão se nenhuma existir
    if not categories_data:
        # Cria categorias padrão para o usuário se não existirem
        default_cats = [{'name': 'Alimentação', 'user_id': user_id, 'id': str(uuid.uuid4())},
                        {'name': 'Transporte', 'user_id': user_id, 'id': str(uuid.uuid4())}]
        for cat in default_cats:
            create(FILE_MAP['categories'], cat, user_id)
        categories_data = default_cats
        
    return jsonify(categories_data), 200

@app.route('/api/categories', methods=['POST'])
@authenticate_token
def add_category():
    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({'error': 'Nome da categoria é obrigatório.'}), 400
    
    # Verifica se a categoria já existe para o usuário
    existing_cats = find_all(FILE_MAP['categories'], request.user_id)
    if any(c['name'] == name for c in existing_cats):
        return jsonify({'error': 'Categoria já existe.'}), 409
        
    new_cat = create(FILE_MAP['categories'], {'name': name}, request.user_id)
    return jsonify(new_cat), 201

@app.route('/api/categories/<name>', methods=['DELETE'])
@authenticate_token
def remove_category(name):
    # Simula a busca da categoria pelo nome (pois o frontend usa o nome)
    existing_cats = find_all(FILE_MAP['categories'], request.user_id)
    category_to_delete = next((c for c in existing_cats if c['name'] == name), None)
    
    if not category_to_delete:
        return jsonify({'error': 'Categoria não encontrada'}), 404

    # Usa o ID gerado para a exclusão
    if delete(FILE_MAP['categories'], category_to_delete['id'], request.user_id):
        return jsonify({'message': 'Categoria deletada com sucesso'}), 200
    return jsonify({'error': 'Categoria não encontrada'}), 404


# --- TRANSAÇÕES (Simulação CRUD) ---
@app.route('/api/transactions', methods=['GET'])
@authenticate_token
def get_transactions():
    transactions = find_all(FILE_MAP['transactions'], request.user_id)
    return jsonify(transactions), 200

@app.route('/api/transactions', methods=['POST'])
@authenticate_token
def add_transaction():
    new_transaction = create(FILE_MAP['transactions'], request.get_json(), request.user_id)
    return jsonify(new_transaction), 201

@app.route('/api/transactions/<id>', methods=['PUT'])
@authenticate_token
def update_transaction(id):
    updated = update(FILE_MAP['transactions'], id, request.get_json(), request.user_id)
    if updated:
        return jsonify(updated)
    return jsonify({'error': 'Transação não encontrada'}), 404

@app.route('/api/transactions/<id>', methods=['DELETE'])
@authenticate_token
def delete_transaction(id):
    if delete(FILE_MAP['transactions'], id, request.user_id):
        return jsonify({'message': 'Transação deletada com sucesso'}), 200
    return jsonify({'error': 'Transação não encontrada'}), 404

# --- METAS (Simulação CRUD) ---
@app.route('/api/goals', methods=['GET'])
@authenticate_token
def get_goals():
    goals = find_all(FILE_MAP['goals'], request.user_id)
    return jsonify(goals), 200

@app.route('/api/goals', methods=['POST'])
@authenticate_token
def add_goal():
    new_goal = create(FILE_MAP['goals'], request.get_json(), request.user_id)
    return jsonify(new_goal), 201

@app.route('/api/goals/<id>', methods=['PUT'])
@authenticate_token
def update_goal(id):
    updated = update(FILE_MAP['goals'], id, request.get_json(), request.user_id)
    if updated:
        return jsonify(updated)
    return jsonify({'error': 'Meta não encontrada'}), 404

@app.route('/api/goals/<id>', methods=['DELETE'])
@authenticate_token
def delete_goal(id):
    if delete(FILE_MAP['goals'], id, request.user_id):
        return jsonify({'message': 'Meta deletada com sucesso'}), 200
    return jsonify({'error': 'Meta não encontrada'}), 404

# --- CONTAS A PAGAR (Simulação CRUD) ---
@app.route('/api/bills', methods=['GET'])
@authenticate_token
def get_bills():
    bills = find_all(FILE_MAP['bills'], request.user_id)
    return jsonify(bills), 200

@app.route('/api/bills', methods=['POST'])
@authenticate_token
def add_bill():
    new_bill = create(FILE_MAP['bills'], request.get_json(), request.user_id)
    return jsonify(new_bill), 201

@app.route('/api/bills/<id>', methods=['PUT'])
@authenticate_token
def update_bill(id):
    updated = update(FILE_MAP['bills'], id, request.get_json(), request.user_id)
    if updated:
        return jsonify(updated)
    return jsonify({'error': 'Conta não encontrada'}), 404

@app.route('/api/bills/<id>', methods=['DELETE'])
@authenticate_token
def delete_bill(id):
    if delete(FILE_MAP['bills'], id, request.user_id):
        return jsonify({'message': 'Conta deletada com sucesso'}), 200
    return jsonify({'error': 'Conta não encontrada'}), 404


