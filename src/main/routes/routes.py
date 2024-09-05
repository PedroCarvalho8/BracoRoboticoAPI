from flask import jsonify, Blueprint, request
from flask_sock import Sock

from src.main.controllers.game_manager import GameManager
from src.main.models.repositories.game_events_repository import GameEventsRepository

from src.main.models.settings.db_connection_handler import db_connection_handler

from src.main.queues.message_queue import message_queue

game_routes_bp = Blueprint("game_routes", __name__)



@game_routes_bp.route("/startnewgame", methods=["POST"])
def start_game():
    conn = db_connection_handler.get_connection()
    game_events_repository = GameEventsRepository(conn)
    game_manager = GameManager(game_events_repository)

    response = game_manager.start_game(request.json)

    return jsonify(response['body']), response['status_code']


@game_routes_bp.route("/<game_id>/end_game", methods=["GET"])
def end_game(game_id):
    conn = db_connection_handler.get_connection()
    game_events_repository = GameEventsRepository(conn)
    game_manager = GameManager(game_events_repository)

    response = game_manager.end_game(game_id)

    return jsonify(response['body']), response['status_code']


@game_routes_bp.route("/<game_id>")
def get_game(game_id):
    conn = db_connection_handler.get_connection()
    game_events_repository = GameEventsRepository(conn)
    game_manager = GameManager(game_events_repository)

    response = game_manager.get_game(str(game_id))

    message_queue.put(f"Novo evento para o jogo {game_id}")

    return jsonify(response['body']), response['status_code']


@Sock.route(self=Sock(), bp=game_routes_bp, path='/teste')
def websocket_handler(ws):
    while True:
         if not message_queue.empty():
            message = message_queue.get()
            ws.send(message)