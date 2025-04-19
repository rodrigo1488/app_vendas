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

@usuarios_bp.route('/listar_usuarios', methods=['GET'])
def listar_usuarios():
    try:
        page = int(request.args.get('page', 1))
        per_page = 10
        offset = (page - 1) * per_page

        conn = sqlite3.connect(CAMINHO_DB_LOCAL)
        cur = conn.cursor()
        

        cur.execute("""
            SELECT COUNT(*) FROM  usuarios
        """)
        total_usuarios = cur.fetchone()[0]

        cur.execute("""
            SELECT id, nome, senha, adm FROM usuarios
            ORDER BY nome ASC
            LIMIT ? OFFSET ?
        """, (per_page, offset))

        result = cur.fetchall()
        conn.close()

        if result:
            usuarios = [{
                "id":  row[0],
                "nome": row[1],
                "senha": row[2],
                "adm": row[3]
            } for row in result]

            return jsonify({
                "page": page,
                "per_page": per_page,
                "total_usuarios": total_usuarios,
                "usuarios": usuarios
            }), 200
        else:
            return jsonify({
                "page": page,
                "per_page": per_page,
                "total_usuarios": total_usuarios,
                "usuarios": [],
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


###
@usuarios_bp.route('/deletar_usuario/<int:id>', methods=['DELETE'])
def deletar_usuario(id):
    try:
        conn = sqlite3.connect(CAMINHO_DB_LOCAL)
        cur = conn.cursor()
        cur.execute("DELETE FROM usuarios WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return jsonify({"message": "Usuário deletado com sucesso"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@usuarios_bp.route('/atualizar_usuario/<int:id>', methods=['PUT'])
def atualizar_usuario(id):
    try:
        data = request.get_json()
        nome = data.get("nome")
        senha = data.get("senha")
        adm = data.get("adm", False)  
        
        conn = sqlite3.connect(CAMINHO_DB_LOCAL)
        cur = conn.cursor()
        cur.execute("""
            UPDATE usuarios
            SET nome = ?, senha = ?, adm = ?
            WHERE id = ?
        """, (nome, senha, adm, id))
        conn.commit()
        conn.close()
        return jsonify({"message": "Usuário atualizado com sucesso"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500  



@usuarios_bp.route('/buscar_usuario/<int:id>', methods=['GET'])
def buscar_usuario(id):
    try:        
        conn = sqlite3.connect(CAMINHO_DB_LOCAL)
        cur = conn.cursor()
        cur.execute("SELECT id, nome, senha, adm FROM usuarios where id = ?", (id,))
        result = cur.fetchall()
        conn.close()
        return jsonify([{ "id": row[0], "nome": row[1], "senha": row[2], "adm": row[3] } for row in result]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
