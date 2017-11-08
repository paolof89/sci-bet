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

    create_matches_table(db)

    create_elo_dict(db)

    create_elo_scores(db)



if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)

    main()
