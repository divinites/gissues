import sublime
import sublime_plugin
import os


class IssueListListener(sublime_plugin.EventListener):
    def on_selection_modified_async(self, view):
        syntax_name = view.settings().get('syntax').split('/')[-1]
        if syntax_name == 'list.sublime-syntax':
            view.add_regions('selected', [view.full_line(view.sel()[0])], "text.issue.list", "dot", sublime.DRAW_SQUIGGLY_UNDERLINE)