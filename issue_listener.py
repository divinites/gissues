import sublime
import sublime_plugin
from . import parameter_container as pc


if int(sublime.version()) >= 3118:
    class IssueListListener(sublime_plugin.ViewEventListener):
        def __init__(self, view):
            self.view = view

        @classmethod
        def is_applicable(cls, settings):
            if settings.get('syntax') == pc.list_syntax:
                return True
            return False

        def on_selection_modified_async(self):
            self.view.add_regions(
                'selected', [self.view.full_line(self.view.sel()[0])],
                "text.issue.list", "dot", sublime.DRAW_SQUIGGLY_UNDERLINE)

else:
    class OldIssueListListener(sublime_plugin.EventListener):
        def on_selection_modified_async(self, view):
            if view.settings.get('syntax') == pc.list_syntax:
                view.add_regions('selected', [view.full_line(view.sel()[0])],
                                 "text.issue.list", "dot",
                                 sublime.DRAW_SQUIGGLY_UNDERLINE)



