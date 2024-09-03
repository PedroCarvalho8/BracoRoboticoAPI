CREATE TABLE IF NOT EXISTS modes
(
    mode_id TEXT CONSTRAINT mode_id_pk PRIMARY KEY,
    mode_highscore NUMBER(10) CONSTRAINT mode_highscore_ck CHECK(mode_highscore>=0)
);

CREATE TABLE IF NOT EXISTS games
(
    game_id TEXT CONSTRAINT game_id_pk PRIMARY KEY,
    game_player_name VARCHAR2(20),
    game_score NUMBER(10) CONSTRAINT game_score_ck CHECK(game_score>=0),
    game_mode_id TEXT CONSTRAINT game_mode_nn NOT NULL,
    game_status TEXT CONSTRAINT game_status_nn NOT NULL,
    CONSTRAINT game_mode_fk FOREIGN KEY(game_mode_id) REFERENCES modes(mode_id)
);
