import logging
from queue import Queue
import sublime


##
# @brief      Class for issue setting.
##
class SettingContainer:

    ##
    # @brief      Constructs the object.
    ##
    # @param      self      The object
    # @param      settings  Sublime Setting Object
    ##
    def __init__(self, settings=None):
        self.settings = settings
        self.setting_dictionary = {}

    ##
    # @brief      refresh the setting_dictionary
    ##
    # @param      self  The object
    ##
    # @return     { None }
    ##
    def refresh(self):
        self.settings = sublime.load_settings('github_issue.sublime-settings')
        for flag in ("token", "username", "password", "debug", "syntax", "git_path", "issue_title_completion",
                     "user_completion", "label_completion", "commit_completion",
                     "commit_completion_trigger", "disable_local_repositories", "wrap_width", "draw_centered"):
            self.setting_dictionary[flag] = self.settings.get(flag)

    ##
    # @brief      get corresponding parameters from Setting Object
    ##
    # @param      self     The object
    # @param      flag     configuration parameters
    # @param      default  The default value of flag
    ##
    # @return     return setting_dictionary[flag] if it is valid otherwise return the default value.
    ##
    def get(self, flag, default=None):
        result = self.setting_dictionary[flag]
        if not result:
            result = default
        return result


class FlagContainer:

    def __init__(self):
        self.pagination_flags = {"_First_": False,
                                 "_Last_": False,
                                 "_Prev_": False,
                                 "_Next_": False
                                 }


def log(info):
    github_logger.info(info)


LINE_END = "\n"
settings = SettingContainer()
flag_container = FlagContainer()
github_logger = logging.getLogger("GitHubIssue")
github_logger.propagate = True
issue_obj_storage = Queue()
repo_info_storage = Queue()
global_title_list = {}
global_person_list = {}
global_label_list = {}
global_commit_list = {}
issue_obj_storage.put({})
repo_info_storage.put({})
COMMENT_START = lambda x: "*" + "<" * 10 + "START <Comment {}>".format(str(x)) + ">" * 10 + "*"
COMMENT_END = lambda x: "*" + ">" * 10 + "END   <Comment {}>".format(str(x)) + "<" * 10 + "*"
COMMENT_INFO = lambda x, y: "*<commented by " + x + "   UpdateTime: " + y + '>*'
ISSUE_START = "*" + "<" * 17 + "ISSUE START" + ">" * 17 + "*"
ISSUE_END = "*" + ">" * 17 + "ISSUE   END" + "<" * 17 + "*"
HEADER_END = "##" + "-" * 17 + "**CONTENT**" + "-" * 18 + "*"
CONTENT_END = "##" + "-" * 19 + "**END**" + "-" * 20 + "*"
ADD_COMMENT = "## ADD NEW COMMENT" + "-" * 28 + "*"
