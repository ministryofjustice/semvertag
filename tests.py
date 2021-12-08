import os
import subprocess
import unittest
import semvertag

DEVNULL = open(os.devnull, 'wb')


class BaseSemVerTagTest(unittest.TestCase):
    def setUp(self):
        subprocess.run("rm -Rf tmp".split())
        subprocess.run("mkdir -p tmp/repo-origin".split())
        subprocess.run("ls",
                              cwd="tmp",
                              stdout=DEVNULL
                              )
        subprocess.run("git init".split(),
                              cwd="tmp/repo-origin",
                              stdout=DEVNULL)
        subprocess.run("touch readme.md".split(),
                              cwd="tmp/repo-origin",
                              stdout=DEVNULL)
        subprocess.run("git add .".split(),
                              cwd="tmp/repo-origin",
                              stdout=DEVNULL)
        subprocess.run("git commit -m start".split(),
                              cwd="tmp/repo-origin",
                              stdout=DEVNULL)
        subprocess.run("git clone repo-origin repo".split(),
                              cwd="tmp",
                              stdout=DEVNULL,
                              stderr=DEVNULL)

    @staticmethod
    def semvertag(command, cwd='tmp/repo'):
        parser = semvertag.get_argparser()
        args_list = ['--cwd', cwd]
        args_list.extend(command.split())
        args = parser.parse_args(args_list)
        response = args.func(args)
        return response

    @staticmethod
    def gittag(tagname):
        subprocess.run('git tag {}'.format(tagname).split(),
                         cwd="tmp/repo",
                         stdout=DEVNULL)

    def tearDown(self):
        subprocess.run("rm -Rf tmp".split())


class TestSemVerTag(BaseSemVerTagTest):
    def setUp(self):
        super(TestSemVerTag, self).setUp()
        self.gittag('1.0.0')
        self.gittag('1.0.1+1')
        self.gittag('1.0.1+2')
        self.gittag('1.0.1+3')
        self.gittag('1.2.1+3')
        self.gittag('1.2.1-foo+2')
        self.gittag('1.2.1-foo+1')
        self.gittag('1.3.1-bar+1')
        self.gittag('1.3.2-bar')
        self.gittag('plum-0.0.2-bar+1')
        self.gittag('plum-0.0.2-bar+2')
        self.gittag('plum-0.0.1-bar+2')
        # unsupported strings
        self.gittag('plum-0.0.a-bar+2')
        self.gittag('plum-0.0.a-bar+2bc')

    def test_latest(self):
        ver = self.semvertag('latest').strip()
        assert ver == "1.2.1+3"

        ver = self.semvertag('latest --stage foo ').strip()
        assert ver == "1.2.1-foo+2"

        ver = self.semvertag('latest --stage bar ').strip()
        assert ver == "1.3.2-bar"

        ver = self.semvertag('latest --stage bar --prefix plum- ').strip()
        assert ver == "plum-0.0.2-bar+2"

    def test_bump(self):
        ver = self.semvertag('bump').strip()
        assert ver == "1.2.1+4"

        ver = self.semvertag('bump --stage foo').strip()
        assert ver == "1.2.1-foo+3"

        ver = self.semvertag('bump --stage bar').strip()
        assert ver == "1.3.2-bar+1"

        ver = self.semvertag('bump --stage bar --prefix plum-').strip()
        assert ver == "plum-0.0.2-bar+3"

    def test_bump_tagging(self):
        ver = self.semvertag('bump --tag').strip()
        assert ver == "1.2.1+4"

        ver = self.semvertag('bump --tag').strip()
        assert ver == "1.2.1+5"

        ver = self.semvertag('bump --stage foo --tag').strip()
        assert ver == "1.2.1-foo+3"
        ver = self.semvertag('bump --stage foo --tag').strip()
        assert ver == "1.2.1-foo+4"

        ver = self.semvertag('bump --stage bar --prefix plum- --tag').strip()
        assert ver == "plum-0.0.2-bar+3"

        ver = self.semvertag('bump --stage bar --prefix plum- --tag').strip()
        assert ver == "plum-0.0.2-bar+4"

    def test_set_arbitrary_tag(self):
        ver = self.semvertag('tag foobar-1.2.3').strip()
        assert ver == 'foobar-1.2.3'

    def test_fields_bumping(self):
        ver = self.semvertag('tag precious-0.0.1').strip()
        assert ver == 'precious-0.0.1'
        ver = self.semvertag('bump --prefix precious- --tag').strip()
        assert ver == "precious-0.0.1+1"
        ver = self.semvertag('bump --prefix precious- --tag patch').strip()
        assert ver == "precious-0.0.2"
        ver = self.semvertag('bump --prefix precious- --tag minor').strip()
        assert ver == "precious-0.1.0"
        ver = self.semvertag('bump --prefix precious- --tag major').strip()
        assert ver == "precious-1.0.0"
        ver = self.semvertag('bump --prefix precious- --tag').strip()
        assert ver == "precious-1.0.0+1"

    def test_list(self):
        tags = self.semvertag('list').strip()
        assert tags == "1.2.1+3\n1.0.1+3\n1.0.1+2\n1.0.1+1\n1.0.0"
        tags = self.semvertag('list --csv').strip()
        assert tags == "1.2.1+3,1.0.1+3,1.0.1+2,1.0.1+1,1.0.0"
        tags = self.semvertag('list --reverse').strip()
        assert tags == "1.0.0\n1.0.1+1\n1.0.1+2\n1.0.1+3\n1.2.1+3"
        tags = self.semvertag('list --reverse --csv').strip()
        assert tags == "1.0.0,1.0.1+1,1.0.1+2,1.0.1+3,1.2.1+3"


