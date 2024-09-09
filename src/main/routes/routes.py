from flask import jsonify, Blueprint, request
from flask_sock import Sock

from src.main.controllers.game_manager import GameManager
from src.models.repositories.game_events_repository import GameEventsRepository

from src.models.settings.db_connection_handler import db_connection_handler

from src.main.queues.message_queue import message_queue
from src.main.queues.desafios_queues import desafios_completed, desafios_todo

from src.main.controllers.game_handler import GameHandler

import json

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

    return jsonify(response['body']), response['status_code']


@game_routes_bp.route("/completardesafio", methods=["GET"])
def completar_desafio_atual():
    if not desafios_todo.empty():
        desafio = desafios_todo.get()
        desafios_completed.put(desafio)

    return jsonify({
        'message': "Desafio concluído!"
    }), 200

@game_routes_bp.route("/testarjogo", methods=["GET"])
def testar_jogo():
    message_queue.put("Teste iniciado")
    conn = db_connection_handler.get_connection()
    jogo = GameHandler(GameEventsRepository(conn))
    jogo.game_handle(10)

    return jsonify({
        'message': "Teste finalizado!"
    }), 200

@Sock.route(self=Sock(), bp=game_routes_bp, path='/teste')
def websocket_handler(ws):
    while True:
         if not message_queue.empty():
            message = message_queue.get()
            ws.send(message)