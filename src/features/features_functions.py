import pandas as pd

def average_last_5_matches(matches):
    #matches = pd.read_sql(con=con, sql="Select * from match_teams")
    team_history = matches.melt(id_vars=['MATCH_ID', 'Date', 'competition_code', 'season_code'], value_vars=['HomeTeam', 'AwayTeam'],
                                var_name='home_or_away', value_name='Team')

    team_history = pivot_stats(df=team_history, matches=matches, home_stat='FTHG', away_stat='FTAG', stat_name='scored')
    team_history = pivot_stats(df=team_history, matches=matches, home_stat='FTAG', away_stat='FTHG', stat_name='conceded')
    team_history = pivot_stats(df=team_history, matches=matches, home_stat='HomeTeamElo', away_stat='AwayTeamElo', stat_name='elo')

    team_history.sort_values(by=['Team','Date'], inplace=True)
    team_history.set_index(['MATCH_ID','home_or_away'], inplace=True)
    team_history = team_history.groupby(['season_code', 'Team'], as_index=False).rolling(window=5).mean()

    matches = pd.merge(matches, team_history, how='left',
                       left_on=['Date', 'competition_code', 'season_code', 'HomeTeam'],
                       right_on=['Date', 'competition_code', 'season_code', 'Team'])
    matches.rename(columns={'scored': 'h_avg_scored', 'conceded': 'h_avg_conceded', 'elo': 'h_avg_elo'},
                   inplace=True)

    matches = pd.merge(matches, team_history, how='left',
                       left_on=['Date', 'competition_code', 'season_code', 'AwayTeam'],
                       right_on=['Date', 'competition_code', 'season_code', 'Team'])
    matches.rename(columns={'scored': 'a_avg_scored', 'conceded': 'a_avg_conceded', 'elo': 'a_avg_elo'},
                   inplace=True)

    return matches


def pivot_stats(df, matches, home_stat, away_stat, stat_name):
    df = df.copy()
    df[stat_name] = 0
    df = pd.merge(df, matches[['MATCH_ID', 'HomeTeam', home_stat]], how='left',
                    left_on=['MATCH_ID', 'Team'], right_on=['MATCH_ID', 'HomeTeam'])
    df = pd.merge(df, matches[['MATCH_ID', 'AwayTeam', away_stat]], how='left',
                    left_on=['MATCH_ID', 'Team'], right_on=['MATCH_ID', 'AwayTeam'])

    df.loc[df.home_or_away=='HomeTeam', stat_name] = df.loc[df.home_or_away=='HomeTeam', home_stat] 
    df.loc[df.home_or_away=='AwayTeam', stat_name] = df.loc[df.home_or_away=='AwayTeam', away_stat]

    df.drop(axis=1, labels=['HomeTeam', 'AwayTeam', home_stat, away_stat], inplace=True)
    return df



from sqlalchemy import create_engine
con = create_engine("mysql://root@localhost/football_data")

