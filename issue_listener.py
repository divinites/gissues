import sublime
import sublime_plugin
from . import parameter_container as pc
from . import flag_container as fc


def highlight(view, flags_dict):
    content = view.substr(sublime.Region(0, view.size()))
    target_regions = []
    for word, value in flags_dict.items():
        if value:
            begin = content.find(word)
            if begin == -1:
                raise Exception("Cannot find the targe word!")
            end = begin + len(word)
            target_regions.append(sublime.Region(begin, end))
            # view.sel().add(target_region)
    view.add_regions("indicator", target_regions, "text", "dot", sublime.DRAW_SQUIGGLY_UNDERLINE)


class IssuePageIndicator(sublime_plugin.EventListener):
    def on_post_text_command(self, view, command, args):
        if view.settings().get('syntax') == pc.list_syntax and command == "change_issue_page":
                highlight(view, fc.pagination_flags)
        else:
            pass


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



