from sqlite3 import Connection

class GameEventsRepository:
    def __init__(self, conn: Connection) -> None:
        self.__conn = conn

    def game_start(self, body: dict) -> dict:
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
        cursor.commit()

    def game_end(self, game_id: str) -> dict:
        cursor = self.__conn.cursor()
        cursor.execute('''
        UPDATE games SET game_status = ?
        WHERE game_id = ?
        ''', ("fechado", game_id))