import time

from src.models.repositories.game_events_repository import GameEventsRepository
import random
from datetime import datetime, timedelta
from src.models.settings.db_connection_handler import DbConnectionHandler

class GameHandler:
    def __init__(self) -> None:
        self.__desafios = [
            {
                'nome': 'A',
                'status': False,
                'timer': 0
            },
            {
                'nome': 'B',
                'status': False,
                'timer': 0,
            },
            {
                'nome': 'C',
                'status': False,
                'timer': 0,
            },
            {
                'nome': 'D',
                'status': False,
                'timer': 0,
            },
            {
                'nome': 'E',
                'status': False,
                'timer': 0,
            }
        ]
        self.__desafios_selecionados = list()
        self.__tempo_inicio = datetime.now()
        self.__tempo_final = self.__tempo_inicio + timedelta(minutes=10)
        self.__flag_acabou_tempo = False
        self.__score = 0
        self.desafio_atual = None


    def game_handle(self, game_id: str, desafios_todo, desafios_completed, message_queue, game_comu_queue) -> None:
        db_connection_handler = DbConnectionHandler()
        conn = db_connection_handler.connect()
        game_events_repository = GameEventsRepository(conn)
        game_infos = game_events_repository.get_game(game_id = game_id)
        message_queue.put(game_infos)
        desafios_disponiveis = self.__desafios.copy()
        max_rounds = 3
        message_queue.put(f"Maximo de rodadas: {max_rounds}")
        score_por_rodada = 10
        desafio_anterior = None

        for rodada in range(max_rounds):
            if not self.__flag_acabou_tempo:
                if len(desafios_disponiveis) == 0:
                    desafios_disponiveis = self.__desafios.copy()

                desafio_da_rodada = random.choice(range(len(desafios_disponiveis)))
                self.__desafios_selecionados.append(desafios_disponiveis.pop(desafio_da_rodada))

                for desafio in self.__desafios:
                    if desafio not in desafios_disponiveis:
                        if desafio['timer'] >= 2:
                            desafios_disponiveis.append(desafio)
                        else:
                            desafio['timer'] += 1

                message = f"Desafios selecionados: {self.__desafios_selecionados}"
                message_queue.put(message)
                game_comu_queue.put(message)
                message = {
                    'body': {
                        'status': "game_open",
                        'message': "desafios_list",
                        'desafios': self.__desafios_selecionados,
                    }
                }
                message_queue.put(message)
                game_comu_queue.put(message)
                time.sleep(len(self.__desafios_selecionados) * 0.4 + 1)
                for desafio in self.__desafios_selecionados:
                    if not self.__flag_acabou_tempo:
                        self.desafio_atual = desafio
                        desafios_todo.put(desafio)
                        while not desafio['status']:
                            if datetime.now() >= self.__tempo_final:
                                self.__flag_acabou_tempo = True
                                break
                            if not(desafios_completed.empty()):
                                desafios_completed.get()
                                time.sleep(0.2)
                                print(".", end='')
                                desafio['status'] = True
                        desafio['status'] = False

                        if not self.__flag_acabou_tempo:
                            self.__score += score_por_rodada
                            message = {
                                'body': {
                                    'message': "desafio_concluido",
                                    'score': self.__score,
                                    'desafio': desafio
                                }
                            }
                            message_queue.put(message)
                            game_comu_queue.put(message)

                print('')

            if self.__flag_acabou_tempo:
                break
                
        if self.__flag_acabou_tempo:
            final_score = self.__score
            message = {
                    'body': {
                        'status': "game_ended",
                        'message': "O tempo acabou!",
                        'score': self.__score
                    }
                }
            message_queue.put(message)
            game_comu_queue.put(message)
        else:
            tempo_restante = self.__tempo_final - datetime.now()
            final_score = self.__score + int(self.__score * int(tempo_restante.total_seconds()) / 50)
            message = {
                    'body': {
                        'status': "game_ended",
                        'message': "desafio_all_ended",
                        'score': final_score,
                        'tempo_restante': tempo_restante.total_seconds()
                    }
                }
            message_queue.put(message)
            game_comu_queue.put(message)

        game_events_repository.game_score_update(game_id=game_id, new_score=final_score)
        game_events_repository.end_game(game_id=game_id)
