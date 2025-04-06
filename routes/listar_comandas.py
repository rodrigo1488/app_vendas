from flask import Flask, request, jsonify, render_template,Blueprint
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from waitress import serve
import sqlite3
import os
import datetime
from config import inicializar_banco_sqlite, CAMINHO_DB_LOCAL, db


listar_comandas_bp = Blueprint('listar_comandas_bp', __name__)






###ROTA PARA LISTAR COMANDAS ATIVAS####
@listar_comandas_bp.route('/listarcomandas', methods=['GET'])
def get_comandas_ativas():
    try:
        query = text("""
            SELECT id, numeromesa, valortotal AS valortotal_comanda
            FROM contamesa WHERE status = '1'
        """)
        result = db.session.execute(query).fetchall()
        return jsonify([dict(row._mapping) for row in result]) if result else jsonify(), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



