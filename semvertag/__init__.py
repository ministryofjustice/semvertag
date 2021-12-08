#!/usr/bin/env python
from __future__ import print_function

import os
import re
import sys
import subprocess
import argparse


_REGEX = re.compile('^(?P<major>(?:0|[1-9][0-9]*))'
                    '\.(?P<minor>(?:0|[1-9][0-9]*))'
                    '\.(?P<patch>(?:0|[1-9][0-9]*))'
                    '(\-(?P<stage>[0-9A-Za-z-]+(\.[0-9A-Za-z-]+)*))?'
                    '(\+(?P<build>[0-9A-Za-z-]+(\.[0-9A-Za-z-]+)*))?$')


class ExecutionError(Exception):
    pass


def sorter(item):
    """
    Calling function for sorter method
    :param item:
    :return:
    """
    include = {"major", "minor", "patch", "build"}
    return list({x: item.data[x] for x in item.data if x in include}.values())


class Tag(object):
    """
    Object encapsulating SemVer and tag prefix.
    :raises Exception on parsing errors
    """
    data = None
    prefix = ''

    def __init__(self, version_string, prefix=''):
        # let's cut off prefix
        assert str(version_string).startswith(prefix)
        version_string = str(version_string).lstrip(prefix)
        self.prefix = prefix
        match = _REGEX.match(version_string)
        if match is None:
            raise ValueError('%s is not valid SemVer string' % version_string)

        parsed_data = match.groupdict()

        parsed_data['major'] = int(parsed_data['major'])
        parsed_data['minor'] = int(parsed_data['minor'])
        parsed_data['patch'] = int(parsed_data['patch'])
        # following is stricter than SemVer
        if parsed_data['build'] is not None:
            parsed_data['build'] = int(parsed_data.get('build'))
        else:
            parsed_data['build'] = 0

        self.data = parsed_data

    def __repr__(self):
        return "Tag('{}')".format(self.__str__())

    def __str__(self):
        stage = ''
        if self.data['stage']:
            stage = "-{}".format(self.data['stage'])

        build = ''
        if self.data['build']:  # > 0
            build = "+{}".format(self.data['build'])

        return "{}{}.{}.{}{}{}".format(self.prefix, self.data['major'], self.data['minor'], self.data['patch'], stage,
                                       build)


