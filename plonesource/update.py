from plonesource.config import CONFIG


def generate_buildout(principals):
    repositories = {}

    for principal in principals:
        load_repositories(principal, repositories)


def load_repositories(principal, result):
    pass


def main():
    print 'hello world', CONFIG
