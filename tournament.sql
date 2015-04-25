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

drop view  if exists CandidateMatches;
drop view  if exists PlayerStandings;
drop table if exists Matches;
drop table if exists Players;

drop function if exists standings_difference(integer, integer);


create table Players (
    id     serial  primary key,
    name   text
);


create table Matches (
    winner integer references Players (id),
    loser  integer references Players (id),
    primary key (winner, loser)
);


create view PlayerStandings as
    -- returns players with most wins first
    select id,
           name,

           (select count(winner) from Matches
            where winner = id)                as wins,

           (select count(loser) from Matches
            where loser = id)                 as losses,

           (select count(*) from Matches
            where winner = id or loser = id)  as matches

    from Players
    order by wins desc, id asc;
           

create function standings_difference(player1 integer, player2 integer) 
returns integer as $$
    select abs((select wins from PlayerStandings where id = player1) -
               (select wins from PlayerStandings where id = player2))::int;
$$ language sql;


create view CandidateMatches as
    -- List all possible matches for next round
    --     - Return the 2 players and their difference in the standings
    -- Restrictions:
    --     - A player cannot play his/her self
    --     - A pair only appears once -- if (p1,p2) exists, suppress (p2,p1).
    --     - A player cannot play the same player a second time

    select p1.id   as id1,
           p1.name as name1, 
           p2.id   as id2, 
           p2.name as name2,
           standings_difference(p1.id, p2.id) as ranking_difference
    from Players as p1 
          cross join Players as p2
    where p1.id < p2.id -- eliminate  (id1, id1) -- same player
                        -- keep only one of [(id1, id2), (id2, id1)]
          -- eliminate players who have already played each other
      and not exists(select 1 from Matches
                     where (winner = p1.id and loser = p2.id)
                        or (winner = p2.id and loser = p1.id))
    order by ranking_difference asc, id1 asc;
