# Football Bets

# Create the database structure

# Author: Paolo Finardi
# Date: Dec 2017

# Tanks to Liam Culligan

# Import required packages and functions
import pymysql
pymysql.install_as_MySQLdb()  # Install MySQL driver
import  as my
from sqlalchemy import create_engine

user='paolo'
pwd='password'

# Drop existing db
try:
# Connect to the localhost
    db = my.connect(host='localhost', user=user, passwd=pwd)
    cursor = db.cursor()

# Drop old version of the database
    sql = ("DROP DATABASE football_data ")
    sql_execute = cursor.execute(sql)
    # Commit the query
    db.commit()
    # Close the connection
    db.close()
except:
    pass


# Create new database
db = my.connect(host='localhost', user=user, password=pwd)
cursor = db.cursor()
sql = ("CREATE DATABASE football_data COLLATE 'utf8_general_ci'")
sql_execute = cursor.execute(sql)
db.commit()
db.close()


# Connect to the newly-created database
db = my.connect(host='localhost', user=user, passwd=pwd, db='football_data')
cursor = db.cursor()


# Create teams table
sql = ("CREATE TABLE teams "
       "(team_id INT(8) UNSIGNED PRIMARY KEY AUTO_INCREMENT, "
       "long_name VARCHAR(255), "
       "short_name VARCHAR(255), "
       "logo VARCHAR(255), "
       "colour VARCHAR(255),"
       "elo_name VARCHAR(255),"
       "OPTA_name VARCHAR(255))")
sql_execute = cursor.execute(sql)


# Create seasons table
sql = ("CREATE TABLE seasons "
       "(season_code VARCHAR(4)  PRIMARY KEY, "
       "season_name VARCHAR(7))")
sql_execute = cursor.execute(sql)


# Insert season rows
sql = ("INSERT INTO seasons "
       "(season_code, season_name) "
       "VALUES (%s, %s)")
sql_execute = cursor.executemany(sql, [['0910', "2009/10"], ['1011', "2010/11"], ['1112', "2011/12"]
    , ['1213', "2012/13"], ['1314', "2013/14"], ['1415', "2014/15"], ['1516', "2015/16"], ['1617', "2016/17"]])


# Create competitions table
sql = ("CREATE TABLE competitions "
       "(competition_code VARCHAR(4) PRIMARY KEY, "
       "competition_name VARCHAR(100))")
sql_execute = cursor.execute(sql)


# Insert competition rows
sql = ("INSERT INTO competitions "
       "(competition_name, competition_code) "
       "VALUES (%s, %s)")
competitions = [["English Premier League", "E0"], ["Spanish La Liga", "SP1"], \
                ["German Bundesliga", "D1"], ["German Bundesliga 2", "D2"], \
                ["French Ligue 1", "F1"], ["French Ligue 2", "F2"],
                ["Dutch Eredivisie", "N1"], ["Belgium", "B1"], \
                ["English Championship", "E1"], ["English League 1", "E2"], \
                ["Scotland Premier League", "SC0"], ["Scotland Division 1", "SC1"], \
                ["Italian Serie A", "I1"], ["Italian Serie B", "I2"], \
                ["Turkish Super Lig", "T1"], ["Portugal La Liga", "P1"]]
sql_execute = cursor.executemany(sql, competitions)


