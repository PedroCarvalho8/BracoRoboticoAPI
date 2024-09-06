from src.main.models.repositories.game_events_repository import GameEventsRepository
import random

class GameHandler():
    def __init__(self) -> None:
        self.__game_events_repository = GameEventsRepository
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
        self.__desafios_seleciodados = list()

    def game_handle(self, game_id: str):
        game_infos = self.__game_events_repository.get_game(game_id)
        desafios_disponiveis = self.__desafios
        max_rounds = len(self.desafios)
        score_por_rodada = 10
        score=0

        for rodada in range(max_rounds):
            desafio_da_rodada = random.choice(len(desafios_disponiveis)-1)
            self.__desafios_selecionados.append(desafios_disponiveis[desafio_da_rodada])
            desafios_disponiveis.pop(desafio_da_rodada)

            for desafio in self.__desafios_selecionados:
                while desafio['status'] != True:
                    continue
                score += score_por_rodada
                


    