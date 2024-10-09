# SQL-komennot, jolla muokkasin tietokannan rakennetta

USE flight_game;

DROP TABLE game;
DROP TABLE goal_reached;
DROP TABLE goal;

# Tarkistetaan tietokannan taulut
SHOW TABLES;

# Luotiin uusi taulu player_stats

CREATE TABLE player_stats (
    id INT(11) NOT NULL AUTO_INCREMENT,
    player_name VARCHAR(50) UNIQUE,
    wins INT(11) DEFAULT 0,
    losses INT(11) DEFAULT 0,
    airports_visited TEXT,
    num_airports_visited INT(11),
    time_used VARCHAR(10),
    distance_traveled FLOAT,
    PRIMARY KEY (id));

# Tarkistetaan tietokannan taulut
SHOW TABLES;

# Tarkistetaan taulun player_stats rakenne ja sarakkeet
DESCRIBE player_stats;

