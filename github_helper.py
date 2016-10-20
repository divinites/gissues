import sublime_plugin
import sublime
from . import log
from . import COMMENT_START, COMMENT_END
from .libgit.utils import ViewConverter


class EraseCurrentCommentFromViewCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        current_point = self.view.sel()[0].a
        row, col = self.view.rowcol(current_point)
        view_converter = ViewConverter(self.view)
        view_lines = view_converter.readlines()
        crucial_lines = ViewConverter.split_issue(view_lines)
        for idx, line in enumerate(crucial_lines['comment_start']):
            if row > line.idx:
                continue
            elif row == line.idx:
                comment_start = crucial_lines['comment_start'][idx]
            else:
                comment_start = crucial_lines['comment_start'][idx - 1]
                break
        else:
            comment_start = crucial_lines['comment_start'][-1]
        for idx, line in enumerate(crucial_lines['comment_end']):
            if row > line.idx:
                continue
            else:
                comment_end = crucial_lines['comment_end'][idx]
                break
        else:
            raise Exception("Something wrong with comment splitting")
        view_lines = self.view.lines(sublime.Region(0, self.view.size()))
        self.view.erase(edit, sublime.Region(view_lines[comment_start.idx].a, view_lines[comment_end.idx].b + 1))


class EraseCurrentCommentCommand(sublime_plugin.WindowCommand):
    def run(self):
        view = self.window.active_view()
        view.run_command("erase_current_comment_from_view")
        self.window.run_command("update_github_issue")


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


class FindAndReplaceCommand(sublime_plugin.TextCommand):
    def run(self, edit, start_point, word, replacement):
        region = self.view.find(word, start_point, sublime.LITERAL)
        if region:
            self.view.run_command("erase_snippet", {"start_point": region.a,
                                                      "end_point": region.b
                                                      })
            self.view.run_command("insert_issue_snippet", {"start_point":region.a,
                                                           "snippet": replacement})


class PostOrUpdateIssueCommand(sublime_plugin.WindowCommand):

    def is_enabled(self):
        self.window = sublime.active_window()
        self.view = self.window.active_view()
        if self.view.settings().get("issue_flag"):
            return True
        return False

    def run(self):
        log("post or update?")
        if self.view.settings().get("new_issue"):
            log("post")
            self.window.run_command("post_github_issue")
        else:
            log("update")
            self.window.run_command("update_github_issue")
