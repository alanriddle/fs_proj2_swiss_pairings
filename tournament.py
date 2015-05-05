#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def createTournament(description):
    """Create a record in the tournaments table."""
    conn = connect()
    cur = conn.cursor()
    sql = """INSERT INTO Tournaments (description)
             VALUES (%s) RETURNING id"""
    cur.execute(sql, (description,))
    tournament_id = cur.fetchall()[0]
    conn.commit()
    conn.close()

    return tournament_id


def deleteMatches(tournament_id):
    """
    Remove all the match records from the database 
    for the specified tournament.
    """
    conn = connect()
    cur = conn.cursor()
    sql = "DELETE FROM Matches WHERE tournament_id = (%s)"
    cur.execute(sql, (tournament_id,))
    conn.commit()
    conn.close()


def deletePlayers(tournament_id):
    """
    Remove all the player records from the database
    for the specified tournament.
    """
    conn = connect()
    cur = conn.cursor()
    sql = "DELETE FROM PlayersInTournaments WHERE tournament_id = (%s)"
    cur.execute(sql, (tournament_id,))
    conn.commit()
    conn.close()


def countPlayers(tournament_id):
    """Returns the number of players currently registered in tournament."""
    conn = connect()
    cur = conn.cursor()
    sql = "SELECT count(*) FROM PlayersInTournaments WHERE tournament_id = (%s)"
    cur.execute(sql, (tournament_id,))
    player_count = cur.fetchone()[0]
    conn.close()
    return player_count


def registerPlayerInDatabase(name):
    """
    Adds a player to the Player table and returns the player id.

    Note: To enter the player in a tournament, you will need to
          call enterPlayerInTournament(tournament_id, player_id).

    Args:
        name: the name of the player
    """
    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO Players (name) values (%s) RETURNING id", 
                (name,))
    player_id = cur.fetchone()[0]
    conn.commit()
    conn.close()

    return player_id


def enterPlayerInTournament(tournament_id, player_id):
    """
    Adds a player for the the specified tournament.
  
    Args:
      tournament_id: id of tournament
      player_id: the player's id
    """
    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO PlayersInTournaments (tournament_id, player_id) values (%s, %s)", 
                (tournament_id, player_id,))
    conn.commit()
    conn.close()


def playerStandings(tournament_id):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Arg:
      Id of tournament
    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    conn = connect()
    cur = conn.cursor()
    sql = """SELECT player_id, player_name, wins, matches
             FROM player_standings(%s)"""
    cur.execute(sql, (tournament_id,))
    player_standings = cur.fetchall()
    conn.close()
    return player_standings


def reportMatch(tournament_id, round_number, winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      tournament_id: id of tournament
      round_number: the number of the round -- first round is 1
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    conn = connect()
    cur = conn.cursor()
    sql = """INSERT INTO Matches (tournament_id, round, winner, loser)
             VALUES (%s, %s, %s, %s)"""
    cur.execute(sql, (tournament_id, round_number, winner, loser))
    conn.commit()
    conn.close()
 

def make_pairings(standings):
    """
    standings is a list of player records with highest rankings first.

    returns a set of matches. A match is tuple of 2 player records.
    """

    assert len(standings) % 2 == 0, "number of players must be even"
    pairings = []
    i = 0
    while i < len(standings):
        pairings.append((standings[i][0], standings[i][1],
                         standings[i+1][0], standings[i+1][1]))
        i += 2

    return pairings


def swissPairings(tournament_id):
    """
    Returns a list of pairs of players for the next round of a match for
    specified tournament.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
   
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    conn = connect()
    cur = conn.cursor()
    sql = "SELECT player_id, player_name FROM player_standings(%s)"
    cur.execute(sql, (tournament_id,))
    standings = cur.fetchall()

    pairings = make_pairings(standings)
    conn.close()
    
    return pairings

