import json

from flask import jsonify, Blueprint, request
from flask_sock import Sock
import multiprocessing as mp

from src.main.controllers.game_manager import GameManager
from src.models.repositories.game_events_repository import GameEventsRepository

from src.models.settings.db_connection_handler import db_connection_handler

from src.main.controllers.game_handler import GameHandler

from src.main.readers.handReader import ler_mao

import multiprocessing

game_routes_bp = Blueprint("game_routes", __name__)

message_queue = multiprocessing.Queue()

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

    return jsonify({
        'message': "Desafio concluído!"
    }), 200

@game_routes_bp.route("/iniciarjogo/<player_name>", methods=["GET"])
def testar_jogo(player_name):
    desafios_todo = multiprocessing.Queue()
    desafios_completed = multiprocessing.Queue()
    game_comu_queue = multiprocessing.Queue()
    global message_queue


    message_queue.put("Teste iniciado")
    jogo = GameHandler()

    conn = db_connection_handler.get_connection()
    game_events_repository = GameEventsRepository(conn)
    game_manager = GameManager(game_events_repository)
    game = game_manager.start_game(body={
        "game_player_name": player_name,
    })
    game_id = game.get('body').get('game_id')

    process_ler = mp.Process(target=ler_mao, args=(desafios_todo, desafios_completed, game_comu_queue))
    process_game = mp.Process(target=jogo.game_handle, args=(game_id, desafios_todo, desafios_completed, message_queue, game_comu_queue))

    process_ler.start()
    process_game.start()

    process_ler.join()
    process_game.join()

    return jsonify({
        'message': "Teste finalizado!"
    }), 200

@Sock.route(self=Sock(), bp=game_routes_bp, path='/websocket')
def websocket_handler(ws):
    global message_queue
    while True:
         if not message_queue.empty():
             message = message_queue.get()
             message = json.dumps(message) if isinstance(message, dict) else message
             ws.send(message)