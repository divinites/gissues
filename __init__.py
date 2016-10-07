import logging
from queue import Queue

global parameter_container, github_logger, flag_container


class ParameterContainer:
    def __init__(self):
        self.issue_syntax = "Packages/GitHubIssue/Issue.sublime-syntax"
        self.list_syntax = "Packages/GitHubIssue/list.sublime-syntax"
        self.line_ends = '\n'
        self.debug_flag = 0
        self.git_path = ""

    def read_settings(self, settings):
        self.issue_syntax = settings.get('syntax', 'Packages/GitHubIssue/Issue.sublime-syntax')
        self.git_path = settings.get("git_path", '')
        self.debug_flag = settings.get('debug', 0)


class FlagContainer:
    def __init__(self):
        self.pagination_flags = {"_First_": False,
                                 "_Last_": False,
                                 "_Prev_": False,
                                 "_Next_": False}


flag_container = FlagContainer()
parameter_container = ParameterContainer()
github_logger = logging.getLogger("GitHubIssue")
issue_obj_storage = Queue()
repo_info_storage = Queue()
issue_obj_storage.put({})
repo_info_storage.put({})
