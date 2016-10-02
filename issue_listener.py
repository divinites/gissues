import sublime
import sublime_plugin


if int(sublime.version()) >= 3118:
    class IssueListListener(sublime_plugin.ViewEventListener):
        def __init__(self, view):
            self.view = view

        @classmethod
        def is_applicable(cls, settings):
            syntax = settings.get('syntax').split('/')[-1]
            return syntax == 'list.sublime-syntax'

        def on_selection_modified_async(self):
            self.view.add_regions(
                'selected', [self.view.full_line(self.view.sel()[0])],
                "text.issue.list", "dot", sublime.DRAW_SQUIGGLY_UNDERLINE)

else:
    class OldIssueListListener(sublime_plugin.EventListener):
        def on_selection_modified_async(self, view):
            syntax_name = view.settings().get('syntax').split('/')[-1]
            if syntax_name == 'list.sublime-syntax':
                view.add_regions('selected', [view.full_line(view.sel()[0])],
                                 "text.issue.list", "dot",
                                 sublime.DRAW_SQUIGGLY_UNDERLINE)



