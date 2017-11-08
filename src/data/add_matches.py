#Football Analytics

#Add matches to the database that will be scraped

#Author: Liam Culligan
#Date: January 2017

#Import required packages and functions
import pymysql
pymysql.install_as_MySQLdb() ##Install MySQL driver
import MySQLdb as my

#Connect to the MySQL database
db = my.connect(host = 'localhost', user = 'root', passwd = '', db = 'football_data')

cursor = db.cursor()

#Finding the matches to add is a manual process
#Need to locate the relevant range of match ids
 
#Initialise an empty list
files = []

seasons = ['0910', '1011', '1112', '1213', '1314', '1415', '1516', '1617']
competitions = ["E0", "SP1", "D1", "D2", "F1", "F2", "N1", "B1", "E1", "E2", "SC0", "SC1", "I1", "I2", "T1", "P1"]
#For example...

#English Premier League - competition_id 1
#2012/2013 - season_id 4

#Loop through all seasons and competitions ids for the selected league-season

for s in seasons:
    for c in competitions:
        files.append([s, c])
    
#Insert the matches that will be scraped into the add_matches table 
sql = ("INSERT IGNORE INTO add_files "
      "(season_code, competition_code) "
      "VALUES (%s, %s)")
                
sql_execute = cursor.executemany(sql, files)

#Commit the query
db.commit()

#Close the connection
db.close()

