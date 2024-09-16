from sqlite3 import Connection

class GameEventsRepository:
    def __init__(self, conn: Connection) -> None:
        self.__conn = conn

    def start_new_game(self, body: dict) -> None:
        cursor = self.__conn.cursor()
        cursor.execute('''
        INSERT INTO games (
            game_id, 
            game_player_name,
            game_score,
            game_mode_id,
            game_status
        )
        VALUES (?, ?, ?, ?, ?)
        ''', (
            body['game_id'],
            body['game_player_name'],
            0,
            body['game_mode_id'],
            "aberto"
            ))
        self.__conn.commit()

    def end_game(self, game_id: str) -> None:
        cursor = self.__conn.cursor()
        cursor.execute('''
        UPDATE games SET game_status = ?
        WHERE game_id = ?
        ''', ("fechado", game_id))
        self.__conn.commit()

    def get_game(self, game_id: str) -> dict:
        cursor = self.__conn.cursor()
        cursor.execute('''
        SELECT * FROM games
        WHERE game_id = ?
        ''', (game_id,))
        game = cursor.fetchone()

        return game

    def game_score_update(self, game_id: str, new_score: int) -> None:
        cursor = self.__conn.cursor()
        cursor.execute('''
        UPDATE games SET game_score = ?
        WHERE game_id = ?
        ''', (new_score, game_id))
        self.__conn.commit()