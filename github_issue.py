import sublime
import sublime_plugin
from gissues.libgit import issue


def plugin_loaded():
    global issue_list
    settings = sublime.load_settings("github_issue.sublime-settings")
    issue_list = issue.IssueList(settings)


class ShowGithubIssueListCommand(sublime_plugin.WindowCommand):
    def run(self):
        global issue_list
        issue_list.find_repo()
        list_obj = issue_list.get()
        issue_list.print_list(list_obj)


class NewGithubIssueCommand(sublime_plugin.WindowCommand):
    pass


class CommentGithubIssueCommand(sublime_plugin.WindowCommand):
    pass


class AutoSyncIssueListener(sublime_plugin.EventListener):

    def on_post_save_async(view):
        pass
