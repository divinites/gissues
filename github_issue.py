import sublime
import sublime_plugin
from gissues.libgit import issue
from gissues.libgit import utils
import re


def plugin_loaded():
    global issue_list, issue_dict
    settings = sublime.load_settings("github_issue.sublime-settings")
    issue_list = issue.IssueList(settings)
    issue_dict = {}


class ShowGithubIssueListCommand(sublime_plugin.WindowCommand):
    def run(self):
        global issue_list
        issue_list.find_repo()
        print_in_view = issue.PrintListInView(issue_list)
        print_in_view.start()


class ShowGithubIssueCommand(sublime_plugin.WindowCommand):
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

    def run(self):
        global issue_list
        issue_list.find_repo()
        post_issue = issue.PostNewIssue(issue_list=issue_list)
        post_issue.start()


class UpdateGithubIssueCommand(sublime_plugin.WindowCommand):

    def run(self):
        pass


class AutoSyncIssueListener(sublime_plugin.EventListener):
    pass


class AutoSelectIssueListListener(sublime_plugin.EventListener):
    pass


class InsertIssueCommand(sublime_plugin.TextCommand):
    def run(self, edit,  start_point=0, issue=None):
        if issue:
            self.view.insert(edit, start_point, issue)
