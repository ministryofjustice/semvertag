import os
from subprocess import call
import unittest
import semvertag

DEVNULL = open(os.devnull, 'wb')


# TODO: case with no tags at all on repo


class SemVerTagTest(unittest.TestCase):
    def setUp(self):
        print "setUp"
        call("rm -Rf tmp".split())
        call("mkdir -p tmp/repo-origin".split())
        call("ls",
             cwd="tmp",
             stdout=DEVNULL)
        call("git init".split(),
             cwd="tmp/repo-origin",
             stdout=DEVNULL)
        call("touch readme.md".split(),
             cwd="tmp/repo-origin",
             stdout=DEVNULL)
        call("git add .".split(),
             cwd="tmp/repo-origin",
             stdout=DEVNULL)
        call("git commit -m start".split(),
             cwd="tmp/repo-origin",
             stdout=DEVNULL)
        call("git clone repo-origin repo".split(),
             cwd="tmp",
             stdout=DEVNULL,
             stderr=DEVNULL)
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

    def semvertag(self, command, cwd='tmp/repo'):
        parser = semvertag.get_argparser()
        args_list = ['--cwd', cwd]
        args_list.extend(command.split())
        args = parser.parse_args(args_list)
        response = args.func(args)
        return response

    def gittag(self, tagname):
        call('git tag {}'.format(tagname).split(),
             cwd="tmp/repo",
             stdout=DEVNULL)

    def tearDown(self):
        print "tearDown"
        call("rm -Rf tmp".split())


class TestSemVerTag(SemVerTagTest):
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

    def test_no_tags_error(self):
        ver = self.semvertag('latest --stage baz').strip()
        assert "ERROR" in ver
        ver = self.semvertag('bump --stage baz').strip()
        assert "ERROR" in ver

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


if __name__ == '__main__':
    unittest.main()
