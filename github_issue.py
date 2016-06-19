import sublime
import sublime_plugin
import os



class ShowGithubIssueListCommand(sublime_plugin.WindowCommand):
    pass


class NewGithubIssueCommand(sublime_plugin.WindowCommand):
    pass


class CommentGithubIssueCommand(sublime_plugin.WindowCommand):
    pass


class AutoSyncIssueListener(sublime_plugin.EventListener):

    def on_post_save_async(view):
        pass
