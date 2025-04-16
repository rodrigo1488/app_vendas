from flask import Flask, request, jsonify, render_template,Blueprint
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from waitress import serve
import sqlite3
import os
import datetime
from config import inicializar_banco_sqlite, CAMINHO_DB_LOCAL, db


login_bp = Blueprint('login_bp', __name__)

@login_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Verificar as credenciais no banco de dados
    conn = sqlite3.connect(CAMINHO_DB_LOCAL)
    cur = conn.cursor()
    cur.execute("SELECT * FROM USUARIOS WHERE NOME = ? AND SENHA = ?", (username, password))
    user = cur.fetchone()
    conn.close()

    if user:
        return jsonify({"message": "Login bem-sucedido", "user": {"id": user[0], "nome": user[1] , "senha": user[2], "adm": user[3]}}), 200
    else:
        return jsonify({"error": "Credenciais inválidas"}), 401 

