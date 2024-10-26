from flask import Flask
from flask_cors import CORS
from flask_sock import Sock
from src.main.routes.routes import game_routes_bp

sock = Sock()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
sock.init_app(app)
app.register_blueprint(game_routes_bp)
