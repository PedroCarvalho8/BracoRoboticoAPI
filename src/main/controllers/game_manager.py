from src.main.models.repositories.game_events_repository import GameEventsRepository

import uuid


class GameManager:
    def __init__(self, game_events_repository: GameEventsRepository) -> None:
        self.__game_events_repository = game_events_repository

    def start_game(self, body) -> dict:
        try: 
            game_id = str(uuid.uuid4())
            game_infos = {
                "game_id": game_id,
                "game_player_name": body["game_player_name"] if body["game_player_name"] else None,
                "game_mode_id": body['game_mode_id']
            }

            self.__game_events_repository.start_new_game(body=game_infos)

            return {
                "body": {
                    "game_id": game_id,
                    "message": "Jogo iniciado com sucesso"
                },
                "status_code": 201
            }

        except Exception as exception:
            return {
                "body": {
                    "error": "Bad Request",
                    "message": str(exception)
                },
                "status_code": 400
            }
        
    def end_game(self, game_id: str) -> dict:
        try:
            self.__game_events_repository.end_game(game_id)

            game_infos = self.__game_events_repository.get_game(game_id)

            return {
                "body": {
                    "game_infos": game_infos,
                    "message": "Jogo encerrado com sucesso"
                },
                "status_code": 200
            }
        
        except Exception as exception:
            return {
                "body": {
                    "error": "Bad Request",
                    "message": str(exception)
                },
                "status_code": 400
            }
        
    def get_game(self, game_id: str) -> dict:
        try:
            game_infos = self.__game_events_repository.get_game(game_id)

            return {
                "body": {
                    "game_infos": game_infos
                },
                "status_code": 200
            }
        
        except Exception as exception:
            return {
                "body": {
                    "error": "Bad Request",
                    "message": str(exception)
                },
                "status_code": 400
            }