import sublime
import sublime_plugin
from . import parameter_container as pc
from . import flag_container as fc
from . import global_person_list, global_title_list, global_label_list
from . import repo_info_storage, issue_obj_storage
from .libgit.utils import destock, show_stock
from . import github_logger


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


COMPLETIONS_SCOPES = ['text.html.github.issue']
COMPLETIONS_SCOPES.extend(pc.custom_scope)


class IssueListListener(sublime_plugin.EventListener):

    def on_selection_modified_async(self, view):
        if view.settings().get('syntax') == pc.list_syntax:
            view.add_regions('selected', [view.full_line(view.sel()[0])],
                             "text.issue.list", "dot",
                             sublime.DRAW_SQUIGGLY_UNDERLINE)

    def on_post_text_command(self, view, command, args):
        if view.settings().get('syntax') == pc.list_syntax and command == "change_issue_page":
                highlight(view, fc.pagination_flags)

    def on_pre_close(self, view):
        if view.settings().get('syntax') == pc.issue_syntax:
            try:
                view_id = view.id()
                destock(issue_obj_storage, view_id)
                destock(repo_info_storage, view_id)
                del global_person_list[view_id]
                github_logger.info("delete view related issue stock")
            except:
                pass

    def on_query_completions(self, view, prefix, locations):
        in_scope = any(view.match_selector(locations[0], scope) for scope in COMPLETIONS_SCOPES)
        if in_scope:
            pt = locations[0] - len(prefix) - 1
            ch = view.substr(sublime.Region(pt, pt + 1))
            github_logger.info("the trigger is {}".format(ch))
            if view.substr(view.line(locations[0])).startswith("## Label        :"):
                github_logger.info("find label line!")
                if ch == "@" and pc.label_completion:
                    github_logger.info("wow, find labels!")
                    username, repo_name, _ = show_stock(repo_info_storage, view.id())
                    return [[label, label] for label in global_label_list["{}/{}".format(username, repo_name)] if prefix in label]
            else:
                if ch == "@" and pc.name_completion:
                    search = prefix.replace("@", "")
                    github_logger.info("location is {}".format(str(locations[0])))
                    results = [[key, key] for key in global_person_list[view.id()] if search in key]
                    if len(results) > 0:
                        return (results, sublime.INHIBIT_WORD_COMPLETIONS)
                    else:
                        return results
                elif ch == "#" and pc.title_completion:
                    search = prefix.replace("#", "")
                    github_logger.info("title list is {}".format(repr(global_title_list)))
                    username, repo_name, _ = show_stock(repo_info_storage, view.id())
                    result = [[title, str(number)] for title, number, state in global_title_list["{}/{}".format(username, repo_name)] if search in title]
                    github_logger.info("filtered result is {}".format(repr(result)))
                    if len(result) > 0:
                        return (result, sublime.INHIBIT_WORD_COMPLETIONS)
                    else:
                        return result
                else:
                    pass



