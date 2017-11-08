# -*- coding: utf-8 -*-
import logging
import os
import click
import pandas as pd
import pymysql
from sqlalchemy import create_engine
pymysql.install_as_MySQLdb() #Install MySQL driver


@click.command()
@click.option('--input-file', type=click.Path(exists=True), default='data/processed/dummy_features.csv')
@click.option('--output-file', default='data/bets/dummy_bets.csv')
def main(input_file, output_file):
    """
    Compute dummy bets based on elo score. If HomeTeamElo > AwayTeamElo then bet=H else bet=A
    :param input_file: input file with necessary features
    :param output_file: output file with format: MATCH_ID, BH, BD, BA
    :return:
    """
    logger = logging.getLogger(__name__)
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

    logger.info('Load bets saved in: {}'.format(input_file))
    df = pd.read_csv(input_file)

    df['BH'] = 0
    df['BD'] = 0
    df['BA'] = 0

    home_bet = df.HomeTeamElo > df.AwayTeamElo
    away_bet = df.HomeTeamElo < df.AwayTeamElo

    df.loc[home_bet, 'BH'] = 1
    df.loc[away_bet, 'BA'] = 1

    df[['MATCH_ID', 'BH', 'BD', 'BA']].to_csv(output_file, index=False)


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    project_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)

    main()

