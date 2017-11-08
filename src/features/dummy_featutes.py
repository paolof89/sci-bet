
def elo_features(db_connection):

    sql_update_home_elo = """update match_teams set match_teams.HomeTeamElo = (
        select h.Elo from elo_scores h where match_teams.HomeTeam = h.team_id and
        match_teams.Date between h.`From` and h.`To`)
    where
    match_teams.HomeTeamElo is null"""

    db_connection.execute(sql_update_home_elo)

    sql_update_away_elo = """update match_teams set match_teams.AwayTeamElo = (
        select aw.Elo from elo_scores aw where match_teams.AwayTeam = aw.team_id and
        match_teams.Date between aw.`From` and aw.`To`)
    where
    match_teams.AwayTeamElo is null"""

    db_connection.execute(sql_update_away_elo)

