import sublime_plugin
import sublime
from . import log
from .github_issue import settings


class InsertIssueSnippetCommand(sublime_plugin.TextCommand):

    def run(self, edit, start_point=0, snippet=None):
        if snippet:
            self.view.insert(edit, start_point, snippet)


class EraseSnippetCommand(sublime_plugin.TextCommand):

    def run(self, edit, start_point=0, end_point=0):
        self.view.erase(edit, sublime.Region(start_point, end_point))


class ReplaceSnippetCommand(sublime_plugin.TextCommand):

    def run(self, edit, start_point, end_point, snippet):
        if snippet:
            self.view.replace(edit, sublime.Region(
                start_point, end_point), snippet)


class PostOrUpdateIssueCommand(sublime_plugin.WindowCommand):

    def is_enabled(self):
        self.window = sublime.active_window()
        self.view = self.window.active_view()
        syntax_name = self.view.settings().get('syntax')
        if syntax_name == settings.get("syntax", "Packages/GitHubIssue/Issue.sublime-syntax"):
            return True
        return False

    def run(self):
        header_split = "*----------Content----------*"
        possible_header = self.view.lines(
            sublime.Region(0, self.view.size()))[:7]
        header_split_line = 6
        log("post or update?")
        log("view.substr(possible_header[3]) is {}".format(
            self.view.substr(possible_header[3])))
        if self.view.substr(possible_header[3]) == header_split:
            header_split_line = 3
        if header_split_line == 3:
            log("post")
            self.window.run_command("post_github_issue")
        elif header_split_line == 6:
            log("update")
            self.window.run_command("update_github_issue")
        else:
            pass
