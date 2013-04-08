from ConfigParser import ConfigParser
import os


def to_list(value):
    return value.strip().split()


def read_config():
    path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'config.ini'))

    parser = ConfigParser()

    with open(path) as file_:
        parser.readfp(file_)

    return {'principals': to_list(parser.get('plonesource', 'principals'))}


CONFIG = read_config()
