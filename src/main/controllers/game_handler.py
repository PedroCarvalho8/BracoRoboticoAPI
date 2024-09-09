from src.models.repositories.game_events_repository import GameEventsRepository
import random
from datetime import datetime, timedelta
from src.main.queues.message_queue import message_queue
from src.main.queues.desafios_queues import desafios_completed, desafios_todo

class GameHandler():
    def __init__(self, game_events_repository) -> None:
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


    def game_handle(self, game_id: str):
        # game_infos = self.__game_events_repository.get_game(game_id)
        desafios_disponiveis = self.__desafios
        max_rounds = len(self.__desafios)
        message_queue.put(f"Maximo de rodadas: {max_rounds}")
        score_por_rodada = 10

        while not desafios_completed.empty():
                desafios_completed.get()

        while not desafios_todo.empty():
                desafios_todo.get()

        for rodada in range(max_rounds):
            if not(self.__flag_acabou_tempo):
                desafio_da_rodada = random.choice(range(len(desafios_disponiveis)))
                self.__desafios_selecionados.append(desafios_disponiveis[desafio_da_rodada])
                desafios_disponiveis.pop(desafio_da_rodada)

                message_queue.put(f"Desafios selecionados: {self.__desafios_selecionados}")
                for desafio in self.__desafios_selecionados:
                    if not(self.__flag_acabou_tempo):
                        self.desafio_atual = desafio
                        desafios_todo.put(desafio)
                        while desafio['status'] != True:
                            print("esperando o desafio ser conlcuido")
                            if datetime.now() >= self.__tempo_final:
                                self.__flag_acabou_tempo = True
                                break
                            if not(desafios_completed.empty()):
                                desafios_completed.get()
                                desafio['status'] = True
                        desafio['status'] = False

                        if not(self.__flag_acabou_tempo):
                            self.__score += score_por_rodada
                            message_queue.put({
                                'body': {
                                    'message': "Um desafio foi confluido!",
                                    'score': self.__score,
                                    'desafio': desafio
                                }
                            })
                
        if self.__flag_acabou_tempo:
            print("O tempo acabou!!!")
            message_queue.put({
                    'body': {
                        'message': "O tempo acabou!",
                        'score': self.__score
                    }
                })
        else:
            tempo_restante = self.__tempo_final - datetime.now()
            message_queue.put({
                    'body': {
                        'message': "Parabéns, você concluiu todos os desafios!",
                        'score': self.__score + int(self.__score * int(tempo_restante.total_seconds()) / 100),
                        'tempo_restante': tempo_restante.total_seconds()
                    }
                })