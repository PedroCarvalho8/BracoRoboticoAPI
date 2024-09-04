from flask import jsonify, Blueprint, request
from flask_sock import Sock

from src.main.controllers.game_starter import GameStarter
from src.main.models.repositories.game_events_repository import GameEventsRepository

from src.main.models.settings.db_connection_handler import db_connection_handler



game_routes_bp = Blueprint("game_routes", __name__)

@game_routes_bp.route("/startnewgame", methods=["POST"])
def start_game():
    conn = db_connection_handler.get_connection()
    game_events_repository = GameEventsRepository(conn)
    game_starter = GameStarter(game_events_repository)

    response = game_starter.start_game(request.json)

    return jsonify(response['body']), response['status_code']

@Sock.route(self=Sock(), path="/teste")
def websocket_handler(ws):
    while True:
        pass