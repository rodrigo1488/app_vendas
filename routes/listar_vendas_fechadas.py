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
def get_comandas_finalizadas():
    try:
        # Filtros e paginação
        numero_comanda = request.args.get('numero_comanda')  # Parâmetro que estamos utilizando para filtrar
        page = int(request.args.get('page', 1))  # Página atual
        per_page = int(request.args.get('per_page', 10))  # Registros por página
        offset = (page - 1) * per_page  # Cálculo de offset para paginação

        conn = sqlite3.connect(CAMINHO_DB_LOCAL)  # Conexão com o banco de dados
        cur = conn.cursor()

        # Base da query
        where_clause = ""  # Inicializamos sem filtros
        params = []  # Lista para os parâmetros da consulta

        if numero_comanda:  # Se o parâmetro numero_comanda for passado
            where_clause = "WHERE numero_comanda = ?"  # Adicionamos o filtro na cláusula WHERE
            params.append(numero_comanda)  # Adicionamos o valor do parâmetro para ser usado na consulta

        # Total de registros
        cur.execute(f"SELECT COUNT(*) FROM vendas {where_clause}", params)  # Conta o total de registros com o filtro
        total_count = cur.fetchone()[0]  # Obtemos o total de registros

        # Consulta paginada com a cláusula WHERE (se necessário)
        query = f"""
            SELECT id, numero_comanda, meio_pagamento, valor_total, data_hora, id_garcom
            FROM vendas
            {where_clause}  -- Condicionalmente insere WHERE ou nada
            ORDER BY data_hora DESC
            LIMIT ? OFFSET ?
        """
        cur.execute(query, params + [per_page, offset])  # Executa a consulta com paginação
        rows = cur.fetchall()  # Obtém os resultados da consulta
        conn.close()  # Fecha a conexão com o banco

        # Preparando os dados para resposta
        vendas = [
            {
                "id": r[0],
                "numero_comanda": r[1],
                "meio_pagamento": r[2],
                "valor_total": r[3],
                "data_hora": r[4],
                "id_garcom": r[5]
            }
            for r in rows
        ]

        # Retorna a resposta com os dados de vendas
        return jsonify({
            "page": page,
            "per_page": per_page,
            "total_count": total_count,
            "vendas": vendas
        }), 200

    except Exception as e:
        # Em caso de erro, retornamos a mensagem de erro
        return jsonify({"error": str(e)}), 500