class TestInitialiseTags(BaseSemVerTagTest):
    # Test that initial tag is created correctly with empty repos.
    def test_starting_tag(self):
        ver = self.semvertag('bump --tag').strip()
        tags = self.semvertag('list').strip()
        assert ver == '0.0.0+1'
        assert tags == '0.0.0+1'

    def test_starting_tag_patch(self):
        ver = self.semvertag('bump patch --tag').strip()
        tags = self.semvertag('list').strip()
        assert ver == '0.0.1'
        assert tags == '0.0.1'

    def test_starting_tag_minor(self):
        ver = self.semvertag('bump minor --tag').strip()
        tags = self.semvertag('list').strip()
        assert ver == '0.1.0'
        assert tags == '0.1.0'

    def test_starting_tag_minor_suffix(self):
        ver = self.semvertag('bump minor --tag --stage foo').strip()
        tags = self.semvertag('list --stage foo').strip()
        assert ver == '0.1.0-foo'
        assert tags == '0.1.0-foo'

    def test_starting_tag_minor_prefix(self):
        ver = self.semvertag('bump minor --tag --prefix plum-').strip()
        tags = self.semvertag('list --prefix plum-').strip()
        assert ver == 'plum-0.1.0'
        assert tags == 'plum-0.1.0'

    def test_tagging_scheme_initialisation_can_coexist(self):
        ver = self.semvertag('bump patch --tag').strip()
        foo_ver = self.semvertag('bump patch --tag --stage foo').strip()
        plum_ver = self.semvertag('bump patch --tag --prefix plum-').strip()
        assert ver == '0.0.1'
        assert foo_ver == '0.0.1-foo'
        assert plum_ver == 'plum-0.0.1'
        tags = self.semvertag('list').strip()
        assert tags == '0.0.1'
        tags = self.semvertag('list --stage foo').strip()
        assert tags == '0.0.1-foo'
        tags = self.semvertag('list --prefix plum-').strip()
        assert tags == 'plum-0.0.1'

    # Test that latest command reports the correct tags when no tags are present
    def test_starting_latest(self):
        ver = self.semvertag('latest').strip()
        assert ver == '0.0.0'

    def test_starting_latest_suffix(self):
        ver = self.semvertag('latest --stage foo').strip()
        assert ver == '0.0.0-foo'

    def test_starting_latest_prefix(self):
        ver = self.semvertag('latest --prefix plum-').strip()
        assert ver == 'plum-0.0.0'


if __name__ == '__main__':
    unittest.main()
    # DEVNULL.close()