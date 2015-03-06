# semvertag
SemVer compliant Git repository tagging tool.


For start you can use it to quickly check what is the current latest version tag on your git repository
```
semvertag latest
```
When you have multiple streams of tags within repository you can filter them with --prefix, --stage options.
For example you may have a repo with multiple apps. I.e.: front-0.0.1, api-0.0.1, api-0.1.0-alpha
```
semvertag latest --prefix api-
semvertag latest --prefix api- --stage alpha
```

You can also use it to automatically tag the repository with next 'bumped' tag.
```
semvertag bump --tag
```
Note that if `--tag` option is not specified then semvertag will not modify repo at all. It will only calculate for you
next available version tag.

Bumping can be done on major:
```
semvertag bump major
```
minor:
```
semvertag bump minor
```
patch:
```
semvertag bump patch
```
or on build segment:
```
semvertag bump build
```
of SemVer formatted tag.

By default it bumps build segment. So you can shorten your commandline to:
```
semvertag bump
```

In case you've splited your app into multiple git repositories, you will soon need to keep them in sync. Cross repo
baselining comes to the rescue.
Usually you will have a main repository that will be used to calculate bumped tags. Then calculated tag will be applied
to other repositories.
Depending on your needs you may even want to have this main tagging repository not to contain any code, only use it to
track tags. Your choice actually.
```bash
VER=$(semvertag --cwd main_repo bump --tag)
semvertag --cwd child_repo_1 tag ${VER}
semvertag --cwd child_repo_2 tag ${VER}
```


## SemVer
Actually it is stricter then SemVer 2.0. Current version enforces build segment to be integer. If you believe that 
it's too much submit an issue.


## Install
pip install git+https://github.com/ministryofjustice/semvertag.git


## Test
```
python tests.py
```

## Examples
```bash
# let's set few tags and push them instantly to origin git repository
$ semvertag tag 0.0.1
$ semvertag tag 0.1.0
$ semvertag tag app-0.1.1
$ semvertag tag app-0.1.1-alpha+1
$ semvertag tag app-0.1.1-alpha+2

# check latest available tag on main stream (no prefix and stage)
$ semvertag latest
0.1.0

# filter tag stream to capture app-0.1.1
$ semvertag latest --prefix app-
app-0.1.1

# filter tag stream to capture app-0.1.1-alpha
$ semvertag latest --prefix app- --stage alpha
app-0.1.1-alpha+2

# bump build version
$ semvertag bump
0.1.0+1

# to record changes on git repo and push to origin
$ semvertag bump --tag
0.1.0+1

# bump major version and save
$ semvertag bump major --tag
1.0.0

# bump minor version and save
$ semvertag bump minor --tag
1.1.0

# bump patch version and save
$ semvertag bump patch --tag
1.1.1

# and again bump build few times
$ semvertag bump --tag
1.1.1+1
$ semvertag bump --tag
1.1.1+2

```


## Help
semvertag -h

