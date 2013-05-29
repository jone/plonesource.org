from mocker import MockerTestCase
from unittest2 import TestCase


class GithubStubTestCase(MockerTestCase, TestCase):

    def __init__(self, *args, **kwargs):
        super(GithubStubTestCase, self).__init__(*args, **kwargs)
        self.repositories_by_principal = {}

    def setUp(self):
        super(GithubStubTestCase, self).setUp()
        self.github_stub = self.mocker.mock(count=False)

        from plonesource import update
        update.GITHUB__ORI = update.GITHUB
        update.GITHUB = self.github_stub

    def tearDown(self):
        from plonesource import update
        update.GITHUB = update.GITHUB__ORI
        del update.GITHUB__ORI
        super(MockerTestCase, self).tearDown()

    def replay(self):
        self.mocker.replay()

    def stub_repositories(self, *repositories):
        for repo in repositories:
            self._stub_repo(repo)

    def _stub_repo(self, repo):
        self.expect(self.github_stub.repos.get(
                repo=repo.name,
                user=repo.principal)).result(repo)

        if repo.principal not in self.repositories_by_principal:
            self.repositories_by_principal[repo.principal] = []
            self.expect(
                self.github_stub.repos.list(repo.principal).all()).result(
                self.repositories_by_principal[repo.principal])

        self.repositories_by_principal[repo.principal].append(repo)


class Repository(object):

    def __init__(self, fullname, master_branch='master', parent=None):
        self.principal, self.name = fullname.split('/')
        self.clone_url = 'https://github.com/%s.git' % fullname
        self.ssh_url = 'git@github.com:%s.git' % fullname

        if parent:
            self.parent = parent
            self.fork = True
        else:
            self.fork = False

        if master_branch is not None:
            # github returns no master_branch on empty repositories, so
            # it should not be set to None her but not set at all.
            self.master_branch = master_branch
