from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
import jwt
import datetime
import os
import uuid
from data_manager import find_user_by_username, create_user

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt() # Inicializado no app.py, mas usado aqui

# Para simplificar, vamos definir a chave secreta aqui para teste, 
# mas em produção deve vir de uma variável de ambiente!
SECRET_KEY = os.environ.get('SECRET_KEY', '7c7769737faea4ff3adeda50fada7fa7c0d141f347e6f69d21399d4865ab3c94')


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username e senha são obrigatórios.'}), 400

    if find_user_by_username(username):
        return jsonify({'error': 'Nome de usuário já existe.'}), 409 # 409 Conflict

    # Hashing da senha
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    # Criação do usuário via data_manager
    user = create_user(username, password_hash)

    # Retorna o user_id como 'id' para consistência
    return jsonify({
        'message': 'Usuário registrado com sucesso!',
        'user': {'id': user['id'], 'username': user['username']}
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = find_user_by_username(username)

    if not user or not bcrypt.check_password_hash(user['password_hash'], password):
        return jsonify({'error': 'Usuário ou senha incorretos.'}), 400

    # Criação do JWT
    token = jwt.encode({
        'userId': user['id'], 
        'username': user['username'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1) # Expira em 1 hora
    }, SECRET_KEY, algorithm='HS256')

    return jsonify({
        'token': token, 
        'message': 'Login bem-sucedido!', 
        'username': user['username']
    })