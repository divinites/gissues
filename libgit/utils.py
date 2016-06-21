import os
import sublime


LINE_ENDS = '\n' if sublime.platform() != 'windows' else '\r\n'


def find_git():
    pass


def filter_line_ends(issue):
    if sublime.platform() != 'windows':
        return issue.replace('\r', '')
    else:
        return issue