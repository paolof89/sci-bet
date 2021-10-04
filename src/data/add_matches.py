#Football Analytics
from sqlalchemy import create_engine
import click
import pandas as pd
from dotenv import dotenv_values


@click.command()
def add_matches():
    #Connect to the MySQL database
    config = dotenv_values()
    db = create_engine("mysql://{user}:{pwd}@localhost/football_data".format(user=config['USER'], pwd=config['PWD']))

    #Initialise an empty list
    files = []
    seasons = ['2021'] #['0910', '1011', '1112', '1213', '1314', '1415', '1516', '1617', '1718', '1819', '1920', '2021']

    competitions = ['I1'] #["E0", "SP1", "D1", "D2", "F1", "F2", "N1", "B1", "E1", "E2", "SC0", "SC1", "I1", "I2", "T1", "P1"]

    for s in seasons:
        for c in competitions:
            files.append([s, c])
    df = pd.DataFrame(data=files, columns=['season', 'competion'])
    #Insert the matches that will be scraped into the add_matches table
    df.to_sql(name='temp_add_files', con=db, if_exists='replace')
    db.execute("""insert into add_files (competition_code, season_code, added, failed)
        select competion, season, 0, 0
        from temp_add_files""")
    db.execute("""drop table temp_add_files""")


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    add_matches()
