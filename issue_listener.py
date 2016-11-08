import sublime
import sublime_plugin
from . import flag_container as fc
from . import global_person_list, global_title_list, global_label_list, global_commit_list
from . import repo_info_storage, issue_obj_storage
from .libgit.utils import destock, show_stock
from . import log, settings
from . import ISSUE_START, ISSUE_END, HEADER_END, CONTENT_END, ADD_COMMENT


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
    view.add_regions("indicator", target_regions, "text", "dot",
                     sublime.DRAW_SQUIGGLY_UNDERLINE)


# def push_cursor(view, point):
#     new_cursor_position = point.a + 1
#     view.sel().clear()
#     view.sel().add(
#         sublime.Region(new_cursor_position,
#                        new_cursor_position))


class IssueListListener(sublime_plugin.EventListener):

    def on_selection_modified(self, view):
        if view.settings().get('issue_flag'):
            header_flag = False
            current_point = view.sel()[0].a
            for header in (ISSUE_START(),
                           ISSUE_END(),
                           HEADER_END(),
                           CONTENT_END(),
                           ADD_COMMENT()):
                if view.substr(view.line(current_point)).strip() == header:
                    header_flag = True
            header_split = HEADER_END()
            all_lines = view.lines(sublime.Region(0, view.size()))
            if len(all_lines) > 7:
                possible_header = view.lines(sublime.Region(0, view.size()))[:7]
            else:
                possible_header = all_lines
            header_split_line = -1
            for idx, line in enumerate(possible_header):
                if view.substr(line) == header_split:
                    header_split_line = idx
                    break
            if header_split_line > 0:
                log("current cursor is located at {}".format(current_point))
                row, col = view.rowcol(current_point)
                log("find the row {} and the col {}".format(row, col))
                if (row < header_split_line and col < 17) or header_flag:
                    if not view.is_read_only():
                        log("set the view read-only")
                        view.set_read_only(True)
                elif row < header_split_line and col == 17:
                    view.run_command("insert_issue_snippet", {"snippet": " ", "start_point": current_point})
                else:
                    if view.is_read_only():
                        log("set the view writable")
                        view.set_read_only(False)

    def on_selection_modified_async(self, view):
        if view.settings().get('list_flag'):
            view.add_regions('selected', [view.full_line(view.sel()[0])],
                             "text.issue.list", "dot",
                             sublime.DRAW_SQUIGGLY_UNDERLINE)

    def on_post_text_command(self, view, command, args):
        if view.settings().get("list_flag"):
            highlight(view, fc.pagination_flags)

    def on_pre_close(self, view):
        if view.settings().get('issue_flag'):
            try:
                view_id = view.id()
                destock(issue_obj_storage, view_id)
                destock(repo_info_storage, view_id)
                del global_person_list[view_id]
                log("delete view related issue stock")
            except:
                pass

    def on_query_completions(self, view, prefix, locations):
        if view.settings().get('issue_flag'):
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
                    search = prefix.replace("@", "")
                    log("location is {}".format(str(locations[0])))
                    results = []
                    try:
                        results = [[key, key]
                                   for key in global_person_list[view.id()]
                                   if search in key]
                    except KeyError:
                        pass
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
                elif ch == settings.get("commit_completion_trigger", "&") and settings.get("commit_completion", True):
                    username, repo_name, _ = show_stock(repo_info_storage,
                                                        view.id())
                    repo_info = "{}/{}".format(username, repo_name)
                    search = prefix.replace("&", "")
                    log("commit list is {}".format(repr(global_commit_list)))
                    if global_commit_list[repo_info]:
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
