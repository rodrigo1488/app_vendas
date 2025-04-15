from flask import Flask, request, jsonify, render_template,Blueprint
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from waitress import serve
import sqlite3
import os
import datetime
from config import inicializar_banco_sqlite, CAMINHO_DB_LOCAL, db


fechamento_bp = Blueprint('fechamento_bp', __name__)
# Inicializa o banco SQLite


@fechamento_bp.route('/fechamento', methods=['POST'])
def fechamento():
    try:
        data = request.get_json()
        total_caixa = data.get("total_caixa")
        total_contado = data.get("total_contado")
        operador = data.get("operador")
        observacao = data.get("observacao")

        conn = sqlite3.connect(CAMINHO_DB_LOCAL)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO FECHAMENTO_CAIXA (total_caixa,total_contado, operador, observacao)
            VALUES (?, ?, ?, ?)
        """, (total_caixa, total_contado, operador, observacao))
        conn.commit()
        conn.close()
        return jsonify({"message": "Fechamento realizado com sucesso!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500