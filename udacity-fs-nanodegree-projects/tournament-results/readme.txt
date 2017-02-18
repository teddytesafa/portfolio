-- SUMMARY --
The tournament application enables creating a swiss style pairing of players.
With it, it is possible to add and remove players, report standings, and do swiss pairings.

--CONTENTS OF tournament.zip--
tournament.py
tournament.sql
tournament_test.py
tournament.pyc

--SUCCESSFULLY RUNNING THE PROGRAM--
To successfully run the program, follow the following steps:
(1) Setup the database
To successfully run the program, you need to have postgresql database installed. If you don't have postgresql database installed, please check "https://wiki.postgresql.org/wiki/Detailed_installation_guides" for detailed installation instructions.
If you have postgresql database installed, please follow the following steps to setup the tournament database:
  (a) Download the tournament folder to the working directory
  (b) Switch to the working directory 
  (c) In command line / terminal, type psql
  (d) Then on the => prompt type \i tournament.sql
  (e) Now you can exit the database with \q command
  (f) To test the program, run "python tournament_test.py" on the command line
 (2) Using functions in tournament.py
   (a) To delete players use deletePlayers()
   (b) To delete matches use deleteMatches()
   (c) To count players use countPlayers()
   (d) To register payer use registerPlayer(name) 
   (e) To report player standing, use playerStanding()
   (f) To report match, use reportMatch(winner,loser)
   () To do swiss pairing, use swissPairings()

