from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from waitress import serve
import sqlite3
import os
import datetime

# Inicializando o Flask
app = Flask(__name__)
CORS(app)

# Configuração do Banco de Dados PostgreSQL
DB_NAME = "unico"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Testar conexão com PostgreSQL
def testar_conexao():
    try:
        with app.app_context():
            db.session.execute(text("SELECT 1"))
            db.session.commit()
        print("✅ Conexão com o banco de dados PostgreSQL estabelecida com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco de dados: {e}")
        return False

if not testar_conexao():
    exit(1)


@app.route('/')
def index():
    return render_template('index.html')

# Caminho do banco local SQLite
CAMINHO_DB_LOCAL = "vendas.db"

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


### Rotas da API PARA BUSCAR ITENS DA COMANDAATIVA####
@app.route('/comanda/<numeromesa>', methods=['GET'])
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

###ROTA PARA LISTAR COMANDAS ATIVAS####
@app.route('/listarcomandas', methods=['GET'])
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




###ROTA PARA FINALIZAR COMANDA####
@app.route('/finalizar_venda', methods=['POST'])
def finalizar_venda():
    try:
        data = request.get_json()
        numero_comanda = data.get("numero_comanda")
        meio_pagamento = data.get("meio_pagamento")
        valor_total = data.get("valor_total")
        id_garcom = data.get("id_garcom")
        numeromesa = data.get("numeromesa") 

        if not all([numero_comanda, meio_pagamento, valor_total, numeromesa]):
            return jsonify({"error": "Todos os campos são obrigatórios"}), 400

        # Inserir a venda no SQLite
        conn = sqlite3.connect(CAMINHO_DB_LOCAL)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO vendas (numero_comanda, meio_pagamento, valor_total, id_garcom)
            VALUES (?, ?, ?, ?)
        """, (numero_comanda, meio_pagamento, valor_total, id_garcom))
        conn.commit()
        conn.close()

        # Atualizar o status da mesa no banco via SQLAlchemy
        query = text("""
            UPDATE contamesa 
            SET status = 4, horafechamento = NOW()
            WHERE numeromesa = :numeromesa
        """)
        db.session.execute(query, {'numeromesa': numeromesa})
        db.session.commit()

        return jsonify({"message": f"Venda registrada e mesa {numeromesa} fechada com sucesso."}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


###ROTA PARA LISTAR VENDAS FINALIZADAS####
@app.route('/finalizadas', methods=['GET'])
def get_comadas_finalizadas():
    try:
        conn = sqlite3.connect(CAMINHO_DB_LOCAL)
        cur = conn.cursor()
        cur.execute("SELECT id, numero_comanda, meio_pagamento, valor_total, data_hora, id_garcom FROM vendas LIMIT 5 OFFSET 0")

        result = cur.fetchall()
        conn.close()
        return jsonify([{ "id": row[0], "numero_comanda": row[1], "meio_pagamento": row[2], "valor_total": row[3], "data_hora": row[4], "id_garcom": row[5] } for row in result]) if result else jsonify({"message": "Nenhuma comanda finalizada"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

###ROTA PARA LISTAR TOTAL EM R$ DE VENDAS NO DIA ####
@app.route('/total_dia', methods=['GET'])
def get_total_dia():
    try:
        hoje = datetime.datetime.now().strftime('%Y-%m-%d')

        # Conecta ao banco SQLite
        conn = sqlite3.connect(CAMINHO_DB_LOCAL)
        cur = conn.cursor()

        # Consulta o total de vendas feitas hoje
        cur.execute("""
            SELECT SUM(valor_total) AS total_vendas
            FROM vendas
            WHERE DATE(data_hora) = ?
        """, (hoje,))
        result_vendas = cur.fetchone()

        # Consulta a quantidade de comandas fechadas hoje
        cur.execute("""
            SELECT COUNT(*) AS total_fechadas
            FROM vendas
            WHERE DATE(data_hora) = ?
        """, (hoje,))
        result_fechadas = cur.fetchone()

        conn.close()

        # Obtém os valores corretamente
        total_vendas = result_vendas[0] if result_vendas and result_vendas[0] else 0
        total_fechadas = result_fechadas[0] if result_fechadas and result_fechadas[0] else 0

        return jsonify({
            "total_vendas": total_vendas,
            "total_fechadas": total_fechadas
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



###ROTA PARA LISTAR TOTAL EM R$ DE VENDAS NO MÊS ####
@app.route('/vendasmesatual', methods=['GET'])
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
@app.route('/vendas120dias', methods=['GET'])
def get_vendas_por_mes_120_dias():
    try:
        hoje = datetime.datetime.now()
        data_inicio = (hoje - datetime.timedelta(days=120)).strftime('%Y-%m-%d')

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



def run_flask():
    app.run(debug=True, host="0.0.0.0", port=5000)

if __name__ == '__main__':
    run_flask()
