from flask import Flask, request, jsonify, render_template,Blueprint
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from waitress import serve
import sqlite3
import os
import datetime
from config import inicializar_banco_sqlite, CAMINHO_DB_LOCAL

listar_vendas_fechadas_bp = Blueprint('listar_vendas_fechadas_bp', __name__)

from flask import request

@listar_vendas_fechadas_bp.route('/finalizadas', methods=['GET'])
def get_comadas_finalizadas():
    try:
        # Obtem os parâmetros de paginação da query string
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        offset = (page - 1) * per_page

        conn = sqlite3.connect(CAMINHO_DB_LOCAL)
        cur = conn.cursor()

        # Conta o total de vendas
        cur.execute("""
            SELECT COUNT(*) FROM vendas
        """)
        total_count = cur.fetchone()[0]

        cur.execute("""
            SELECT id, numero_comanda, meio_pagamento, valor_total, data_hora, id_garcom
            FROM vendas
            ORDER BY data_hora DESC
            LIMIT ? OFFSET ?
        """, (per_page, offset))

        result = cur.fetchall()
        conn.close()

        if result:
            vendas = [
                {
                    "id": row[0],
                    "numero_comanda": row[1],
                    "meio_pagamento": row[2],
                    "valor_total": row[3],
                    "data_hora": row[4],
                    "id_garcom": row[5]
                }
                for row in result
            ]
            return jsonify({
                "page": page,
                "per_page": per_page,
                "total_count": total_count,
                "vendas": vendas
            }), 200
        else:
            return jsonify({
                "page": page,
                "per_page": per_page,
                "total_count": total_count,
                "vendas": [],
            }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
