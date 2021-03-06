# -*- coding: utf-8 -*-
import logging
import os
import click
import pandas as pd
import numpy as np
from src.libs.utils import read_yaml, read_query
from sklearn.preprocessing import StandardScaler
from sqlalchemy import create_engine
import csv
from src.libs.models_utils import load_model
import datetime as dt


@click.command()
@click.option('--input-query', type=click.Path(exists=True), default='queries/mlp_1_input.sql')
@click.option('--save_train_prediction', default=True)
def main(input_query, save_train_prediction):
    """
    Compute dummy bets based on elo score. If HomeTeamElo > AwayTeamElo then bet=H else bet=A
    :param input_file: input file with necessary features
    :param output_file: output file with format: MATCH_ID, BH, BD, BA
    :return:
    """
    logger = logging.getLogger(__name__)
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

    config_file = 'configs/mlp1_config.yml'
    logger.info('Model config in {}'.format(config_file))
    cfg = read_yaml(config_file)

    db = create_engine("mysql://root@localhost/football_data")
    logger.debug('Load match features in: {}'.format(input_query))
    query = read_query(input_query)
    df = pd.read_sql(query, con=db)

    df = df.set_index('MATCH_ID')
    df = df.loc[~(df[cfg['features']].isnull().any(1))]
    train = df.loc[df.season_code.isin(cfg['train_seasons'])]
    test = df.loc[df.season_code.isin(cfg['test_seasons'])]

    train_HomeTeam = train.HomeTeam
    train_AwayTeam = train.AwayTeam

    test = test.loc[(test.HomeTeam.isin(train_HomeTeam)) & (test.AwayTeam.isin(train_AwayTeam))]
    test_HomeTeam = test.HomeTeam
    test_AwayTeam = test.AwayTeam

    ss = StandardScaler()
    train_x = ss.fit_transform(X=train[cfg['features']])
    train_y = pd.get_dummies(train[cfg['output']])

    test_x = ss.transform(X=test[cfg['features']])
    test_y = pd.get_dummies(test[cfg['output']])

    model = load_model('models/mlp_1')
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    print('Train loss, acc ', model.evaluate([train_x, train_HomeTeam, train_AwayTeam], train_y.as_matrix(), verbose=0))
    print('Test loss, acc ', model.evaluate([test_x, test_HomeTeam, test_AwayTeam], test_y.as_matrix(), verbose=0))

    db.execute(""" Delete from match_prob where MODEL='{}' """.format('mlp_1'))
    probs = pd.DataFrame(data=model.predict([test_x, test_HomeTeam, test_AwayTeam]),
                        columns=['pA', 'pD', 'pH'], index=test.index)
    prob_to_db(probs, db)

    if save_train_prediction == True:
        probs = pd.DataFrame(data=model.predict([train_x, train_HomeTeam, train_AwayTeam]),
                         columns=['pA', 'pD', 'pH'], index=train.index)
        prob_to_db(probs, db)


def prob_to_db(probs, db):
    probs['MODEL'] = 'mlp_1'
    probs.to_sql(name='temp_prob', con=db, if_exists='replace')

    db.execute("""insert into match_prob
        select `MODEL`, `MATCH_ID`, `pH`, `pD`, `pA`
        from temp_prob """)

    db.execute("""drop table temp_prob""")


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    project_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    main()

