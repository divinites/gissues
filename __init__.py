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
                     "user_completion", "label_completion", "commit_completion","split_line_width",
                     "commit_completion_trigger", "disable_local_repositories", "wrap_width", "draw_centered", "disable_vintageous"):
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
    debug_flag = sublime.load_settings("github_issue.sublime-settings").get('debug', 0)
    if debug_flag != 0:
        print("GitHub Issue >>> " + info)


LINE_END = "\n"
settings = SettingContainer()
flag_container = FlagContainer()
issue_obj_storage = Queue()
repo_info_storage = Queue()
global_title_list = {}
global_person_list = {}
global_label_list = {}
global_commit_list = {}
issue_obj_storage.put({})
repo_info_storage.put({})
COMMENT_START = lambda x: format_split("*" + "<" * 26 + "START <Comment {}>".format(str(x)) + ">" * 26 + "*")
COMMENT_END = lambda x: format_split("*" + ">" * 26 + "END   <Comment {}>".format(str(x)) + "<" * 26 + "*")
COMMENT_INFO = lambda x, y: format_split("*" + "-" * 9 + "<commented by " + x + "   UpdateTime: " + y + '>' + "-" * 9 + '*')
ISSUE_START = lambda: format_split("*" + "<" * 33 + "ISSUE START" + ">" * 33 + "*")
ISSUE_END = lambda: format_split("*" + ">" * 33 + "ISSUE   END" + "<" * 33 + "*")
HEADER_END = lambda: format_split("*" + "=" * 33 + "**CONTENT**" + "=" * 33 + "*")
CONTENT_END = lambda: format_split("*" + "=" * 35 + "**END**" + "=" * 35 + "*")
ADD_COMMENT = lambda: format_split("*" + "-" * 31 + "ADD NEW COMMENT" + "-" * 31 + "*")


def format_split(line):
    split_line_width = settings.get("split_line_width", 0)
    wrap_width = settings.get("wrap_width", 80)
    if split_line_width > wrap_width or split_line_width == 0:
        split_line_width = wrap_width
        if wrap_width == 80 or wrap_width == 0:
            return line
    line = list(line)
    while len(line) != split_line_width - 1:
        if len(line) > split_line_width - 1:
            line.pop(-2)
        if len(line) > split_line_width - 1:
            line.pop(1)
        if len(line) < split_line_width - 1:
            line.insert(1, line[1])
        if len(line) < split_line_width - 1:
            line.insert(-1, line[-2])
    return "".join(line)
