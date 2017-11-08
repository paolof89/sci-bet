# -*- coding: utf-8 -*-
import os
import click
import logging
import pandas as pd
import pymysql
from sqlalchemy import create_engine
pymysql.install_as_MySQLdb() #Install MySQL driver
from src.features.dummy_featutes import elo_features


@click.command()
@click.option('--output-filepath', type=click.Path(), default='data/processed/dummy_features.csv')
def main(output_filepath):
    """
    """
    logger = logging.getLogger(__name__)
    logger.info('Build features')

    # db = my.connect(host='localhost', user='root', passwd='', db='football_data')
    db = create_engine("mysql://root@localhost/football_data")

    elo_features(db)

    matches = pd.read_sql("select * from match_teams", db)

    matches.to_csv(output_filepath, index=False)
    # logger.info("Loaded matches: ", matches.shape[0])


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    #load_dotenv(find_dotenv())

    main()
