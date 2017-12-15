import logging
import pandas as pd
import pymysql
import numpy as np
pymysql.install_as_MySQLdb() #Install MySQL driver


def create_matches_table(db):
    leagues = pd.read_sql('SELECT * FROM add_files WHERE added = 0 and failed = 0', db)

    logger = logging.getLogger(__name__)
    for idx, league in leagues.iterrows():
        s = league.season_code
        c = league.competition_code

        try:
            print('http://www.football-data.co.uk/mmz4281/'+s+'/'+c+'.csv')
            data = pd.read_csv('http://www.football-data.co.uk/mmz4281/'+s+'/'+c+'.csv')
        except Exception as e:
            # TODO manage error file not exist
            print('No data for this league: {competition} / {season}'.format(competition=c, season=s))
            logger.error('Failed: ' + str(e))
            db.execute("UPDATE add_files SET failed=2 "
                       "WHERE competition_code='{competition}' and season_code='{season}'".format(competition=c,
                                                                                                  season=s))
            continue

        try:
            data['Date'] = pd.to_datetime(data['Date'], format='%d/%m/%y').apply(lambda x: x.strftime('%Y-%m-%d'))
        except Exception as e:
            logger.error('Failed: ' + str(e))
            db.execute("UPDATE add_files SET failed=2 "
                       "WHERE competition_code='{competition}' and season_code='{season}'".format(competition=c,
                                                                                                  season=s))
            continue

        data, teams_names = clean_team_names(data)

        update_team_sql = ("UPDATE teams "
           "SET long_name='{team}' "
           "WHERE long_name='{team}'")
        insert_team_sql = ("INSERT INTO teams"
                       "(long_name) "
                       "VALUES ('{team}')")


        for t in teams_names:
            exist = pd.read_sql("SELECT team_id FROM teams WHERE long_name = '{}'".format(t), db)
            if exist.empty:
                sql_execute = db.execute(insert_team_sql.format(team=t))

        data = add_teams_id(data, db)

        data['season_code'] = s
        data['competition_code'] = c

        data = fill_shots_columns(data)

        matches_to_db(data, db, c, s, logger)


def clean_team_names(data):
    teams_names = list(set(data.HomeTeam.unique()) & set(data.AwayTeam.unique()))
    teams_names = [x.replace('\'', ' ') for x in teams_names]
    data['HomeTeam'] = [x.replace('\'', ' ') for x in data['HomeTeam']]
    data['AwayTeam'] = [x.replace('\'', ' ') for x in data['AwayTeam']]
    return data, teams_names

def add_teams_id(data, db):
    teams_sql = ("SELECT m.team_id, m.long_name FROM teams m")
    teams = pd.read_sql(teams_sql, con=db)

    data = pd.merge(data, teams, how='left', left_on='HomeTeam', right_on='long_name')
    data = data.rename(columns={'team_id': 'HomeTeam_id'})
    data = pd.merge(data, teams, how='left', left_on='AwayTeam', right_on='long_name')
    data = data.rename(columns={'team_id': 'AwayTeam_id'})
    return data


def fill_shots_columns(data):
    if 'HS' not in data.columns:
        data['HS'] = np.nan
        data['AS'] = np.nan
        data['HST'] = np.nan
        data['AST'] = np.nan
    return data

def matches_to_db(data, db, c, s, logger):
    try:
        data[['Date', 'competition_code', 'season_code', 'HomeTeam_id', 'AwayTeam_id', 'FTHG', 'FTAG', 'FTR',
              'HTHG', 'HTAG', 'HTR', 'HS', 'AS', 'HST', 'AST', 'B365H', 'B365D', 'B365A', 'BWH', 'BWD', 'BWA', 'WHH',
              'WHD', 'WHA', 'BbMxH', 'BbAvH', 'BbMxD', 'BbAvD', 'BbMxA', 'BbAvA', 'BbMx>2.5', 'BbAv>2.5', 'BbMx<2.5',
              'BbAv<2.5']].to_sql(name='temp_match_teams', con=db, if_exists='replace', index=False)

        insert_team_sql = ("""INSERT INTO match_teams (Date, competition_code, season_code, HomeTeam, AwayTeam,
         FTHG, FTAG, FTR, HTHG, HTAG, HTR, HS, `AS`, HST, AST, B365H, B365D, B365A, BWH, BWD, BWA, WHH,
        WHD, WHA, BbMxH, BbAvH,	BbMxD, BbAvD, BbMxA, BbAvA, `BbMx>2.5`, `BbAv>2.5`, `BbMx<2.5`, `BbAv<2.5`)
         SELECT Date, competition_code, season_code, HomeTeam_id, AwayTeam_id,
          FTHG, FTAG, FTR, HTHG, HTAG, HTR, HS, `AS`, HST, AST, B365H, B365D, B365A, BWH, BWD, BWA, WHH,
        WHD, WHA, BbMxH, BbAvH,	BbMxD, BbAvD, BbMxA, BbAvA, `BbMx>2.5`, `BbAv>2.5`, `BbMx<2.5`, `BbAv<2.5` from temp_match_teams""")

        db.execute(insert_team_sql)
        db.execute("UPDATE add_files SET added=1 "
                   "WHERE competition_code='{competition}' and season_code='{season}'".format(competition=c, season=s))
    except Exception as e:
        logger.error('Failed: ' + str(e))
        db.execute("UPDATE add_files SET failed=1 "
                   "WHERE competition_code='{competition}' and season_code='{season}'".format(competition=c, season=s))


def add_latest_matches(db, season):
    logger = logging.getLogger(__name__)
    data = pd.read_csv('http://www.football-data.co.uk/fixtures.csv')
    data['Date'] = pd.to_datetime(data['Date'], format='%d/%m/%y').apply(lambda x: x.strftime('%Y-%m-%d'))

    data, teams_names = clean_team_names(data)
    data = add_teams_id(data, db)

    data['season_code'] = season
    data['competition_code'] = data['Div']

    data = fill_shots_columns(data)

    matches_to_db(data, db, c='latest', s=season, logger=logger)
