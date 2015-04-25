-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- tables
--     Players (name, id)
--     Matches (winner, loser)  -- can 2 players play each other > 1 time?
--

DROP TABLE IF EXISTS Matches;
DROP TABLE IF EXISTS Players;
DROP TABLE IF EXISTS Tournaments;

DROP FUNCTION IF EXISTS player_standings(INTEGER);


CREATE TABLE Tournaments(
    id SERIAL PRIMARY KEY,
    description TEXT
);

CREATE TABLE Players (
    id            SERIAL PRIMARY KEY,
    name          TEXT,
    tournament_id INTEGER REFERENCES Tournaments (id)
);


CREATE TABLE Matches (
    id            SERIAL PRIMARY KEY,
    tournament_id INTEGER REFERENCES Tournaments (id),
    round         INTEGER,
    winner        INTEGER References Players (id),
    loser         INTEGER References Players (id),

    -- players can only play each other once in a tournament
    UNIQUE (tournament_id, winner, loser),
    UNIQUE (tournament_id, loser,  winner)
);


CREATE FUNCTION player_standings(tournament_id INTEGER)
RETURNS TABLE(player_id INTEGER, player_name TEXT,
              wins INTEGER, losses INTEGER, matches INTEGER) AS $$
    -- returns player in the specified tournament with most wins first

    SELECT 
        id                                  AS player_id,
        name                                AS player_name,

        (SELECT count(winner)::int FROM Matches
          WHERE winner = Players.id)        AS wins,

        (SELECT count(loser)::int FROM Matches
          WHERE loser = Players.id)         AS losses,

        (SELECT count(*)::int FROM Matches
          WHERE winner = Players.id
             OR loser = Players.id)         AS matches

    FROM Players
    WHERE Players.tournament_id = $1 -- tournament_id input parameter
    ORDER BY wins DESC, player_id ASC;

$$ LANGUAGE SQL;

