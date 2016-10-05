import logging

global parameter_container, github_logger


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


parameter_container = ParameterContainer()
github_logger = logging.getLogger("GitHubIssue")

