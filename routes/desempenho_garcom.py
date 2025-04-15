from flask import Flask, request, jsonify, render_template,Blueprint
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from waitress import serve
import sqlite3
import os
import datetime
from config import inicializar_banco_sqlite, CAMINHO_DB_LOCAL, db


desempenho_garcom_bp = Blueprint('desempenho_garcom_bp', __name__)


@desempenho_garcom_bp.route('/desempenho_garcom', methods=['GET'])
def desempenho_garcom():
    try:
        hoje = datetime.datetime.now()
        mes_atual = f"{hoje.month:02}"
        ano_atual = str(hoje.year)

        # Conexão com o SQLite
        conn = sqlite3.connect(CAMINHO_DB_LOCAL)
        cur = conn.cursor()

        cur.execute("""
            SELECT id_garcom, SUM(valor_total) as total
            FROM vendas
            WHERE strftime('%m', data_hora) = ? AND strftime('%Y', data_hora) = ?
            GROUP BY id_garcom
            ORDER BY total DESC
        """, (mes_atual, ano_atual))

        rows = cur.fetchall()
        conn.close()

        desempenho_garcom = []

        for id_garcom, total in rows:
            # Consulta no banco Postgres usando SQLAlchemy
            query = text("""
                SELECT nome FROM entidade WHERE id = :codigo
            """)
            result = db.session.execute(query, {'codigo': str(id_garcom)}).fetchone()
            nome = result[0] if result else 'Desconhecido'

            desempenho_garcom.append({

                "id_garcom": id_garcom,
                "data_hora": hoje.strftime('%d/%m/%y'),
                "nome": nome,
                "valor": round(total, 2)
            })

        return jsonify(desempenho_garcom), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
