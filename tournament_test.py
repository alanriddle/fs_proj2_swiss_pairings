#!/usr/bin/env python
#
# Test cases for tournament.py

from tournament import *

def testDeleteMatches(tournament_id):
    deleteMatches(tournament_id)
    print "1. Old matches for a tournament can be deleted."


def testDelete(tournament_id):
    deleteMatches(tournament_id)
    deletePlayers(tournament_id)
    print "2. Player records for a tournament can be deleted."


def testCount(tournament_id):
    deleteMatches(tournament_id)
    deletePlayers(tournament_id)
    c = countPlayers(tournament_id)
    if c == '0':
        raise TypeError(
            "countPlayers() should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "3. After deleting, countPlayers() returns zero."


def testRegister(tournament_id):
    deleteMatches(tournament_id)
    deletePlayers(tournament_id)
    player_id = registerPlayerInDatabase("Chandra Nalaar")
    enterPlayerInTournament(tournament_id, player_id)

    c = countPlayers(tournament_id)
    if c != 1:
        raise ValueError(
            "After one player registers, countPlayers() should be 1.")
    print "4. After registering a player, countPlayers() returns 1."


def testRegisterCountDelete(tournament_id):
    deleteMatches(tournament_id)
    deletePlayers(tournament_id)
    mc = registerPlayerInDatabase("Markov Chaney")
    jm = registerPlayerInDatabase("Joe Malik")
    mt = registerPlayerInDatabase("Mao Tsu-hsi")
    ah = registerPlayerInDatabase("Atlanta Hope")

    enterPlayerInTournament(tournament_id, mc)
    enterPlayerInTournament(tournament_id, jm)
    enterPlayerInTournament(tournament_id, mt)
    enterPlayerInTournament(tournament_id, ah)

    c = countPlayers(tournament_id)
    if c != 4:
        raise ValueError(
            "After registering four players, countPlayers should be 4.")
    deletePlayers(tournament_id)
    c = countPlayers(tournament_id)
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "5. Players can be registered and deleted."


def testStandingsBeforeMatches(tournament_id):
    deleteMatches(tournament_id)
    deletePlayers(tournament_id)
    mm = registerPlayerInDatabase("Melpomene Murray")
    rs = registerPlayerInDatabase("Randy Schwartz")

    enterPlayerInTournament(tournament_id, mm)
    enterPlayerInTournament(tournament_id, rs)

    standings = playerStandings(tournament_id)
    if len(standings) < 2:
        raise ValueError("Players should appear in playerStandings even before "
                         "they have played any matches.")
    elif len(standings) > 2:
        raise ValueError("Only registered players should appear in standings.")
    if len(standings[0]) != 4:
        raise ValueError("Each playerStandings row should have four columns.")
    [(id1, name1, wins1, matches1), (id2, name2, wins2, matches2)] = standings
    if matches1 != 0 or matches2 != 0 or wins1 != 0 or wins2 != 0:
        raise ValueError(
            "Newly registered players should have no matches or wins.")
    if set([name1, name2]) != set(["Melpomene Murray", "Randy Schwartz"]):
        raise ValueError("Registered players' names should appear in standings, "
                         "even if they have no matches played.")
    print "6. Newly registered players appear in the standings with no matches."


def testReportMatches(tournament_id):
    deleteMatches(tournament_id)
    deletePlayers(tournament_id)

    bw = registerPlayerInDatabase("Bruno Walton")
    bo = registerPlayerInDatabase("Boots O'Neal")
    cb = registerPlayerInDatabase("Cathy Burton")
    dg = registerPlayerInDatabase("Diane Grant")

    enterPlayerInTournament(tournament_id, bw)
    enterPlayerInTournament(tournament_id, bo)
    enterPlayerInTournament(tournament_id, cb)
    enterPlayerInTournament(tournament_id, dg)

    standings = playerStandings(tournament_id)
    [id1, id2, id3, id4] = [row[0] for row in standings]

    round = 1
    reportMatch(tournament_id, round, id1, id2)
    reportMatch(tournament_id, round, id3, id4)
    standings = playerStandings(tournament_id)
    
    for (i, n, w, m) in standings:
        if m != 1:
            raise ValueError("Each player should have one match recorded.")
        if i in (id1, id3) and w != 1:
            raise ValueError("Each match winner should have one win recorded.")
        elif i in (id2, id4) and w != 0:
            raise ValueError("Each match loser should have zero wins recorded.")
    print "7. After a match, players have updated standings."


def testPairings(tournament_id):
    deleteMatches(tournament_id)
    deletePlayers(tournament_id)

    ts = registerPlayerInDatabase("Twilight Sparkle")
    fs = registerPlayerInDatabase("Fluttershy")
    aj = registerPlayerInDatabase("Applejack")
    pp = registerPlayerInDatabase("Pinkie Pie")

    enterPlayerInTournament(tournament_id, ts)
    enterPlayerInTournament(tournament_id, fs)
    enterPlayerInTournament(tournament_id, aj)
    enterPlayerInTournament(tournament_id, pp)

    standings = playerStandings(tournament_id)
    [id1, id2, id3, id4] = [row[0] for row in standings]
    round = 1
    reportMatch(tournament_id, round, id1, id2)
    reportMatch(tournament_id, round, id3, id4)
    pairings = swissPairings(tournament_id)
    if len(pairings) != 2:
        raise ValueError(
            "For four players, swissPairings should return two pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    correct_pairs = set([frozenset([id1, id3]), frozenset([id2, id4])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After one match, players with one win should be paired.")
    print "8. After one match, players with one win are paired."


def standingsWithOpponentWins(tournament_id):
    conn = connect()
    cur = conn.cursor()
    sql = """SELECT player_id, player_name, wins, opponent_wins, matches
             FROM player_standings(%s)"""
    cur.execute(sql, (tournament_id,))
    standings = cur.fetchall()
    conn.close()

    return standings


def printStandings(tournament_id, heading, column_widths):
    """Print out a table of player standings."""

    line_length = sum(column_widths)
    heading_format = "{:^" + str(line_length) + "}"
    print heading_format.format(*heading)

    columns1 = ["Player", "", "", "Opponent", "Total"]
    columns2 = ["Id", "Name", "Wins", "Wins", "Matches"]
    row_format = ["{:^" + str(c) + "}" for c in column_widths]
    row_format = "".join(row_format)

    # Print out 2 row column headings and a row of '-'
    print row_format.format(*columns1)
    print row_format.format(*columns2)
    print "-" * line_length

    # For each player in standings, print a row 
    standings = standingsWithOpponentWins(tournament_id)
    for row in standings:
        print row_format.format(*row)


def testOpponentWins4Players(tournament_id):
    """
    Play a tournament with 4 players for 2 rounds.

    Verify the opponent match wins are calculated correctly.
    Here the opponent match wins for a player X is equal to
    the sum of the wins for all opponents that player X 
    defeated. Wins for opponents who defeated player X are
    not counted.
    """

    deleteMatches(tournament_id)
    deletePlayers(tournament_id)

    ts = registerPlayerInDatabase("Twilight Sparkle")
    fs = registerPlayerInDatabase("Fluttershy")
    aj = registerPlayerInDatabase("Applejack")
    pp = registerPlayerInDatabase("Pinkie Pie")

    enterPlayerInTournament(tournament_id, ts)
    enterPlayerInTournament(tournament_id, fs)
    enterPlayerInTournament(tournament_id, aj)
    enterPlayerInTournament(tournament_id, pp)

    pairings = swissPairings(tournament_id)
    id1 = pairings[0][0]
    id2 = pairings[0][2]
    id3 = pairings[1][0]
    id4 = pairings[1][2]

    # Play the first round
    round = 1
    reportMatch(tournament_id, round, id1, id2)
    reportMatch(tournament_id, round, id3, id4)

    standings = standingsWithOpponentWins(tournament_id)
    actual_opponent_wins   = set([(p[0], p[3]) for p in standings])
    s = standings
    expected_opponent_wins = set([(s[0][0], 0), (s[1][0], 0),
                                  (s[2][0], 1), (s[3][0], 1)])

    if actual_opponent_wins != expected_opponent_wins:
       raise ValueError("Expected opponent wins after Round 1"
                        "do not match actual.")
    print "9a. After one round, expected opponent wins equals"
    print "    actual opponent wins."

    # print out table of standings after round 1
    print        # blank line
    column_widths = [6, 20, 7, 10, 8]
    heading = ["STANDINGS AFTER ROUND 1"]
    printStandings(tournament_id, heading, column_widths)

    pairings = swissPairings(tournament_id)
    id1 = pairings[0][0]
    id2 = pairings[0][2]
    id3 = pairings[1][0]
    id4 = pairings[1][2]

    # Play the second round
    round = 2
    reportMatch(tournament_id, round, id1, id2)
    reportMatch(tournament_id, round, id3, id4)

    standings = standingsWithOpponentWins(tournament_id)
    actual_opponent_wins = set([(s[0], s[3]) for s in standings])
    # top player opponent wins is 2
    # others are all zero -- only counts opponent wins for opponents player defeated
    expected_opponent_wins = set([(s[0], 2) for s in standings])
                              

    # print out table of standings after round 2
    print        # blank line
    if actual_opponent_wins != expected_opponent_wins:
        raise ValueError("Expected opponent wins after Round 2"
                         " do not match actual.")
    print "9b. After two rounds, expected opponent wins equals"
    print "    actual opponent wins."

    print
    heading = ["STANDINGS AFTER ROUND 2"]
    printStandings(tournament_id, heading, column_widths)


if __name__ == '__main__':
    # 1 tournament in database

    tournament_id = createTournament('Test 1 tournament')

    testDeleteMatches(tournament_id)
    testDelete(tournament_id)
    testCount(tournament_id)
    testRegister(tournament_id)
    testRegisterCountDelete(tournament_id)
    testStandingsBeforeMatches(tournament_id)
    testReportMatches(tournament_id)
    testPairings(tournament_id)
    print "Success!  All tests for single tournament pass!"

    print
    print "Testing Opponent wins -- 4 player tournament"
    testOpponentWins4Players(tournament_id)

