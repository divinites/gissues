global parameter_container


class ParameterContainer:
    def __init__(self):
        self.issue_syntax = "Packages/GitHubIssue/Issue.sublime-syntax"
        self.list_syntax = "Packages/GitHubIssue/list.sublime-syntax"
        self.line_ends = '\n'
        self.debug_flag = 0

    def read_settings(self, settings):
        self.issue_syntax = settings.get('syntax', 'Packages/GitHubIssue/Issue.sublime-syntax')
        self.debug_flag = settings.get('debug', 0)


parameter_container = ParameterContainer()
