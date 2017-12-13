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
@click.option('--model', default='mlp_1')
@click.option('--strategy', default='value_bet_0.5')
def main(model='mlp_1', strategy='value_bet_0.5'):
    """

    :param bet_file:
    :return:
    """
    logger = logging.getLogger(__name__)
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

    logger.info('Load bets: model={model}, strategy={strategy}'.format(model=model, strategy=strategy))

    db = create_engine("mysql://root@localhost/football_data")
    bet = pd.read_sql(sql="select MATCH_ID, bH, bD, bA from match_bet where MODEL = '{model}' and STRATEGY = '{strategy}'"
                      .format(model=model, strategy=strategy), con=db)

    matches = pd.read_sql(sql="select MATCH_ID, BbAvH, BbAvD, BbAvA, FTR from match_teams", con=db)

    matches = pd.merge(matches, bet, on='MATCH_ID')

    bm = BookMaker()
    matches = bm.simulate(matches)
    matches = matches.dropna(0)
    print('Yield: {}'.format(bm.compute_yield(matches)))
    print('Total payout: {}'.format(sum(matches.payout)))
    print('Total bet: {}'.format(sum(matches.bet_value)))
    print('Total match: {}'.format(matches.shape[0]))

    matches[['MATCH_ID', 'payout']].to_sql(name='temp_payout', con=db, if_exists='replace')
    db.execute("""UPDATE match_bet t1, temp_payout t2
    SET t1.payout = t2.payout
    WHERE t1.MATCH_ID = t2.MATCH_ID and MODEL = '{model}' and STRATEGY = '{strategy}'""".format(model=model, strategy=strategy))
    db.execute("""drop table temp_payout""")


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    main()

