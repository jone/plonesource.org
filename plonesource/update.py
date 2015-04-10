from datetime import datetime
from plonesource import config
from pygithub3 import Github
from pygithub3.exceptions import NotFound
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
    organisations = reversed(config.get('organisations', []))
    repos = config.get('repos', [])

    repositories = {}

    for principal in organisations:
        load_principal_repositories(principal, repositories)

    for fullname in repos:
        try:
            load_single_repositories(fullname, repositories)
        except EmptyRepositoryException:
            pass

    return generate_sources_cfg(repositories)


def load_principal_repositories(principal, result):
    for repo in GITHUB.repos.list_by_org(principal).all():
        while repo.fork:
            # The repo from repos.list does not have "parent" set.
            # We need to re-get the repo with the parent.
            repo = get_repository(repo.full_name)

            if not hasattr(repo, 'parent'):
                break
            else:
                repo = repo.parent

        try:
            result[repo.name] = extract_repo_data(repo)
        except EmptyRepositoryException:
            pass


def load_single_repositories(fullname, result):
    repo = get_repository(fullname)
    result[repo.name] = extract_repo_data(repo)


def get_repository(fullname):
    username, reponame = fullname.split('/')
    try:
        return GITHUB.repos.get(user=username, repo=reponame)
    except NotFound:
        print "Repo %s not found." % reponame
        raise EmptyRepositoryException('%s not found.' % reponame)

def extract_repo_data(repo):
    if getattr(repo, 'default_branch', None) is None:
        raise EmptyRepositoryException('%s is empty' % repo.name)

    clone_url = '${buildout:github-cloneurl}${forks:%s}/%s.git' % (
        repo.name, repo.name)

    push_url = '${buildout:github-pushurl}${forks:%s}/%s.git' % (
        repo.name, repo.name)

    return {'name': repo.name,
            'owner': repo.owner.login,
            'clone_url': clone_url,
            'push_url': push_url,
            'branch': repo.default_branch}


def generate_sources_cfg(repositories):
    branches = []
    sources = []
    forks = []

    for _name, item in repositories.items():
        branches.append('%(name)s = %(branch)s' % item)
        sources.append('%(name)s = git %(clone_url)s pushurl=%(push_url)s'
                       ' branch=${branches:%(name)s}' % item)
        forks.append('%(name)s = %(owner)s' % item)

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

        '[forks]'] + \
        sorted(forks) + [
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
