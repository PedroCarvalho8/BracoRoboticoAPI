from flask import jsonify, Blueprint, request
from flask_sock import Sock

routes_bp = Blueprint("trips_routes", __name__)

@routes_bp.route("/endpoint", methods=["POST"])
def route_function():
    return None

@sock.route("/...")
def websocket_handler():
    while True:
        pass