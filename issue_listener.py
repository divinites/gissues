import sublime
import sublime_plugin
from . import flag_container as fc
from . import global_person_list, global_title_list, global_label_list, global_commit_list
from . import repo_info_storage, issue_obj_storage
from .libgit.utils import destock, show_stock
from . import log, settings, COMPLETIONS_SCOPES


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
    view.add_regions("indicator", target_regions, "text", "dot",
                     sublime.DRAW_SQUIGGLY_UNDERLINE)


class IssueListListener(sublime_plugin.EventListener):

    def on_selection_modified(self, view):
        if view.settings().get('syntax') == settings.get("syntax", "Packages/GitHubIssue/Issue.sublime-syntax"):
            header_split = "*----------Content----------*"
            all_lines = view.lines(sublime.Region(0, view.size()))
            if len(all_lines) > 7:
                possible_header = view.lines(sublime.Region(0, view.size()))[:
                                                                             7]
            else:
                possible_header = all_lines
            header_split_line = -1
            for idx, line in enumerate(possible_header):
                if view.substr(line) == header_split:
                    header_split_line = idx
                    break
            if header_split_line > 0:
                current_point = view.sel()[0].a
                log("current cursor is located at {}".format(current_point))
                row, col = view.rowcol(current_point)
                log("find the row {} and the col {}".format(row, col))
                if row < header_split_line and col < 19:
                    log("starting pushing back the cursor")
                    new_cursor_position = view.line(current_point).a + 18
                    log("push back the cursor to {}".format(
                        new_cursor_position))
                    view.sel().clear()
                    view.sel().add(
                        sublime.Region(new_cursor_position,
                                       new_cursor_position))
                elif row == header_split_line and col < 29:
                    new_cursor_position = view.line(current_point).a + 29
                    log("push back the cursor to {}".format(
                        new_cursor_position))
                    view.sel().clear()
                    view.sel().add(
                        sublime.Region(new_cursor_position,
                                       new_cursor_position))
                else:
                    pass

    def on_selection_modified_async(self, view):
        if view.settings().get('syntax') == "Packages/GitHubIssue/list.sublime-syntax":
            view.add_regions('selected', [view.full_line(view.sel()[0])],
                             "text.issue.list", "dot",
                             sublime.DRAW_SQUIGGLY_UNDERLINE)

    def on_post_text_command(self, view, command, args):
        if view.settings().get(
                'syntax') == "Packages/GitHubIssue/list.sublime-syntax" and command == "change_issue_page":
            highlight(view, fc.pagination_flags)

    def on_pre_close(self, view):
        if view.settings().get('syntax') == settings.get("syntax", "Packages/GitHubIssue/Issue.sublime-syntax"):
            try:
                view_id = view.id()
                destock(issue_obj_storage, view_id)
                destock(repo_info_storage, view_id)
                del global_person_list[view_id]
                log("delete view related issue stock")
            except:
                pass

    def on_query_completions(self, view, prefix, locations):
        in_scope = any(
            view.match_selector(locations[0], scope)
            for scope in COMPLETIONS_SCOPES)
        if in_scope:
            pt = locations[0] - len(prefix) - 1
            ch = view.substr(sublime.Region(pt, pt + 1))
            log("the trigger is {}".format(ch))
            if view.substr(view.line(locations[0])).startswith(
                    "## Label        :"):
                log("find label line!")
                username, repo_name, _ = show_stock(repo_info_storage,
                                                    view.id())
                repo_info = "{}/{}".format(username, repo_name)
                if ch == "@" and settings.get("label_completion", True):
                    log("wow, find labels!")
                    return [[label, label]
                            for label in global_label_list[repo_info]
                            if prefix in label]
            else:
                if ch == "@" and settings.get("user_completion", True):
                    username, repo_name, _ = show_stock(repo_info_storage,
                                                        view.id())
                    repo_info = "{}/{}".format(username, repo_name)
                    search = prefix.replace("@", "")
                    log("location is {}".format(str(locations[0])))
                    results = [[key, key]
                               for key in global_person_list[view.id()]
                               if search in key]
                    if len(results) > 0:
                        return (results, sublime.INHIBIT_WORD_COMPLETIONS)
                    else:
                        return results
                elif ch == "#" and settings.get("issue_title_completion", True):
                    username, repo_name, _ = show_stock(repo_info_storage,
                                                        view.id())
                    repo_info = "{}/{}".format(username, repo_name)
                    search = prefix.replace("#", "")
                    log("title list is {}".format(repr(global_title_list)))
                    result = [[title, str(number)]
                              for title, number, state in global_title_list[
                                  repo_info] if search in title]
                    log("filtered result is {}".format(repr(result)))
                    if len(result) > 0:
                        return (result, sublime.INHIBIT_WORD_COMPLETIONS)
                    else:
                        return result
                elif ch == settings.get("commit_completion_trigger", ":") and settings.get("commit_completion", True):
                    username, repo_name, _ = show_stock(repo_info_storage,
                                                        view.id())
                    repo_info = "{}/{}".format(username, repo_name)
                    search = prefix.replace(":", "")
                    log("commit list is {}".format(repr(global_commit_list)))
                    result = [[message, ' ' + sha]
                              for sha, message in global_commit_list[repo_info]
                              if search in message]
                    log("filtered commit result is {}".format(repr(result)))
                    if len(result) > 0:
                        return (result, sublime.INHIBIT_WORD_COMPLETIONS)
                    else:
                        return result
                else:
                    pass
