# -*- coding: utf-8 -*-
import os
import click
import logging
import pandas as pd
import pymysql
from sqlalchemy import create_engine
pymysql.install_as_MySQLdb() #Install MySQL driver
from src.features.features_functions import average_last_5_matches


@click.command()
def main():
    """
    """
    logger = logging.getLogger(__name__)
    logger.info('Build features')

    db = create_engine("mysql://root@localhost/football_data")

    matches = pd.read_sql("select * from match_teams", db)
    matches = average_last_5_matches(matches)

    matches[['MATCH_ID', 'h_avg_scored', 'h_avg_conceded', 'h_avg_elo',
       'Team_y', 'a_avg_scored', 'a_avg_conceded', 'a_avg_elo']]\
        .to_sql(name='features_basic', con=db, if_exists='replace', index=False)

    db.execute("""alter table features_basic
    ADD PRIMARY KEY(MATCH_ID)""")


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    #load_dotenv(find_dotenv())

    main()
