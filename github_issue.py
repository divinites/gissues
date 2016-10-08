import sublime
import sublime_plugin
from .libgit import issue
from .libgit import utils
from .libgit import github
from . import parameter_container as pc
from . import flag_container as fc
from . import github_logger
from . import repo_info_storage, issue_obj_storage
from . import global_person_list, global_title_list
import re
import logging
from queue import Queue
from functools import partial

active_issue_obj = None


def plugin_loaded():
    global active_issue_obj
    settings = sublime.load_settings("github_issue.sublime-settings")
    pc.read_settings(settings)
    # pc.line_ends = find_line_ends()
    pc.line_ends = "\n"
    logging.basicConfig(level=logging.DEBUG if pc.debug_flag == 0 else logging.INFO)
    active_issue_obj = issue.IssueObj(settings)


class IssueStocks(sublime_plugin.EventListener):
    def on_pre_close(self, view):
        if view.settings().get('syntax') == pc.issue_syntax:
            try:
                view_id = view.id()
                utils.destock(issue_obj_storage, view_id)
                utils.destock(repo_info_storage, view_id)
                del global_person_list[view_id]
                github_logger.info("delete view related issue stock")
            except:
                pass


class ChangeIssuePageCommand(sublime_plugin.TextCommand):
    def is_enabled(self):
        syntax_name = self.view.settings().get('syntax')
        if syntax_name == pc.list_syntax:
            return True
        return False

    def run(self, edit, command):
        global active_issue_obj
        github_logger.info("we have the command {}".format(command))
        view_text = "_{}_".format(command.capitalize())
        github_logger.info("we are matching {}".format(view_text))
        for flag in fc.pagination_flags.keys():
            fc.pagination_flags[flag] = False
            github_logger.info("{} set to False".format(flag))
            if flag == view_text:
                github_logger.info("flag matches, set {} to True".format(flag))
                fc.pagination_flags[flag] = True
        print_next_page_issues = issue.PrintListInView(self.view, active_issue_obj, repo_info_storage, command, False)
        print_next_page_issues.start()


class ShowGithubIssueListCommand(sublime_plugin.WindowCommand):
    def run(self, **args):
        repo_loader = LoadRepoList()
        repo_loader.format_entries()
        github_logger.info("I am showing the issue list!")
        repo_loader.show_panel_then_print_list(**args)


class ShowGithubIssueCommand(sublime_plugin.WindowCommand):
    def is_enabled(self):
        current_view = sublime.active_window().active_view()
        syntax_name = current_view.settings().get('syntax')
        if syntax_name == pc.list_syntax:
            return True
        return False

    def run(self):
        global active_issue_obj
        view = sublime.active_window().active_view()
        target_line = view.substr(view.line(view.sel()[0]))
        match_id = re.search(r'^\d+(?=\s)', target_line)
        issue_number = int(match_id.group(0))
        try:
            active_issue_obj.find_repo(view, repo_info_storage)
            repo_info = (active_issue_obj.username, active_issue_obj.repo_name, None)
            print_in_view = issue.PrintIssueInView(
                active_issue_obj, issue_number, issue_obj_storage, repo_info, repo_info_storage)
            print_in_view.start()
        except:
            # repo_info_storage.put(repo_info_dictionary)
            raise Exception("Cannot find repo information!")


class NewGithubIssueCommand(sublime_plugin.WindowCommand):
    def run(self):
        repo_loader = LoadRepoList()
        repo_loader.format_entries()
        repo_loader.show_panel_then_create_issue()


class PostGithubIssueCommand(sublime_plugin.WindowCommand):
    def is_enabled(self):
        self.view = sublime.active_window().active_view()
        syntax_name = self.view.settings().get('syntax')
        if syntax_name == pc.issue_syntax:
            return True
        return False

    def run(self):
        global active_issue_obj
        active_issue_obj.find_repo(self.view, repo_info_storage)
        post_issue = issue.PostNewIssue(
            issue_list=active_issue_obj, issue_storage=issue_obj_storage)
        post_issue.start()


class UpdateGithubIssueCommand(sublime_plugin.WindowCommand):
    def is_enabled(self):
        self.view = sublime.active_window().active_view()
        syntax_name = self.view.settings().get('syntax')
        if syntax_name == pc.issue_syntax:
            return True
        return False

    def run(self):
        global active_issue_obj
        if not repo_info_storage.empty():
            active_issue_obj.find_repo(self.view, repo_info_storage)
        else:
            raise Exception("Error in obtaining Repo Info!")
        update_issue = issue.UpdateIssue(
            issue_list=active_issue_obj, issue_storage=issue_obj_storage)
        update_issue.start()


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
            self.username, self.repo_name = [x.strip() for x in content.split('/')]
            github_logger.info("username is " + str(self.username))
            github_logger.info("repo name is " + str(self.repo_name))
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
        global active_issue_obj
        active_issue_obj.get_repo(self.username, self.repo_name)
        issue_view = utils.print_list_framework()
        acquire_list = issue.AcquireIssueTitle(active_issue_obj)
        acquire_list.start()
        print_in_view = issue.PrintListInView(issue_view, active_issue_obj,
                                              repo_info_storage, **args)
        print_in_view.start()

    def create_issue(self):
        create_new_issue_view()
        view_id = sublime.active_window().active_view().id()
        utils.restock(repo_info_storage, view_id, (self.username, self.repo_name, None))


def create_new_issue_view():
    snippet = ''
    snippet += "# Title         : " + pc.line_ends
    snippet += "## Assignee     : " + pc.line_ends
    snippet += "*" + '-' * 10 + "Content" + '-' * 10 + "*" + pc.line_ends
    snippet += pc.line_ends
    snippet += "*" + '-' * 10 + "END" + '-' * 10 + "*" + pc.line_ends
    view = sublime.active_window().new_file()
    github_logger.info("Create new view to write the issue")
    view.run_command("set_file_type",
                      {"syntax":
                       pc.issue_syntax})
    github_logger.info("new issue will have a syntax {}".format(pc.issue_syntax))
    view.run_command("insert_issue_snippet", {"snippet": snippet})
    view.sel().clear()
    start_point = view.text_point(0, 18)
    view.sel().add(sublime.Region(start_point))
    view.show(start_point)
    view.set_encoding('UTF-8')
    github_logger.info("insert a blank issue")
    view.set_scratch(True)


def find_line_ends():
    system_setting = sublime.load_settings("Preferences.sublime-settings").get('default_line_ending')
    if system_setting != 'system':
        if system_setting == 'windows':
            return '\r\n'
        else:
            return '\n'
    else:
        if sublime.platform() == 'windows':
            return '\r\n'
        else:
            return '\n'
