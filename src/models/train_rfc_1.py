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
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import log_loss
import pickle

@click.command()
@click.option('--input-query', type=click.Path(exists=True), default='queries/mlp_1_input.sql')
def main(input_query='queries/mlp_1_input.sql'):
    """
    Compute dummy bets based on elo score. If HomeTeamElo > AwayTeamElo then bet=H else bet=A
    :param input_file: input file with necessary features
    :param output_file: output file with format: MATCH_ID, BH, BD, BA
    :return:
    """
    logger = logging.getLogger(__name__)
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    config_file = 'configs/rfc1_config.yml'
    logger.info('Model config in {}'.format(config_file))
    cfg = read_yaml(config_file)

    db = create_engine("mysql://root@localhost/football_data")
    logger.debug('Load match features in: {}'.format(input_query))
    query = read_query(input_query)
    df = pd.read_sql(query, con=db)

    df = df.set_index('MATCH_ID')
    df = df.loc[~(df[cfg['features']+cfg['output']].isnull().any(1))]
    train = df.loc[df.season_code.isin(cfg['train_seasons'])]
    valid = df.loc[df.season_code.isin(cfg['valid_seasons'])]
    test = df.loc[df.season_code.isin(cfg['test_seasons'])]

    ss = StandardScaler()
    train_x = ss.fit_transform(X=train[cfg['features']])
    train_y = train[cfg['output']]

    valid_x = ss.transform(X=valid[cfg['features']])
    valid_y = valid[cfg['output']]

    test_x = ss.transform(X=test[cfg['features']])
    test_y = test[cfg['output']]

    clf = RandomForestClassifier(n_estimators=25, max_leaf_nodes=50)
    clf.fit(train_x, train_y)
    clf_probs = clf.predict_proba(test_x)
    sig_clf = CalibratedClassifierCV(clf, method="sigmoid", cv="prefit")
    sig_clf.fit(valid_x, valid_y)
    sig_clf_probs = sig_clf.predict_proba(test_x)

    train_score = log_loss(train_y, sig_clf.predict_proba(train_x))
    test_score = log_loss(test_y, sig_clf_probs)

    print('Train loss ', train_score)
    print('Test loss ', test_score)

    pickle.dump(sig_clf, open("models/rfc_1.p", "wb"))




def delete_folder(pth):
    for sub in pth.iterdir():
        if sub.is_dir():
            delete_folder(sub)
        else:
            sub.unlink()
    #pth.rmdir() # if you just want to delete dir content, remove this line


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    project_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    main()

