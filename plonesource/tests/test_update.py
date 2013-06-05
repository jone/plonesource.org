from plonesource.tests.base import GithubStubTestCase
from plonesource.tests.base import Repository
from plonesource.update import update
from unittest2 import TestCase
import tempfile


class TestUpdateSourcesConfig(GithubStubTestCase):

    def test_contains_all_principal_repositories(self):
        self.stub_repositories(
            Repository('foo/foo.bar'),
            Repository('foo/foo.baz'))
        self.replay()

        result = update({'principals': ['foo']})

        self.maxDiff = None
        self.assertMultiLineEqual(
            '''[buildout]
auto-checkout =
sources = sources
github-cloneurl = ${buildout:github-https}
github-pushurl = ${buildout:github-ssh}


github-https = https://github.com/
github-ssh = git@github.com:
github-git = git://github.com/


[branches]
foo.bar = master
foo.baz = master


[forks]
foo.bar = foo
foo.baz = foo


[sources]
foo.bar = git ${buildout:github-cloneurl}${forks:foo.bar}/foo.bar.git pushurl=${buildout:github-pushurl}${forks:foo.bar}/foo.bar.git branch=${branches:foo.bar}
foo.baz = git ${buildout:github-cloneurl}${forks:foo.baz}/foo.baz.git pushurl=${buildout:github-pushurl}${forks:foo.baz}/foo.baz.git branch=${branches:foo.baz}
''',

            result,
            'The sources.cfg should exactly contain the repositories foo/foo.bar'
            ' and foo/foo.baz.')

    def test_top_principals_have_precedence(self):
        self.stub_repositories(
            Repository('foo/foo'),
            Repository('foo/bar'),
            Repository('bar/bar'),
            Repository('bar/baz'))
        self.replay()

        result = update({'principals': ['foo', 'bar']})

        self.maxDiff = None
        self.assertMultiLineEqual(
            '''[buildout]
auto-checkout =
sources = sources
github-cloneurl = ${buildout:github-https}
github-pushurl = ${buildout:github-ssh}


github-https = https://github.com/
github-ssh = git@github.com:
github-git = git://github.com/


[branches]
bar = master
baz = master
foo = master


[forks]
bar = foo
baz = bar
foo = foo


[sources]
bar = git ${buildout:github-cloneurl}${forks:bar}/bar.git pushurl=${buildout:github-pushurl}${forks:bar}/bar.git branch=${branches:bar}
baz = git ${buildout:github-cloneurl}${forks:baz}/baz.git pushurl=${buildout:github-pushurl}${forks:baz}/baz.git branch=${branches:baz}
foo = git ${buildout:github-cloneurl}${forks:foo}/foo.git pushurl=${buildout:github-pushurl}${forks:foo}/foo.git branch=${branches:foo}
''',

            result)

    def test_single_repos(self):
        self.stub_repositories(
            Repository('foo/foo.bar'),
            Repository('foo/foo.baz'))
        self.replay()

        result = update({'repos': ['foo/foo.bar', 'foo/foo.baz']})

        self.maxDiff = None
        self.assertMultiLineEqual(
            '''[buildout]
auto-checkout =
sources = sources
github-cloneurl = ${buildout:github-https}
github-pushurl = ${buildout:github-ssh}


github-https = https://github.com/
github-ssh = git@github.com:
github-git = git://github.com/


[branches]
foo.bar = master
foo.baz = master


[forks]
foo.bar = foo
foo.baz = foo


[sources]
foo.bar = git ${buildout:github-cloneurl}${forks:foo.bar}/foo.bar.git pushurl=${buildout:github-pushurl}${forks:foo.bar}/foo.bar.git branch=${branches:foo.bar}
foo.baz = git ${buildout:github-cloneurl}${forks:foo.baz}/foo.baz.git pushurl=${buildout:github-pushurl}${forks:foo.baz}/foo.baz.git branch=${branches:foo.baz}
''',

            result)

    def test_single_repositories_have_precendence(self):
        self.stub_repositories(
            Repository('foo/the-repo'),
            Repository('foo/another'),
            Repository('bar/the-repo'))
        self.replay()

        result = update({'principals': ['foo'],
                         'repos': ['bar/the-repo']})

        self.maxDiff = None
        self.assertMultiLineEqual(
            '''[buildout]
auto-checkout =
sources = sources
github-cloneurl = ${buildout:github-https}
github-pushurl = ${buildout:github-ssh}


github-https = https://github.com/
github-ssh = git@github.com:
github-git = git://github.com/


[branches]
another = master
the-repo = master


[forks]
another = foo
the-repo = bar


[sources]
another = git ${buildout:github-cloneurl}${forks:another}/another.git pushurl=${buildout:github-pushurl}${forks:another}/another.git branch=${branches:another}
the-repo = git ${buildout:github-cloneurl}${forks:the-repo}/the-repo.git pushurl=${buildout:github-pushurl}${forks:the-repo}/the-repo.git branch=${branches:the-repo}
''',

            result)

    def test_empty_repository_is_skipped(self):
        # empty repositories are those which have no master branch
        self.stub_repositories(
            Repository('foo/foo', master_branch=None),
            Repository('bar/bar', master_branch=None))
        self.replay()

        result = update({'principals': ['foo'],
                         'repos': ['bar/bar']})

        self.maxDiff = None
        self.assertMultiLineEqual(
            '''[buildout]
auto-checkout =
sources = sources
github-cloneurl = ${buildout:github-https}
github-pushurl = ${buildout:github-ssh}


github-https = https://github.com/
github-ssh = git@github.com:
github-git = git://github.com/


[branches]


[forks]


[sources]
''',

            result)

    def test_forks_should_be_followed_recursively(self):
        original = Repository('organisation/the.repo')
        first_fork = Repository('john.doe/the.repo', parent=original)
        second_fork = Repository('peter.griffin/the.repo', parent=first_fork)

        self.stub_repositories(original, first_fork, second_fork)
        self.replay()

        result = update({'principals': ['peter.griffin']})

        self.maxDiff = None
        self.assertMultiLineEqual(
            '''[buildout]
auto-checkout =
sources = sources
github-cloneurl = ${buildout:github-https}
github-pushurl = ${buildout:github-ssh}


github-https = https://github.com/
github-ssh = git@github.com:
github-git = git://github.com/


[branches]
the.repo = master


[forks]
the.repo = organisation


[sources]
the.repo = git ${buildout:github-cloneurl}${forks:the.repo}/the.repo.git pushurl=${buildout:github-pushurl}${forks:the.repo}/the.repo.git branch=${branches:the.repo}
''',
            result)

    def test_forks_can_be_used_by_defining_it_explictily(self):
        original = Repository('organisation/the.repo')
        fork = Repository('john.doe/the.repo', parent=original)

        self.stub_repositories(original, fork)
        self.replay()

        result = update({'principals': ['john.doe'],
                         'repos': ['john.doe/the.repo']})

        self.maxDiff = None
        self.assertMultiLineEqual(
            '''[buildout]
auto-checkout =
sources = sources
github-cloneurl = ${buildout:github-https}
github-pushurl = ${buildout:github-ssh}


github-https = https://github.com/
github-ssh = git@github.com:
github-git = git://github.com/


[branches]
the.repo = master


[forks]
the.repo = john.doe


[sources]
the.repo = git ${buildout:github-cloneurl}${forks:the.repo}/the.repo.git pushurl=${buildout:github-pushurl}${forks:the.repo}/the.repo.git branch=${branches:the.repo}
''',
            result)

    def test_forks_have_precedence_over_principal_order(self):
        bottom_repo = Repository('bottom/the.repo')
        top_repo = Repository('top/the.repo', parent=bottom_repo)

        self.stub_repositories(top_repo, bottom_repo)
        self.replay()

        result = update({'principals': ['top', 'bottom']})

        self.maxDiff = None
        self.assertMultiLineEqual(
            '''[buildout]
auto-checkout =
sources = sources
github-cloneurl = ${buildout:github-https}
github-pushurl = ${buildout:github-ssh}


github-https = https://github.com/
github-ssh = git@github.com:
github-git = git://github.com/


[branches]
the.repo = master


[forks]
the.repo = bottom


[sources]
the.repo = git ${buildout:github-cloneurl}${forks:the.repo}/the.repo.git pushurl=${buildout:github-pushurl}${forks:the.repo}/the.repo.git branch=${branches:the.repo}
''',
            result)


