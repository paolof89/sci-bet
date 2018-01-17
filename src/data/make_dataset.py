# -*- coding: utf-8 -*-
import os
import click
import logging
import pymysql
from sqlalchemy import create_engine
pymysql.install_as_MySQLdb() #Install MySQL driver
from src.data.from_footballdata import create_matches_table
from src.data.from_clubelo import create_elo_scores, create_elo_dict

@click.command()
def main():
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')

    db = create_engine("mysql://root@localhost/football_data")

    #create_matches_table(db)

    #create_elo_dict(db)

    create_elo_scores(db)

    update_elo_on_match_table(db)


def update_elo_on_match_table(db_connection):
    sql_update_home_elo = """update matches set matches.HomeTeamElo = (
        select h.Elo from elo_scores h where matches.HomeTeam = h.team_id and
        matches.Date between h.`From` and h.`To`)
    where
    matches.HomeTeamElo is null"""

    db_connection.execute(sql_update_home_elo)

    sql_update_away_elo = """update matches set matches.AwayTeamElo = (
        select aw.Elo from elo_scores aw where matches.AwayTeam = aw.team_id and
        matches.Date between aw.`From` and aw.`To`)
    where
    matches.AwayTeamElo is null"""

    db_connection.execute(sql_update_away_elo)


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    # not used in this stub but often useful for finding various files
    project_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)

    main()
