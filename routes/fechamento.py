from flask import Flask, request, jsonify, render_template,Blueprint
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from waitress import serve
import sqlite3
import os
import datetime
from config import inicializar_banco_sqlite, CAMINHO_DB_LOCAL, db
from escpos.printer import Network


fechamento_bp = Blueprint('fechamento_bp', __name__)
# Inicializa o banco SQLite




@fechamento_bp.route('/fechamento', methods=['POST'])
def fechamento():
    try:
        data = request.get_json()
        total_caixa = data.get("total_caixa")
        total_contado = data.get("total_contado")
        total_abertura = data.get("total_abertura")
        operador = data.get("operador")
        observacao = data.get("observacao")
        data_fechamento = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect(CAMINHO_DB_LOCAL)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO FECHAMENTO_CAIXA (total_caixa,total_contado,total_abertura, operador, observacao,data_hora)
            VALUES (?, ?, ?,?,?,?)
        """, (total_caixa, total_contado,total_abertura, operador, observacao, data_fechamento))
        conn.commit()
        conn.close()
        imprimir_fechamento(total_caixa, total_contado, operador, observacao, data_fechamento)
        return jsonify({"message": "Fechamento realizado com sucesso!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@fechamento_bp.route('/listar_fechamentos', methods=['GET'])
def listar_fechamentos():
    try:
        conn = sqlite3.connect(CAMINHO_DB_LOCAL)
        cur = conn.cursor()
        query="""
            SELECT id,total_caixa,total_contado, operador, observacao, data_hora FROM FECHAMENTO_CAIXA
            ORDER BY data_hora DESC
        """
        cur.execute(query)
        result = cur.fetchall()
        conn.close()
        return jsonify([{ "id": row[0], "total_caixa": row[1], "total_contado": row[2], "operador": row[3], "observacao": row[4], "data_hora": row[5] } for row in result]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500





IMPRESSORA_PORTA = 9100  # define isso como constante global, se ainda não tiver

def imprimir_fechamento(total_caixa, total_contado, operador, observacao, data_fechamento):
    """Envia os dados de fechamento para a impressora térmica usando ESC/POS"""
    try:
        impressora_ip =  "192.168.2.69"

        p = Network(impressora_ip, IMPRESSORA_PORTA)
        p.set(align='center')
        p.text('\x1B\x21\x08')  # tamanho de fonte um pouco maior
        p.text("=== FECHAMENTO DE CAIXA ===\n\n")

        p.set(align='left')
        p.text(f"Data: {data_fechamento}\n")
        p.text(f"Operador: {operador}\n")
        p.text(f"Total do Caixa: R$ {float(total_caixa):.2f}\n")
        p.text(f"Total Contado: R$ {float(total_contado):.2f}\n")
        p.text(f"Observação: {observacao if observacao else '---'}\n")
        
        p.text("\n-------------------------------\n")
        p.set(align='center')
        p.text("Assinatura: __________________\n\n")
        p.cut()

        print(f"Fechamento impresso com sucesso em {impressora_ip}")

    except Exception as e:
        print(f"Erro ao imprimir fechamento: {e}")



