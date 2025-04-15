from flask import Flask, request, jsonify, render_template,Blueprint
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from waitress import serve
import sqlite3
import os
import datetime
from config import inicializar_banco_sqlite, CAMINHO_DB_LOCAL, db


finalizar_venda_bp = Blueprint('finalizar_venda_bp', __name__)

@finalizar_venda_bp.route('/finalizar_venda', methods=['POST'])
def finalizar_venda():
    now = datetime.datetime.now()
    horario_fechamento = now.strftime('%Y-%m-%d %H:%M:%S')  # <- Aqui pega o horário atual

    try:
        data = request.get_json()
        
        meio_pagamento = data.get("meio_pagamento")
        valor_total = data.get("valor_total")
        id_garcom = data.get("id_garcom")
        numeromesa = data.get("numeromesa")
       
        
        # Inserir a venda no SQLite com horário atual
        conn = sqlite3.connect(CAMINHO_DB_LOCAL)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO vendas (numero_comanda, meio_pagamento, valor_total, id_garcom, data_hora)
            VALUES (?, ?, ?, ?, ?)
        """, (numeromesa, meio_pagamento, valor_total, id_garcom, horario_fechamento))
        conn.commit()
        conn.close()

        # Atualizar status da mesa
        query = text("""
            UPDATE contamesa 
            SET status = 99, horafechamento = CURRENT_TIMESTAMP,ECFCUPOM ='FINALIZADO PELO APP '
            WHERE numeromesa = :numeromesa 
        """)
        db.session.execute(query, {'numeromesa': numeromesa})
        db.session.commit()

        return jsonify({
            "message": f"Venda registrada e mesa {numeromesa} fechada com sucesso.",
            "data_hora": horario_fechamento  # opcional: pode retornar ao front
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500




###ROTA PARA FINALIZAR COMANDA####
# @finalizar_venda_bp.route('/finalizar_venda', methods=['POST'])
# def finalizar_venda():
#     now = datetime.datetime.now()
#     try:
#         data = data.get('%D-%m-%Y %H:%M:%S')
#         numero_comanda = data.get("numeromesa")
#         meio_pagamento = data.get("meio_pagamento")
#         valor_total = data.get("valor_total")
#         id_garcom = data.get("id_garcom")
#         numeromesa = data.get("numeromesa") 

#         if not all([numero_comanda, meio_pagamento, valor_total, numeromesa]):
#             return jsonify({"error": "Todos os campos são obrigatórios"}), 400

#         # Inserir a venda no SQLite
#         conn = sqlite3.connect(CAMINHO_DB_LOCAL)
#         cur = conn.cursor()
#         cur.execute("""
#             INSERT INTO vendas (numero_comanda, meio_pagamento, valor_total, id_garcom)
#             VALUES (?, ?, ?, ?)
#         """, (numero_comanda, meio_pagamento, valor_total, id_garcom))
#         conn.commit()
#         conn.close()

#         # Atualizar o status da mesa no banco via SQLAlchemy
#         query = text("""
#             UPDATE contamesa 
#             SET status = 4, horafechamento = NOW()
#             WHERE numeromesa = :numeromesa
#         """)
#         db.session.execute(query, {'numeromesa': numeromesa})
#         db.session.commit()

#         return jsonify({"message": f"Venda registrada e mesa {numeromesa} fechada com sucesso."}), 201

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500