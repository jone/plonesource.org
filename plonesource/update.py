from datetime import datetime
from plonesource import config
from pygithub3 import Github
import os


GITHUB = Github(token=config.get_api_token())


OUTPUT_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..',
                 'static', 'sources.cfg'))

TIMESTAMP_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..',
                 'static', 'last-update.txt'))


class EmptyRepositoryException(Exception):
    """This happens on freshly created repositories which have no code yet.
    """


def update(config):
    principals = reversed(config.get('principals', []))
    repos = config.get('repos', [])

    repositories = {}

    for principal in principals:
        load_principal_repositories(principal, repositories)

    for fullname in repos:
        try:
            load_single_repositories(fullname, repositories)
        except EmptyRepositoryException:
            pass

    return generate_sources_cfg(repositories)


def load_principal_repositories(principal, result):
    for repo in GITHUB.repos.list(principal).all():
        while repo.fork:
            # The repo from repos.list does not have "parent" set.
            # We need to re-get the repo with the parent.
            repo = get_repository(repo.full_name).parent

        try:
            result[repo.name] = extract_repo_data(repo)
        except EmptyRepositoryException:
            pass


def load_single_repositories(fullname, result):
    repo = get_repository(fullname)
    result[repo.name] = extract_repo_data(repo)


def get_repository(fullname):
    username, reponame = fullname.split('/')
    return GITHUB.repos.get(user=username, repo=reponame)


def extract_repo_data(repo):
    if getattr(repo, 'master_branch', None) is None:
        raise EmptyRepositoryException('%s is empty' % repo.name)

    return {'name': repo.name,
            'clone_url': '${buildout:github-cloneurl}%s.git' % repo.full_name,
            'push_url': '${buildout:github-pushurl}%s.git' % repo.full_name,
            'branch': repo.master_branch}


def generate_sources_cfg(repositories):
    branches = []
    sources = []

    for _name, item in repositories.items():
        branches.append('%(name)s = %(branch)s' % item)
        sources.append('%(name)s = git %(clone_url)s pushurl=%(push_url)s'
                       ' branch=${branches:%(name)s}' % item)

    lines = [
        '[buildout]',
        'auto-checkout =',
        'sources = sources',
        'github-cloneurl = ${buildout:github-https}',
        'github-pushurl = ${buildout:github-ssh}',
        '',
        '',

        'github-https = https://github.com/',
        'github-ssh = git@github.com:',
        'github-git = git://github.com/',
        '',
        '',

        '[branches]'] + \
        sorted(branches) + [
        '',
        '',

        '[sources]'] + \
        sorted(sources) + [
        '']

    return '\n'.join(lines)


def main():
    data = update(config.CONFIG)
    with open(OUTPUT_PATH, 'w+') as file_:
        file_.write(data)

    with open(TIMESTAMP_PATH, 'w+') as file_:
        file_.write(datetime.now().isoformat())

    print 'Updated'
