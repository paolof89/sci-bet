# -*- coding: utf-8 -*-
import logging
import os
import click
import pandas as pd
from src.libs.bookmaker import BookMaker
from sqlalchemy import create_engine
import pymysql
pymysql.install_as_MySQLdb()

@click.command()
@click.option('--bet-file', type=click.Path(exists=True), default='data/bets/dummy_bets.csv')
def main(bet_file):
    """

    :param bet_file:
    :return:
    """
    logger = logging.getLogger(__name__)
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

    logger.info('Load bets saved in: {}'.format(bet_file))

    bet = pd.read_csv(bet_file)
    db = create_engine("mysql://root@localhost/football_data")

    matches = pd.read_sql(sql="select MATCH_ID, BbAvH, BbAvD, BbAvA, FTR from match_teams", con=db)

    matches = pd.merge(matches, bet, on='MATCH_ID')

    bm = BookMaker()
    matches = bm.simulate(matches)
    matches = matches.dropna(0)
    print('Yield: {}'.format(bm.compute_yield(matches)))
    print('Total payout: {}'.format(sum(matches.payout)))
    print('Total bet: {}'.format(sum(matches.bet_value)))


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    main()

