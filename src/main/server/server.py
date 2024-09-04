from flask import Flask
from flask_sock import Sock
from src.main.routes.routes import game_routes_bp

sock = Sock()

app = Flask(__name__)
sock.init_app(app)
app.register_blueprint(game_routes_bp)
