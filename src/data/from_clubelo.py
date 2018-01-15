import logging
import pandas as pd
import requests
import io
import re
import datetime


def create_elo_dict(db):
    elo_dict = pd.read_csv('data/raw/elo_dictionary.csv', sep=';')[['fd.name', 'elo.name']]
    elo_dict = elo_dict.rename(columns={'fd.name':'fd_name', 'elo.name':'elo_name'})
    elo_dict['updated_untill'] = pd.to_datetime(None)
    elo_dict.to_sql(name='elo_master', con=db, if_exists='replace', index=False)

    db.execute("""update teams set elo_name = (
        select `elo_name` from elo_master where teams.long_name = elo_master.`fd_name`)""")


def create_elo_scores(db):
    logger = logging.getLogger(__name__)

    teams = pd.read_sql("""select team_id, elo_name from teams""", db)

    for idx, team in teams.iterrows():
        try:
            url = "http://api.clubelo.com/"+re.sub(' ', '', team.elo_name)
            logger.info(url.strip())
            s = requests.get(url).content
            eloRank = pd.read_csv(io.StringIO(s.decode('utf-8')))
            eloRank.From = pd.to_datetime(eloRank.From).dt.strftime('%Y-%m-%d')
            eloRank.To = pd.to_datetime(eloRank.To).dt.strftime('%Y-%m-%d')
            eloRank['team_id'] = team.team_id
            now = datetime.datetime.now().strftime('%Y-%m-%d')

            try:
                last = pd.read_sql("""SELECT updated_untill FROM elo_master
                 WHERE elo_name = '{}' """.format(team.elo_name), db).updated_untill.values[0]
                if last is None:
                    last = '2009-01-01'
            except:
                last = '2009-01-01'

            logger.info('Last valid:', last)

            eloRank = eloRank.loc[(eloRank.From >= last)&(eloRank.To <= now)]

            eloRank[['team_id', 'Club', 'Elo', 'From', 'To']].to_sql(name='temp_elo', con=db, if_exists='replace', index=False)

            insert_elo_sql = ("""INSERT INTO elo_scores
                             SELECT * from temp_elo""")

            db.execute(insert_elo_sql)

            update_elo_master = ("""UPDATE elo_master SET updated_untill = '{to}'
            WHERE elo_name = '{elo_name}'""".format(to=now, elo_name=team.elo_name))
            db.execute(update_elo_master)

        except Exception as e:
            logger.error('Failed: ' + str(e))
            logger.error('on ', team.elo_name)


def update_elo_scores(db):
    logger = logging.getLogger(__name__)

    teams = pd.read_sql("""select team_id, elo_name from teams
    where team_id in (select HomeTeam FROM matches WHERE FTR IS NULL)
    or team_id in (select AwayTeam FROM matches WHERE FTR IS NULL)""", db)

    dates = pd.read_sql("""select Date FROM matches WHERE FTR IS NULL""", db)

    for date in dates.Date.unique():
        try:
            url = "http://api.clubelo.com/"+str(date)
            logger.info(url.strip())
            s = requests.get(url).content
            eloRank = pd.read_csv(io.StringIO(s.decode('utf-8')))
            eloRank.From = pd.to_datetime(eloRank.From).dt.strftime('%Y-%m-%d')
            eloRank.To = pd.to_datetime(eloRank.To).dt.strftime('%Y-%m-%d')

            eloRank = pd.merge(eloRank, teams, how='inner', right_on='elo_name', left_on='Club')


            eloRank[['team_id', 'Club', 'Elo', 'From', 'To']].to_sql(name='temp_elo', con=db, if_exists='replace', index=False)

            delete_past = ("""delete a.* from  elo_scores a, temp_elo b
            where a.team_id = b.team_id and a.`From` = b.`From` """)
            db.execute(delete_past)

            insert_elo_sql = ("""INSERT INTO elo_scores
                             SELECT * from temp_elo""")
            db.execute(insert_elo_sql)

        except Exception as e:
            logger.error('Failed: ' + str(e))
            logger.error('on ', date)


def update_elo_on_matches(db):
    logger = logging.getLogger(__name__)
    sql = """UPDATE """


