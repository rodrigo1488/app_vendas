from flask import Flask, request, jsonify, render_template,Blueprint
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from waitress import serve
import sqlite3
import os
import datetime
from config import inicializar_banco_sqlite, CAMINHO_DB_LOCAL


listar_totais_bp = Blueprint('listar_totais_bp', __name__)


###ROTA PARA LISTAR TOTAL EM R$ DE VENDAS NO MÊS ####
@listar_totais_bp.route('/vendasmesatual', methods=['GET'])
def get_vendas_por_dia_mes_atual():
    try:
        hoje = datetime.datetime.now()
        mes_atual = f"{hoje.month:02}"
        ano_atual = str(hoje.year)

        conn = sqlite3.connect(CAMINHO_DB_LOCAL)
        cur = conn.cursor()

        cur.execute("""
            SELECT DATE(data_hora) as data, SUM(valor_total) as total
            FROM vendas
            WHERE strftime('%m', data_hora) = ? AND strftime('%Y', data_hora) = ?
            GROUP BY DATE(data_hora)
            ORDER BY DATE(data_hora)
        """, (mes_atual, ano_atual))

        rows = cur.fetchall()
        conn.close()

        vendas_por_dia = []
        for data, total in rows:
            data_formatada = datetime.datetime.strptime(data, '%Y-%m-%d').strftime('%d/%m/%y')
            vendas_por_dia.append({
                "data": data_formatada,
                "valor": round(total, 2)
            })

        return jsonify(vendas_por_dia), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


###ROTA PARA LISTAR TOTAL DE VENDAS NO PERÍODO DE 120 DIAS ####        
@listar_totais_bp.route('/vendas180dias', methods=['GET'])
def get_vendas_por_mes_180_dias():
    try:
        hoje = datetime.datetime.now()
        data_inicio = (hoje - datetime.timedelta(days=180)).strftime('%Y-%m-%d')

        conn = sqlite3.connect(CAMINHO_DB_LOCAL)
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                STRFTIME('%m/%Y', data_hora) AS mes,
                SUM(valor_total) AS total_mes
            FROM vendas
            WHERE DATE(data_hora) >= ?
            GROUP BY mes
            ORDER BY data_hora
        """, (data_inicio,))

        rows = cur.fetchall()
        conn.close()

        resultado = []
        for mes, total in rows:
            resultado.append({
                "total_mes": round(total, 2),
                "mes": mes
            })

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

