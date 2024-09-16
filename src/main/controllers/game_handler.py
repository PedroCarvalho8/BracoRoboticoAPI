from src.models.repositories.game_events_repository import GameEventsRepository
import random
from datetime import datetime, timedelta
from src.main.queues.message_queue import message_queue
from src.main.queues.desafios_queues import desafios_completed, desafios_todo

class GameHandler:
    def __init__(self, game_events_repository: GameEventsRepository) -> None:
        self.__game_events_repository = game_events_repository
        self.__desafios = [
            {
                'nome': 'A',
                'status': False,
            },
            {
                'nome': 'B',
                'status': False,
            },
            {
                'nome': 'C',
                'status': False,
            },
            {
                'nome': 'D',
                'status': False,
            },
        ]
        self.__desafios_selecionados = list()
        self.__tempo_inicio = datetime.now()
        self.__tempo_final = self.__tempo_inicio + timedelta(minutes=1)
        self.__flag_acabou_tempo = False
        self.__score = 0
        self.desafio_atual = None


    def game_handle(self, game_id: str) -> None:
        game_infos = self.__game_events_repository.get_game(game_id = game_id)
        message_queue.put("!!!GAME INFOS!!!")
        message_queue.put(game_infos)
        desafios_disponiveis = self.__desafios.copy()
        max_rounds = 5
        message_queue.put(f"Maximo de rodadas: {max_rounds}")
        score_por_rodada = 10

        while not desafios_completed.empty():
                desafios_completed.get()

        while not desafios_todo.empty():
                desafios_todo.get()

        for rodada in range(max_rounds):
            if not self.__flag_acabou_tempo:
                if len(desafios_disponiveis) == 0:
                    desafios_disponiveis = self.__desafios.copy()
                desafio_da_rodada = random.choice(range(len(desafios_disponiveis)))
                self.__desafios_selecionados.append(desafios_disponiveis.pop(desafio_da_rodada))

                message_queue.put(f"Desafios selecionados: {self.__desafios_selecionados}")
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
                                desafio['status'] = True
                        desafio['status'] = False

                        if not self.__flag_acabou_tempo:
                            self.__score += score_por_rodada
                            message_queue.put({
                                'body': {
                                    'message': "Um desafio foi concluido",
                                    'score': self.__score,
                                    'desafio': desafio
                                }
                            })
                
        if self.__flag_acabou_tempo:
            final_score = self.__score
            message_queue.put({
                    'body': {
                        'message': "O tempo acabou!",
                        'score': self.__score
                    }
                })
        else:
            tempo_restante = self.__tempo_final - datetime.now()
            final_score = self.__score + int(self.__score * int(tempo_restante.total_seconds()) / 100)
            message_queue.put({
                    'body': {
                        'message': "Todos os desafios foram concluidos",
                        'score': final_score,
                        'tempo_restante': tempo_restante.total_seconds()
                    }
                })

        self.__game_events_repository.game_score_update(game_id=game_id, new_score=final_score)
        self.__game_events_repository.end_game(game_id=game_id)