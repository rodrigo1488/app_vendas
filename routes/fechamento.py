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
        data_fechamento = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M")
        end_imp=data.get("end_imp")

        conn = sqlite3.connect(CAMINHO_DB_LOCAL)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO FECHAMENTO_CAIXA (total_caixa,total_contado,total_abertura, operador, observacao,data_hora)
            VALUES (?, ?, ?,?,?,?)
        """, (total_caixa, total_contado,total_abertura, operador, observacao, data_fechamento))
        conn.commit()
        conn.close()
        imprimir_fechamento(total_caixa, total_contado, operador, observacao, data_fechamento,total_abertura, end_imp)
        return jsonify({"message": "Fechamento realizado com sucesso!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@fechamento_bp.route('/listar_fechamentos', methods=['GET'])
def listar_fechamentos():
    try:
        conn = sqlite3.connect(CAMINHO_DB_LOCAL)
        cur = conn.cursor()
        query="""
            SELECT id,total_caixa,total_contado, total_abertura,operador, observacao, data_hora FROM FECHAMENTO_CAIXA
            ORDER BY data_hora ASC
            LIMIT 10
            
        """
        cur.execute(query)
        result = cur.fetchall()
        conn.close()
        return jsonify([{ "id": row[0], "total_caixa": row[1], "total_contado": row[2], "total_abertura": row[3], "operador": row[4], "observacao": row[5], "data_hora": row[6]  } for row in result]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500





IMPRESSORA_PORTA = 9100  # define isso como constante global, se ainda não tiver

def imprimir_fechamento(total_caixa, total_contado, operador, observacao, data_fechamento,total_abertura, end_imp):
    """Envia os dados de fechamento para a impressora térmica usando ESC/POS"""
    try:
        impressora_ip =  end_imp  # IP da impressora, pode ser passado como argumento
        print(end_imp)

        p = Network(impressora_ip, IMPRESSORA_PORTA)
        p.set(align='center')
        p.text('\x1B\x21\x08')  # tamanho de fonte um pouco maior
        p.text("=== FECHAMENTO DE CAIXA ===\n\n")

        p.set(align='left')
  
        p.text(f"Data: {data_fechamento}\n")
        p.text(f"\n Operador: {operador}\n")
        p.text(f"\n******************************************\n")
        p.text(f"\n Total Abertura: R$ {float(total_abertura):.2f}\n")
        p.text(f"\n Total do Caixa: R$ {float(total_caixa):.2f}\n")
        p.text(f"\n******************************************")
        p.text(f"\n Total Contado: R$ {float(total_contado):.2f}\n")
        p.text(f"\n Observação:{observacao if observacao else '---'}\n")
        
        p.text(f"\n******************************************\n")
        p.set(align='center')
        p.text("Assinatura: __________________\n\n")
        p.cut()

        print(f"Fechamento impresso com sucesso em {impressora_ip}")

    except Exception as e:
        print(f"Erro ao imprimir fechamento: {e}")


@fechamento_bp.route('/SELECT_IMPRESSORA', methods=['GET'])
def select_impressora():
    try:
        conn = sqlite3.connect(CAMINHO_DB_LOCAL)
        cur = conn.cursor()
        cur.execute("SELECT id, ip, nome_impressora, porta FROM IMPRESSORAS")
        result = cur.fetchall()
        conn.close()
        return jsonify([{ "id": row[0], "ip": row[1], "nome_impressora": row[2], "porta": row[3] } for row in result]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



