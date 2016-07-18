import sublime
import sublime_plugin
from .libgit import issue
from .libgit import utils
import re
import os
from queue import Queue


def plugin_loaded():
    global issue_list, issue_dict
    settings = sublime.load_settings("github_issue.sublime-settings")
    issue_dict = Queue()
    issue_list = issue.IssueList(settings)
    issue_dict.put({})


class ShowGithubIssueListCommand(sublime_plugin.WindowCommand):
    def run(self, **args):
        global issue_list
        issue_list.find_repo()
        print_in_view = issue.PrintListInView(issue_list, **args)
        print_in_view.start()


class ShowGithubIssueCommand(sublime_plugin.WindowCommand):
    def is_enabled(self):
        current_view = sublime.active_window().active_view()
        _, syntax_name = os.path.split(current_view.settings().get('syntax'))
        if syntax_name == "list.sublime-syntax":
            return True
        return False

    def run(self):
        global issue_list, issue_dict
        view = sublime.active_window().active_view()
        target_line = view.substr(view.line(view.sel()[0]))
        match_id = re.search(r'^\d+(?=\s)', target_line)
        issue_number = int(match_id.group(0))
        issue_list.find_repo()
        print_in_view = issue.PrintIssueInView(issue_list, issue_number, issue_dict)
        print_in_view.start()


class NewGithubIssueCommand(sublime_plugin.WindowCommand):

    def run(self):
        utils.create_new_issue_view()


class PostGithubIssueCommand(sublime_plugin.WindowCommand):
    def is_enabled(self):
        current_view = sublime.active_window().active_view()
        _, syntax_name = os.path.split(current_view.settings().get('syntax'))
        if syntax_name == "issue.tmLanguage":
            return True
        return False

    def run(self):
        global issue_list, issue_dict
        issue_list.find_repo()
        post_issue = issue.PostNewIssue(issue_list=issue_list, issue_dict=issue_dict)
        post_issue.start()


class UpdateGithubIssueCommand(sublime_plugin.WindowCommand):
    def is_enabled(self):
        current_view = sublime.active_window().active_view()
        _, syntax_name = os.path.split(current_view.settings().get('syntax'))
        if syntax_name == "issue.tmLanguage":
            return True
        return False

    def run(self):
        global issue_list, issue_dict
        issue_list.find_repo()
        update_issue = issue.UpdateIssue(issue_list=issue_list, issue_dict=issue_dict)
        update_issue.start()


class InsertIssueCommand(sublime_plugin.TextCommand):
    def run(self, edit, start_point=0, issue=None):
        if issue:
            self.view.insert(edit, start_point, issue)


class ReplaceIssueCommand(sublime_plugin.TextCommand):
    def run(self, edit, start, end, snippet):
        if snippet:
            self.view.replace(edit, sublime.Region(start, end), snippet)


class ClearViewCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.erase(edit, sublime.Region(0, self.view.size()))