from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_cors import CORS
import sys
from PIL import Image
from pystray import Icon, MenuItem as item
from pystray import Menu as menu
import threading
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
from routes.fechamento import fechamento_bp
from routes.usuarios import usuarios_bp
from routes.login import login_bp

# Inicializa o app Flask
app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return jsonify({"message": "Servidor Flask em execução!"})

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

# Registro das blueprints
app.register_blueprint(comandas_bp)
app.register_blueprint(finalizar_venda_bp)
app.register_blueprint(listar_comandas_bp)
app.register_blueprint(listar_totais_bp)
app.register_blueprint(listar_vendas_fechadas_bp)
app.register_blueprint(total_dia_bp)
app.register_blueprint(desempenho_garcom_bp)
app.register_blueprint(fechamento_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(login_bp)

def load_icon():
    if hasattr(sys, "_MEIPASS"):
          base_path = sys._MEIPASS   #PyInstaller extrai os arquivos temporariamente aqui
    else:
        base_path = os.path.abspath(".")
        icon_path = os.path.join(base_path, "icon.ico")
        return Image.open(icon_path)

def on_exit(icon, item):
      icon.stop()
    


def run_tray():
      icon = Icon("ServidorFlask", load_icon(), title="Servidor de Vendas", menu=(
          item('Reiniciar', lambda _: run_flask()),
          item('Sair', on_exit)
      ))    
      icon.run()

def run_flask():
     app.run(debug=False, use_reloader=False, host="0.0.0.0", port=5000)


if __name__ == "__main__":
      flask_thread = threading.Thread(target=run_flask, daemon=True)
      flask_thread.start()
      run_tray()


# if __name__ == "__main__":
#        app.run(debug=True, host="0.0.0.0", port=5000) #serve(app, host="0.0.0.0", port=5000)