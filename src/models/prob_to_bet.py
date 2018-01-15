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
@click.option('--threshold', default=0.1)
def prob_to_bet(model, threshold=0.1):

    threshold = threshold
    logger = logging.getLogger(__name__)
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

    logger.info('Load bets saved in: match_prob')

    db = create_engine("mysql://root@localhost/football_data")
    prob = pd.read_sql("""select * from match_prob where model='{}'""".format(model), con=db)

    quotes = pd.read_sql(sql="select MATCH_ID, BbAvH, BbAvD, BbAvA from matches", con=db)

    matches = pd.merge(quotes, prob, on='MATCH_ID')

    ## strategy value_bet
    strategy = 'value_bet_'+str(threshold)
    prob.loc[prob['pH'] == 0, 'H'] = 0.001
    prob.loc[prob['pD'] == 0, 'D'] = 0.001
    prob.loc[prob['pA'] == 0, 'A'] = 0.001
    matches['fairH'] = 1 / prob['pH']
    matches['fairD'] = 1 / prob['pD']
    matches['fairA'] = 1 / prob['pA']

    matches['bH'] = 0
    matches['bD'] = 0
    matches['bA'] = 0
    matches.loc[matches.BbAvH / matches.fairH > 1+threshold, 'bH'] = 1
    matches.loc[matches.BbAvD / matches.fairD > 1+threshold, 'bD'] = 1
    matches.loc[matches.BbAvA / matches.fairA > 1+threshold, 'bA'] = 1

    matches['MODEL'] = model
    matches['STRATEGY'] = strategy

    matches.to_sql(name='temp_bet', con=db, if_exists='replace')
    db.execute("""Delete from match_bet where MODEL='{}' and strategy='{}' """.format(model, strategy))
    db.execute("""insert into match_bet
        select `MODEL`, `STRATEGY`, `MATCH_ID`, `bH`, `bD`, `bA`, 0
        from temp_bet""")
    db.execute("""drop table temp_bet""")




if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    prob_to_bet()