def git_tag(new_tag, cwd=None):
    """
    tag and push the tag
    does not check if tag is already there
    :param new_tag:
    :param cwd: git repository directory
    :return:
    """
    assert new_tag
    try:
        subprocess.run(['git', 'tag', '-a', '-m', 'Release', new_tag], cwd=cwd,
                       stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(e.stderr, file=sys.stderr)
        raise ExecutionError("Error tagging")

    try:
        subprocess.run(['git', 'push', 'origin', 'tag', new_tag], cwd=cwd,
                         stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(e.stderr, file=sys.stderr)
        raise ExecutionError("Error pushing tag to origin")


def tags_get_filtered(stage=None, prefix='', cwd=None, create_default_tags=False):
    """
    gets list of all tags and filters them based on stage and prefix
    :param stage:
    :param prefix:
    :param cwd: git repository directory
    :return:
    """
    try:
        p = subprocess.run(['git', 'tag', '--list'], cwd=cwd, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(e.stderr, file=sys.stderr)
        raise ExecutionError("Error getting tags")

    tags = []

    for line in p.stdout.decode().splitlines():
        try:
            tag = Tag(line.strip(), prefix=prefix)
        except ValueError:
            tag = None
        except AssertionError:
            tag = None
        if tag and tag.data['stage'] == stage:
            tags.append(tag)

    # Create some base tags if none have been created.
    if not tags and create_default_tags:
        if stage:
            tags = [Tag("{}0.0.0-{}".format(prefix, stage), prefix=prefix)]
        else:
            tags = [Tag("{}0.0.0".format(prefix), prefix=prefix)]

    return tags


def latest_tag(stage=None, prefix='', cwd=None):
    """
    :param stage:
    :param prefix:
    :param cwd: git repository directory
    :return: latest available tag that matches prefix and stage
    """
    tags = sorted(
        tags_get_filtered(
            stage=stage,
            prefix=prefix,
            cwd=cwd,
            create_default_tags=True
        ),
        reverse=True,
        key=sorter
    )
    if tags:
        return tags[0]
    return


def bump_tag(stage=None, prefix='', cwd=None, field='build'):
    """
    creates bumped version tag 1st filtering all tags based on stage and prefix
    :param stage: release stage
    :param prefix: tag prefix
    :param cwd: git repository directory
    :param field: which field to bump (major, minor, patch, build)
    :return: bumped version tag
    """
    tags = sorted(
        tags_get_filtered(
            stage=stage,
            prefix=prefix,
            cwd=cwd,
            create_default_tags=True
        ),
        reverse=True,
        key=sorter
    )
    if tags:
        ver = tags[0]
        # print("Bumping:{}".format(ver), file=sys.stderr)
        if field == 'major':
            ver.data[field] += 1
            ver.data['minor'] = 0
            ver.data['patch'] = 0
            ver.data['build'] = 0
        elif field == 'minor':
            ver.data[field] += 1
            ver.data['patch'] = 0
            ver.data['build'] = 0
        elif field == 'patch':
            ver.data[field] += 1
            ver.data['build'] = 0
        elif field == 'build':
            ver.data[field] += 1
        else:
            raise NotImplementedError
        # print("Bumped:{}".format(ver), file=sys.stderr)
        return ver
    return


def list_tags(stage=None, prefix='', cwd=None, reverse=True):
    """
    returns all tags based on stage and prefix, optionally
    in reverse order
    :param stage: release stage
    :param prefix: tag prefix
    :param cwd: git repository directory
    :param reverse: sort order (descending by default)
    :return: sorted list of available tags that match prefix and stage
    """
    tags = sorted(
        tags_get_filtered(
            stage=stage,
            prefix=prefix,
            cwd=cwd,
            create_default_tags=True
        ),
        reverse=reverse,
        key=sorter
    )
    if tags:
        return tags


def command_latest(args):
    """
    semvertag latest
    :param args:
    :return:
    """
    ver = latest_tag(args.stage, args.prefix, args.cwd)
    if ver is None:
        return "ERROR: No matching tag has been found. Please create 1st SemVer tag i.e. 'git tag 0.0.1'"
    return str(ver)


def command_bump(args):
    """
    semvertag bump
    :param args:
    :return:
    """
    ver = bump_tag(stage=args.stage, prefix=args.prefix, cwd=args.cwd, field=args.field)
    if args.tag:
        git_tag(str(ver), args.cwd)
    if ver is None:
        return "ERROR: No matching tag has been found. Please create 1st SemVer tag i.e. 'git tag 0.0.1'"
    return str(ver)


def command_tag(args):
    """
    semvertag tag
    :param args:
    :return:
    """
    tag = args.tag[0]
    git_tag(tag, args.cwd)
    return tag


def command_list(args):
    """
    semvertag list
    :param args:
    :return:
    """
    delimeter = "\n"
    if args.csv:
        delimeter = ','
    tags = list_tags(stage=args.stage, prefix=args.prefix, cwd=args.cwd, reverse=args.reverse)
    if tags is None:
        return "ERROR: No tags has been found. Please create 1st SemVer tag i.e. 'git tag 0.0.1'"

    return delimeter.join([str(t) for t in tags])


def get_argparser():
    """
    configure commandline arguments parsing
    :return:
    """
    parser = argparse.ArgumentParser(description="Tags git repository with next release number")
    parser.add_argument('--cwd', default=None,
                        help='Git repo location')

    def add_stage_prefix(my_parser):
        my_parser.add_argument('--stage', default=None,
                               help='Optional release stage we are working on. Specify only if not a production release. I.e.: patch, feature, alpha, beta. (default: %(default)s)')

        my_parser.add_argument('--prefix', default='',
                               help='Optional tag prefix. I.e.: v, app-, base- (default: %(default)s)')

    subparsers = parser.add_subparsers(title='commands')

    parser_bump = subparsers.add_parser('bump')
    add_stage_prefix(parser_bump)
    parser_bump.add_argument('field', choices=['major', 'minor', 'patch', 'build'], default='build', nargs='?',
                             help='Which version segment to bump (default: %(default)s)')
    parser_bump.add_argument('--tag', action='store_true', help='Tag current HEAD with bumped version')
    parser_bump.set_defaults(func=command_bump)

    parser_latest = subparsers.add_parser('latest')
    add_stage_prefix(parser_latest)
    parser_latest.set_defaults(func=command_latest)

    parser_tag = subparsers.add_parser('tag')
    parser_tag.add_argument('tag', metavar='tag_to_assign', nargs=1, help="New tag to assign and push to remote")
    parser_tag.set_defaults(func=command_tag)

    parser_list = subparsers.add_parser('list')
    parser_list.add_argument('--reverse', action='store_false', help='Whether to '
                                                                     'reverse the sort order (descending by default) '
                                                                     'when listing tags')
    parser_list.add_argument('--csv', action='store_true', help='Use a comma '
                                                                'to separate tags when listing')
    add_stage_prefix(parser_list)
    parser_list.set_defaults(func=command_list)

    return parser


def main():
    DEVNULL = open(os.devnull, 'wb')
    parser = get_argparser()
    args = parser.parse_args()
    response = args.func(args)
    print(response)
    DEVNULL.close()


if __name__ == '__main__':
    main()
