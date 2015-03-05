# semvertag
SemVer compliant Git repo tagging command line tool


## Install
pip install git+https://github.com/ministryofjustice/semvertag.git


## Test
```
python tests.py
```

## Help
semvertag -h

## Examples
```bash
# check latest available tag
$ semvertag latest

# filter tag stream to capture app-0.1.1
$ semvertag latest --prefix app-

# filter tag stream to capture app-0.1.1-alpha
$ semvertag latest --prefix app- --stage alpha

# bump build version
$ semvertag bump

# to record changes on git repo and push to origin
$ semvertag bump --tag

# bump major version and save
$ semvertag bump major --tag

# bump minor version and save
$ semvertag bump minor --tag

# bump patch version and save
$ semvertag bump patch --tag

```
