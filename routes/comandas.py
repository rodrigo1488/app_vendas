from flask import Flask, request, jsonify, render_template,Blueprint
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from waitress import serve
import sqlite3
import os
import datetime
from config import inicializar_banco_sqlite, CAMINHO_DB_LOCAL, db

import sqlite3

comandas_bp = Blueprint('comandas_bp', __name__)


### Rotas da API PARA BUSCAR ITENS DA COMANDAATIVA####
@comandas_bp.route('/comanda/<numeromesa>', methods=['GET'])
def get_comanda_por_mesa(numeromesa):
    try:
        query = text("""
            SELECT 
                c.id,
                c.nomeproduto,
                c.quantidade,
                c.precounitario,
                c.idcontamesa,
                c.idgarcom,
                c.valortotal AS valortotal_item,
                m.valortotal AS valortotal_comanda
            FROM contamesaitem c
            JOIN contamesa m ON c.idcontamesa = m.id
            WHERE m.numeromesa = :numeromesa
            AND status = '1'
        """)
        result = db.session.execute(query, {'numeromesa': numeromesa}).fetchall()

        if result:
            return jsonify([dict(row._mapping) for row in result]), 200
        else:
            return jsonify({"message": "Nenhum item encontrado para essa mesa"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
