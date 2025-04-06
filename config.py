from flask import Flask, request, jsonify, render_template, Blueprint
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import sqlite3

# Caminho do banco local SQLite
CAMINHO_DB_LOCAL = "vendas.db"

# Instância global do SQLAlchemy (usada no app principal e nos blueprints)
db = SQLAlchemy()

# Função para inicializar o banco SQLite local
def inicializar_banco_sqlite():
    conn = sqlite3.connect(CAMINHO_DB_LOCAL)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_comanda INTEGER,
            meio_pagamento TEXT,
            valor_total REAL,
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            id_garcom INTEGER
        )
    """)
    conn.commit()
    conn.close()

inicializar_banco_sqlite()