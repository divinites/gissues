import sublime
import sublime_plugin
from .libgit import issue
from .libgit import utils
from .libgit import github
import re
import os
import logging
from queue import Queue
from functools import partial


def plugin_loaded():
    global active_issue_obj, issue_obj_storage, repo_info_storage
    settings = sublime.load_settings("github_issue.sublime-settings")
    repo_info_storage = Queue()
    issue_obj_storage = Queue()
    active_issue_obj = issue.IssueObj(settings)
    issue_obj_storage.put({})
    repo_info_storage.put({})


class ShowGithubIssueListCommand(sublime_plugin.WindowCommand):
    def run(self, **args):
        repo_loader = LoadRepoList()
        repo_loader.format_entries()
        logging.debug("I am showing the issue list!")
        repo_loader.show_panel_then_print_list(**args)


class ShowGithubIssueCommand(sublime_plugin.WindowCommand):
    def is_enabled(self):
        current_view = sublime.active_window().active_view()
        _, syntax_name = os.path.split(current_view.settings().get('syntax'))
        if syntax_name == "list.sublime-syntax":
            return True
        return False

    def run(self):
        global active_issue_obj, issue_obj_storage, repo_info_storage
        view = sublime.active_window().active_view()
        target_line = view.substr(view.line(view.sel()[0]))
        match_id = re.search(r'^\d+(?=\s)', target_line)
        issue_number = int(match_id.group(0))
        try:
            active_issue_obj.find_repo(view, repo_info_storage)
            print_in_view = issue.PrintIssueInView(
                active_issue_obj, issue_number, issue_obj_storage)
            print_in_view.start()
        except:
            # repo_info_storage.put(repo_info_dictionary)
            raise Exception("Cannot find repo information!")


class NewGithubIssueCommand(sublime_plugin.WindowCommand):
    def run(self):
        global repo_info_storage
        repo_loader = LoadRepoList()
        repo_loader.format_entries()
        repo_loader.show_panel_then_create_issue()


class PostGithubIssueCommand(sublime_plugin.WindowCommand):
    def is_enabled(self):
        self.view = sublime.active_window().active_view()
        _, syntax_name = os.path.split(self.view.settings().get('syntax'))
        if syntax_name == "issue.tmLanguage":
            return True
        return False

    def run(self):
        global active_issue_obj, issue_obj_storage, repo_info_storage
        active_issue_obj.find_repo(self.view, repo_info_storage)
        post_issue = issue.PostNewIssue(
            issue_list=active_issue_obj, issue_dict=issue_obj_storage)
        post_issue.start()


class UpdateGithubIssueCommand(sublime_plugin.WindowCommand):
    def is_enabled(self):
        self.view = sublime.active_window().active_view()
        _, syntax_name = os.path.split(self.view.settings().get('syntax'))
        if syntax_name == "issue.tmLanguage":
            return True
        return False

    def run(self):
        global active_issue_obj, issue_obj_storage, repo_info_storage
        active_issue_obj.find_repo(self.view, repo_info_storage)
        update_issue = issue.UpdateIssue(
            issue_list=active_issue_obj, issue_dict=issue_obj_storage)
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
        entries.extend(
            ["{}/{}".format(repo[0], repo[1]) for repo in repo_list])
        self.entries = entries

    def show_panel_then_print_list(self, **args):
        _param_on_repo_selection = partial(
            self.on_repo_selection,
            subsequent_action=self.print_issue_list,
            **args)
        self.window.show_quick_panel(self.entries, _param_on_repo_selection)

    def show_panel_then_create_issue(self):
        _param_on_repo_selection = partial(
            self.on_repo_selection,
            subsequent_action=self.create_issue)

        self.window.show_quick_panel(self.entries, _param_on_repo_selection)

    def on_enter_repo_info(self, content, subsequent_action, **args):
        if '/' in content:
            self.username, self.repo_name = content.split('/')
            subsequent_action(**args)
        else:
            raise Exception(
                "Please enter repo in the format username/repo_name")

    def on_repo_selection(self, selection, subsequent_action, **args):
        if selection >= 0:
            if selection == 0:
                self.window.run_command('hide_panel')
                _param_on_enter_repo_info = partial(
                    self.on_enter_repo_info,
                    subsequent_action=subsequent_action,
                    **args)
                self.window.show_input_panel(
                    'Enter repo in the format username/repo_name:', '',
                    _param_on_enter_repo_info, None, None)
            else:
                self.username, self.repo_name = self.entries[selection].split(
                    '/')
                subsequent_action(**args)

    def print_issue_list(self, **args):
        global active_issue_obj, repo_info_storage
        active_issue_obj.get_repo(self.username, self.repo_name)
        print_in_view = issue.PrintListInView(active_issue_obj,
                                              repo_info_storage, **args)
        print_in_view.start()

    def create_issue(self):
        global repo_info_storage
        utils.create_new_issue_view()
        view_id = sublime.active_window().active_view().id()
        repo_dictionary = repo_info_storage.get()
        repo_dictionary[view_id] = (self.username, self.repo_name)
        repo_info_storage.put(repo_dictionary)
