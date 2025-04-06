from flask import Flask, request, jsonify, render_template,Blueprint
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from waitress import serve
import sqlite3
import os
import datetime
from config import inicializar_banco_sqlite, CAMINHO_DB_LOCAL


total_dia_bp = Blueprint('total_dia_bp', __name__)

###ROTA PARA LISTAR TOTAL EM R$ DE VENDAS NO DIA ####
@total_dia_bp.route('/total_dia', methods=['GET'])
def get_total_dia():
    try:
        hoje = datetime.datetime.now().strftime('%Y-%m-%d')

        # Conecta ao banco SQLite
        conn = sqlite3.connect(CAMINHO_DB_LOCAL)
        cur = conn.cursor()

        # Consulta o total de vendas feitas hoje
        cur.execute("""
            SELECT SUM(valor_total) AS total_vendas
            FROM vendas
            WHERE DATE(data_hora) = ?
        """, (hoje,))
        result_vendas = cur.fetchone()

        # Consulta a quantidade de comandas fechadas hoje
        cur.execute("""
            SELECT COUNT(*) AS total_fechadas
            FROM vendas
            WHERE DATE(data_hora) = ?
        """, (hoje,))
        result_fechadas = cur.fetchone()

        conn.close()

        # Obtém os valores corretamente
        total_vendas = result_vendas[0] if result_vendas and result_vendas[0] else 0
        total_fechadas = result_fechadas[0] if result_fechadas and result_fechadas[0] else 0

        return jsonify({
            "total_vendas": total_vendas,
            "total_fechadas": total_fechadas
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
