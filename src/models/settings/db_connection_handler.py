import sqlite3
from sqlite3 import Connection

class DbConnectionHandler:
    def __init__(self) -> None:
        self.__connection_string = "storage.db"
        self.__conn = None

    def connect(self) -> Connection :
        self.__conn = sqlite3.connect(self.__connection_string, check_same_thread=False)
        return self.__conn

    def get_connection(self) -> Connection:
        return self.__conn
    
db_connection_handler = DbConnectionHandler()