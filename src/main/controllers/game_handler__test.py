from src.models.repositories.game_events_repository import GameEventsRepository
from src.main.controllers.game_handler import GameHandler
from src.models.settings.db_connection_handler import db_connection_handler
import pytest
from src.main.queues.message_queue import message_queue

def test_game_handler():
    message_queue.put("Teste iniciado")
    print("tamanho: ", message_queue.qsize())
    # conn = db_connection_handler.get_connection()
    # jogo = GameHandler(GameEventsRepository(conn))
    # jogo.game_handle(10)