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

    return {'organisations': to_list(parser.get('plonesource', 'organisations')),
            'repos': to_list(parser.get('plonesource', 'repos'))}


def get_api_token():
    path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'TOKEN'))

    if not os.path.exists(path):
        return None

    with open(path) as file_:
        return file_.read().strip()


CONFIG = read_config()
