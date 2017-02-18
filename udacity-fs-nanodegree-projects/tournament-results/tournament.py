#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
from contextlib import contextmanager

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


@contextmanager
def get_cursor():
    """
    Don't forget to document this function if you use it!
    """
    conn = connect()
    cur = conn.cursor()
    try:
        yield cur
    except:
        raise
    else:
        conn.commit()
    finally:
        cur.close()
        conn.close()

def deleteMatches():
    """Remove all the match records from the database."""
    with get_cursor() as cursor:
         cursor.execute('DELETE FROM MATCHES;')

def deletePlayers():
    """Remove all the player records from the database."""
    with get_cursor() as cursor:
         cursor.execute('DELETE FROM PLAYERS;')

def countPlayers():
    """Returns the number of players currently registered."""
    with get_cursor() as cursor:
         cursor.execute('SELECT COUNT(name) FROM PLAYERS;')
         numberOfPlayers = cursor.fetchone()[0];
    return numberOfPlayers;

def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    inputName = []
    inputName.append(name)
    with get_cursor() as cursor:
         query = "INSERT INTO PLAYERS (name) VALUES (%s)"
         cursor.execute(query, inputName)

def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    with get_cursor() as cursor:
         cursor.execute('SELECT COUNT(name) FROM PLAYERS;')
         query = 'select d.id, d.name, d.wins, (d.wins + d.loses) as matches from (select a.id, a.name, count(b.winner) as wins, count(c.loser) AS loses FROM players a left outer join matches b on a.id = b.winner left outer join matches c on a.id = c.loser GROUP BY a.id, a.name) AS d order by d.wins desc'
         cursor.execute(query)
         playerStanding = cursor.fetchall()
    return playerStanding


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    with get_cursor() as cursor:
         cursor.execute('SELECT COUNT(name) FROM PLAYERS;')
         query = 'INSERT INTO MATCHES(WINNER, LOSER) (SELECT a.ID, b.ID FROM PLAYERS a, PLAYERS b WHERE a.ID = %s AND b.ID = %s);'
         cursor.execute(query, [ winner,  loser])
    
def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
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
    def swissPairingInner(standings, pairings):
	      [i1, n1, w1, l1] = standings.pop()
      	      [i2, n2, w2, l2] = standings.pop()
              pairings.append((i1, n1, i2, n2))
   

	      if len(standings) != 0:
                    
		    return swissPairingInner(standings, pairings)          
	      else:
		    return pairings


    standings = playerStandings()
    pairings = []
    return  swissPairingInner(standings, pairings)
