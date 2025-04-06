from flask import Flask
from flask_cors import CORS
from sqlalchemy import text
from waitress import serve
import os

from config import db  # <-- pega a instância de db aqui

# Blueprints
from routes.finalizar_venda import finalizar_venda_bp
from routes.total_dia import total_dia_bp
from routes.listar_vendas_fechadas import listar_vendas_fechadas_bp
from routes.listar_totais import listar_totais_bp
from routes.comandas import comandas_bp
from routes.listar_comandas import listar_comandas_bp
from routes.desempenho_garcom import desempenho_garcom_bp

# Inicializa o app Flask
app = Flask(__name__)
CORS(app)

# Configuração do banco PostgreSQL
DB_NAME = "unico"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa o SQLAlchemy com a app
db.init_app(app)

# Testar conexão com PostgreSQL
def testar_conexao():
    try:
        with app.app_context():
            db.session.execute(text("SELECT 1"))
            db.session.commit()
        return True
    except Exception as e:
        print(f"Erro ao conectar no PostgreSQL: {e}")
        return False

if not testar_conexao():
    exit(1)

# Registra blueprints
app.register_blueprint(comandas_bp)
app.register_blueprint(finalizar_venda_bp)
app.register_blueprint(listar_comandas_bp)
app.register_blueprint(listar_totais_bp)
app.register_blueprint(listar_vendas_fechadas_bp)
app.register_blueprint(total_dia_bp)
app.register_blueprint(desempenho_garcom_bp)

def run_flask():
    app.run(debug=True, host="0.0.0.0", port=5000)

if __name__ == '__main__':
    run_flask()
