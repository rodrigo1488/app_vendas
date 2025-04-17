from flask import Flask, request, jsonify, render_template, Blueprint
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import sqlite3

# Caminho do banco local SQLite
CAMINHO_DB_LOCAL = "vendas.db"

# Instância global do SQLAlchemy (usada no app principal e nos blueprints)
db = SQLAlchemy()


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

    cur.execute("""
        CREATE TABLE IF NOT EXISTS FECHAMENTO_CAIXA (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_caixa REAL,
            total_contado REAL,
            total_abertura REAL,
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            operador TEXT,
            observacao TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS USUARIOS (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            senha TEXT NOT NULL,
            adm BOLEAN DEFALT FALSE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS IMPRESSORAS(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT NOT NULL,
            nome_impressora TEXT NOT NULL,
            porta INTEGER NOT NULL
        )
        """)

    conn.commit()
    conn.close()


inicializar_banco_sqlite()