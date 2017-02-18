-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'tournament'
  AND pid <> pg_backend_pid();

DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;

\c tournament

DROP TABLE IF EXISTS players;
CREATE TABLE players (
    id serial PRIMARY KEY NOT NULL,
    name VARCHAR NOT NULL
);
DROP TABLE IF EXISTS matches;
CREATE TABLE matches (
    matchid serial,
    winner INT references players(id) ON DELETE CASCADE, 
    loser INT references players(id) ON DELETE CASCADE
);