# Create matches table
sql = ("""CREATE TABLE matches (
	`MATCH_ID` BIGINT(20) UNSIGNED PRIMARY KEY AUTO_INCREMENT,
	`Date` DATE NULL DEFAULT NULL,
	`competition_code` VARCHAR(4) NULL,
	`season_code` VARCHAR(4) NULL,
	`HomeTeam` MEDIUMINT(8) UNSIGNED DEFAULT NULL,
	`AwayTeam` MEDIUMINT(8) UNSIGNED DEFAULT NULL,
	`FTHG` BIGINT(20) NULL DEFAULT NULL,
	`FTAG` BIGINT(20) NULL DEFAULT NULL,
	`FTR` TEXT NULL,
	`HomeTeamElo` MEDIUMINT(8) UNSIGNED DEFAULT NULL,
	`AwayTeamElo` MEDIUMINT(8) UNSIGNED DEFAULT NULL,
	`HTHG` BIGINT(20) NULL DEFAULT NULL,
	`HTAG` BIGINT(20) NULL DEFAULT NULL,
	`HTR` TEXT NULL,
	`HS` DOUBLE NULL DEFAULT NULL,
	`AS` DOUBLE NULL DEFAULT NULL,
	`HST` DOUBLE NULL DEFAULT NULL,
	`AST` DOUBLE NULL DEFAULT NULL,
	`B365H` DOUBLE NULL DEFAULT NULL,
	`B365D` DOUBLE NULL DEFAULT NULL,
	`B365A` DOUBLE NULL DEFAULT NULL,
	`BWH` DOUBLE NULL DEFAULT NULL,
	`BWD` DOUBLE NULL DEFAULT NULL,
	`BWA` DOUBLE NULL DEFAULT NULL,
	`WHH` DOUBLE NULL DEFAULT NULL,
	`WHD` DOUBLE NULL DEFAULT NULL,
	`WHA` DOUBLE NULL DEFAULT NULL,
	`BbMxH` DOUBLE NULL DEFAULT NULL,
	`BbAvH` DOUBLE NULL DEFAULT NULL,
	`BbMxD` DOUBLE NULL DEFAULT NULL,
	`BbAvD` DOUBLE NULL DEFAULT NULL,
    `BbMxA` DOUBLE NULL DEFAULT NULL,
    `BbAvA` DOUBLE NULL DEFAULT NULL,
    `BbMx>2.5` DOUBLE NULL DEFAULT NULL,
    `BbAv>2.5` DOUBLE NULL DEFAULT NULL,
    `BbMx<2.5`  DOUBLE NULL DEFAULT NULL,
    `BbAv<2.5` DOUBLE NULL DEFAULT NULL,
    INDEX date_teams USING BTREE (Date, HomeTeam, AwayTeam))
    COLLATE='latin1_swedish_ci'
    ENGINE=InnoDB""")
sql_execute = cursor.execute(sql)


# Create table of matches to add to the database
sql = ("CREATE TABLE add_files "
       "(file_id INT(10) UNSIGNED PRIMARY KEY AUTO_INCREMENT, "
       "competition_code VARCHAR(4), "
       "season_code VARCHAR(4), "
       "added TINYINT(1) UNSIGNED DEFAULT '0', "
       "failed TINYINT(1) UNSIGNED DEFAULT '0', "
       "KEY added (added))")
sql_execute = cursor.execute(sql)


# Create table of elo records
sql = ("""create table elo_scores (
       `team_id` BIGINT(20) NOT NULL,
       `Club` VARCHAR(30) NULL,
       `Elo` DOUBLE NULL,
       `From` DATE NOT NULL,
       `To` DATE NOT NULL,
        CONSTRAINT PK_elo primary key (team_id, `From`, `To`))
       COLLATE='latin1_swedish_ci'
       ENGINE=InnoDB""")
sql_execute = cursor.execute(sql)


# Create table for probability outcome
sql = ("""create table match_prob (
       `MODEL` VARCHAR(20) NOT NULL,
       `MATCH_ID` BIGINT(20) UNSIGNED,
       `pH` DOUBLE NULL,
       `pD` DOUBLE NULL,
       `pA` DOUBLE NULL,
       CONSTRAINT PK_elo primary key (`MODEL`, `MATCH_ID`))
       COLLATE='latin1_swedish_ci'
       ENGINE=InnoDB""")
sql_execute = cursor.execute(sql)


# Create table for bet outcome
sql = ("""create table match_bet (
       `MODEL` VARCHAR(20) NOT NULL,
       `STRATEGY` VARCHAR(20) NOT NULL,
       `MATCH_ID` BIGINT(20) UNSIGNED,
       `bH` DOUBLE NULL,
       `bD` DOUBLE NULL,
       `bA` DOUBLE NULL,
       `payout` DOUBLE NULL,
       CONSTRAINT PK_elo primary key (`MODEL`, `STRATEGY`, `MATCH_ID`))
       COLLATE='latin1_swedish_ci'
       ENGINE=InnoDB""")
sql_execute = cursor.execute(sql)


# Commit the query
db.commit()
# Close the connection
db.close()
