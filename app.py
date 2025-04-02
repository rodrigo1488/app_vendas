from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import sqlite3
import os
import datetime

# Inicializando o Flask
app = Flask(__name__)

# Configuração do Banco de Dados
DB_NAME = "unico"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializando o SQLAlchemy com o app
db = SQLAlchemy(app)

# Função para testar a conexão com o banco de dados usando SQLAlchemy
def testar_conexao():
    try:
        with app.app_context():
            db.session.execute(text("SELECT 1"))
            db.session.commit()
        print("✅ Conexão com o banco de dados estabelecida com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco de dados: {e}")
        return False

# Verifica a conexão antes de iniciar a aplicação
if not testar_conexao():
    exit(1)
@app.route('/comanda/<numeromesa>', methods=['GET'])
def get_comanda_por_mesa(numeromesa):
    try:
        query = text("""
            SELECT 
                c.nomeproduto,
                c.quantidade,
                c.precounitario,
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
            return jsonify({"message": "Nenhum item encontrado para essa mesa"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/status/<int:numeromesa>', methods=['POST'])
def set_status(numeromesa):
    try:
        query = text("""
            UPDATE contamesa 
            SET status = 4, horafechamento = NOW() 
            WHERE numeromesa = :numeromesa
        """)
        db.session.execute(query, {'numeromesa': numeromesa})
        db.session.commit()

        return jsonify({"message": f"Status da mesa {numeromesa} atualizado para 4 e horário de fechamento registrado"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Caminho do banco local SQLite
CAMINHO_DB_LOCAL = "vendas.db"

# Criar banco e tabela, se não existirem
def inicializar_banco():
    conn = sqlite3.connect(CAMINHO_DB_LOCAL)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_comanda INTEGER,
            meio_pagamento TEXT,
            valor_total REAL,
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# Inicializa o banco ao iniciar o app
inicializar_banco()

@app.route('/finalizar_venda', methods=['POST'])
def finalizar_venda():
    try:
        data = request.get_json()

        numero_comanda = data.get("numero_comanda")
        meio_pagamento = data.get("meio_pagamento")
        valor_total = data.get("valor_total")

        if not numero_comanda or not meio_pagamento or not valor_total:
            return jsonify({"error": "Todos os campos são obrigatórios"}), 400

        conn = sqlite3.connect(CAMINHO_DB_LOCAL)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO vendas (numero_comanda, meio_pagamento, valor_total) 
            VALUES (?, ?, ?)
        """, (numero_comanda, meio_pagamento, valor_total))

        conn.commit()
        conn.close()

        return jsonify({"message": "Venda registrada com sucesso"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/vendas_dia', methods=['GET'])
def get_vendas_dia():
    try:
        # Obtém a data de hoje
        hoje = datetime.datetime.now().strftime('%Y-%m-%d')

        # Consulta as vendas feitas hoje
        query = text("""
            SELECT numero_comanda, meio_pagamento, valor_total, data_hora
            FROM vendas
            WHERE DATE(data_hora) = :hoje
        """)
        
        # Executa a consulta com a data de hoje
        result = db.session.execute(query, {'hoje': hoje}).fetchall()

        if result:
            # Retorna os resultados no formato JSON
            return jsonify([dict(row._mapping) for row in result]), 200
        else:
            return jsonify({"message": "Nenhuma venda registrada para hoje"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/total_dia', methods=['GET'])
def get_total_dia():
    try:
        # Obtém a data de hoje
        hoje = datetime.datetime.now().strftime('%Y-%m-%d')

        # Consulta as vendas feitas hoje
        query = text("""
            SELECT SUM(valor_total) AS total_vendas
            FROM vendas
            WHERE DATE(data_hora) = :hoje
        """)
        
        # Executa a consulta com a data de hoje
        result = db.session.execute(query, {'hoje': hoje}).fetchall()

        if result:
            # Retorna os resultados no formato JSON
            return jsonify([dict(row._mapping) for row in result]), 200
        else:
            return jsonify({"message": "Nenhuma venda registrada para hoje"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500





# Rodando a aplicação Flask
if __name__ == '__main__':
    app.run(debug=True)
