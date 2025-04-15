from flask import Flask, request, jsonify, Blueprint
from config import inicializar_banco_sqlite, CAMINHO_DB_LOCAL
import sqlite3

usuarios_bp = Blueprint('usuarios_bp', __name__)

@usuarios_bp.route('/cadastrar_usuario', methods=['POST'])
def cadastrar_usuario():
    try:
        data = request.get_json()
        nome = data.get("nome")
        senha = data.get("senha")
        adm = data.get("adm", False)  
        
        
        conn = sqlite3.connect(CAMINHO_DB_LOCAL)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO usuarios (nome,senha,adm)
            VALUES (?, ?, ?)
        """, (nome,senha,adm))
        conn.commit()
        conn.close()
        return jsonify({"message": "Usuário cadastrado com sucesso"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


