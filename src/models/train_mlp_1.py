# -*- coding: utf-8 -*-
import logging
import os
import click
import pandas as pd
import numpy as np
from src.libs.utils import read_yaml, read_query
from sklearn.preprocessing import StandardScaler
from keras.models import Sequential, Model
from keras.layers import Dense, Dropout, Input, Embedding, Flatten
import pathlib
import keras.backend as K
from keras.callbacks import TensorBoard
from keras.layers.merge import concatenate
from sqlalchemy import create_engine
import csv
from src.libs.models_utils import save_model

@click.command()
@click.option('--input-query', type=click.Path(exists=True), default='queries/mlp_1_input.sql')
def main(input_query):
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

    teams = pd.read_sql("select team_id, long_name from teams", con=db)

    df = df.set_index('MATCH_ID')
    df = df.loc[~(df[cfg['features']+cfg['output']].isnull().any(1))]
    train = df.loc[df.season_code.isin(cfg['train_seasons'])]
    test = df.loc[df.season_code.isin(cfg['test_seasons'])]

    train_HomeTeam = train.HomeTeam
    train_AwayTeam = train.AwayTeam
    team_number = int(max(train_HomeTeam.unique()))+1

    test = test.loc[(test.HomeTeam.isin(train_HomeTeam)) & (test.AwayTeam.isin(train_AwayTeam))]
    test_HomeTeam = test.HomeTeam
    test_AwayTeam = test.AwayTeam

    ss = StandardScaler()
    train_x = ss.fit_transform(X=train[cfg['features']])
    train_y = pd.get_dummies(train[cfg['output']])

    test_x = ss.transform(X=test[cfg['features']])
    test_y = pd.get_dummies(test[cfg['output']])


    #### MLP MODEL ####
    mlp_input = Input(shape=(train_x.shape[1], ))
    input_home_team = Input(shape=(1,))
    input_away_team = Input(shape=(1,))

    embedding_home_team = Embedding(team_number, 3)(input_home_team)
    flatten_home_team = Flatten()(embedding_home_team)

    embedding_away_team = Embedding(team_number, 3)(input_away_team)
    flatten_away_team = Flatten()(embedding_away_team)

    merge = concatenate([flatten_home_team, flatten_away_team])
    merge = concatenate([mlp_input, merge])

    layer1 = Dense(10, activation='relu')(merge)
    layer2 = Dense(10, activation='relu')(layer1)
    layer3 = Dense(10, activation='relu')(layer2)
    dense_output = Dense(train_y.shape[1], activation='softmax')(layer3)

    model = Model(inputs=[mlp_input, input_home_team, input_away_team], outputs=[dense_output])
    ###################

    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    print(model.summary())
    delete_folder(pathlib.Path('Graph'))

    tb_callback = TensorBoard(log_dir='Graph', histogram_freq=5, write_graph=True, batch_size=10, embeddings_freq=20)
    teams_ = pd.merge(pd.DataFrame(data=np.arange(team_number), columns=['team_id']),teams, on='team_id', how='left')
    teams_.to_csv('Graph/teams.tsv', sep='\t', index=False, quoting=csv.QUOTE_NONNUMERIC)

    model.fit([train_x, train_HomeTeam, train_AwayTeam], train_y.as_matrix(), validation_split=0.01, epochs=2, verbose=2, callbacks=[tb_callback])

    print('Train loss, acc ', model.evaluate([train_x, train_HomeTeam, train_AwayTeam], train_y.as_matrix(), verbose=0))
    print('Test loss, acc ', model.evaluate([test_x, test_HomeTeam, test_AwayTeam], test_y.as_matrix(), verbose=0))

    save_model(model, 'models/mlp_1')


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

