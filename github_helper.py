import sublime_plugin
import sublime
# from . import parameter_container as pc
# from . import flag_container as fc
# from . import repo_info_storage



class InsertIssueSnippetCommand(sublime_plugin.TextCommand):
    def run(self, edit, start_point=0, snippet=None):
        if snippet:
            self.view.insert(edit, start_point, snippet)


class EraseSnippetCommand(sublime_plugin.TextCommand):
    def run(self, edit, start_point=0, end_point=0):
        self.view.erase(edit, sublime.Region(start_point, end_point))


class ReplaceSnippetCommand(sublime_plugin.TextCommand):
    def run(self, edit, start_point, end_point, snippet):
        if snippet:
            self.view.replace(edit, sublime.Region(start_point, end_point), snippet)
