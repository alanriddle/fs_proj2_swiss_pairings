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


CREATE OR REPLACE FUNCTION player_wins(tournament_id INTEGER, player_id INTEGER)
RETURNS INTEGER AS $$
    SELECT count(winner)::int 
      FROM Matches
     WHERE Matches.tournament_id = $1 -- input tournament_id
       AND winner = player_id
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION opponent_wins(tournament_id INTEGER,
                                         player_id INTEGER)
RETURNS INTEGER AS $$
    SELECT count(player_wins(tournament_id, loser))
      FROM Matches
     WHERE Matches.tournament_id = $1 
       AND winner = player_id
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION player_standings(tournament_id INTEGER)
RETURNS TABLE(player_id INTEGER, player_name TEXT,
              wins INTEGER, matches INTEGER) AS $$
    -- returns player in the specified tournament with most wins first
    -- tie breaker is opponent match wins

    SELECT 
        id                                  AS player_id,
        name                                AS player_name,
        player_wins(tournament_id, id)      AS wins,
        opponent_wins(tournament_id, id)    AS opponent_wins,

        (SELECT count(*)::int FROM Matches
          WHERE winner = Players.id
             OR loser = Players.id)         AS matches

    FROM Players
    WHERE Players.tournament_id = $1 -- tournament_id input parameter
    ORDER BY wins DESC, opponent_wins DESC;

$$ LANGUAGE SQL;

