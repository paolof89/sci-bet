import yaml

def read_yaml(yaml_file):
    with open(yaml_file, 'r') as ymlfile:
        yml = yaml.load(ymlfile)
    return yml

def read_query(path):
    with open(path, 'r') as f:
        query = f.read()
    return query