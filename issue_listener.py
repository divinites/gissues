import sublime
import sublime_plugin
import os


class IssueListListener(sublime_plugin.EventListener):
    def on_selection_modified(self, view):
        _, syntax_name = os.path.split(view.settings().get('syntax'))
        if syntax_name == 'list.sublime-syntax':
            view.add_regions('selected', [view.line(view.sel()[0])], "text.issue.list", "dot", sublime.DRAW_SQUIGGLY_UNDERLINE)