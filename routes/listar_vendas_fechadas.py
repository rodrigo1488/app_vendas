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

###ROTA PARA LISTAR VENDAS FINALIZADAS####
@listar_vendas_fechadas_bp.route('/finalizadas', methods=['GET'])
def get_comadas_finalizadas():
    try:
        conn = sqlite3.connect(CAMINHO_DB_LOCAL)
        cur = conn.cursor()
        cur.execute("SELECT id, numero_comanda, meio_pagamento, valor_total, data_hora, id_garcom FROM vendas LIMIT 5 OFFSET 0")

        result = cur.fetchall()
        conn.close()
        return jsonify([{ "id": row[0], "numero_comanda": row[1], "meio_pagamento": row[2], "valor_total": row[3], "data_hora": row[4], "id_garcom": row[5] } for row in result]) if result else jsonify({"message": "Nenhuma comanda finalizada"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500