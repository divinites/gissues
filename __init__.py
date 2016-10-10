import logging
from queue import Queue

global parameter_container, github_logger, flag_container


class ParameterContainer:
    def __init__(self, settings=None):
        self.issue_syntax = "Packages/GitHubIssue/Issue.sublime-syntax"
        self.list_syntax = "Packages/GitHubIssue/list.sublime-syntax"
        self.line_ends = '\n'
        self.debug_flag = 0
        self.git_path = ""
        self.title_completion = True
        self.name_completion = True
        self.custom_scope = []
        self.label_completion = True
        self.commit_completion = True
        self.commit_completion_trigger = ":"
        if settings:
            self.read_settings(settings)

    def read_settings(self, settings):
        self.issue_syntax = settings.get('syntax', 'Packages/GitHubIssue/Issue.sublime-syntax')
        self.git_path = settings.get("git_path", '')
        self.debug_flag = self.get_debug_flag(settings)
        self.title_completion = settings.get('issue_title_completion', True)
        self.name_completion = settings.get('user_completion', True)
        self.label_completion = settings.get("label_completion", True)
        self.commit_completion = settings.get("commit_completion", True)
        self.custom_scope = settings.get('custom_completion_scope', [])
        self.commit_completion_trigger = settings.get('commit_completion_trigger', ":")

    def get_debug_flag(self, settings):
        return settings.get('debug', 0)


class FlagContainer:
    def __init__(self):
        self.pagination_flags = {"_First_": False,
                                 "_Last_": False,
                                 "_Prev_": False,
                                 "_Next_": False}
        # self.label_change = False
        # self.title_change = False


def log(info):
    log_level = logging.DEBUG if parameter_container.debug_flag == 0 else logging.INFO
    github_logger.setLevel(log_level)
    github_logger.info(info)


flag_container = FlagContainer()
parameter_container = ParameterContainer()
github_logger = logging.getLogger("GitHubIssue")
issue_obj_storage = Queue()
repo_info_storage = Queue()
global_title_list = {}
global_person_list = {}
global_label_list = {}
global_commit_list = {}
# global_title_list_storage.put({})
# global_person_list_storage.put({})
issue_obj_storage.put({})
repo_info_storage.put({})
