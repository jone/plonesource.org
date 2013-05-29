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

[branches]
bar = master
baz = master
foo = master


[sources]
bar = git https://github.com/foo/bar.git pushurl=git@github.com:foo/bar.git branch=${branches:bar}
baz = git https://github.com/bar/baz.git pushurl=git@github.com:bar/baz.git branch=${branches:baz}
foo = git https://github.com/foo/foo.git pushurl=git@github.com:foo/foo.git branch=${branches:foo}
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

[branches]
foo.bar = master
foo.baz = master


[sources]
foo.bar = git https://github.com/foo/foo.bar.git pushurl=git@github.com:foo/foo.bar.git branch=${branches:foo.bar}
foo.baz = git https://github.com/foo/foo.baz.git pushurl=git@github.com:foo/foo.baz.git branch=${branches:foo.baz}
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

[branches]
another = master
the-repo = master


[sources]
another = git https://github.com/foo/another.git pushurl=git@github.com:foo/another.git branch=${branches:another}
the-repo = git https://github.com/bar/the-repo.git pushurl=git@github.com:bar/the-repo.git branch=${branches:the-repo}
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

[branches]


[sources]
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

[branches]


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
