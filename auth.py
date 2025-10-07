from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
import jwt
import datetime
import os
import uuid # Mantenha o uuid, embora não seja usado diretamente neste arquivo
from data_manager import find_user_by_username, create_user

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

# Chave Secreta
SECRET_KEY = os.environ.get('SECRET_KEY', '7c7769737faea4ff3adeda50fada7fa7c0d141f347e6f69d21399d4865ab3c94')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username e senha são obrigatórios.'}), 400

    if find_user_by_username(username):
        return jsonify({'error': 'Nome de usuário já existe.'}), 409

    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    user = create_user(username, password_hash)

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

    # 1. Geração do Access Token (curta validade: 15 minutos)
    access_token = jwt.encode({
        'userId': user['id'], 
        'username': user['username'],
        'type': 'access',
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    }, SECRET_KEY, algorithm='HS256')
    
    # 2. Geração do Refresh Token (longa validade: 30 dias)
    refresh_token = jwt.encode({
        'userId': user['id'], 
        'username': user['username'],
        'type': 'refresh',
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)
    }, SECRET_KEY, algorithm='HS256')

    return jsonify({
        'token': access_token,             # Access Token principal (usado nas APIs)
        'refreshToken': refresh_token,     # Token de renovação (usado para obter novos access tokens)
        'message': 'Login bem-sucedido!', 
        'username': user['username']
    })


@auth_bp.route('/token/refresh', methods=['POST'])
def refresh_token():
    data = request.get_json()
    refresh_token = data.get('refreshToken')

    if not refresh_token:
        return jsonify({'error': 'Refresh Token é obrigatório.'}), 401

    try:
        # Tenta verificar se o Refresh Token é válido
        decoded = jwt.decode(refresh_token, SECRET_KEY, algorithms=['HS256'])

        if decoded.get('type') != 'refresh':
            return jsonify({'error': 'Token inválido para renovação.'}), 403

        # Se válido, gera um NOVO Access Token (15 minutos)
        new_access_token = jwt.encode(
            { 'userId': decoded['userId'], 
              'username': decoded['username'], 
              'type': 'access',
              'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
            },
            SECRET_KEY,
            algorithm='HS256'
        )

        return jsonify({'token': new_access_token}), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Refresh Token expirado. Faça login novamente.'}), 403
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Refresh Token inválido.'}), 403
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500