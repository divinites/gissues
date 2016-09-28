import sublime
import sublime_plugin
from .libgit import issue
from .libgit import utils
from .libgit import github
import re
import os
from queue import Queue
from functools import partial


def plugin_loaded():
    global issue_list, issue_dict
    settings = sublime.load_settings("github_issue.sublime-settings")
    issue_dict = Queue()
    issue_list = issue.IssueObj(settings)
    issue_dict.put({})


class ShowGithubIssueListCommand(sublime_plugin.WindowCommand):
    def run(self, **args):
        global issue_list
        repo_loader = LoadRepoList()
        repo_loader.format_entries()
        repo_loader.show_selection_panel(**args)


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


class LoadRepoList:

    def __init__(self):
        self.username = None
        self.repo_name = None
        self.window = sublime.active_window()
        self.entries = None

    def format_entries(self):
        repo_list = []
        folder_list = sublime.active_window().folders()
        if folder_list:
            for folder_path in folder_list:
                repo_info = github.get_github_repo_info(folder_path)
                if repo_info != (-1, -1):
                    repo_list.append(repo_info)
        entries = ["manually enter repository..."]
        entries.extend(["{}/{}".format(repo[0], repo[1]) for repo in repo_list])
        self.entries = entries

    def show_selection_panel(self, **args):
        _param_on_repo_selection = partial()
        self.window.show_quick_panel(self.entries, self.on_repo_selection)

    def on_done(self, content, **args):
        if '/' in content:
            self.username, self.repo_name = content.split('/')
            self.print_in_view(**args)
        else:
            raise Exception("Please enter repo in the format username/repo_name")

    def on_repo_selection(self, selection, **args):
        if selection >= 0:
            if selection == 0:
                self.window.run_command('hide_panel')
                self.window.show_input_panel('Enter repo in the format username/repo_name:', '', self.on_done, None, None)
            else:
                global issue_list
                self.username, self.repo_name = self.entries[selection].split('/')
                self.print_in_view(**args)

    def print_in_view(self, **args):
        issue_list.find_repo(self.username, self.repo_name)
        print_in_view = issue.PrintListInView(issue_list, **args)
        print_in_view.start()