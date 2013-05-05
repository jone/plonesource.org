from plonesource.tests.base import GithubStubTestCase
from plonesource.tests.base import Repository
from plonesource.update import update


class TestUpdateSourcesConfig(GithubStubTestCase):

    def test_contains_all_repositories(self):
        self.stub_repositories(
            Repository('foo/foo.bar'),
            Repository('foo/foo.baz'))
        self.replay()

        result = update({'principals': ['foo']})

        self.assertMultiLineEqual(
            '''[buildout]
auto-checkout =
sources = sources

[branches]
foo.bar = master
foo.baz = master


[sources]
foo.bar = git https://github.com/foo/foo.bar.git pushurl=git@github.com:foo/foo.bar.git branch=${branches:foo.bar}
foo.baz = git https://github.com/foo/foo.baz.git pushurl=git@github.com:foo/foo.baz.git branch=${branches:foo.baz}
''',

            result,
            'The sources.cfg should exactly contain the repositories foo/foo.bar'
            ' and foo/foo.baz.')