class TestUpdateCommand(TestCase):

    def setUp(self):
        self._constants = []

        from plonesource import config
        self.backup_constant(config, 'CONFIG')

        from plonesource import update
        self.backup_constant(update, 'OUTPUT_PATH')
        self.backup_constant(update, 'TIMESTAMP_PATH')

    def tearDown(self):
        self.reset_constants()

    def test_output_paths_are_in_static_folder(self):
        from plonesource import update

        expected_end = '/static/sources.cfg'
        self.assertTrue(
            update.OUTPUT_PATH.endswith(expected_end),
            'Expected the output path (%s) to end with %s' % (
                update.OUTPUT_PATH, expected_end))

        expected_end = '/static/last-update.txt'
        self.assertTrue(
            update.TIMESTAMP_PATH.endswith(expected_end),
            'Expected the timestamp path (%s) to end with %s' % (
                update.OUTPUT_PATH, expected_end))

    def test_update_command_writes_to_files(self):
        output = tempfile.NamedTemporaryFile()
        timestamp = tempfile.NamedTemporaryFile()

        from plonesource import update
        update.OUTPUT_PATH = output.name
        update.TIMESTAMP_PATH = timestamp.name

        from plonesource import config
        config.CONFIG = {}

        update.main()

        self.maxDiff = None
        self.assertMultiLineEqual(
            '''[buildout]
auto-checkout =
sources = sources
github-cloneurl = ${buildout:github-https}
github-pushurl = ${buildout:github-ssh}


github-https = https://github.com/
github-ssh = git@github.com:
github-git = git://github.com/


[branches]


[forks]


[sources]
''',
            output.read(),
            'Expected update command to write into sources.cfg')

        self.assertGreater(len(timestamp.read()), 0,
                           'Expected timestamp file to be written.')

    def backup_constant(self, module, name):
        setattr(module, '%s__ORI' % name, getattr(module, name))
        self._constants.append((module, name))

    def reset_constants(self):
        for module, name in self._constants:
            setattr(module, name, getattr(module, '%s__ORI' % name))
            delattr(module, '%s__ORI' % name)
